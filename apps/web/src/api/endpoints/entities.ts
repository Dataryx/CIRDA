import { apiRequest, buildQuery } from '@/api/client';
import type { EntityListResponse, EntityResponse } from '@/api/generated/schema.d';

export function fetchEntities(params: {
  offset?: number;
  limit?: number;
  entity_type?: string;
}): Promise<EntityListResponse> {
  return apiRequest<EntityListResponse>(`/api/v1/entities${buildQuery(params)}`);
}

export function fetchEntity(entityId: string): Promise<EntityResponse> {
  return apiRequest<EntityResponse>(`/api/v1/entities/${encodeURIComponent(entityId)}`);
}
