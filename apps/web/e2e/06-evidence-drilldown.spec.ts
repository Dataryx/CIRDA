import { test, expect } from '@playwright/test';
import { fetchFirstEdgeId, requireLiveDemo } from './helpers/live-api';
import { EvidencePage } from './pages/evidence.page';

test.describe('Evidence drilldown', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('lists evidence and drills into edge fusion breakdown', async ({ page, request }) => {
    const evidence = new EvidencePage(page);
    await evidence.open();
    await expect(page.getByRole('heading', { name: 'Evidence', exact: true })).toBeVisible();

    const edgeId = await fetchFirstEdgeId(request);
    test.skip(!edgeId, 'No edges available for drilldown');

    await evidence.openEdgeDrilldown(edgeId!);
    await expect(page.getByRole('heading', { name: /Evidence|Edge/i }).first()).toBeVisible();
    // Fusion breakdown shows calibrated support wording or fused score.
    await expect(
      page.getByText(/Fused support|calibrated support|Channel contribution/i).first(),
    ).toBeVisible();
  });
});
