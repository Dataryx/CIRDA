import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Navigate, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/hooks/use-auth';
import { APP_NAME, ROLES } from '@/lib/constants';
import { loginSchema, type LoginFormValues } from '@/lib/zod-schemas';

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { setValue, handleSubmit, watch } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { role: 'viewer' },
  });

  const role = watch('role');

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{APP_NAME} Dashboard</CardTitle>
          <CardDescription>Sign in with dev credentials to access the analysis console.</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="space-y-4"
            onSubmit={handleSubmit((values) => {
              login(values.role);
              navigate('/');
            })}
          >
            <div className="space-y-2">
              <label htmlFor="role" className="text-sm font-medium">
                Role
              </label>
              <Select value={role} onValueChange={(value) => setValue('role', value as LoginFormValues['role'])}>
                <SelectTrigger id="role">
                  <SelectValue placeholder="Select role" />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((r) => (
                    <SelectItem key={r} value={r} className="capitalize">
                      {r}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" className="w-full" variant="brand">
              Continue as {role}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
