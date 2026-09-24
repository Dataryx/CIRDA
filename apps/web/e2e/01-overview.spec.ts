import { test, expect } from '@playwright/test';
import { requireLiveDemo } from './helpers/live-api';
import { OverviewPage } from './pages/overview.page';

test.describe('Overview', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('loads dashboard with health and coverage sections', async ({ page }) => {
    const overview = new OverviewPage(page);
    await overview.open();
    await expect(page.getByText('API Status')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Coverage', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Verdict reference' })).toBeVisible();
  });
});
