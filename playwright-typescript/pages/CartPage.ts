import { type Locator, type Page } from '@playwright/test';

export class CartPage {
  readonly checkoutButton: Locator;

  constructor(private readonly page: Page) {
    this.checkoutButton = page.getByRole('button', { name: 'Checkout' });
  }

  async checkout(): Promise<void> {
    await this.checkoutButton.click();
  }
}
