import { screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { FusionBreakdownCard } from '@/components/data-display/fusion-breakdown-card';
import { renderWithProviders } from '@/test/render-with-providers';

describe('FusionBreakdownCard', () => {
  it('renders fused support and channel rows from API data', () => {
    renderWithProviders(
      <FusionBreakdownCard
        breakdown={{
          fused_support: 0.82,
          channels: [
            { channel: 'trace', count: 12, strength: 0.55 },
            { channel: 'config', count: 3, strength: 0.31 },
          ],
        }}
      />,
    );

    expect(screen.getByText('82.0%')).toBeInTheDocument();
    expect(screen.getByText('trace')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText('0.55')).toBeInTheDocument();
    expect(screen.getByText('config')).toBeInTheDocument();
  });
});
