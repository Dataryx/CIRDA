import { useEffect } from 'react';
import { Navigate, useSearchParams } from 'react-router-dom';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { useAuth } from '@/hooks/use-auth';
import type { UserRole } from '@/types/domain';

const VALID_ROLES: UserRole[] = ['viewer', 'analyst', 'approver', 'admin'];

function parseRole(value: string | null): UserRole {
  if (value && VALID_ROLES.includes(value as UserRole)) {
    return value as UserRole;
  }
  return 'viewer';
}

export function AuthCallbackPage() {
  const [params] = useSearchParams();
  const { login, isAuthenticated } = useAuth();

  useEffect(() => {
    const role = parseRole(params.get('role'));
    login(role);
  }, [login, params]);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <LoadingSpinner label="Completing sign-in…" />;
}
