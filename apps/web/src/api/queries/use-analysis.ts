import { useMutation, useQuery } from '@tanstack/react-query';
import {
  fetchCriticalPaths,
  postBlastRadius,
  postReachability,
} from '@/api/endpoints/analysis';
import { queryKeys } from '@/api/query-keys';

export function useBlastRadius() {
  return useMutation({
    mutationFn: postBlastRadius,
  });
}

export function useReachability() {
  return useMutation({
    mutationFn: postReachability,
  });
}

export function useCriticalPaths(params: {
  source_id: string;
  target_id?: string;
  max_depth?: number;
  max_paths?: number;
  enabled?: boolean;
}) {
  const { enabled = true, ...query } = params;
  return useQuery({
    queryKey: queryKeys.analysis?.paths?.(query) ?? ['analysis', 'paths', query],
    queryFn: () => fetchCriticalPaths(query),
    enabled: enabled && Boolean(query.source_id),
  });
}
