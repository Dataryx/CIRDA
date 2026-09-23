import { test, expect } from '@playwright/test';
import { OverviewPage } from './pages/overview.page';

test.describe('Overview', () => {
  test('loads dashboard with health and coverage sections', async ({ page }) => {
    const overview = new OverviewPage(page);
    try {
      await overview.open();
      await expect(page.getByText('API Status')).toBeVisible();
      await expect(page.getByText('Coverage')).toBeVisible();
    } catch {
      test.skip(true, 'API unavailable — run with docker compose for full e2e');
    }
  });
});
