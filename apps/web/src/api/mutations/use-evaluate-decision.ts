import { useMutation, useQueryClient } from '@tanstack/react-query';
import { evaluateDecision, rerunDecision } from '@/api/endpoints/decisions';
import { queryKeys } from '@/api/query-keys';
import type { DecisionEvaluateRequest } from '@/api/generated/schema.d';

export function useEvaluateDecision() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: DecisionEvaluateRequest) => evaluateDecision(body),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.decisions.detail(data.decision_id) });
      void queryClient.invalidateQueries({ queryKey: ['decisions'] });
    },
  });
}

export function useRerunDecision() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (decisionId: string) => rerunDecision(decisionId),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.decisions.detail(data.decision_id) });
      void queryClient.invalidateQueries({ queryKey: ['decisions'] });
    },
  });
}
