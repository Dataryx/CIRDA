import type { AppRuntimeConfig } from '@/types/domain';

const DEFAULT_CONFIG: AppRuntimeConfig = {
  apiBaseUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000/api/v1/stream',
  authMode: 'dev',
};

let cachedConfig: AppRuntimeConfig | null = null;

export async function loadRuntimeConfig(): Promise<AppRuntimeConfig> {
  if (cachedConfig) return cachedConfig;

  try {
    const response = await fetch('/config.json');
    if (response.ok) {
      const json = (await response.json()) as AppRuntimeConfig;
      cachedConfig = { ...DEFAULT_CONFIG, ...json };
      return cachedConfig;
    }
  } catch {
    // fall through to defaults
  }

  cachedConfig = {
    ...DEFAULT_CONFIG,
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? DEFAULT_CONFIG.apiBaseUrl,
    wsUrl: import.meta.env.VITE_WS_URL ?? DEFAULT_CONFIG.wsUrl,
  };
  return cachedConfig;
}

export function getApiBaseUrl(): string {
  return cachedConfig?.apiBaseUrl ?? DEFAULT_CONFIG.apiBaseUrl;
}

export function getWsUrl(): string {
  return cachedConfig?.wsUrl ?? DEFAULT_CONFIG.wsUrl;
}
