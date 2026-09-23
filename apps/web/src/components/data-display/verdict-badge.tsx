import type { Verdict } from '@/api/generated/schema.d';
import { cn } from '@/lib/cn';
import { getVerdictDisplay } from '@/lib/verdict';

interface VerdictBadgeProps {
  verdict: Verdict;
  size?: 'sm' | 'md' | 'lg';
  showDescription?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
  lg: 'px-4 py-2 text-base',
};

export function VerdictBadge({ verdict, size = 'md', showDescription = false, className }: VerdictBadgeProps) {
  const display = getVerdictDisplay(verdict);
  const Icon = display.icon;

  return (
    <div className={cn('inline-flex flex-col gap-1', className)}>
      <span
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full border font-semibold',
          display.textClass,
          display.bgClass,
          display.borderClass,
          sizeClasses[size],
        )}
        role="status"
        aria-label={`Verdict: ${display.label}`}
      >
        <Icon className={size === 'lg' ? 'h-5 w-5' : 'h-4 w-4'} aria-hidden />
        {display.label}
      </span>
      {showDescription ? (
        <p className="max-w-prose text-sm text-muted-foreground">{display.description}</p>
      ) : null}
    </div>
  );
}
