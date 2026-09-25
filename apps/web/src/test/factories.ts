import type {
  CoverageEstimate,
  DecisionReport,
  EntityResponse,
  GraphPayload,
  HealthResponse,
} from '@/api/generated/schema.d';

export function createHealthResponse(overrides: Partial<HealthResponse> = {}): HealthResponse {
  return { status: 'ok', version: '0.1.0-test', ...overrides };
}

export function createCoverageEstimate(overrides: Partial<CoverageEstimate> = {}): CoverageEstimate {
  return {
    coverage: 0.91,
    observed_entities: 91,
    total_entities: 100,
    suppressed_channels: [],
    meets_threshold: true,
    c_min: 0.85,
    as_of: '2026-01-15T12:00:00Z',
    ...overrides,
  };
}

export function createEntity(overrides: Partial<EntityResponse> = {}): EntityResponse {
  return {
    entity_id: 'svc-billing',
    entity_type: 'service',
    name: 'Billing Service',
    criticality: 'high',
    metadata: {},
    aliases: [],
    ...overrides,
  };
}

export function createDecisionReport(overrides: Partial<DecisionReport> = {}): DecisionReport {
  return {
    decision_id: 'dec-001',
    entity_id: 'svc-billing',
    verdict: 'INDETERMINATE',
    coverage: 0.91,
    truncated: false,
    reason_codes: ['COVERAGE_BELOW_THRESHOLD'],
    rationale: {
      summary: 'Entity svc-billing is INDETERMINATE: insufficient evidence or coverage.',
      details: ['COVERAGE_BELOW_THRESHOLD'],
      reason_codes: ['COVERAGE_BELOW_THRESHOLD'],
      blast_radius: {
        all_reachable_count: 5,
        critical_reachable_count: 1,
        critical_reachable: ['db-payments'],
        truncated: false,
        layer: 'possible',
      },
      coverage_breakdown: createCoverageEstimate(),
      suggested_runbook: [
        { stage: 'observe_downstream', description: 'Observe downstream impact', entity_id: 'svc-billing' },
      ],
      suggested_probes: [
        {
          entity_id: 'svc-billing',
          channels: ['database'],
          rationale: 'Restore database audit/collector coverage for this entity\'s data dependencies.',
          expected_delta_c: 0.112,
        },
      ],
    },
    limitations_footer:
      'Limitations (§X): CIRDA decisions reflect observability coverage and inferred dependency structure at the evaluation timestamp.',
    as_of: '2026-01-15T12:00:00Z',
    engine_version: '0.1.0-test',
    paths: [
      {
        path_nodes: ['svc-billing', 'db-payments'],
        path_confidence: 0.87,
        is_critical_path: true,
      },
    ],
    ...overrides,
  };
}

export function createGraphPayload(overrides: Partial<GraphPayload> = {}): GraphPayload {
  return {
    nodes: [
      { entity_id: 'svc-a', entity_type: 'service', name: 'Service A', criticality: 'high' },
      { entity_id: 'svc-b', entity_type: 'service', name: 'Service B', criticality: 'low' },
    ],
    edges: [
      {
        edge_id: 'svc-a->svc-b:calls',
        source_id: 'svc-b',
        target_id: 'svc-a',
        relation: 'calls',
        layer: 'confirmed',
        confidence: 0.82,
        evidence_count: 12,
      },
    ],
    layer: 'all',
    engine_version: '0.1.0-test',
    ...overrides,
  };
}
