import json
from pathlib import Path
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import TestCaseState
from src.core import get_langchain_llm, pick_requirement, search_vector_store
from src.prompts.testcase_prompts import TESTCASE_SYSTEM_PROMPT

# Setup
ROOT = Path(__file__).resolve().parents[3]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated_langgraph"
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
    req_file = pick_requirement(None, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    print(f"Read requirement: {req_file.name}")
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
    """Generate test cases with RAG context."""
    print("Generating test cases with RAG context...")

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
        print(f"Generated {len(testcases)} test cases using RAG")

        return {
            "test_cases": testcases,
            "errors": [],
            "retry_count": state.get("retry_count", 0),
            "validation_status": "pending"
        }

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return {
            "test_cases": [],
            "errors": [f"JSON parse error: {e}"],
            "retry_count": state.get("retry_count", 0),
            "validation_status": "fail"
        }
    except Exception as e:
        print(f"LLM call failed: {e}")
        return {
            "test_cases": [],
            "errors": [f"LLM error: {e}"],
            "retry_count": state.get("retry_count", 0),
            "validation_status": "fail"
        }



def save_outputs(state: TestCaseState) -> TestCaseState:
    """Save test cases to files."""
    test_cases = state["test_cases"]

    if not test_cases:
        print("No test cases to save")
        return {}

    # Save raw JSON
    raw_file = OUT_DIR / "raw_output.txt"
    raw_file.write_text(json.dumps(test_cases, indent=2), encoding="utf-8")
    print(f"Saved raw JSON: {raw_file.relative_to(ROOT)}")

    # Save CSV
    df = pd.DataFrame(test_cases)
    if "steps" in df.columns:
        df["steps"] = df["steps"].apply(
            lambda x: " | ".join(x) if isinstance(x, list) else x
        )

    csv_file = OUT_DIR / "test_cases.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved CSV: {csv_file.relative_to(ROOT)}")

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
    logger.warning(f"🔄 Retry attempt {retry_count}/3")

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