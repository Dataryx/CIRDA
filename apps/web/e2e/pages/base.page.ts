import type { Page } from '@playwright/test';

export class BasePage {
  protected readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto(path: string): Promise<void> {
    await this.page.goto(path);
  }

  async waitForHeading(name: string | RegExp): Promise<void> {
    if (typeof name === 'string') {
      await this.page.getByRole('heading', { name, exact: true }).waitFor();
      return;
    }
    await this.page.getByRole('heading', { name }).waitFor();
  }
}
