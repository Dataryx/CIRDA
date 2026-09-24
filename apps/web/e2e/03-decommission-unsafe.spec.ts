import { test, expect } from '@playwright/test';
import { DEMO_AGENTS, evaluateDecision, requireLiveDemo } from './helpers/live-api';
import { DecommissionPage } from './pages/decommission.page';

test.describe('Decommission UNSAFE path', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('invoice-reconciler shows UNSAFE banner and witness paths', async ({ page, request }) => {
    const report = await evaluateDecision(request, DEMO_AGENTS.unsafe);
    test.skip(!report, 'Could not evaluate invoice-reconciler-agent');
    expect(report!.verdict).toBe('UNSAFE');

    const decommission = new DecommissionPage(page);
    await decommission.openReport(report!.decision_id);
    await decommission.expectVerdict('Unsafe');

    await expect(page.getByRole('heading', { name: 'Blast radius (G_p)' })).toBeVisible();
    await expect(page.getByText('Critical reachable:')).toBeVisible();
    await expect(
      page.getByRole('link', { name: /invoice-queue|payment-api|payment-mediator-service/ }),
    ).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Suggested runbook' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'report_and_remediate' })).toBeVisible();
  });
});
