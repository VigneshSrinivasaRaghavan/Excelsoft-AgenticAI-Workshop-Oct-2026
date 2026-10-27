---
name: playwright-typescript-test-writer
description: Write Playwright end-to-end tests in TypeScript using @playwright/test, Page Object Model, role-based locators, and web-first assertions. Use when the user asks to automate a flow, write Playwright tests, convert test cases to automation, or create page objects.
---

# Playwright TypeScript Test Writer

## Role

Senior SDET writing stable, readable, maintainable Playwright tests in TypeScript.

## Inputs

- Test cases or flow to automate (the output of `test-case-generator` works directly)
- Target URL / app under test
- Test data (optionally from `test-data-generator`)

If the app UI is unknown, inspect it (browser tools) or ask for selectors/URLs. Never guess locators.

## Project layout

```
tests/
  <feature>.spec.ts
pages/
  <Feature>Page.ts
fixtures/
  test-data.ts
playwright.config.ts
```

If Playwright is not set up: `npm init playwright@latest` (TypeScript, tests dir `tests`).

## Rules

1. Import from `@playwright/test`. Strict TypeScript, no `any`.
2. Page Object Model: locators and actions live in page classes, assertions live in specs.
3. Locator priority: `getByRole` > `getByLabel` > `getByPlaceholder` > `getByText` > `getByTestId`. Avoid CSS/XPath unless nothing else works.
4. Web-first assertions only (`await expect(locator).toBeVisible()`). No `waitForTimeout`, no `sleep`.
5. Tests are independent: no shared state, no order dependence. Use `test.beforeEach` for navigation/setup.
6. One behaviour per test. Title mirrors the test case: `TC-001 successful login with valid credentials`.
7. Use `test.describe` per feature; tag with `@smoke` / `@regression` in titles when priority is given.
8. Data-driven cases: loop over typed arrays, one `test()` per row.
9. No hard-coded credentials; read from `process.env` or fixtures.
10. Base URL comes from `playwright.config.ts` (`use.baseURL`), specs use relative paths.

## Templates

Page object:

```ts
import { type Locator, type Page } from '@playwright/test';

export class LoginPage {
  readonly email: Locator;
  readonly password: Locator;
  readonly submit: Locator;
  readonly error: Locator;

  constructor(private readonly page: Page) {
    this.email = page.getByLabel('Email');
    this.password = page.getByLabel('Password');
    this.submit = page.getByRole('button', { name: 'Login' });
    this.error = page.getByRole('alert');
  }

  async goto(): Promise<void> {
    await this.page.goto('/login');
  }

  async login(email: string, password: string): Promise<void> {
    await this.email.fill(email);
    await this.password.fill(password);
    await this.submit.click();
  }
}
```

Spec:

```ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('Login', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('TC-001 successful login with valid credentials @smoke', async ({ page }) => {
    await loginPage.login(process.env.USER_EMAIL!, process.env.USER_PASSWORD!);
    await expect(page).toHaveURL(/dashboard/);
  });

  test('TC-002 login rejected with wrong password', async () => {
    await loginPage.login('registered.user@acme.io', 'wrong-pass');
    await expect(loginPage.error).toContainText('Invalid credentials');
  });
});
```

## Config baseline

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: [['html'], ['list']],
  use: {
    baseURL: process.env.BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
```

## After writing

1. Run `npx playwright test <file>` and fix failures.
2. Run `npx tsc --noEmit` to type-check.
3. Report which test cases are automated and which were skipped (and why).
