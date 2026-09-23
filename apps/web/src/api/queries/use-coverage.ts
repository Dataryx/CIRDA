import { useQuery } from '@tanstack/react-query';
import {
  fetchChannelHealth,
  fetchCoverage,
  fetchCoverageSnapshots,
} from '@/api/endpoints/coverage';
import { queryKeys } from '@/api/query-keys';

export function useCoverage(asOf?: string) {
  return useQuery({
    queryKey: queryKeys.coverage.current({ as_of: asOf }),
    queryFn: () => fetchCoverage(asOf),
  });
}

export function useCoverageSnapshots(params: { offset?: number; limit?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.coverage.snapshots(params),
    queryFn: () => fetchCoverageSnapshots(params),
  });
}

export function useChannelHealth() {
  return useQuery({
    queryKey: queryKeys.coverage.channelHealth,
    queryFn: fetchChannelHealth,
  });
}
