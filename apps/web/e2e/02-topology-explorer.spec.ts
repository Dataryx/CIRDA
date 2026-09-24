import { test, expect } from '@playwright/test';
import { requireLiveDemo } from './helpers/live-api';
import { TopologyPage } from './pages/topology.page';

test.describe('Topology explorer', () => {
  test.beforeEach(async ({ request }) => {
    await requireLiveDemo(request);
  });

  test('renders dependency graph visualization', async ({ page }) => {
    const topology = new TopologyPage(page);
    await topology.open();
    await expect(page.getByLabel('Dependency graph visualization')).toBeVisible({ timeout: 15_000 });
  });
});
