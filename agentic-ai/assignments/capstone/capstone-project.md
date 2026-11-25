# Capstone Assignment: Build a QA Agent from Scratch

## What This Assignment Proves

During this workshop you learned the core building blocks of Agentic AI: LangChain prompts and chains, LangGraph state machines, RAG over your own documents, and short-term and long-term memory. You built a Test Case Generator and a Log Analyzer with them. Today you apply the same skills to a **new QA problem** that you design, build, and demo yourself.

By the end of this session you will have built a working QA agent that:

- Orchestrates nodes using LangGraph with a custom `TypedDict` state
- Uses a LangChain `ChatPromptTemplate` + LLM + `StrOutputParser` chain to generate output
- Uses RAG to ground decisions in real QA standards documents
- Remembers what it did using `PersistentMemory` (and short-term memory where noted)
- Reads local input files and writes a clear report to `outputs/capstone/`
- Runs end-to-end from the terminal and produces a result you can demo live

Pick ONE option from the four below. Work as a team of 3–4. One person codes, everyone contributes — discussing prompts, designing nodes, and reviewing outputs.

> There are no external services in this capstone. All input comes from files in `assignments/capstone/sample_data/` and all output is written to `outputs/capstone/`.

---

## Pre-requisites & Setup

Complete all three steps before you start building.

### Step 1 — Copy the Knowledge Base Documents

Four QA documents have been prepared for the RAG knowledge base. Copy all files from:

```
assignments/capstone/knowledge_base/
```

Into:

```
data/knowledge_base/
```

The four documents are:

- `sprint_qa_checklist.md` — what counts as covered, Go / Caution / Block thresholds, minimum cases per story
- `regression_testing_guide.md` — which bugs need regression tests, naming rule, priority mapping
- `test_case_quality_standards.md` — 100-point scoring rubric, anti-patterns, rewrite rules
- `release_readiness_criteria.md` — Go / Conditional / No-Go rules, calculations, decision format

### Step 2 — Rebuild the RAG Index

The vector store already holds the workshop documents. Rebuild it so your agent can search the 4 new ones too:

```bash
python build_index.py
```

Then confirm RAG sees the new documents:

```bash
python test_vector_search.py
```

### Step 3 — Look at the Sample Data

All input files are in `assignments/capstone/sample_data/`:

| File | Content | Used by |
|------|---------|---------|
| `stories.json` | 8 user stories (ST-101 to ST-108) with priority and acceptance criteria | Option 1 |
| `bugs.json` | 6 bugs (BUG-201 to BUG-206), 4 Fixed and 2 Open | Option 2, Option 4 |
| `existing_test_cases.json` | 9 existing test cases, some linked to a story or bug | Option 1, Option 2 |
| `poor_quality_test_cases.json` | 10 test cases of mixed quality (good, vague, empty, kitchen-sink) | Option 3 |
| `test_run_results.json` | Test cycle results for release ShopEasy v2.4.0 (120 tests, per-module numbers, notable failures) | Option 4 |
| `release_notes.md` | Release scope, fixed bugs, known issues, QA lead notes | Option 4 |

Open the files for your option and read them before designing your graph.

---

## Mandatory Tech Stack

Every option must use all four of the following:

| Topic | What to Use | Reference File |
|-------|-------------|----------------|
| LangGraph | `StateGraph` with `TypedDict` state, nodes, edges (add conditional edges where your option needs them) | `src/graph/test_case_generator_memory/graph.py` |
| LangChain | `ChatPromptTemplate` + `llm` + `StrOutputParser` chain | `src/graph/test_case_generator/nodes.py` |
| RAG | `search_vector_store()` called in at least one node, before the LLM generates | `src/graph/test_case_generator_rag/nodes.py` |
| Memory | `PersistentMemory` — load at start, save at end | `src/graph/test_case_generator_memory/nodes.py` |

Option 4 additionally requires validation with retry and a human-approval step (see below).

---

## The Four Options

Pick ONE. Every option covers all mandatory topics.

---

### Option 1 — Sprint Coverage Gap Checker

**The Problem**

QA teams often discover at sprint review — or worse, after release — that certain stories were shipped without a single test case. This agent detects coverage gaps early and fills them automatically.

**What This Agent Does**

The agent loads every user story and every existing test case, and maps which stories are covered. For every uncovered story it uses the LLM, guided by RAG over your sprint QA standards, to generate test cases. It then writes a coverage report with a Go / Caution / Block recommendation.

**Input**

- `sample_data/stories.json`
- `sample_data/existing_test_cases.json`

**Expected Output**

- `outputs/capstone/coverage_gap/new_test_cases.json` — generated test cases for every uncovered story
- `outputs/capstone/coverage_gap/coverage_report.md` containing:
  - Total stories analysed
  - Covered vs uncovered count
  - Coverage percentage
  - Go / Caution / Block recommendation with the one-line reason
  - A table of stories that had test cases generated

**Recommended Graph**

```
load_stories → load_existing_cases → analyze_coverage →
load_memory → retrieve_standards → generate_test_cases →
write_report → save_memory
```

**What Each Node Should Do**

- `load_stories` — Read `stories.json`. Store the list of stories in state.
- `load_existing_cases` — Read `existing_test_cases.json`. Store the cases in state.
- `analyze_coverage` — For each story, check whether any existing case has that story key in `story_key` or in its title. Mark each story COVERED or UNCOVERED, calculate coverage percentage, and compute the recommendation using the thresholds and override rule in `sprint_qa_checklist.md`. No LLM here — pure Python logic.
- `load_memory` — Use `PersistentMemory` to retrieve the story keys that previous runs already generated cases for. Remove those from the to-generate list.
- `retrieve_standards` — Call `search_vector_store()` with a query built from the uncovered stories' summaries. Store the top 3 results in state.
- `generate_test_cases` — For each uncovered story, use a LangChain chain with the story, its acceptance criteria, and the RAG context to generate the minimum number of cases required by its priority. Parse the JSON output.
- `write_report` — Build the Markdown coverage report and save both output files.
- `save_memory` — Store the story keys processed in this run.

**RAG Documents to Query**

- `sprint_qa_checklist.md`
- `test_case_quality_standards.md`

**Must-Have Requirements**

1. Coverage analysis runs before any test case is generated — never generate for a covered story
2. RAG is called before the LLM generates test cases
3. Memory records which stories were processed — a second run skips them and says so in the console
4. Every generated test case title starts with its story key, and there is at least one case per acceptance criterion
5. The report shows the coverage percentage and the Go / Caution / Block signal

**Sanity check**

With the provided sample data, 4 of 8 stories are covered (50%), so the recommendation must be **BLOCK**.

**Stretch Goal**

Add a conditional edge: if coverage is already 100%, skip straight to `write_report` without calling RAG or the LLM.

---

### Option 2 — Bug-to-Regression Test Mapper

**The Problem**

When a bug is fixed, the code is merged but no regression test is written. The same bug silently reappears in a future release. This agent closes that gap automatically.

**What This Agent Does**

The agent loads every bug and checks the existing test cases to see whether a regression test already exists. Open bugs are deferred, because there is nothing to protect yet. For fixed bugs with no regression test, it generates a targeted regression test using the bug's details and RAG over regression standards.

**Input**

- `sample_data/bugs.json`
- `sample_data/existing_test_cases.json`

**Expected Output**

- `outputs/capstone/regression_mapper/regression_cases.json` — generated regression tests
- `outputs/capstone/regression_mapper/regression_report.md` containing:
  - Total bugs analysed
  - Bugs skipped because they are Open
  - Bugs that already had a regression test
  - New regression tests created
  - The statement "X of Y fixed bugs now have regression coverage"

**Recommended Graph**

```
load_bugs → load_existing_cases → classify_bugs → (conditional)
      ├── nothing to generate → write_report
      └── bugs to cover → load_memory → retrieve_standards →
                          generate_regression_tests → write_report → save_memory
```

**What Each Node Should Do**

- `load_bugs` — Read `bugs.json` into state.
- `load_existing_cases` — Read `existing_test_cases.json` into state.
- `classify_bugs` — Split bugs into three lists: `deferred` (status Open), `already_covered` (a case has this `bug_key`), and `needs_regression` (Fixed or Verified with no case). No LLM — pure Python.
- A conditional edge after `classify_bugs`: if `needs_regression` is empty, go directly to `write_report`.
- `load_memory` — Use `PersistentMemory` to find bugs already handled in earlier runs and drop them from `needs_regression`.
- `retrieve_standards` — Call `search_vector_store()` with the bug summaries as the query. Store the top 3 results.
- `generate_regression_tests` — For each bug, use a LangChain chain with the bug's steps to reproduce, expected behaviour, and the RAG context to generate one regression test. Title must follow `REG — <BUG_KEY> — <scenario>`. Map priority from severity using `regression_testing_guide.md`.
- `write_report` — Build the Markdown report and save both output files.
- `save_memory` — Store the bug keys processed in this run.

**RAG Documents to Query**

- `regression_testing_guide.md`
- `test_case_quality_standards.md`

**Must-Have Requirements**

1. The agent checks existing cases FIRST — never generate a duplicate regression test for a covered bug
2. RAG is called before the LLM generates each regression test
3. Memory tracks which bugs were processed — a re-run skips them
4. Every regression test title includes the bug key in the form `REG — BUG-xxx — ...`
5. Open bugs are listed as deferred and never get a test generated
6. The graph contains at least one conditional edge

**Sanity check**

With the sample data: 4 bugs are Fixed, 2 are Open. BUG-201 and BUG-204 are already covered, so exactly 2 new regression tests are created (BUG-202 and BUG-205) and the final statement reads "4 of 4 fixed bugs now have regression coverage".

**Stretch Goal**

Run the agent twice in a row. The second run should take the "nothing to generate" branch and say that all fixed bugs are already handled.

---

### Option 3 — Test Case Quality Auditor

**The Problem**

Over time a test suite fills up with vague titles, one-step cases, and expected results like "works fine". Nobody reviews them, so they find fewer bugs and are impossible to automate. This agent audits a suite against company standards and rewrites the weak cases.

**What This Agent Does**

The agent loads a test suite, scores every case against the quality rubric from RAG, and flags anti-patterns. Weak and poor cases are rewritten by the LLM. A validation step re-scores each rewrite; any rewrite that does not reach the pass score is sent back for another attempt, up to 3 times. The agent remembers the most common defects it found so future audits focus on them.

**Input**

- `sample_data/poor_quality_test_cases.json`

**Expected Output**

- `outputs/capstone/quality_auditor/audit_report.md` containing:
  - Number of cases audited
  - Average score before and after rewrite
  - A table of case id, score, band, and anti-patterns found
  - The list of rewritten cases with new scores
  - The three most common anti-patterns
- `outputs/capstone/quality_auditor/improved_test_cases.json` — the full suite after improvements

**Recommended Graph**

```
load_cases → load_memory → retrieve_standards → score_cases →
generate_rewrites → validate_rewrites → (conditional)
      ├── all pass or retries exhausted → write_report → save_memory
      └── some still fail → retry_rewrite → validate_rewrites
```

**What Each Node Should Do**

- `load_cases` — Read `poor_quality_test_cases.json` into state.
- `load_memory` — Use `PersistentMemory` to fetch the anti-patterns found in earlier audits. Store them in state as `past_patterns` and mention them in the rewrite prompt.
- `retrieve_standards` — Call `search_vector_store()` for the scoring rubric and rewrite rules. Store the top 3 results.
- `score_cases` — Use a LangChain chain that takes the cases and RAG context and returns, as JSON, a score (0–100), band, and list of anti-patterns for each case. Store the results.
- `generate_rewrites` — For each case in the Weak or Poor band, use a LangChain chain to rewrite it following the rewrite rules. Split kitchen-sink cases into several cases.
- `validate_rewrites` — Check each rewrite in plain Python: at least 3 steps, non-empty expected result without banned words ("works", "fine", "correct", "properly"), priority present, title of 6 or more words. Set `validation_status` to `pass` or `fail` and record which cases failed.
- `retry_rewrite` — Increment `retry_count` and regenerate only the failing cases, passing the failure reasons to the LLM.
- A conditional edge after `validate_rewrites`: pass → report, fail and `retry_count < 3` → retry, otherwise → report with the failing cases clearly marked.
- `write_report` — Build the Markdown report and the improved test case file (good cases unchanged, weak cases replaced by their rewrites).
- `save_memory` — Store the three most common anti-patterns from this audit.

**RAG Documents to Query**

- `test_case_quality_standards.md`
- `sprint_qa_checklist.md`

**Must-Have Requirements**

1. RAG is called before scoring and before rewriting
2. Memory is loaded before the rewrite prompt is built and saved at the end — a second run mentions the remembered patterns in its console output
3. Validation uses deterministic Python checks, not another LLM call
4. The retry loop is capped at 3 attempts and uses a conditional edge
5. Cases that already score 85 or more are never modified
6. Rewritten cases keep the original id with the `-R` suffix as defined in the standards

**Sanity check**

PQ-002, PQ-007, and PQ-010 are well written and should land in the Good or Acceptable band and remain unchanged. PQ-001, PQ-003, PQ-006, and PQ-009 should be flagged as vague, and PQ-004 as a kitchen-sink case that gets split.

**Stretch Goal**

Detect near-duplicate cases (PQ-001 and PQ-008 overlap on login) and recommend which to merge.

---

### Option 4 — Release Readiness Advisor

**The Problem**

Before every release someone has to read test results, check open bugs, compare against the release criteria, and decide Go or No-Go — often under schedule pressure. Decisions become inconsistent and hard to explain afterward. This agent produces a consistent, evidence-based recommendation, then lets a human approve or reject it.

**What This Agent Does**

The agent loads the test cycle results, the bug list, and the release notes. It computes the key metrics with plain Python, retrieves the release criteria through RAG, and asks the LLM to write a Go / Go with Conditions / No-Go recommendation with reasons. A validation step checks that the recommendation is consistent with the numbers. The result is shown to a human, who approves or rejects it. A rejection sends the feedback back for a regenerated recommendation. After approval, the user can ask follow-up questions in the same session, and the decision is saved to long-term memory.

**Input**

- `sample_data/test_run_results.json`
- `sample_data/bugs.json`
- `sample_data/release_notes.md`

**Expected Output**

- `outputs/capstone/release_advisor/release_decision.md` containing the decision in the format defined in `release_readiness_criteria.md`: decision, key metrics, reasons, conditions or blockers, and the pressure note
- The terminal session showing the human approval step and at least one follow-up question answered from short-term memory

**Recommended Graph**

```
load_inputs → compute_metrics → load_memory → retrieve_criteria →
generate_decision → validate_decision → (conditional)
      ├── pass → preview → human_approval → (conditional)
      │              ├── approved → save_decision → END
      │              └── rejected → retry_decision → validate_decision
      └── fail and retry_count < 3 → retry_decision → validate_decision
```

**What Each Node Should Do**

- `load_inputs` — Read the three input files into state.
- `compute_metrics` — In plain Python compute: overall pass rate, blocked plus skipped share, per-module pass rates and the lowest one, open Critical and High bug counts, and the number of failures with no linked bug. Store them in state as a dictionary. The LLM must receive these numbers, never calculate them.
- `load_memory` — Use `PersistentMemory` to fetch past release decisions for context ("last release was No-Go because of ...").
- `retrieve_criteria` — Call `search_vector_store()` for the release readiness rules. Store the top 3 results.
- `generate_decision` — Use a LangChain chain with the metrics, the RAG context, the memory context, and the release notes to produce a decision in the required format. On a retry, also include the human's feedback or the validation failure reasons.
- `validate_decision` — Plain Python checks: the decision is exactly one of the three allowed values, it is NO-GO when an open Critical bug exists or the pass rate is below 85%, reasons are present, and the response mentions the actual pass rate. Set `validation_status` and the failure reasons.
- `preview` — Print the recommendation and its key metrics to the terminal.
- `human_approval` — Ask the user to approve, reject (with feedback), or view full details, like the flow in `test_case_generator_memory`.
- `retry_decision` — Increment `retry_count` and regenerate, passing the validation failures or human feedback.
- `save_decision` — Write `release_decision.md` and store the decision, the metrics, and the reasons in `PersistentMemory`.

**Short-term memory.** Compile the graph with `MemorySaver` and reuse one `thread_id` for the whole session, as in `src/graph/drivers/run_test_case_memory_pipeline.py`. After approval, the driver should loop: the user types a follow-up question (for example "Which module is the riskiest?" or "What would make this a Go?") and the agent answers using the conversation history and stored metrics. Typing `quit` ends the session.

**RAG Documents to Query**

- `release_readiness_criteria.md`
- `sprint_qa_checklist.md`

**Must-Have Requirements**

1. Metrics are computed in Python, not by the LLM
2. RAG is called before the decision is generated
3. Memory is loaded before generation and the approved decision is saved after
4. Validation with retry is implemented using conditional edges and capped at 3 attempts
5. A human approval step exists, and a rejection regenerates the decision using the reviewer's feedback
6. Short-term memory works: a follow-up question refers to earlier context without restating it

**Sanity check**

With the sample data the pass rate is about 81.7% and BUG-206 is an open Critical bug in the payment flow, so the validated decision must be **NO-GO**. If your agent returns Go or Go with Conditions, your validation step is not working.

**Stretch Goal**

Add a "what-if" follow-up: the user says "assume BUG-206 is fixed and its blocked tests pass" and the agent recomputes the metrics and re-evaluates the decision without regenerating from scratch.

---

## Demo Expectations

One person per team shares their screen and runs the agent live.

**Your demo must show:**

1. The agent running end-to-end from the terminal (`python -m src.graph.drivers.run_your_agent`)
2. Terminal output showing each node executing in sequence
3. The output files in `outputs/capstone/` opened and explained
4. Memory working: a second run that behaves differently because of what was remembered
5. A 1-minute explanation: what QA problem your agent solves and how it solves it

**Remember:** a working agent that runs end-to-end beats polished code that does not run.

---

## Code Reference — Where to Look in This Repo

| What you need | Copy from |
|---------------|-----------|
| Graph wiring + conditional edges | `src/graph/test_case_generator_memory/graph.py` |
| Custom `TypedDict` state | `src/graph/test_case_generator_memory/state.py` |
| LangChain chain in a node | `src/graph/test_case_generator/nodes.py` |
| Prompt template pattern | `src/prompts/testcase_prompts.py` |
| RAG query in a node | `src/graph/test_case_generator_rag/nodes.py` |
| Memory load + save in nodes | `src/graph/test_case_generator_memory/nodes.py` |
| `PersistentMemory` API | `src/core/memory.py` |
| Validation + retry routing | `validate_tests`, `retry_generate`, `route_after_validation` in `src/graph/test_case_generator_memory/nodes.py` |
| Human approval + reject loop | `show_preview`, `human_approval`, `route_after_human_approval` in `src/graph/test_case_generator_memory/nodes.py` |
| Short-term memory + `thread_id` driver | `src/graph/drivers/run_test_case_memory_pipeline.py` |
| Analysing structured data with an LLM | `src/graph/log_analyzer_memory/nodes.py` |
| Driver entry point pattern | `src/graph/drivers/run_log_analyzer_memory_pipeline.py` |
