import { AlertTriangle } from 'lucide-react';
import { ApiError } from '@/api/client';
import { cn } from '@/lib/cn';

interface ErrorAlertProps {
  error: unknown;
  title?: string;
  className?: string;
}

export function ErrorAlert({ error, title = 'Failed to load data', className }: ErrorAlertProps) {
  const message =
    error instanceof ApiError
      ? error.message
      : error instanceof Error
        ? error.message
        : 'An unexpected error occurred';

  return (
    <div
      className={cn(
        'flex gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm',
        className,
      )}
      role="alert"
    >
      <AlertTriangle className="h-5 w-5 shrink-0 text-destructive" aria-hidden />
      <div>
        <p className="font-medium text-destructive">{title}</p>
        <p className="mt-1 text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}
