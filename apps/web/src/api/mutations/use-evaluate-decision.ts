import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  applyProbes,
  evaluateDecision,
  rerunDecision,
  updateRunbookStage,
} from '@/api/endpoints/decisions';
import { queryKeys } from '@/api/query-keys';
import type { DecisionEvaluateRequest } from '@/api/generated/schema.d';
import type { ProbeApplyRequest } from '@/api/endpoints/decisions';

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

export function useApplyProbes() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ProbeApplyRequest) => applyProbes(body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['decisions'] });
      void queryClient.invalidateQueries({ queryKey: ['coverage'] });
    },
  });
}

export function useUpdateRunbookStage(decisionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      executionId,
      status,
      notes,
    }: {
      executionId: string;
      status: string;
      notes?: string | null;
    }) => updateRunbookStage(decisionId, executionId, { status, notes }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.decisions.detail(decisionId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.decisions.runbook(decisionId) });
    },
  });
}
