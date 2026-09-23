import { apiRequest, buildQuery } from '@/api/client';
import type { GraphLayer, GraphPayload } from '@/api/generated/schema.d';

export function fetchGraph(params: {
  layer?: GraphLayer;
  as_of?: string;
}): Promise<GraphPayload> {
  return apiRequest<GraphPayload>(`/api/v1/graph${buildQuery(params)}`);
}
