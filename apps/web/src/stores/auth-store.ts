import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthSession, UserRole } from '@/types/domain';

interface AuthState {
  session: AuthSession | null;
  login: (role: UserRole) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      session: null,
      login: (role) =>
        set({
          session: {
            token: 'dev',
            role,
            principalId: `dev-${role}`,
          },
        }),
      logout: () => set({ session: null }),
    }),
    { name: 'cirda-auth' },
  ),
);
