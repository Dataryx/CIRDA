import { test, expect } from '@playwright/test';
import { DEMO_AGENTS, evaluateDecision, requireLiveDemo } from './helpers/live-api';
import { DecommissionPage } from './pages/decommission.page';

test.describe('Decommission SAFE path', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('legacy-csv-export shows SAFE verdict and staged decommission eligibility', async ({
    page,
    request,
  }) => {
    const report = await evaluateDecision(request, DEMO_AGENTS.safe);
    test.skip(!report, 'Could not evaluate legacy-csv-export-agent');
    expect(report!.verdict).toBe('SAFE');

    const decommission = new DecommissionPage(page);
    await decommission.openReport(report!.decision_id);
    await decommission.expectVerdict('Safe');
    await expect(page.getByText(/eligible for staged decommission/i)).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Suggested runbook' })).toBeVisible();
  });
});
