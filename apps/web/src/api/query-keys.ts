export const queryKeys = {
  health: ['health'] as const,
  readiness: ['readiness'] as const,
  entities: {
    all: ['entities'] as const,
    list: (params: Record<string, unknown>) => ['entities', 'list', params] as const,
    detail: (entityId: string) => ['entities', 'detail', entityId] as const,
  },
  graph: (params: Record<string, unknown>) => ['graph', params] as const,
  edges: {
    list: (params: Record<string, unknown>) => ['edges', 'list', params] as const,
    detail: (edgeId: string, params?: Record<string, unknown>) =>
      ['edges', 'detail', edgeId, params ?? {}] as const,
    evidence: (edgeId: string) => ['edges', 'evidence', edgeId] as const,
    necessitySuggestions: (sourceId: string) =>
      ['edges', 'necessitySuggestions', sourceId] as const,
  },
  evidence: {
    list: (params: Record<string, unknown>) => ['evidence', 'list', params] as const,
    detail: (eventId: string) => ['evidence', 'detail', eventId] as const,
  },
  decisions: {
    detail: (decisionId: string) => ['decisions', 'detail', decisionId] as const,
    byEntity: (entityId: string, params: Record<string, unknown>) =>
      ['decisions', 'byEntity', entityId, params] as const,
  },
  coverage: {
    current: (params?: Record<string, unknown>) => ['coverage', 'current', params ?? {}] as const,
    snapshots: (params: Record<string, unknown>) => ['coverage', 'snapshots', params] as const,
    channelHealth: ['coverage', 'channelHealth'] as const,
  },
  calibration: ['calibration'] as const,
  benchmarks: {
    runs: (params: Record<string, unknown>) => ['benchmarks', 'runs', params] as const,
    run: (runId: string) => ['benchmarks', 'run', runId] as const,
  },
  audit: (params: Record<string, unknown>) => ['audit', params] as const,
};
