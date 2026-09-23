import { useQuery } from '@tanstack/react-query';
import { fetchGraph } from '@/api/endpoints/graph';
import { queryKeys } from '@/api/query-keys';
import type { GraphLayer } from '@/api/generated/schema.d';

export function useGraph(params: { layer?: GraphLayer; as_of?: string } = {}) {
  return useQuery({
    queryKey: queryKeys.graph(params),
    queryFn: () => fetchGraph(params),
  });
}
