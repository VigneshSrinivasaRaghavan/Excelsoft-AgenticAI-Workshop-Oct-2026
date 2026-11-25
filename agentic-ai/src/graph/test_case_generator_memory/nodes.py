import json
from pathlib import Path
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import TestCaseState
from src.core import get_langchain_llm, pick_requirement, search_vector_store
from src.prompts.testcase_prompts import TESTCASE_SYSTEM_PROMPT
from src.core import PersistentMemory
# Long Term Memory Object
persistent_memory = PersistentMemory(collection_name="testcase_generator_memory")

# Setup
ROOT = Path(__file__).resolve().parents[3]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated_memory"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Langchain components
llm = get_langchain_llm()
prompt_template = ChatPromptTemplate.from_messages(
    [("system", TESTCASE_SYSTEM_PROMPT), ("user", "Requirements:\n\n{requirement}")]
)
parser = StrOutputParser()
chain = prompt_template | llm | parser


# Build Langgraph nodes
def read_requirement(state: TestCaseState) -> TestCaseState:
    """Read requirement file on first run. Skip if requirement already set by driver or follow-up."""
    if state.get("requirement"):
        if state.get("conversation_history"):
            # Actual follow-up — user typed an instruction in the CLI loop
            print(f"Follow-up instruction: {state['requirement'][:60]}...")
        else:
            # Requirement passed via CLI arg on first run
            print(f"Requirement loaded from file.")
        return {}
    req_file = pick_requirement(None, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    return {"requirement": requirement}

def retrieve_context(state: TestCaseState) -> TestCaseState:
    """Retrieve relevant testing guidelines from knowledge base."""

    requirement = state["requirement"]
    print("Retrieving relevant testing guidelines...")

    # Search vector store
    results = search_vector_store(
        query=f"test case guidelines for: {requirement[:200]}",
        top_k=3
    )

    # Format context
    context_parts = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown').split('/')[-1]
        similarity = 1 - score

        print(f"Retrieved [{i}] {source} (similarity: {similarity:.2f})")

        context_parts.append(f"[Source: {source}]\\n{doc.page_content}\\n")

    retrieved_context = "\\n---\\n".join(context_parts)

    print(f"Retrieved {len(results)} relevant documents")

    return {"retrieved_context": retrieved_context}



def generate_tests(state: TestCaseState) -> TestCaseState:
    """Generate test cases using RAG + STM + LTM context."""
    requirement = state["requirement"]
    retrieved_context = state.get("retrieved_context", "")
    past_patterns = state.get("past_patterns", "")
    conversation_history = state.get("conversation_history", [])
    existing_test_cases = state.get("test_cases", [])  # restored from checkpoint by MemorySaver

    # Build conversation context from STM (last 6 messages)
    conversation_text = ""
    if conversation_history:
        lines = [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]]
        conversation_text = "\n".join(lines)

    # Compose prompt — three context sources + requirement
    user_message = f"""COMPANY TESTING GUIDELINES:
{retrieved_context}
"""
    if past_patterns:
        user_message += f"""
PAST TEST CASE PATTERNS (from previous sessions):
{past_patterns}
"""

    if conversation_history and existing_test_cases:
        # Follow-up mode — LLM must ADD to existing test cases, not regenerate
        existing_json = json.dumps(existing_test_cases, indent=2)
        user_message += f"""
CONVERSATION HISTORY (current session):
{conversation_text}

EXISTING TEST CASES (already generated in this session):
{existing_json}

FOLLOW-UP INSTRUCTION: {requirement}
Add the requested test cases to the existing list above.
Return ALL test cases (existing + new ones) as a single JSON array.
Do NOT regenerate existing ones — only append new ones with the next available TC IDs.
"""
    else:
        # First run — generate fresh
        user_message += f"""
REQUIREMENT:
{requirement}
"""

    try:
        response = chain.invoke({"requirement": user_message})
        testcases = json.loads(response)

        # Update STM — append this turn to conversation history
        updated_history = list(conversation_history)
        updated_history.append({"role": "user", "content": requirement})
        tc_ids = ", ".join(tc.get("id", "") for tc in testcases)
        updated_history.append({
            "role": "agent",
            "content": f"Generated {len(testcases)} test case(s): {tc_ids}"
        })

        return {
            "test_cases": testcases,
            "errors": [],
            "conversation_history": updated_history
        }

    except json.JSONDecodeError as e:
        return {"test_cases": [], "errors": [f"JSON parse error: {e}"]}
    except Exception as e:
        return {"test_cases": [], "errors": [f"LLM error: {e}"]}


def save_outputs(state: TestCaseState) -> TestCaseState:
    """Save test cases to files. LTM save happens in driver after user confirms."""
    from datetime import datetime
    test_cases = state["test_cases"]

    if not test_cases:
        return {}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw JSON — timestamped so sessions don't overwrite each other
    raw_file = OUT_DIR / f"raw_output_{timestamp}.txt"
    raw_file.write_text(json.dumps(test_cases, indent=2), encoding="utf-8")

    # Save CSV — timestamped
    df = pd.DataFrame(test_cases)
    if "steps" in df.columns:
        df["steps"] = df["steps"].apply(
            lambda x: " | ".join(x) if isinstance(x, list) else x
        )
    csv_file = OUT_DIR / f"test_cases_{timestamp}.csv"
    df.to_csv(csv_file, index=False)

    print(f"Saved {len(test_cases)} test cases to {OUT_DIR}")
    return {}



def validate_tests(state: TestCaseState) -> TestCaseState:
    test_cases = state.get("test_cases", [])
    print(f"Validating {len(test_cases)} test cases...")

    if len(test_cases) < 5:
        print("Less than 5 test cases. Validation failed.")
        return {"validation_status": "fail"}

    required_fields = ["id", "title", "steps", "expected", "priority"]
    for test in test_cases:
        missing_fields = [field for field in required_fields if field not in test]
        if missing_fields:
            print(f"Missing fields: {missing_fields} in test case: {test['id']}")
            return {"validation_status": "fail"}

        if not isinstance(test["steps"], list) or len(test["steps"]) < 2:
            print(f"Invalid steps in test case: {test['id']}")
            return {"validation_status": "fail"}

    print("Validation successful.")
    return {"validation_status": "pass"}


def retry_generate(state: TestCaseState) -> TestCaseState:
    """Retry test case generation with RAG context."""
    retry_count = state.get("retry_count", 0) + 1
    print(f"🔄 Retry attempt {retry_count}/3")

    requirement = state["requirement"]
    context = state.get("retrieved_context", "")

    # Build enhanced prompt with context
    user_message = f"""Based on the following company testing guidelines:

{context}

---

Now generate test cases for this requirement:

{requirement}"""

    try:
        response = chain.invoke({"requirement": user_message})
        testcases = json.loads(response)
        print(f"Regenerated {len(testcases)} test cases with RAG")

        return {
            "test_cases": testcases,
            "errors": [],
            "retry_count": retry_count,
            "validation_status": "pending"
        }

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return {
            "test_cases": [],
            "errors": [f"JSON parse error: {e}"],
            "retry_count": retry_count,
            "validation_status": "fail"
        }
    except Exception as e:
        print(f"LLM call failed: {e}")
        return {
            "test_cases": [],
            "errors": [f"LLM error: {e}"],
            "retry_count": retry_count,
            "validation_status": "fail"
        }


def route_after_validation(state: TestCaseState) -> TestCaseState:
    validation_status = state.get("validation_status", "pending")
    retry_count = state.get("retry_count", 0)

    # If validation passed, then proceed to save the test cases
    if validation_status == "pass":
        print("Routing to Preview for human approval...")
        return "preview"

    # If Failed and retry count is less than 3, then retry the generation
    if validation_status == "fail" and retry_count < 3:
        print(f"Validation failed. Retrying generation... (attempt {retry_count + 1})")
        return "retry"

    # If maximum retries reached, then stop the generation
    if validation_status == "fail" and retry_count >= 3:
        print("Maximum retries reached. Stopping the generation.")
        return "preview" # In Real time agent creation using return "stop"

def show_preview(state: TestCaseState) -> TestCaseState:
    test_cases = state.get("test_cases", [])
    print("\n" + "="*60)
    print("TEST CASES PREVIEW - AWAITING APPROVAL")
    print("="*60)

    for i, tc in enumerate(test_cases, 1):
        print(f"\n[{i}] {tc.get('id', 'N/A')}: {tc.get('title', 'N/A')}")
        print(f"    Priority: {tc.get('priority', 'N/A')}")
        print(f"    Steps: {len(tc.get('steps', []))} steps")
        print(f"    Expected: {tc.get('expected', 'N/A')[:50]}...")

    print("\n" + "="*60)
    print(f"Total: {len(test_cases)} test cases generated")
    print("="*60 + "\n")

def _show_full_details(state: TestCaseState):
    """Show complete test case details."""
    test_cases = state.get("test_cases", [])

    print("\n" + "="*60)
    print("FULL TEST CASE DETAILS")
    print("="*60)

    for i, tc in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"Test Case #{i}")
        print(f"{'─'*60}")
        print(f"ID:       {tc.get('id', 'N/A')}")
        print(f"Title:    {tc.get('title', 'N/A')}")
        print(f"Priority: {tc.get('priority', 'N/A')}")
        print(f"\nSteps:")
        for j, step in enumerate(tc.get('steps', []), 1):
            print(f"  {j}. {step}")
        print(f"\nExpected Result:")
        print(f"  {tc.get('expected', 'N/A')}")

    print("\n" + "="*60 + "\n")

def human_approval(state: TestCaseState) -> TestCaseState:
    print("\n🤔 What would you like to do?")
    print("  1. APPROVE - Save test cases")
    print("  2. REJECT - Regenerate test cases")
    print("  3. VIEW - Show full details")

    while True:
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            print("Test cases approved. Saving...")
            return {
                "human_approval": "approved",
                "human_feedback": "Test cases approved by human"
            }

        elif choice == "2":
            feedback = input("Why reject? : ").strip()
            return {
                "human_approval": "rejected",
                "human_feedback": feedback or "No feedback provided"
            }

        elif choice == "3":
            _show_full_details(state)
            continue # Ask again for approval

        else:
            print("Invalid choice. Please try again.")

def route_after_human_approval(state: TestCaseState) -> TestCaseState:
    approval = state.get("human_approval", "pending")

    if approval == "approved":
        print("Test cases approved. Saving...")
        return "save"
    
    elif approval == "rejected":
        print("Test cases rejected. Regenerating...")
        return "retry"
    
    else:
        print("Invalid approval status. Stopping the generation.")
        return "save" # In Real time agent creation using return "stop"


def load_memories(state: TestCaseState) -> TestCaseState:
    """Load STM (from state) and LTM (from ChromaDB) before generation."""
    requirement = state.get("requirement", "")
    conversation_history = state.get("conversation_history", [])

    # STM is already in state — restored automatically by MemorySaver
    print(f"Loaded conversation history: {len(conversation_history)} message(s)")

    # LTM — semantic search for past test patterns
    past_patterns = persistent_memory.get_context(
        query=f"test case patterns for {requirement[:200]}",
        top_k=3
    )

    return {"past_patterns": past_patterns}