import { BasePage } from './base.page';

export class OverviewPage extends BasePage {
  async open(): Promise<void> {
    await this.goto('/');
    await this.waitForHeading('Overview');
  }
}
