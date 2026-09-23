import { useQuery } from '@tanstack/react-query';
import { fetchEvidenceEvent, fetchEvidenceList } from '@/api/endpoints/evidence';
import { queryKeys } from '@/api/query-keys';

export function useEvidenceList(params: {
  source_id?: string;
  target_id?: string;
  channel?: string;
  offset?: number;
  limit?: number;
} = {}) {
  return useQuery({
    queryKey: queryKeys.evidence.list(params),
    queryFn: () => fetchEvidenceList(params),
  });
}

export function useEvidenceEvent(eventId: string) {
  return useQuery({
    queryKey: queryKeys.evidence.detail(eventId),
    queryFn: () => fetchEvidenceEvent(eventId),
    enabled: Boolean(eventId),
  });
}
