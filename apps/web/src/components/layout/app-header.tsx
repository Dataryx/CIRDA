import { LogOut, Moon, Sun } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/hooks/use-auth';
import { useTheme } from '@/hooks/use-theme';

export function AppHeader() {
  const { session, logout } = useAuth();
  const { theme, setTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background/95 px-4 backdrop-blur md:px-6">
      <div className="text-sm text-muted-foreground">
        Risk-aware decommissioning analysis
      </div>
      <div className="flex items-center gap-2">
        {session ? (
          <Badge variant="secondary" className="capitalize">
            {session.role}
          </Badge>
        ) : (
          <Button variant="outline" size="sm" asChild>
            <Link to="/login">Sign in</Link>
          </Button>
        )}
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
        {session ? (
          <Button variant="ghost" size="icon" onClick={logout} aria-label="Sign out">
            <LogOut className="h-5 w-5" />
          </Button>
        ) : null}
      </div>
    </header>
  );
}
