# Sprint QA Checklist — Coverage Standards

Use this document to decide whether a sprint is ready for review and how to write test cases for stories that have no coverage yet.

## 1. What counts as "covered"

A user story is **covered** when at least one existing test case references the story key (for example `ST-101`) in its `story_key` field or in its title.

A story with zero referencing test cases is **uncovered** and must get new test cases before the sprint review.

Coverage percentage = covered stories / total stories x 100, rounded to the nearest whole number.

## 2. Sprint recommendation thresholds

| Coverage | Recommendation | Meaning |
|----------|----------------|---------|
| 90% or more | GO | Sprint can proceed to review |
| 70% to 89% | CAUTION | Proceed only if every uncovered story is Low or Medium priority |
| Below 70% | BLOCK | Sprint review must wait until gaps are closed |

Override rule: if any uncovered story has priority **Critical** or **High**, the recommendation is downgraded one level (GO becomes CAUTION, CAUTION becomes BLOCK) regardless of the percentage.

## 3. Minimum test cases per story

| Story priority | Minimum test cases | Required scenario types |
|----------------|--------------------|-------------------------|
| Critical | 5 | positive, negative, edge, security or data-integrity, error handling |
| High | 4 | positive, negative, edge, error handling |
| Medium | 3 | positive, negative, edge |
| Low | 2 | positive, negative |

## 4. Generating test cases for an uncovered story

1. Read the story summary, description and every acceptance criterion.
2. Create at least one test case per acceptance criterion; do not merge two criteria into one case.
3. Add at least one negative case (invalid input, missing data, unauthorized action).
4. Add at least one edge case (boundary value, empty state, maximum length, rapid repeated action).
5. Put the story key at the start of every title, for example `ST-103 Add to cart rejects quantity above stock`.
6. Every case needs: `id`, `title`, `priority`, `steps` (3 or more concrete steps) and `expected` (observable result with a value, message or status).
7. Case priority follows story priority; negative and edge cases may be one level lower.

## 5. Sprint exit criteria

- Every Critical and High story is covered.
- Every acceptance criterion maps to at least one test case.
- No test case is a duplicate of another (same steps and same expected result).
- The coverage report lists each story with COVERED or UNCOVERED and the number of cases found.

## 6. Coverage report format

A sprint coverage report must contain:

- Total stories analysed
- Covered count and uncovered count
- Coverage percentage
- Recommendation (GO, CAUTION or BLOCK) with the one-line reason
- A table of uncovered stories with the number of new cases generated for each
