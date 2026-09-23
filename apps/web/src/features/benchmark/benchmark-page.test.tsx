import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { BenchmarkPage } from '@/features/benchmark/benchmark-page';
import { renderWithProviders } from '@/test/render-with-providers';

describe('BenchmarkPage', () => {
  it('shows synthetic data banner', async () => {
    renderWithProviders(<BenchmarkPage />);
    await waitFor(() => {
      expect(screen.getByText(/Synthetic benchmark data/)).toBeInTheDocument();
    });
  });
});
