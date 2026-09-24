import { test, type APIRequestContext } from '@playwright/test';

export const API_BASE = process.env.CIRDA_API_URL ?? process.env.PLAYWRIGHT_API_URL ?? 'http://localhost:8000';

export const AUTH_HEADERS = {
  Authorization: 'Bearer dev',
  'X-CIRDA-Role': 'admin',
};

export const DEMO_AGENTS = {
  unsafe: 'invoice-reconciler-agent',
  safe: 'legacy-csv-export-agent',
  indeterminate: 'vendor-risk-agent',
} as const;

const HEALTH_PATHS = ['/healthz', '/api/v1/health', '/health'];

export type LiveApiStatus = {
  ok: boolean;
  reason?: string;
  healthPath?: string;
};

export async function checkLiveApi(request: APIRequestContext): Promise<LiveApiStatus> {
  for (const path of HEALTH_PATHS) {
    try {
      const response = await request.get(`${API_BASE}${path}`, { headers: AUTH_HEADERS });
      if (response.status() >= 500) {
        return { ok: false, reason: `${path} returned ${response.status()}` };
      }
      if (response.ok()) {
        return { ok: true, healthPath: path };
      }
    } catch {
      // try next path
    }
  }
  return { ok: false, reason: 'API unreachable on /healthz, /api/v1/health, and /health' };
}

export async function isDemoEstateSeeded(request: APIRequestContext): Promise<boolean> {
  try {
    const response = await request.get(`${API_BASE}/api/v1/entities`, {
      headers: AUTH_HEADERS,
      params: { limit: 100 },
    });
    if (!response.ok()) {
      return false;
    }
    const payload = (await response.json()) as { items: Array<{ entity_id: string }> };
    const ids = new Set(payload.items.map((item) => item.entity_id));
    return Object.values(DEMO_AGENTS).every((agentId) => ids.has(agentId));
  } catch {
    return false;
  }
}

export type DecisionReport = {
  decision_id: string;
  entity_id: string;
  verdict: 'UNSAFE' | 'SAFE' | 'INDETERMINATE';
};

/** Historical as_of for vendor-risk INDETERMINATE (coverage gap before full ingest). */
export const VENDOR_INDETERMINATE_AS_OF = new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString();

export async function evaluateDecision(
  request: APIRequestContext,
  entityId: string,
  options?: { asOf?: string },
): Promise<DecisionReport | null> {
  const response = await request.post(`${API_BASE}/api/v1/decisions/evaluate`, {
    headers: { ...AUTH_HEADERS, 'Content-Type': 'application/json' },
    data: {
      entity_id: entityId,
      change_type: 'decommission',
      ...(options?.asOf ? { as_of: options.asOf } : {}),
    },
  });
  if (!response.ok()) {
    return null;
  }
  return (await response.json()) as DecisionReport;
}

export async function fetchFirstEdgeId(request: APIRequestContext): Promise<string | null> {
  const response = await request.get(`${API_BASE}/api/v1/edges`, {
    headers: AUTH_HEADERS,
    params: { limit: 1 },
  });
  if (!response.ok()) {
    return null;
  }
  const payload = (await response.json()) as { items: Array<{ edge_id: string }> };
  return payload.items[0]?.edge_id ?? null;
}

/** Soft-skip when live API is down, returns 5xx, or demo estate is missing. */
export async function requireLiveDemo(request: APIRequestContext): Promise<void> {
  const health = await checkLiveApi(request);
  if (!health.ok) {
    test.skip(true, health.reason ?? 'Live API unavailable');
  }

  const seeded = await isDemoEstateSeeded(request);
  if (!seeded) {
    test.skip(true, 'Demo estate not seeded — run scripts/dev-lite.ps1 or seed_demo_estate.py');
  }
}
