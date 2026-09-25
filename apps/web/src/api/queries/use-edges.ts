import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  fetchEdge,
  fetchEdgeEvidence,
  fetchEdges,
  fetchNecessitySuggestions,
  patchEdgeNecessity,
} from '@/api/endpoints/edges';
import { queryKeys } from '@/api/query-keys';

export function useEdges(params: {
  layer?: string;
  source_id?: string;
  target_id?: string;
  offset?: number;
  limit?: number;
} = {}) {
  return useQuery({
    queryKey: queryKeys.edges.list(params),
    queryFn: () => fetchEdges(params),
  });
}

export function useEdge(edgeId: string, asOf?: string) {
  return useQuery({
    queryKey: queryKeys.edges.detail(edgeId, { as_of: asOf }),
    queryFn: () => fetchEdge(edgeId, asOf),
    enabled: Boolean(edgeId),
  });
}

export function useEdgeEvidence(edgeId: string) {
  return useQuery({
    queryKey: queryKeys.edges.evidence(edgeId),
    queryFn: () => fetchEdgeEvidence(edgeId),
    enabled: Boolean(edgeId),
  });
}

export function useNecessitySuggestions(sourceId: string) {
  return useQuery({
    queryKey: queryKeys.edges.necessitySuggestions(sourceId),
    queryFn: () => fetchNecessitySuggestions(sourceId),
    enabled: Boolean(sourceId),
  });
}

export function usePatchEdgeNecessity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ edgeId, necessity }: { edgeId: string; necessity: string }) =>
      patchEdgeNecessity(edgeId, necessity),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.edges.detail(data.edge_id) });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.edges.necessitySuggestions(data.source_id),
      });
      void queryClient.invalidateQueries({ queryKey: ['edges'] });
    },
  });
}
