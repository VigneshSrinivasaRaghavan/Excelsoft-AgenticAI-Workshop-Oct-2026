import json
from pathlib import Path
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import TestCaseState
from src.core import get_langchain_llm, pick_requirement
from src.prompts.testcase_prompts import TESTCASE_SYSTEM_PROMPT

# Setup
ROOT = Path(__file__).resolve().parents[3]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated_langgraph"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Langchain components
llm = get_langchain_llm()
prompt_template = ChatPromptTemplate.from_messages([
    ("system", TESTCASE_SYSTEM_PROMPT),
    ("user", "Requirements:\n\n{requirement}")
])
parser = StrOutputParser()
chain = prompt_template | llm | parser


# Build Langgraph nodes
def read_requirement(state:TestCaseState) -> TestCaseState:
    req_file = pick_requirement(None, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    print(f"Read requirement: {req_file.name}")
    return {"requirement": requirement}


def generate_tests(state: TestCaseState) -> TestCaseState:
    """Generate test cases with LLM."""
    print("Generating test cases with LLM...")

    try:
        # Call LLM
        response = chain.invoke({"requirement": state["requirement"]})

        # Parse JSON
        testcases = json.loads(response)
        print(f"Generated {len(testcases)} test cases")

        return {"test_cases": testcases, "errors": []}

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return {"test_cases": [], "errors": [f"JSON parse error: {e}"]}
    except Exception as e:
        print(f"LLM call failed: {e}")
        return {"test_cases": [], "errors": [f"LLM error: {e}"]}


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
    if 'steps' in df.columns:
        df['steps'] = df['steps'].apply(lambda x: ' | '.join(x) if isinstance(x, list) else x)

    csv_file = OUT_DIR / "test_cases.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved CSV: {csv_file.relative_to(ROOT)}")

    return {}