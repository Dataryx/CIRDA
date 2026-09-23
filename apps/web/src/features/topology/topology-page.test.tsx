import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { TopologyPage } from '@/features/topology/topology-page';
import { renderWithProviders } from '@/test/render-with-providers';

vi.mock('@/components/charts/graph-viewer', () => ({
  GraphViewer: () => <div aria-label="Dependency graph visualization" />,
}));

describe('TopologyPage', () => {
  it('renders graph stats from API', async () => {
    renderWithProviders(<TopologyPage />);
    await waitFor(() => {
      expect(screen.getByText('2 nodes')).toBeInTheDocument();
    });
    expect(screen.getByText('1 edges')).toBeInTheDocument();
  });
});
