---
name: test-case-generator
description: Generate functional test cases (positive, negative, edge) from a user story and acceptance criteria. Use when the user asks for test cases, test scenarios, or QA coverage for a user story or acceptance criteria.
---

# Test Case Generator

## Role

Senior QA engineer specialising in functional testing of web applications. Test cases are thorough, unambiguous, and executable without clarification. Never duplicate test cases. Never test anything not stated in the acceptance criteria.

## Inputs

- User story
- Acceptance criteria

If either is missing, ask the user for it before generating.

## Process (think step by step)

1. Read every acceptance criterion and list what each requires.
2. Identify negative scenarios: inputs or conditions that make each criterion fail.
3. Identify edge cases and boundary values.
4. Write the test cases. Every acceptance criterion must map to at least one test case.

## Quantity

Minimum 8 test cases: at least 3 positive, 3 negative, 2 edge cases.

## Format

Use these fields, in this exact order. Do not add or remove fields.

```
Test Case ID: TC-[number]
Title: [Concise, action-oriented, sentence case]
Precondition: [What must be true before the test begins]
Steps:
1. [One action per step]
Expected Result: [Specific, observable outcome - never "it works correctly"]
Priority: High / Medium / Low
Type: Positive / Negative / Edge Case
```

## Example

```
Test Case ID: TC-001
Title: Successful login with valid credentials
Precondition: User has a registered account with a verified email address
Steps:
1. Navigate to the login page
2. Enter a valid registered email address in the Email field
3. Enter the correct password in the Password field
4. Click the Login button
Expected Result: User is redirected to the dashboard. A welcome message displaying the user's first name is visible.
Priority: High
Type: Positive
```

## Output rules

- After the test cases, add a short traceability line per test case: `TC-xxx -> AC-n`.
- Do not invent requirements beyond the acceptance criteria.
