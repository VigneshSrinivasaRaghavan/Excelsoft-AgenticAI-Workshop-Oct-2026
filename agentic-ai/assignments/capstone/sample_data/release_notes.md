# ShopEasy v2.4.0 — Release Notes (Release Candidate 2)

Planned release date: 2026-11-27

## Scope

| Story  | Summary                          | Status in RC2 |
|--------|----------------------------------|---------------|
| ST-101 | User login                       | Done          |
| ST-102 | Forgot password via email link   | Done          |
| ST-103 | Add product to shopping cart     | Done          |
| ST-104 | Search products by keyword       | Done          |
| ST-105 | Apply discount coupon            | Done          |
| ST-106 | Update profile details           | Done          |
| ST-107 | Pay with a credit card           | Done          |
| ST-108 | View order history               | Deferred to v2.5.0 |

## Fixed in this release

- BUG-201 Login accepted passwords with trailing spaces
- BUG-202 Password reset link could be reused
- BUG-204 Cart quantity could be negative
- BUG-205 Profile phone number accepted letters

## Known issues going into the release

- BUG-203 Search shows stale results after clearing the keyword (Medium, Open)
- BUG-206 Double-click on Pay creates two charges (Critical, Open)

## Notes from the QA lead

- The payment flow is the highest-risk area of this release because real money is involved.
- Product wants to ship on 2026-11-27 because a marketing campaign starts the same day.
- Three coupon-related failures were not yet triaged at the time of writing.
