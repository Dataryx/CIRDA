import { apiRequest, buildQuery } from '@/api/client';
import type { AuditListResponse } from '@/api/generated/schema.d';

export function fetchAuditLog(params: {
  offset?: number;
  limit?: number;
}): Promise<AuditListResponse> {
  return apiRequest<AuditListResponse>(`/api/v1/audit${buildQuery(params)}`);
}
