import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { loadRuntimeConfig } from '@/app/config';
import { createQueryClient } from '@/app/query-client';
import { router } from '@/app/router';
import { ErrorBoundary } from '@/app/error-boundary';
import { TooltipProvider } from '@/components/ui/tooltip';
import { useAuthInit } from '@/hooks/use-auth';
import { useThemeEffect } from '@/hooks/use-theme';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { useAuthStore } from '@/stores/auth-store';

const queryClient = createQueryClient();

function AppInitializer({ children }: { children: React.ReactNode }) {
  useAuthInit();
  useThemeEffect();
  return children;
}

export function Providers() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    void loadRuntimeConfig().then((config) => {
      if (config.authMode === 'dev' && !useAuthStore.getState().session) {
        useAuthStore.getState().login('viewer');
      }
      setReady(true);
    });
  }, []);

  if (!ready) {
    return <LoadingSpinner label="Initializing…" className="min-h-screen" />;
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <AppInitializer>
            <RouterProvider router={router} />
          </AppInitializer>
        </TooltipProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
