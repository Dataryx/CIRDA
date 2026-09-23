import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

interface LoadingSpinnerProps {
  label?: string;
  className?: string;
}

export function LoadingSpinner({ label = 'Loading…', className }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground', className)}>
      <Loader2 className="h-8 w-8 animate-spin" aria-hidden />
      <span className="text-sm">{label}</span>
    </div>
  );
}
