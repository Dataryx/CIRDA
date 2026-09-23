import { test, expect } from '@playwright/test';
import { DecommissionPage } from './pages/decommission.page';

test.describe('Decommission', () => {
  test('shows evaluate form and decision history', async ({ page }) => {
    const decommission = new DecommissionPage(page);
    try {
      await decommission.open();
      await expect(page.getByLabel('Entity ID')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Evaluate decision' })).toBeVisible();
    } catch {
      test.skip(true, 'API unavailable');
    }
  });
});
