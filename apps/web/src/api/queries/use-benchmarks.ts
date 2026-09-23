import { useQuery } from '@tanstack/react-query';
import { fetchBenchmarkRun, fetchBenchmarkRuns } from '@/api/endpoints/benchmarks';
import { queryKeys } from '@/api/query-keys';

export function useBenchmarkRuns(params: { offset?: number; limit?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.benchmarks.runs(params),
    queryFn: () => fetchBenchmarkRuns(params),
  });
}

export function useBenchmarkRun(runId: string) {
  return useQuery({
    queryKey: queryKeys.benchmarks.run(runId),
    queryFn: () => fetchBenchmarkRun(runId),
    enabled: Boolean(runId),
  });
}
