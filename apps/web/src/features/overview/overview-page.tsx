import { Link } from 'react-router-dom';
import { useCoverage } from '@/api/queries/use-coverage';
import { useEntities } from '@/api/queries/use-entities';
import { useEdges } from '@/api/queries/use-edges';
import { useHealth } from '@/api/queries/use-health';
import { StatCard } from '@/components/data-display/stat-card';
import { VerdictBadge } from '@/components/data-display/verdict-badge';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatPercent } from '@/lib/format';
import { formatDateTime } from '@/lib/datetime';

export function OverviewPage() {
  const health = useHealth();
  const coverage = useCoverage();
  const entities = useEntities({ limit: 1 });
  const edges = useEdges({ limit: 1 });

  const isLoading = health.isLoading || coverage.isLoading || entities.isLoading || edges.isLoading;
  const error = health.error ?? coverage.error ?? entities.error ?? edges.error;

  if (isLoading) return <LoadingSpinner label="Loading overview…" />;
  if (error) return <ErrorAlert error={error} />;

  const coverageData = coverage.data;
  const entityTotal = entities.data?.page.total ?? 0;
  const edgeTotal = edges.data?.page.total ?? 0;

  return (
    <div>
      <PageHeader
        title="Overview"
        description="System health, observability coverage, and dependency graph summary."
      />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="API Status"
          value={health.data?.status === 'ok' ? 'Healthy' : 'Degraded'}
          description={`Engine ${health.data?.version ?? '—'}`}
        />
        <StatCard
          title="Coverage"
          value={coverageData ? formatPercent(coverageData.coverage) : '—'}
          description={
            coverageData
              ? `${coverageData.observed_entities} / ${coverageData.total_entities} entities observed`
              : undefined
          }
        />
        <StatCard title="Entities" value={String(entityTotal)} description="Registered in graph" />
        <StatCard title="Edges" value={String(edgeTotal)} description="Dependency relationships" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Coverage threshold</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {coverageData ? (
              <>
                <p>
                  Minimum required (C<sub>min</sub>):{' '}
                  <span className="font-mono font-medium">{formatPercent(coverageData.c_min)}</span>
                </p>
                <p>
                  Meets threshold:{' '}
                  <span className="font-medium">{coverageData.meets_threshold ? 'Yes' : 'No'}</span>
                </p>
                {coverageData.suppressed_channels.length > 0 ? (
                  <p className="text-muted-foreground">
                    Suppressed channels: {coverageData.suppressed_channels.join(', ')}
                  </p>
                ) : null}
                {coverageData.as_of ? (
                  <p className="text-muted-foreground">As of {formatDateTime(coverageData.as_of)}</p>
                ) : null}
              </>
            ) : (
              <p className="text-muted-foreground">No coverage data available.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick actions</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2 text-sm">
            <Link to="/decommission" className="text-primary hover:underline">
              Evaluate decommission decision →
            </Link>
            <Link to="/topology" className="text-primary hover:underline">
              Explore dependency topology →
            </Link>
            <Link to="/coverage" className="text-primary hover:underline">
              Review channel health →
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="mt-6">
        <h2 className="mb-3 text-lg font-semibold">Verdict reference</h2>
        <div className="flex flex-wrap gap-4">
          <VerdictBadge verdict="UNSAFE" showDescription />
          <VerdictBadge verdict="SAFE" showDescription />
          <VerdictBadge verdict="INDETERMINATE" showDescription />
        </div>
      </div>
    </div>
  );
}
