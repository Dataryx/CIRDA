import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createEntity, fetchEntities, fetchEntity } from '@/api/endpoints/entities';
import { queryKeys } from '@/api/query-keys';

export function useEntities(params: { offset?: number; limit?: number; entity_type?: string } = {}) {
  return useQuery({
    queryKey: queryKeys.entities.list(params),
    queryFn: () => fetchEntities(params),
  });
}

export function useEntity(entityId: string) {
  return useQuery({
    queryKey: queryKeys.entities.detail(entityId),
    queryFn: () => fetchEntity(entityId),
    enabled: Boolean(entityId),
  });
}

export function useCreateEntity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createEntity,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.entities.all });
    },
  });
}
