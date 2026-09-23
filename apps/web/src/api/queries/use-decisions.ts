import { useQuery } from '@tanstack/react-query';
import { fetchDecision, fetchDecisionsByEntity } from '@/api/endpoints/decisions';
import { queryKeys } from '@/api/query-keys';

export function useDecision(decisionId: string) {
  return useQuery({
    queryKey: queryKeys.decisions.detail(decisionId),
    queryFn: () => fetchDecision(decisionId),
    enabled: Boolean(decisionId),
  });
}

export function useDecisionsByEntity(
  entityId: string,
  params: { offset?: number; limit?: number } = {},
) {
  return useQuery({
    queryKey: queryKeys.decisions.byEntity(entityId, params),
    queryFn: () => fetchDecisionsByEntity(entityId, params),
    enabled: Boolean(entityId),
  });
}
