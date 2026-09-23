import { Outlet } from 'react-router-dom';
import { AppHeader } from '@/components/layout/app-header';
import { AppSidebar } from '@/components/layout/app-sidebar';
import { cn } from '@/lib/cn';
import { useUiStore } from '@/stores/ui-store';

export function AppShell() {
  const collapsed = useUiStore((s) => s.sidebarCollapsed);

  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <div className={cn('flex min-h-screen flex-1 flex-col transition-all', collapsed ? 'md:pl-16' : 'md:pl-64')}>
        <AppHeader />
        <main className="flex-1 p-4 md:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
