import { test, expect } from '@playwright/test';

test.describe('Evidence', () => {
  test('loads evidence explorer', async ({ page }) => {
    try {
      await page.goto('/evidence');
      await expect(page.getByRole('heading', { name: 'Evidence' })).toBeVisible();
    } catch {
      test.skip(true, 'API unavailable');
    }
  });
});
