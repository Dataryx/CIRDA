/** Hand-authored OpenAPI-derived types for CIRDA API v1 */

export type Verdict = 'UNSAFE' | 'SAFE' | 'INDETERMINATE';
export type GraphLayer = 'confirmed' | 'possible' | 'all';
export type EntityType =
  | 'agent'
  | 'tool'
  | 'service'
  | 'data'
  | 'queue'
  | 'credential'
  | 'model';

export interface PageMeta {
  total: number;
  offset: number;
  limit: number;
}

export interface Paginated<T> {
  items: T[];
  page: PageMeta;
}

export interface HealthResponse {
  status: string;
  version: string;
}

export interface ReadinessResponse {
  status: string;
  database: string;
  redis: string;
}

export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  errors?: Record<string, string[]>;
}

export interface GraphNode {
  entity_id: string;
  entity_type: string;
  name: string;
  criticality: string;
}

export interface GraphEdge {
  edge_id: string;
  source_id: string;
  target_id: string;
  relation: string;
  layer: string;
  confidence: number;
  necessity?: string;
  evidence_count?: number;
}

export interface GraphPayload {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layer: GraphLayer | string;
  as_of?: string;
  engine_version: string;
}

export interface CoverageEstimate {
  coverage: number;
  observed_entities: number;
  total_entities: number;
  suppressed_channels: string[];
  meets_threshold: boolean;
  c_min: number;
  as_of?: string;
}

export interface CoverageSnapshotResponse {
  snapshot_id: string;
  coverage: number;
  observed_entities: number;
  total_entities: number;
  suppressed_channels: string[];
  scope?: string;
  captured_at: string;
}

export interface ChannelHealthEntry {
  channel: string;
  health_score: number;
  lag_seconds?: number;
  last_seen_at?: string;
}

export interface ChannelHealthResponse {
  channels: ChannelHealthEntry[];
}

export interface RunbookAction {
  stage: string;
  description: string;
  entity_id?: string | null;
}

export interface BlastRadiusSummary {
  all_reachable_count: number;
  critical_reachable_count: number;
  critical_reachable: string[];
  truncated: boolean;
  layer: string;
}

export interface ProbePlan {
  entity_id: string;
  channels: string[];
  rationale: string;
  expected_delta_c?: number;
}

export interface ProbeApplyRequest {
  entity_id: string;
  channels: string[];
  as_of?: string | null;
}

export interface ProbeApplyResult {
  entity_id: string;
  channels: string[];
  mode: string;
  coverage_before: number;
  coverage_after: number;
  expected_delta_c: number;
  actual_delta_c: number;
  suppressed_channels_after: string[];
  as_of?: string | null;
}

export interface DecisionRationale {
  summary: string;
  details: string[];
  reason_codes: string[];
  blast_radius: BlastRadiusSummary;
  coverage_breakdown: CoverageEstimate;
  suggested_runbook: RunbookAction[];
  suggested_probes?: ProbePlan[];
}

export interface DecisionPath {
  nodes: string[];
  edges: string[];
  length?: number;
}

export interface DecisionReport {
  decision_id: string;
  entity_id: string;
  verdict: Verdict;
  coverage: number;
  truncated: boolean;
  reason_codes: string[];
  rationale: DecisionRationale;
  limitations_footer: string;
  as_of: string;
  engine_version: string;
  change_type?: string | null;
  supersedes?: string | null;
  superseded_by?: string | null;
  created_by?: string | null;
  created_at?: string | null;
  paths: DecisionPath[] | Record<string, unknown>[];
}

export interface DecisionEvaluateRequest {
  entity_id: string;
  as_of?: string;
  change_type?: string;
}

export interface EntityResponse {
  entity_id: string;
  entity_type: EntityType | string;
  name: string;
  criticality?: string;
  metadata?: Record<string, unknown>;
  aliases?: string[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface EntityCreateRequest {
  entity_id: string;
  entity_type: EntityType;
  name: string;
  criticality?: string;
  metadata?: Record<string, unknown>;
}

export interface EdgeResponse {
  edge_id: string;
  source_id: string;
  target_id: string;
  relation: string;
  layer: string;
  confidence: number;
  necessity?: string;
  evidence_count?: number;
}

export interface EdgeNecessityUpdate {
  necessity: string;
}

export interface NecessityHint {
  edge_id: string;
  source_id: string;
  target_id: string;
  current_necessity: string;
  suggested_necessity: string;
  confidence: number;
  rationale: string;
  signals?: Record<string, unknown>;
}

export interface NecessityHintListResponse {
  source_id: string;
  items: NecessityHint[];
  mode: string;
}

export interface EdgeEvidenceResponse {
  edge_id: string;
  events: EvidenceEventResponse[];
}

export interface EvidenceEventResponse {
  event_id: string;
  source_id: string;
  target_id: string;
  relation: string;
  channel: string;
  observed_at: string;
  source_type?: string | null;
  target_type?: string | null;
  payload_hash?: string | null;
}

export interface IngestEventRequest {
  raw: Record<string, unknown>;
  idempotency_key?: string;
}

export interface IngestResult {
  event: EvidenceEventResponse;
  created: boolean;
  edge_updated: boolean;
}

export interface BenchmarkRunCreate {
  config?: Record<string, unknown>;
}

export interface BenchmarkRunResponse {
  run_id: string;
  status: string;
  config: Record<string, unknown>;
  started_at?: string | null;
  completed_at?: string | null;
  created_at?: string | null;
}

export interface BenchmarkResultResponse {
  result_id: string;
  run_id: string;
  loss: number;
  method: string;
  metrics: Record<string, unknown>;
  data_class: string;
  created_at?: string | null;
}

export interface BenchmarkResultsEnvelope {
  run: BenchmarkRunResponse;
  results: BenchmarkResultResponse[];
  data_class: string;
}

export interface CalibrationProfile {
  profile_id: string;
  name: string;
  theta_c: number;
  theta_p: number;
  c_min: number;
  is_active: boolean;
}

export interface CalibrationUpdate {
  theta_c: number;
  theta_p: number;
  c_min: number;
}

export interface AuditEntry {
  log_id: string;
  principal_id: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  details: Record<string, unknown>;
  created_at: string;
}

export interface BlastRadiusResponse {
  source_id: string;
  all_reachable: string[];
  critical_reachable: string[];
  truncated: boolean;
  layer: string;
}

export interface ReachabilityResponse {
  source_id: string;
  reachable: string[];
  truncated: boolean;
}

export interface FusionChannelBreakdown {
  channel: string;
  count: number;
  strength: number;
}

export interface FusionBreakdown {
  fused_support: number;
  channels: FusionChannelBreakdown[];
}

export type EntityListResponse = Paginated<EntityResponse>;
export type EdgeListResponse = Paginated<EdgeResponse>;
export type EvidenceListResponse = Paginated<EvidenceEventResponse>;
export type DecisionListResponse = Paginated<DecisionReport>;
export type BenchmarkRunListResponse = Paginated<BenchmarkRunResponse>;
export type AuditListResponse = Paginated<AuditEntry>;
export type CoverageSnapshotListResponse = Paginated<CoverageSnapshotResponse>;
