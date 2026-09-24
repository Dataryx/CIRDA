import { expect } from '@playwright/test';
import { BasePage } from './base.page';

export class DecommissionPage extends BasePage {
  async open(entityId?: string): Promise<void> {
    const query = entityId ? `?entity=${encodeURIComponent(entityId)}` : '';
    await this.goto(`/decommission${query}`);
    await this.waitForHeading('Decommission');
  }

  async evaluateEntity(entityId: string): Promise<void> {
    await this.page.getByLabel('Entity ID').fill(entityId);
    await this.page.getByRole('button', { name: 'Evaluate decision' }).click();
    await this.waitForHeading('Decision Report');
  }

  async openReport(decisionId: string): Promise<void> {
    await this.goto(`/decommission/${decisionId}`);
    await this.waitForHeading('Decision Report');
  }

  async expectVerdict(label: 'Unsafe' | 'Safe' | 'Indeterminate'): Promise<void> {
    await expect(this.page.getByRole('status', { name: `Verdict: ${label}` })).toBeVisible();
  }
}
