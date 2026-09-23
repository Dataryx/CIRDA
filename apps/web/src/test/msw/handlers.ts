import { http, HttpResponse } from 'msw';
import {
  createCoverageEstimate,
  createDecisionReport,
  createEntity,
  createGraphPayload,
  createHealthResponse,
} from '@/test/factories';

const API_BASE = 'http://localhost:8000';

export const handlers = [
  http.get(`${API_BASE}/api/v1/health`, () => HttpResponse.json(createHealthResponse())),
  http.get(`${API_BASE}/api/v1/health/ready`, () =>
    HttpResponse.json({ status: 'ok', database: 'ok', redis: 'ok' }),
  ),
  http.get(`${API_BASE}/api/v1/coverage`, () => HttpResponse.json(createCoverageEstimate())),
  http.get(`${API_BASE}/api/v1/coverage/snapshots`, () =>
    HttpResponse.json({ items: [], page: { total: 0, offset: 0, limit: 20 } }),
  ),
  http.get(`${API_BASE}/api/v1/coverage/channel-health`, () =>
    HttpResponse.json({ channels: [{ channel: 'trace', health_score: 0.95, lag_seconds: 12 }] }),
  ),
  http.get(`${API_BASE}/api/v1/entities`, () =>
    HttpResponse.json({
      items: [createEntity()],
      page: { total: 1, offset: 0, limit: 25 },
    }),
  ),
  http.get(`${API_BASE}/api/v1/entities/:entityId`, ({ params }) =>
    HttpResponse.json(createEntity({ entity_id: String(params.entityId) })),
  ),
  http.get(`${API_BASE}/api/v1/graph`, () => HttpResponse.json(createGraphPayload())),
  http.get(`${API_BASE}/api/v1/edges`, () =>
    HttpResponse.json({ items: [], page: { total: 0, offset: 0, limit: 25 } }),
  ),
  http.get(`${API_BASE}/api/v1/evidence`, () =>
    HttpResponse.json({ items: [], page: { total: 0, offset: 0, limit: 25 } }),
  ),
  http.get(`${API_BASE}/api/v1/decisions/:decisionId`, ({ params }) =>
    HttpResponse.json(createDecisionReport({ decision_id: String(params.decisionId) })),
  ),
  http.get(`${API_BASE}/api/v1/decisions/by-entity/:entityId`, () =>
    HttpResponse.json({ items: [], page: { total: 0, offset: 0, limit: 10 } }),
  ),
  http.get(`${API_BASE}/api/v1/benchmarks/runs`, () =>
    HttpResponse.json({ items: [], page: { total: 0, offset: 0, limit: 25 } }),
  ),
  http.get(`${API_BASE}/api/v1/calibration`, () =>
    HttpResponse.json({
      profile_id: 'default',
      name: 'Default',
      theta_c: 0.62,
      theta_p: 0.28,
      c_min: 0.85,
      is_active: true,
    }),
  ),
  http.get(`${API_BASE}/api/v1/audit`, () =>
    HttpResponse.json({ items: [], page: { total: 0, offset: 0, limit: 25 } }),
  ),
];
