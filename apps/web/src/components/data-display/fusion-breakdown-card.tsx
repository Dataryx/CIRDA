import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { SupportTooltip } from '@/components/data-display/support-tooltip';
import type { FusionBreakdown } from '@/api/generated/schema.d';
import { formatConfidence, formatNumber } from '@/lib/format';

interface FusionBreakdownCardProps {
  breakdown: FusionBreakdown;
}

export function FusionBreakdownCard({ breakdown }: FusionBreakdownCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          Multi-channel fusion
          <SupportTooltip />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="text-sm text-muted-foreground">Fused support</span>
          <span className="font-mono text-2xl font-semibold">{formatConfidence(breakdown.fused_support)}</span>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Channel</TableHead>
              <TableHead className="text-right">Count</TableHead>
              <TableHead className="text-right">Strength (s_k)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {breakdown.channels.map((channel) => (
              <TableRow key={channel.channel}>
                <TableCell className="font-medium">{channel.channel}</TableCell>
                <TableCell className="text-right font-mono">{channel.count}</TableCell>
                <TableCell className="text-right font-mono">{formatNumber(channel.strength)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
