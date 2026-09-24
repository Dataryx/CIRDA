import { test, expect } from '@playwright/test';
import { requireLiveDemo } from './helpers/live-api';
import { OverviewPage } from './pages/overview.page';

test.describe('Accessibility', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('overview has accessible landmarks and focusable nav', async ({ page }) => {
    const overview = new OverviewPage(page);
    await overview.open();
    await expect(page.getByRole('main')).toBeVisible();
    await expect(page.getByRole('navigation')).toBeVisible();
    const links = page.getByRole('link', { name: 'Overview' });
    await expect(links.first()).toBeVisible();
    await links.first().focus();
    await expect(links.first()).toBeFocused();
  });

  test('verdict badges expose status role on overview', async ({ page }) => {
    const overview = new OverviewPage(page);
    await overview.open();
    await expect(page.getByRole('status', { name: /Verdict: Safe/i })).toBeVisible();
    await expect(page.getByRole('status', { name: /Verdict: Unsafe/i })).toBeVisible();
    await expect(page.getByRole('status', { name: /Verdict: Indeterminate/i })).toBeVisible();
  });

  test('axe reports zero serious or critical violations', async ({ page }) => {
    let AxeBuilder: typeof import('@axe-core/playwright').default;
    try {
      AxeBuilder = (await import('@axe-core/playwright')).default;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      test.skip(
        true,
        `@axe-core/playwright unavailable (${message}) — run: pnpm add -D @axe-core/playwright`,
      );
      return;
    }

    const overview = new OverviewPage(page);
    await overview.open();
    const results = await new AxeBuilder({ page }).analyze();
    const serious = results.violations.filter(
      (violation) => violation.impact === 'serious' || violation.impact === 'critical',
    );
    expect(serious).toHaveLength(0);
  });
});
