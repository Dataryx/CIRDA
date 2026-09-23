import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { CHART_COLORS } from '@/lib/constants';
import { formatPercent } from '@/lib/format';

interface CoverageChartProps {
  data: Array<{ label: string; value: number }>;
}

export function CoverageChart({ data }: CoverageChartProps) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
        <YAxis tickFormatter={(v: number) => formatPercent(v, 0)} domain={[0, 1]} tick={{ fontSize: 12 }} />
        <Tooltip formatter={(value: number) => formatPercent(value)} />
        <Bar dataKey="value" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
