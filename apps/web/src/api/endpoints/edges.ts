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
