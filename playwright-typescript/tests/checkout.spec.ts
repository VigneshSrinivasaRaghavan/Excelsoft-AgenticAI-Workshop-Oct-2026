import { test, expect } from '@playwright/test';
import { checkoutCustomer, products, sauceDemoUser } from '../fixtures/test-data';
import { CartPage } from '../pages/CartPage';
import { CheckoutPage } from '../pages/CheckoutPage';
import { InventoryPage } from '../pages/InventoryPage';
import { LoginPage } from '../pages/LoginPage';

test.use({ baseURL: 'https://www.saucedemo.com' });

test.describe('Checkout', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(sauceDemoUser.username, sauceDemoUser.password);
  });

  test('TC-001 complete purchase of backpack and bike light @smoke', async ({ page }) => {
    const inventoryPage = new InventoryPage(page);
    const cartPage = new CartPage(page);
    const checkoutPage = new CheckoutPage(page);

    await inventoryPage.addToCart(products.backpack);
    await inventoryPage.addToCart(products.bikeLight);
    await inventoryPage.openCart();

    await cartPage.checkout();

    await checkoutPage.fillInformation(checkoutCustomer);
    await checkoutPage.continue();
    await checkoutPage.finish();

    await expect(checkoutPage.completeHeader).toBeVisible();
  });
});
