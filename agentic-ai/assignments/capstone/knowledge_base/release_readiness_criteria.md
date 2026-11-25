# Release Readiness Criteria

These criteria decide whether a release candidate can ship. Apply them in order. The first rule that matches determines the minimum outcome.

## 1. Hard stop rules (automatic NO-GO)

- Any **Critical** severity bug is Open.
- Any test blocked or failing in a payment, security or data-loss flow with no workaround.
- Overall pass rate below 85%.

## 2. Conditional rules (GO WITH CONDITIONS)

The release can ship only if the listed conditions are accepted by a human approver.

- Overall pass rate between 85% and 94%.
- One or more **High** severity bugs are Open.
- More than 3 failures are untriaged (no linked bug).
- More than 5% of tests are blocked or skipped.

Every condition must be written down with an owner and a due date before approval.

## 3. GO rules

All of these must be true:

- Overall pass rate is 95% or higher.
- No Critical or High bugs are Open.
- Every module has a pass rate of 90% or higher.
- Blocked plus skipped tests are 5% or less of the total.
- Every failure is linked to a bug.

## 4. Calculations

- Pass rate = passed / total x 100.
- Blocked and skipped share = (blocked + skipped) / total x 100.
- Module pass rate = module passed / module total x 100.
- Open bugs counted for severity rules are bugs whose status is not Fixed or Verified.

## 5. Risk areas

Treat these modules as high risk. A failure here weighs more than the same failure elsewhere:

- Checkout and payment
- Login and password reset
- Anything that handles personal data

## 6. Decision output format

A release readiness decision must contain:

1. **Decision**: GO, GO WITH CONDITIONS, or NO-GO
2. **Key metrics**: pass rate, open Critical bugs, open High bugs, blocked and skipped share, lowest module pass rate
3. **Reasons**: one bullet per rule that triggered, naming the rule and the evidence
4. **Conditions** (only for GO WITH CONDITIONS): owner and due date for each
5. **Blockers** (only for NO-GO): what must change for the decision to improve
6. **Pressure note**: schedule or marketing pressure is never a reason to relax a rule

## 7. Human approval

The decision is a recommendation. A human must approve or reject it before it is final.

- On approval, the decision and its reasons are saved to the decision log.
- On rejection, the reviewer's feedback must be included when the decision is regenerated.
- A rejected NO-GO may only be overturned if the feedback provides new evidence, such as a bug now fixed.
