import { BasePage } from './base.page';

export class BenchmarkPage extends BasePage {
  async open(): Promise<void> {
    await this.goto('/benchmark');
    await this.waitForHeading('Benchmark');
  }
}
