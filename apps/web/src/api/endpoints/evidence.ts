import { apiRequest, buildQuery } from '@/api/client';
import type { EvidenceEventResponse, EvidenceListResponse } from '@/api/generated/schema.d';

export function fetchEvidenceList(params: {
  source_id?: string;
  target_id?: string;
  channel?: string;
  as_of?: string;
  offset?: number;
  limit?: number;
}): Promise<EvidenceListResponse> {
  return apiRequest<EvidenceListResponse>(`/api/v1/evidence${buildQuery(params)}`);
}

export function fetchEvidenceEvent(eventId: string): Promise<EvidenceEventResponse> {
  return apiRequest<EvidenceEventResponse>(`/api/v1/evidence/${encodeURIComponent(eventId)}`);
}
