import { useEffect } from 'react';
import { setAuthGetters } from '@/api/client';
import { useAuthStore } from '@/stores/auth-store';

export function useAuthInit(): void {
  useEffect(() => {
    setAuthGetters(
      () => useAuthStore.getState().session?.token ?? null,
      () => useAuthStore.getState().session?.role ?? null,
    );
  }, []);
}

export function useAuth() {
  const session = useAuthStore((s) => s.session);
  const login = useAuthStore((s) => s.login);
  const logout = useAuthStore((s) => s.logout);
  return { session, login, logout, isAuthenticated: Boolean(session) };
}
