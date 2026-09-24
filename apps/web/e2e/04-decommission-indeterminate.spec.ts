import { test, expect } from '@playwright/test';
import { DEMO_AGENTS, evaluateDecision, requireLiveDemo } from './helpers/live-api';
import { DecommissionPage } from './pages/decommission.page';

test.describe('Decommission INDETERMINATE path', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('vendor-risk shows INDETERMINATE with coverage gap and remediation runbook', async ({
    page,
    request,
  }) => {
    // Coverage is target-scoped: vendor-risk sees silent database/messaging channels.
    const report = await evaluateDecision(request, DEMO_AGENTS.indeterminate);
    test.skip(!report, 'Could not evaluate vendor-risk-agent');
    expect(report!.verdict).toBe('INDETERMINATE');

    const decommission = new DecommissionPage(page);
    await decommission.openReport(report!.decision_id);
    await decommission.expectVerdict('Indeterminate');

    await expect(page.getByRole('heading', { name: 'Coverage breakdown' })).toBeVisible();
    await expect(page.getByText('Meets C_min: No')).toBeVisible();
    await expect(page.getByText(/insufficient evidence or coverage/i).first()).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Suggested runbook' })).toBeVisible();
    await expect(page.getByRole('cell', { name: 'report_and_remediate' })).toBeVisible();
  });
});
