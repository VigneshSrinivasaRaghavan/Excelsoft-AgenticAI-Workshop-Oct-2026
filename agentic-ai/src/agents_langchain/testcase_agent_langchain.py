import sys
from pathlib import Path
from src.core import get_langchain_llm, pick_requirement, save_as_csv
import json

# Langchain Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from src.prompts.testcase_prompts import TESTCASE_SYSTEM_PROMPT

# Project paths
ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_langchain"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system",TESTCASE_SYSTEM_PROMPT),
    ("user","Requirement:\\n\\n{requirement_placeholder}")
])

# Get the LLM
llm = get_langchain_llm()

# Get the output parser
parser = JsonOutputParser()

# Build the chain
chain = prompt_template | llm | parser

def main():
    # 1. Pick requirement file
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    req_file = pick_requirement(file_arg, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")

    print(f"📄 Processing: {req_file.name}")

    # 2. Run the chain
    print("🤖 Calling LLM...")
    test_cases = chain.invoke({"requirement_placeholder": requirement})

    # 3. Save the testcases
    raw_file = OUT_DIR / "raw_output_langchain.txt"
    raw_file.write_text(json.dumps(test_cases, indent=2), encoding="utf-8")

    # 4. Convert to CSV
    csv_file = OUT_DIR / "test_cases_langchain.csv"
    save_as_csv(test_cases, csv_file)

    # 5. Print the results
    print(f"✅ Generated {len(test_cases)} test cases")
    print(f"📝 Raw output: {raw_file.relative_to(ROOT)}")
    print(f"📊 CSV saved: {csv_file.relative_to(ROOT)}")

if __name__ == "__main__":
    main()