import { test, expect } from '@playwright/test';
import { requireLiveDemo } from './helpers/live-api';
import { BenchmarkPage } from './pages/benchmark.page';

test.describe('Benchmark lab', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('shows synthetic data banner on benchmark page', async ({ page }) => {
    const benchmark = new BenchmarkPage(page);
    await benchmark.open();
    await expect(page.getByText(/Synthetic benchmark data/)).toBeVisible();
  });
});
