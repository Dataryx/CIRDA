import { Info } from 'lucide-react';
import { cn } from '@/lib/cn';

interface LimitationsFooterProps {
  text: string;
  className?: string;
}

export function LimitationsFooter({ text, className }: LimitationsFooterProps) {
  if (!text) return null;

  return (
    <footer
      className={cn(
        'mt-8 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-100',
        className,
      )}
      aria-label="Decision limitations"
    >
      <div className="flex gap-3">
        <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
        <p>{text}</p>
      </div>
    </footer>
  );
}
