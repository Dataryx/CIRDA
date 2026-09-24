import { BasePage } from './base.page';

export class EvidencePage extends BasePage {
  async open(): Promise<void> {
    await this.goto('/evidence');
    await this.waitForHeading('Evidence');
  }

  async openEdgeDrilldown(edgeId: string): Promise<void> {
    await this.goto(`/evidence/edges/${encodeURIComponent(edgeId)}`);
    await this.waitForHeading('Edge Evidence');
  }
}
