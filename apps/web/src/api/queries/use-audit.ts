import { useQuery } from '@tanstack/react-query';
import { fetchAuditLog } from '@/api/endpoints/audit';
import { queryKeys } from '@/api/query-keys';

export function useAuditLog(params: { offset?: number; limit?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.audit(params),
    queryFn: () => fetchAuditLog(params),
  });
}
