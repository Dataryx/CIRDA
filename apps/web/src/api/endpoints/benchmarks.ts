import { apiRequest, buildQuery } from '@/api/client';
import type {
  BenchmarkResultsEnvelope,
  BenchmarkRunCreate,
  BenchmarkRunListResponse,
  BenchmarkRunResponse,
} from '@/api/generated/schema.d';

export function fetchBenchmarkRuns(params: {
  offset?: number;
  limit?: number;
}): Promise<BenchmarkRunListResponse> {
  return apiRequest<BenchmarkRunListResponse>(`/api/v1/benchmarks/runs${buildQuery(params)}`);
}

export function fetchBenchmarkRun(runId: string): Promise<BenchmarkResultsEnvelope> {
  return apiRequest<BenchmarkResultsEnvelope>(
    `/api/v1/benchmarks/runs/${encodeURIComponent(runId)}`,
  );
}

export function createBenchmarkRun(body: BenchmarkRunCreate): Promise<BenchmarkRunResponse> {
  return apiRequest<BenchmarkRunResponse>('/api/v1/benchmarks/runs', { method: 'POST', body });
}
