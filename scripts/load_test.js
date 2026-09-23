/**
 * k6 load test stub for CIRDA ingest + decision endpoints.
 *
 * Install k6: https://k6.io/docs/get-started/installation/
 * Run:
 *   k6 run scripts/load_test.js
 *   k6 run -e API_URL=http://localhost:8000 -e VUS=10 -e DURATION=30s scripts/load_test.js
 *
 * Scenarios:
 *   - steady ingest of trace events
 *   - periodic decision evaluation on demo agent
 *   - health check baseline
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

const API_URL = __ENV.API_URL || 'http://localhost:8000';
const AUTH_HEADERS = {
  Authorization: 'Bearer dev',
  'X-CIRDA-Role': 'analyst',
  'Content-Type': 'application/json',
};

const ingestDuration = new Trend('cirda_ingest_duration', true);
const decisionDuration = new Trend('cirda_decision_duration', true);
const ingestErrors = new Rate('cirda_ingest_errors');
const ingestTotal = new Counter('cirda_ingest_total');

export const options = {
  scenarios: {
    health_baseline: {
      executor: 'constant-vus',
      vus: 1,
      duration: __ENV.DURATION || '30s',
      exec: 'healthCheck',
    },
    ingest_steady: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: Number(__ENV.VUS) || 5 },
        { duration: __ENV.DURATION || '30s', target: Number(__ENV.VUS) || 5 },
        { duration: '10s', target: 0 },
      ],
      exec: 'ingestEvent',
    },
    decision_periodic: {
      executor: 'constant-arrival-rate',
      rate: 2,
      timeUnit: '1s',
      duration: __ENV.DURATION || '30s',
      preAllocatedVUs: 3,
      maxVUs: 10,
      exec: 'evaluateDecision',
    },
  },
  thresholds: {
    cirda_ingest_errors: ['rate<0.05'],
    http_req_failed: ['rate<0.1'],
    cirda_ingest_duration: ['p(95)<500'],
    cirda_decision_duration: ['p(95)<2000'],
  },
};

export function healthCheck() {
  const res = http.get(`${API_URL}/api/v1/health`);
  check(res, { 'health ok': (r) => r.status === 200 });
  sleep(1);
}

export function ingestEvent() {
  const eventId = `k6-${__VU}-${__ITER}-${Date.now()}`;
  const payload = JSON.stringify({
    raw: {
      event_id: eventId,
      source: 'trace',
      source_id: 'legacy-csv-export-agent',
      target_id: 'csv-export-bucket',
      relation: 'writes',
      observed_at: new Date().toISOString(),
    },
  });

  const res = http.post(`${API_URL}/api/v1/ingest/events`, payload, { headers: AUTH_HEADERS });
  ingestDuration.add(res.timings.duration);
  ingestTotal.add(1);
  ingestErrors.add(res.status !== 200);
  check(res, { 'ingest 200': (r) => r.status === 200 });
  sleep(0.2);
}

export function evaluateDecision() {
  const payload = JSON.stringify({
    entity_id: 'invoice-reconciler-agent',
    change_type: 'retirement',
  });
  const res = http.post(`${API_URL}/api/v1/decisions/evaluate`, payload, {
    headers: { ...AUTH_HEADERS, 'X-CIRDA-Role': 'approver' },
  });
  decisionDuration.add(res.timings.duration);
  check(res, { 'decision 201/200': (r) => r.status === 201 || r.status === 200 });
  sleep(0.5);
}

export function handleSummary(data) {
  return {
    stdout: JSON.stringify(data, null, 2),
  };
}
