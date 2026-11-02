# Day 8 — Edge / Negative Testcase Generator

## Assignment 1

Question

Implement an agent `edgecase_agent` that reads a requirement text (single file) and produces a JSON array of test cases emphasizing edge and negative scenarios in addition to normal cases.

Requirements

- Input: a requirement text file from `data/requirements` (CLI: `--input PATH`).
- Output: a JSON array (printed or returned) and a CSV `outputs/testcase_generated/test_cases.csv`.
- Each test case object must include: `id`, `title`, `steps`, `expected`, `priority`, `tags`.
- At least 6 and at most 12 test cases. At least 30% must be tagged as `edge` or `negative`.

Expected output (JSON schema per case)

{
  "id": "TC-001",
  "title": "Short test title",
  "steps": ["step 1", "step 2"],
  "expected": "Expected result",
  "priority": "High|Medium|Low",
  "tags": ["edge"|"negative"|"happy"],
}

CSV columns: TestID, Title, Steps, Expected, Priority, Tags, Likelihood

---

## Assignment 2 — Log Analyzer

Question

Implement an agent `log_analyzer` that reads one log file and, from a single LLM call, produces a technical report, a JSON summary, and a plain-language executive summary.

Requirements

- Input: a log file from `data/logs` (CLI: `--input PATH`). If omitted, use the first `*.log` in that directory.
- One LLM call. The model reply must contain, in order: a technical analysis, a fenced `json` block, then `---EXECUTIVE---`.
- Output files under `outputs/log_analyzer/`, named from the log stem:
  - `{stem}_analysis.txt` — technical report
  - `{stem}_analysis.json` — parsed JSON summary
  - `{stem}_executive.txt` — executive summary
- Technical report must cover: Summary, Critical Errors (with timestamps), Root Cause, Impact, Recommendations, Prevention.
- Executive summary: 3–5 sentences, no technical jargon. Cover what happened, business impact, the fix, and when it will be resolved.
- If the JSON block is missing or invalid, write the text and executive files anyway and report the parse failure. Do not crash.

Expected output (JSON summary)

{
  "summary": "Brief one-line summary",
  "error_count": 5,
  "critical_errors": [
    {"timestamp": "2026-01-04 10:24:12", "message": "Payment timeout", "severity": "high"}
  ],
  "root_causes": ["Cause 1", "Cause 2"],
  "affected_systems": ["payment", "database", "api"],
  "recommendations": ["Fix 1", "Fix 2"],
  "severity": "high|medium|low"
}

`error_count` must equal the number of objects in `critical_errors`. `severity` on the summary and on each critical error is `high`, `medium`, or `low`.

---
