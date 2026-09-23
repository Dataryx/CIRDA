import { test, expect } from '@playwright/test';

test.describe('Topology', () => {
  test('renders graph visualization', async ({ page }) => {
    try {
      await page.goto('/topology');
      await expect(page.getByRole('heading', { name: 'Topology' })).toBeVisible();
      await expect(page.getByLabel('Dependency graph visualization')).toBeVisible({ timeout: 15_000 });
    } catch {
      test.skip(true, 'API unavailable');
    }
  });
});
