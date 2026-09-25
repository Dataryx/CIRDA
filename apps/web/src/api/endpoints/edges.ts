import { apiRequest, buildQuery } from '@/api/client';
import type { EdgeEvidenceResponse, EdgeListResponse, EdgeResponse } from '@/api/generated/schema.d';

export function fetchEdges(params: {
  layer?: string;
  source_id?: string;
  target_id?: string;
  as_of?: string;
  offset?: number;
  limit?: number;
}): Promise<EdgeListResponse> {
  return apiRequest<EdgeListResponse>(`/api/v1/edges${buildQuery(params)}`);
}

export function fetchEdge(edgeId: string, asOf?: string): Promise<EdgeResponse> {
  return apiRequest<EdgeResponse>(
    `/api/v1/edges/${encodeURIComponent(edgeId)}${buildQuery({ as_of: asOf })}`,
  );
}

export function fetchEdgeEvidence(edgeId: string): Promise<EdgeEvidenceResponse> {
  return apiRequest<EdgeEvidenceResponse>(`/api/v1/edges/${encodeURIComponent(edgeId)}/evidence`);
}

export function patchEdgeNecessity(
  edgeId: string,
  necessity: string,
): Promise<EdgeResponse> {
  return apiRequest<EdgeResponse>(`/api/v1/edges/${encodeURIComponent(edgeId)}`, {
    method: 'PATCH',
    body: { necessity },
  });
}

export interface NecessityHint {
  edge_id: string;
  source_id: string;
  target_id: string;
  current_necessity: string;
  suggested_necessity: string;
  confidence: number;
  rationale: string;
  signals?: Record<string, unknown>;
}

export interface NecessityHintListResponse {
  source_id: string;
  items: NecessityHint[];
  mode: string;
}

export function fetchNecessitySuggestions(
  sourceId: string,
  asOf?: string,
): Promise<NecessityHintListResponse> {
  return apiRequest<NecessityHintListResponse>(
    `/api/v1/edges/necessity-suggestions${buildQuery({ source_id: sourceId, as_of: asOf })}`,
  );
}
