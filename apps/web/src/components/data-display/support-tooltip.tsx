import { HelpCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { S_SUPPORT_TOOLTIP } from '@/lib/constants';

interface SupportTooltipProps {
  label?: string;
}

export function SupportTooltip({ label = 'S' }: SupportTooltipProps) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground"
            aria-label={`About ${label}`}
          >
            <span className="font-mono font-medium">{label}</span>
            <HelpCircle className="h-3.5 w-3.5" />
          </button>
        </TooltipTrigger>
        <TooltipContent>{S_SUPPORT_TOOLTIP}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
