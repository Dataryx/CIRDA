import { useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useBenchmarkRun } from '@/api/queries/use-benchmarks';
import { BenchmarkMetricsChart } from '@/components/charts/benchmark-metrics-chart';
import { SyntheticDataBanner } from '@/components/data-display/synthetic-data-banner';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatDateTime } from '@/lib/datetime';
import { formatNumber } from '@/lib/format';

export function BenchmarkRunPage() {
  const { runId = '' } = useParams();
  const run = useBenchmarkRun(runId);

  const { chartData, metrics } = useMemo(() => {
    if (!run.data) return { chartData: [], metrics: [] as string[] };
    const metricKeys = new Set<string>();
    for (const result of run.data.results) {
      for (const key of Object.keys(result.metrics)) {
        if (typeof result.metrics[key] === 'number') {
          metricKeys.add(key);
        }
      }
    }
    const keys = [...metricKeys].slice(0, 4);
    const data = run.data.results.map((result) => {
      const row: Record<string, string | number> = { method: result.method };
      for (const key of keys) {
        const value = result.metrics[key];
        if (typeof value === 'number') row[key] = value;
      }
      return row;
    });
    return { chartData: data, metrics: keys };
  }, [run.data]);

  if (run.isLoading) return <LoadingSpinner label="Loading benchmark run…" />;
  if (run.error) return <ErrorAlert error={run.error} />;
  if (!run.data) return null;

  return (
    <div>
      <PageHeader title="Benchmark Run" description={run.data.run.run_id} />

      <SyntheticDataBanner className="mb-6" />

      <div className="mb-6 text-sm text-muted-foreground">
        Status: {run.data.run.status} · Started {formatDateTime(run.data.run.started_at)} · Completed{' '}
        {formatDateTime(run.data.run.completed_at)}
      </div>

      {chartData.length > 0 && metrics.length > 0 ? (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">Method comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <BenchmarkMetricsChart data={chartData} metrics={metrics} />
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Results</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Method</TableHead>
                <TableHead className="text-right">Loss</TableHead>
                <TableHead>Metrics</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {run.data.results.map((result) => (
                <TableRow key={result.result_id}>
                  <TableCell className="font-medium">{result.method}</TableCell>
                  <TableCell className="text-right font-mono">{formatNumber(result.loss)}</TableCell>
                  <TableCell className="font-mono text-xs">
                    {Object.entries(result.metrics)
                      .map(([k, v]) => `${k}=${String(v)}`)
                      .join(', ')}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
