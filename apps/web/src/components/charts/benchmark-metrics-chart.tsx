import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { CHART_COLORS } from '@/lib/constants';

interface BenchmarkMetricsChartProps {
  data: Array<Record<string, string | number>>;
  metrics: string[];
}

export function BenchmarkMetricsChart({ data, metrics }: BenchmarkMetricsChartProps) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis dataKey="method" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        {metrics.map((metric, index) => (
          <Bar
            key={metric}
            dataKey={metric}
            fill={CHART_COLORS[index % CHART_COLORS.length]}
            radius={[4, 4, 0, 0]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
