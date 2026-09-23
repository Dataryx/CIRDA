import { getApiBaseUrl } from '@/app/config';
import type { ProblemDetail } from '@/api/generated/schema.d';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly problem?: ProblemDetail,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

type TokenGetter = () => string | null;
type RoleGetter = () => string | null;

let tokenGetter: TokenGetter = () => null;
let roleGetter: RoleGetter = () => null;

export function setAuthGetters(getToken: TokenGetter, getRole: RoleGetter): void {
  tokenGetter = getToken;
  roleGetter = getRole;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...options.headers,
  };

  const token = tokenGetter();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const role = roleGetter();
  if (role) {
    headers['X-CIRDA-Role'] = role;
  }

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    method: options.method ?? 'GET',
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  if (!response.ok) {
    let problem: ProblemDetail | undefined;
    const contentType = response.headers.get('content-type') ?? '';
    if (contentType.includes('application/problem+json') || contentType.includes('application/json')) {
      try {
        problem = (await response.json()) as ProblemDetail;
      } catch {
        // ignore parse errors
      }
    }
    throw new ApiError(problem?.detail ?? problem?.title ?? response.statusText, response.status, problem);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function buildQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : '';
}
