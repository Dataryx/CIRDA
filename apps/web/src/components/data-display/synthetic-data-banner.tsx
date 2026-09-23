import { FlaskConical } from 'lucide-react';
import { cn } from '@/lib/cn';

interface SyntheticDataBannerProps {
  className?: string;
}

export function SyntheticDataBanner({ className }: SyntheticDataBannerProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-md border border-chart-2/40 bg-chart-2/10 px-4 py-2 text-sm text-foreground',
        className,
      )}
      role="note"
    >
      <FlaskConical className="h-4 w-4 text-chart-2" aria-hidden />
      <span>
        <strong>Synthetic benchmark data.</strong> Metrics shown are from controlled experiments, not production
        telemetry.
      </span>
    </div>
  );
}
