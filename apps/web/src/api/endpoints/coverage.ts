import { apiRequest, buildQuery } from '@/api/client';
import type {
  ChannelHealthResponse,
  CoverageEstimate,
  CoverageSnapshotListResponse,
} from '@/api/generated/schema.d';

export function fetchCoverage(asOf?: string): Promise<CoverageEstimate> {
  return apiRequest<CoverageEstimate>(`/api/v1/coverage${buildQuery({ as_of: asOf })}`);
}

export function fetchCoverageSnapshots(params: {
  offset?: number;
  limit?: number;
}): Promise<CoverageSnapshotListResponse> {
  return apiRequest<CoverageSnapshotListResponse>(
    `/api/v1/coverage/snapshots${buildQuery(params)}`,
  );
}

export function fetchChannelHealth(): Promise<ChannelHealthResponse> {
  return apiRequest<ChannelHealthResponse>('/api/v1/coverage/channel-health');
}
