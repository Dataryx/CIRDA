import { apiRequest } from '@/api/client';
import type { HealthResponse, ReadinessResponse } from '@/api/generated/schema.d';

export function fetchHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/api/v1/health');
}

export function fetchReadiness(): Promise<ReadinessResponse> {
  return apiRequest<ReadinessResponse>('/api/v1/health/ready');
}
