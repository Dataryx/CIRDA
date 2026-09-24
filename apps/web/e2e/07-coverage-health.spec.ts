import { test, expect } from '@playwright/test';
import { requireLiveDemo } from './helpers/live-api';
import { CoveragePage } from './pages/coverage.page';

test.describe('Coverage health', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('displays coverage metrics and channel health table', async ({ page }) => {
    const coverage = new CoveragePage(page);
    await coverage.open();
    await expect(page.getByText('Current coverage')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Channel health' })).toBeVisible();
  });
});
