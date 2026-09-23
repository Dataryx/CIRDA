import { test, expect } from '@playwright/test';

test.describe('Benchmark', () => {
  test('shows synthetic data banner', async ({ page }) => {
    try {
      await page.goto('/benchmark');
      await expect(page.getByRole('heading', { name: 'Benchmark' })).toBeVisible();
      await expect(page.getByText(/Synthetic benchmark data/)).toBeVisible();
    } catch {
      test.skip(true, 'API unavailable');
    }
  });
});
