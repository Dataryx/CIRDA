import { BasePage } from './base.page';

export class DecommissionPage extends BasePage {
  async open(): Promise<void> {
    await this.goto('/decommission');
    await this.waitForHeading('Decommission');
  }

  async openReport(decisionId: string): Promise<void> {
    await this.goto(`/decommission/${decisionId}`);
    await this.waitForHeading('Decision Report');
  }
}
