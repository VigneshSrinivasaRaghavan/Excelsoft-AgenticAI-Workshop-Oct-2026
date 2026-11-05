import sys
from pathlib import Path
"""Test case generator agent."""

from src.core import chat, parse_json_safely, pick_requirement, save_as_csv

# Project paths
ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# System prompt
SYSTEM_PROMPT = """You are a QA engineer. Generate test cases from requirements.

Return ONLY a JSON array with this structure:
[
  {
    "id": "TC-001",
    "title": "Short test title",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "expected": "Expected result",
    "priority": "High"
  }
]

Rules:
- Return 5 test cases
- Cover positive and negative scenarios
- Include edge cases
- Keep steps clear and actionable
- Priority: High, Medium, or Low
- Return ONLY JSON, no markdown fences"""

def main():
    """Run the test case generator agent."""

    # 1. Pick requirement file
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    req_file = pick_requirement(file_arg, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")

    print(f"📄 Processing: {req_file.name}")

    # 2. Build messages for LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Requirement:\\n\\n{requirement}"}
    ]

    # 3. Call LLM
    print("🤖 Calling LLM...")
    response = chat(messages)

    # 4. Parse JSON response
    raw_file = OUT_DIR / "raw_output.txt"
    test_cases = parse_json_safely(response, raw_file)

    # 5. Save as CSV
    csv_file = OUT_DIR / "test_cases.csv"
    save_as_csv(test_cases, csv_file)

    print(f"✅ Generated {len(test_cases)} test cases")
    print(f"📝 Raw output: {raw_file.relative_to(ROOT)}")
    print(f"📊 CSV saved: {csv_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
