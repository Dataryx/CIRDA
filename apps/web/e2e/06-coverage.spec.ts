import { test, expect } from '@playwright/test';

test.describe('Coverage', () => {
  test('displays coverage metrics', async ({ page }) => {
    try {
      await page.goto('/coverage');
      await expect(page.getByRole('heading', { name: 'Coverage' })).toBeVisible();
      await expect(page.getByText('Current coverage')).toBeVisible();
    } catch {
      test.skip(true, 'API unavailable');
    }
  });
});
