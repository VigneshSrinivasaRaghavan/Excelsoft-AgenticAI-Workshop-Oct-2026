# Regression Testing Guide — Turning Fixed Bugs into Regression Tests

A bug that is fixed but has no regression test will eventually come back. This guide defines which bugs need a regression test and how to write one.

## 1. Which bugs need a regression test

| Bug status | Regression test needed? |
|------------|-------------------------|
| Fixed      | Yes, unless one already exists |
| Verified   | Yes, unless one already exists |
| Open       | No. The bug is not fixed yet, so there is nothing to protect. Record it as "deferred" |

A regression test **already exists** when a test case has `bug_key` equal to the bug key, or its title contains the bug key.

## 2. Naming convention

Every regression test title must follow this exact pattern:

`REG — <BUG_KEY> — <short scenario in plain words>`

Examples:
- `REG — BUG-201 — Password with trailing spaces is rejected`
- `REG — BUG-204 — Negative cart quantity is rejected`

Rules:
- The bug key is mandatory and appears exactly once.
- The scenario describes the **correct** behaviour, not the defect.
- Keep the scenario under 12 words.

## 3. Structure of a regression test

A regression test reproduces the original failure path and asserts the fixed behaviour.

- `steps`: reuse the bug's steps to reproduce, rewritten as clear imperative actions, 3 steps or more.
- `expected`: use the bug's expected behaviour, stated as a verifiable result.
- `bug_key` and `story_key`: copy both from the bug record.
- Add one extra step or check that confirms nothing adjacent is broken, for example the happy path still works.

## 4. Priority mapping

| Bug severity | Regression test priority |
|--------------|--------------------------|
| Critical | High |
| High     | High |
| Medium   | Medium |
| Low      | Low |

Critical-severity bugs also require that the regression test be added to the smoke suite.

## 5. Avoiding duplicates

- Check existing cases before generating. Never create a second regression test for the same bug key.
- If a normal test case already checks the same behaviour but has no bug key, add the key to its record instead of creating a new case. Mention this in the report as "linked".

## 6. Regression coverage report

The report must state:

- Total bugs analysed
- Bugs skipped because they are still Open
- Bugs that already had a regression test
- New regression tests created
- Final statement: "X of Y fixed bugs now have regression coverage"
