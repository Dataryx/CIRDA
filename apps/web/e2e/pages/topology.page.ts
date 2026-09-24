import { BasePage } from './base.page';

export class TopologyPage extends BasePage {
  async open(): Promise<void> {
    await this.goto('/topology');
    await this.waitForHeading('Topology');
  }
}
