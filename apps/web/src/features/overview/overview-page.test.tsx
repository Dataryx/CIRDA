import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { OverviewPage } from '@/features/overview/overview-page';
import { renderWithProviders } from '@/test/render-with-providers';

describe('OverviewPage', () => {
  it('renders coverage from API', async () => {
    renderWithProviders(<OverviewPage />);
    await waitFor(() => {
      expect(screen.getByText('91.0%')).toBeInTheDocument();
    });
    expect(screen.getByRole('heading', { name: 'Overview' })).toBeInTheDocument();
  });
});
