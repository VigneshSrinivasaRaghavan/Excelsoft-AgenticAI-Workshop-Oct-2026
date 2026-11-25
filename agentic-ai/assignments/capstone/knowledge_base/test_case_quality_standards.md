# Test Case Quality Standards

This document defines how to score a test case and how to rewrite a weak one.

## 1. Scoring rubric (100 points)

| Dimension | Points | Full marks when |
|-----------|--------|-----------------|
| Title clarity | 20 | Title states the action and expected outcome in 6 to 15 words, for example "Login with wrong password shows generic error" |
| Steps quality | 30 | 3 or more steps, each a single concrete action with real data (email, value, button name) |
| Expected result | 30 | Observable and specific: names a message, status code, value or screen. Not "works", "fine" or "correct" |
| Priority | 10 | One of Critical, High, Medium, Low and consistent with business risk |
| Single purpose | 10 | The case verifies one behaviour only |

Partial credit is allowed. A missing field scores 0 for that dimension.

## 2. Quality bands

| Score | Band | Action |
|-------|------|--------|
| 85 to 100 | Good | Keep as is |
| 70 to 84 | Acceptable | Keep, optional improvement |
| 50 to 69 | Weak | Rewrite |
| Below 50 | Poor | Rewrite, or merge or delete if it duplicates another case |

A rewritten case passes validation only when its re-score is 70 or above.

## 3. Anti-patterns to detect

1. **Vague title**: "Test login", "Cart test", "Check payment".
2. **One-step case**: a single step such as "Login".
3. **Non-observable expected result**: "Works", "Everything works", "Payment should work properly and be fine".
4. **Missing expected result**.
5. **Missing priority**.
6. **Kitchen-sink case**: one case that covers several features (login, cart, coupon, payment, order history).
7. **Non-actionable step**: "Add item", "Search for something", "Pay".
8. **Near duplicate**: same behaviour as another case with different wording.
9. **Missing test data**: no email, coupon code or value where one is needed.

## 4. Rewrite rules

- Keep the original intent of the case; do not invent a new feature.
- Keep the original `id` and add the suffix `-R` for a rewritten case (for example `PQ-003-R`).
- If a case is a kitchen sink, split it into several single-purpose cases with ids `PQ-004-R1`, `PQ-004-R2`, and so on.
- Replace placeholders with realistic data, for example `shopper@example.com`, coupon `SAVE10`, phone `12345`.
- Expected results must contain at least one verifiable detail (message text, status, number, page).
- Do not touch cases that already score 85 or more.

## 5. Output of a quality audit

An audit report must contain:

- Number of cases audited and the average score before and after rewrite
- Table: case id, score, band, list of anti-patterns found
- List of rewritten cases with their new scores
- The three most common anti-patterns found (this is what the agent should remember for next time)
