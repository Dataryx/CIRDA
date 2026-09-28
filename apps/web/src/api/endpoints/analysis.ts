import { apiRequest, buildQuery } from '@/api/client';

export interface BlastRadiusResponse {
  all_reachable: string[];
  critical_reachable: string[];
  truncated: boolean;
  layer?: string;
  [key: string]: unknown;
}

export interface ReachabilityResponse {
  reachable: string[];
  truncated: boolean;
  [key: string]: unknown;
}

export interface CriticalPathItem {
  path_nodes: string[];
  path_confidence: number;
  is_critical_path: boolean;
}

export interface PathsResponse {
  paths: CriticalPathItem[];
  [key: string]: unknown;
}

export function postBlastRadius(body: {
  source_id: string;
  as_of?: string;
  max_depth?: number;
  max_nodes?: number;
}): Promise<BlastRadiusResponse> {
  return apiRequest<BlastRadiusResponse>('/api/v1/analysis/blast-radius', {
    method: 'POST',
    body,
  });
}

export function postReachability(body: {
  source_id: string;
  as_of?: string;
  max_depth?: number;
}): Promise<ReachabilityResponse> {
  return apiRequest<ReachabilityResponse>('/api/v1/analysis/reachability', {
    method: 'POST',
    body,
  });
}

export function fetchCriticalPaths(params: {
  source_id: string;
  target_id?: string;
  as_of?: string;
  max_depth?: number;
  max_paths?: number;
}): Promise<PathsResponse> {
  return apiRequest<PathsResponse>(`/api/v1/analysis/paths${buildQuery(params)}`);
}
