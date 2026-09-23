import { screen, waitFor } from '@testing-library/react';
import { Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { DecisionReportPage } from '@/features/decommission/decision-report-page';
import { renderWithProviders } from '@/test/render-with-providers';

describe('DecisionReportPage', () => {
  it('renders verdict and limitations footer from API', async () => {
    renderWithProviders(
      <Routes>
        <Route path="/decommission/:decisionId" element={<DecisionReportPage />} />
      </Routes>,
      { route: '/decommission/dec-001' },
    );
    await waitFor(() => {
      expect(screen.getByText('Indeterminate')).toBeInTheDocument();
    });
    expect(screen.getByLabelText('Decision limitations')).toBeInTheDocument();
    expect(screen.getByText(/Limitations \(§X\)/)).toBeInTheDocument();
  });
});
