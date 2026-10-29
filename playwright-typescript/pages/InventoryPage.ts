import { type Locator, type Page } from '@playwright/test';

export class InventoryPage {
  readonly cart: Locator;

  constructor(private readonly page: Page) {
    this.cart = page.getByRole('button', { name: /Cart/ });
  }

  private item(name: string): Locator {
    return this.page.locator('[data-test="inventory-item"]').filter({
      has: this.page.getByRole('button', { name: `View details for ${name}`, exact: true }),
    });
  }

  async addToCart(name: string): Promise<void> {
    await this.item(name).getByRole('button', { name: 'Add to cart' }).click();
  }

  async openCart(): Promise<void> {
    await this.cart.click();
  }
}
