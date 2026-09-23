import type {
  CalibrationProfile,
  CoverageEstimate,
  DecisionReport,
  EntityResponse,
  Verdict,
} from '@/api/generated/schema.d';

export type { Verdict, DecisionReport, CoverageEstimate, EntityResponse, CalibrationProfile };

export type UserRole = 'viewer' | 'analyst' | 'approver' | 'admin';

export interface AuthSession {
  token: string;
  role: UserRole;
  principalId: string;
}

export interface AppRuntimeConfig {
  apiBaseUrl: string;
  wsUrl: string;
  authMode: 'dev' | 'jwt' | 'api_key';
}

export interface OverviewStats {
  coverage: CoverageEstimate | null;
  entityCount: number;
  edgeCount: number;
  recentDecisions: DecisionReport[];
}
