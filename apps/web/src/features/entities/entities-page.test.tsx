import { screen, waitFor } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { EntitiesPage } from '@/features/entities/entities-page';
import { renderWithProviders } from '@/test/render-with-providers';

describe('EntitiesPage', () => {
  it('renders entities from API', async () => {
    renderWithProviders(<EntitiesPage />);
    await waitFor(() => {
      expect(screen.getByText('Billing Service')).toBeInTheDocument();
    });
  });
});
