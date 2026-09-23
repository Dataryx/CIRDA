import { Link } from 'react-router-dom';
import { useBenchmarkRuns } from '@/api/queries/use-benchmarks';
import { SyntheticDataBanner } from '@/components/data-display/synthetic-data-banner';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { EmptyState } from '@/components/feedback/empty-state';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatDateTime } from '@/lib/datetime';

export function BenchmarkPage() {
  const runs = useBenchmarkRuns({ limit: 25 });

  return (
    <div>
      <PageHeader
        title="Benchmark"
        description="Synthetic benchmark runs comparing CIRDA against baseline methods."
      />

      <SyntheticDataBanner className="mb-6" />

      {runs.isLoading ? <LoadingSpinner /> : null}
      {runs.error ? <ErrorAlert error={runs.error} /> : null}
      {runs.data && runs.data.items.length === 0 ? (
        <EmptyState title="No benchmark runs" description="Create a run via the API to see results here." />
      ) : null}
      {runs.data && runs.data.items.length > 0 ? (
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Run ID</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>Completed</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.data.items.map((run) => (
                <TableRow key={run.run_id}>
                  <TableCell className="font-mono text-xs">{run.run_id}</TableCell>
                  <TableCell>
                    <Badge variant={run.status === 'completed' ? 'default' : 'secondary'}>{run.status}</Badge>
                  </TableCell>
                  <TableCell className="text-sm">{formatDateTime(run.started_at)}</TableCell>
                  <TableCell className="text-sm">{formatDateTime(run.completed_at)}</TableCell>
                  <TableCell>
                    <Link
                      to={`/benchmark/runs/${encodeURIComponent(run.run_id)}`}
                      className="text-sm text-primary hover:underline"
                    >
                      View results
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}
    </div>
  );
}
