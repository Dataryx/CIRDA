import {
  Activity,
  Beaker,
  ChevronLeft,
  FileSearch,
  Gauge,
  GitBranch,
  LayoutDashboard,
  Network,
  Settings2,
  Shield,
  Trash2,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { APP_NAME } from '@/lib/constants';
import { cn } from '@/lib/cn';
import { useUiStore } from '@/stores/ui-store';

const navItems = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/topology', label: 'Topology', icon: Network },
  { to: '/entities', label: 'Entities', icon: GitBranch },
  { to: '/decommission', label: 'Decommission', icon: Trash2 },
  { to: '/evidence', label: 'Evidence', icon: FileSearch },
  { to: '/coverage', label: 'Coverage', icon: Gauge },
  { to: '/benchmark', label: 'Benchmark', icon: Beaker },
  { to: '/calibration', label: 'Calibration', icon: Settings2 },
  { to: '/audit', label: 'Audit', icon: Shield },
];

export function AppSidebar() {
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUiStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        'fixed inset-y-0 left-0 z-40 flex flex-col border-r bg-brand text-white transition-all',
        collapsed ? 'w-16' : 'w-64',
      )}
    >
      <div className="flex h-16 items-center justify-between px-4">
        {!collapsed ? (
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6" />
            <span className="font-semibold">{APP_NAME}</span>
          </div>
        ) : (
          <Activity className="mx-auto h-6 w-6" />
        )}
      </div>
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive ? 'bg-white/20 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white',
              )
            }
          >
            <Icon className="h-5 w-5 shrink-0" />
            {!collapsed ? <span>{label}</span> : null}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 p-2">
        <Button
          variant="ghost"
          size="icon"
          className="w-full text-white hover:bg-white/10 hover:text-white"
          onClick={toggleSidebar}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <ChevronLeft className={cn('h-5 w-5 transition-transform', collapsed && 'rotate-180')} />
        </Button>
      </div>
    </aside>
  );
}
