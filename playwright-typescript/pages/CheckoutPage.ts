import { type Locator, type Page } from '@playwright/test';

export type CheckoutCustomer = {
  firstName: string;
  lastName: string;
  postalCode: string;
};

export class CheckoutPage {
  readonly firstName: Locator;
  readonly lastName: Locator;
  readonly postalCode: Locator;
  readonly continueButton: Locator;
  readonly finishButton: Locator;
  readonly completeHeader: Locator;

  constructor(private readonly page: Page) {
    this.firstName = page.getByLabel('First Name');
    this.lastName = page.getByLabel('Last Name');
    this.postalCode = page.getByLabel('Zip/Postal Code');
    this.continueButton = page.getByRole('button', { name: 'Continue', exact: true });
    this.finishButton = page.getByRole('button', { name: 'Finish' });
    this.completeHeader = page.getByRole('heading', {
      name: 'Thank you for your order!',
    });
  }

  async fillInformation(customer: CheckoutCustomer): Promise<void> {
    await this.firstName.fill(customer.firstName);
    await this.lastName.fill(customer.lastName);
    await this.postalCode.fill(customer.postalCode);
  }

  async continue(): Promise<void> {
    await this.continueButton.click();
  }

  async finish(): Promise<void> {
    await this.finishButton.click();
  }
}
