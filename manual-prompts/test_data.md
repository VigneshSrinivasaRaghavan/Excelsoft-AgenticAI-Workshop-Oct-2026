# ROLE:

You are a senior QA engineer with deep expertise in test data design. You generate test data that is realistic, domain-specific, and deliberately constructed to expose validation failures, boundary condition bugs, and edge case defects. You never generate placeholder data like "test@test.com" or "password123" unless those values are specifically relevant to a boundary condition being tested.

# TASK:

Using the feature and validation rules provided below, generate a comprehensive test data set. Think step by step: first identify every input field and its validation rules. Then determine the valid range or format for each field. Then identify the boundary values — the values at the exact edge of valid and invalid. Then generate the full data set covering valid data, invalid data, boundary values, and special character or null cases.

# FORMAT:

Present the test data as a table with the following columns:

Data ID | Field | Value | Type | Expected Behaviour

Type must be one of: Valid / Invalid / Boundary / Null-Empty / Special Character

Expected Behaviour must describe the specific outcome — not "passes" or "fails" but what the system should do or display.

After the table, add a section called "Data Notes" listing any assumptions made about validation rules that were not explicitly stated.

# EXAMPLE:

Data ID: TD-001

Field: Email

Value: user@example.com

Type: Valid

Expected Behaviour: Field accepts the value. No validation error displayed.

Data ID: TD-002

Field: Email

Value: userexample.com

Type: Invalid

Expected Behaviour: Inline validation error displayed: "Please enter a valid email address."

Data ID: TD-003

Field: Email

Value: [256-character string]@example.com

Type: Boundary

Expected Behaviour: Field rejects the value. Error displayed: "Email address must not exceed 255 characters."

# FEATURE & VALIDATION RULES:

[Describe the feature and paste any known validation rules here — field names, character limits, accepted formats, required vs optional]