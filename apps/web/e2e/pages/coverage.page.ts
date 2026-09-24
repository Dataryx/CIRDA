import { BasePage } from './base.page';

export class CoveragePage extends BasePage {
  async open(): Promise<void> {
    await this.goto('/coverage');
    await this.waitForHeading('Coverage');
  }
}
