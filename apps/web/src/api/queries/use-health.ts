import { useQuery } from '@tanstack/react-query';
import { fetchHealth, fetchReadiness } from '@/api/endpoints/health';
import { queryKeys } from '@/api/query-keys';

export function useHealth() {
  return useQuery({ queryKey: queryKeys.health, queryFn: fetchHealth, staleTime: 30_000 });
}

export function useReadiness() {
  return useQuery({ queryKey: queryKeys.readiness, queryFn: fetchReadiness, staleTime: 15_000 });
}
