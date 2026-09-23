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
