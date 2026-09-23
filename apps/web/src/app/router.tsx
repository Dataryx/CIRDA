import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppShell } from '@/components/layout/app-shell';
import { LoginPage } from '@/features/auth/login-page';
import { AuthCallbackPage } from '@/features/auth/auth-callback-page';
import { OverviewPage } from '@/features/overview/overview-page';
import { TopologyPage } from '@/features/topology/topology-page';
import { EntitiesPage } from '@/features/entities/entities-page';
import { EntityDetailPage } from '@/features/entities/entity-detail-page';
import { DecommissionPage } from '@/features/decommission/decommission-page';
import { DecisionReportPage } from '@/features/decommission/decision-report-page';
import { EvidencePage } from '@/features/evidence/evidence-page';
import { EdgeEvidencePage } from '@/features/evidence/edge-evidence-page';
import { CoveragePage } from '@/features/coverage/coverage-page';
import { BenchmarkPage } from '@/features/benchmark/benchmark-page';
import { BenchmarkRunPage } from '@/features/benchmark/benchmark-run-page';
import { CalibrationPage } from '@/features/calibration/calibration-page';
import { AuditPage } from '@/features/audit/audit-page';
import { RequireAuth } from '@/app/require-auth';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/auth/callback',
    element: <AuthCallbackPage />,
  },
  {
    path: '/',
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <OverviewPage /> },
      { path: 'topology', element: <TopologyPage /> },
      { path: 'entities', element: <EntitiesPage /> },
      { path: 'entities/:entityId', element: <EntityDetailPage /> },
      { path: 'decommission', element: <DecommissionPage /> },
      { path: 'decommission/:decisionId', element: <DecisionReportPage /> },
      { path: 'evidence', element: <EvidencePage /> },
      { path: 'evidence/edges/:edgeId', element: <EdgeEvidencePage /> },
      { path: 'coverage', element: <CoveragePage /> },
      { path: 'benchmark', element: <BenchmarkPage /> },
      { path: 'benchmark/runs/:runId', element: <BenchmarkRunPage /> },
      { path: 'calibration', element: <CalibrationPage /> },
      { path: 'audit', element: <AuditPage /> },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
