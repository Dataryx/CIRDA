import type { Page } from '@playwright/test';

export class BasePage {
  constructor(protected readonly page: Page) {}

  async goto(path: string): Promise<void> {
    await this.page.goto(path);
  }

  async waitForHeading(name: string | RegExp): Promise<void> {
    await this.page.getByRole('heading', { name }).waitFor();
  }
}
