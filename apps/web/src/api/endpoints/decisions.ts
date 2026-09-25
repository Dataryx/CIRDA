import { apiRequest, buildQuery } from '@/api/client';
import type {
  DecisionEvaluateRequest,
  DecisionListResponse,
  DecisionReport,
} from '@/api/generated/schema.d';

export function fetchDecision(decisionId: string): Promise<DecisionReport> {
  return apiRequest<DecisionReport>(`/api/v1/decisions/${encodeURIComponent(decisionId)}`);
}

export function fetchDecisionsByEntity(
  entityId: string,
  params: { offset?: number; limit?: number } = {},
): Promise<DecisionListResponse> {
  return apiRequest<DecisionListResponse>(
    `/api/v1/decisions/by-entity/${encodeURIComponent(entityId)}${buildQuery(params)}`,
  );
}

export function evaluateDecision(body: DecisionEvaluateRequest): Promise<DecisionReport> {
  return apiRequest<DecisionReport>('/api/v1/decisions/evaluate', { method: 'POST', body });
}

export function rerunDecision(decisionId: string): Promise<DecisionReport> {
  return apiRequest<DecisionReport>(`/api/v1/decisions/${encodeURIComponent(decisionId)}/rerun`, {
    method: 'POST',
  });
}

export interface ProbeApplyRequest {
  entity_id: string;
  channels: string[];
  as_of?: string | null;
}

export interface ProbeApplyResult {
  entity_id: string;
  channels: string[];
  mode: string;
  coverage_before: number;
  coverage_after: number;
  expected_delta_c: number;
  actual_delta_c: number;
  suppressed_channels_after: string[];
  as_of?: string | null;
}

export function applyProbes(body: ProbeApplyRequest): Promise<ProbeApplyResult> {
  return apiRequest<ProbeApplyResult>('/api/v1/decisions/probes/apply', { method: 'POST', body });
}
