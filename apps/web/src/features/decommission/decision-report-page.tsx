import { Download, RefreshCw } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { useDecision } from '@/api/queries/use-decisions';
import { useRerunDecision } from '@/api/mutations/use-evaluate-decision';
import { LimitationsFooter } from '@/components/data-display/limitations-footer';
import { StatCard } from '@/components/data-display/stat-card';
import { VerdictBadge } from '@/components/data-display/verdict-badge';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { downloadJson } from '@/lib/download';
import { formatDateTime } from '@/lib/datetime';
import { formatPercent } from '@/lib/format';
import type { DecisionRationale } from '@/api/generated/schema.d';

function isRationale(value: DecisionRationale | Record<string, unknown>): value is DecisionRationale {
  return 'summary' in value && typeof value.summary === 'string';
}

export function DecisionReportPage() {
  const { decisionId = '' } = useParams();
  const decision = useDecision(decisionId);
  const rerun = useRerunDecision();

  if (decision.isLoading) return <LoadingSpinner label="Loading decision report…" />;
  if (decision.error) return <ErrorAlert error={decision.error} />;
  if (!decision.data) return null;

  const report = decision.data;
  const rationale = isRationale(report.rationale) ? report.rationale : null;

  return (
    <div>
      <PageHeader
        title="Decision Report"
        description={`Evaluation for ${report.entity_id}`}
        actions={
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => downloadJson(`decision-${report.decision_id}.json`, report)}
            >
              <Download className="h-4 w-4" />
              Export JSON
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={rerun.isPending}
              onClick={() => rerun.mutate(report.decision_id)}
            >
              <RefreshCw className={`h-4 w-4 ${rerun.isPending ? 'animate-spin' : ''}`} />
              Rerun
            </Button>
          </div>
        }
      />

      <div className="mb-6">
        <VerdictBadge verdict={report.verdict} size="lg" showDescription />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Coverage" value={formatPercent(report.coverage)} />
        <StatCard title="Truncated" value={report.truncated ? 'Yes' : 'No'} />
        <StatCard title="Engine" value={report.engine_version} />
        <StatCard title="Evaluated" value={formatDateTime(report.as_of)} />
      </div>

      {rationale ? (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Rationale</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <p>{rationale.summary}</p>
              {rationale.details.length > 0 ? (
                <ul className="list-inside list-disc space-y-1 text-muted-foreground">
                  {rationale.details.map((detail) => (
                    <li key={detail}>{detail}</li>
                  ))}
                </ul>
              ) : null}
              {rationale.reason_codes.length > 0 ? (
                <div className="flex flex-wrap gap-1">
                  {rationale.reason_codes.map((code) => (
                    <Badge key={code} variant="outline">
                      {code}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Blast radius (G_p)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>
                All reachable:{' '}
                <span className="font-mono font-medium">{rationale.blast_radius.all_reachable_count}</span>
              </p>
              <p>
                Critical reachable:{' '}
                <span className="font-mono font-medium">{rationale.blast_radius.critical_reachable_count}</span>
              </p>
              <p>Truncated: {rationale.blast_radius.truncated ? 'Yes' : 'No'}</p>
              {rationale.blast_radius.critical_reachable.length > 0 ? (
                <ul className="mt-2 max-h-32 overflow-auto font-mono text-xs text-muted-foreground">
                  {rationale.blast_radius.critical_reachable.map((id) => (
                    <li key={id}>
                      <Link to={`/entities/${encodeURIComponent(id)}`} className="hover:underline">
                        {id}
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Coverage breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>
                Coverage:{' '}
                <span className="font-mono font-medium">
                  {formatPercent(rationale.coverage_breakdown.coverage)}
                </span>
              </p>
              <p>
                Observed: {rationale.coverage_breakdown.observed_entities} /{' '}
                {rationale.coverage_breakdown.total_entities}
              </p>
              <p>Meets C_min: {rationale.coverage_breakdown.meets_threshold ? 'Yes' : 'No'}</p>
              <p>C_min: {formatPercent(rationale.coverage_breakdown.c_min)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Suggested runbook</CardTitle>
            </CardHeader>
            <CardContent>
              {rationale.suggested_runbook.length === 0 ? (
                <p className="text-sm text-muted-foreground">No runbook actions suggested.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Stage</TableHead>
                      <TableHead>Description</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rationale.suggested_runbook.map((action, index) => (
                      <TableRow key={`${action.stage}-${index}`}>
                        <TableCell className="font-medium">{action.stage}</TableCell>
                        <TableCell>{action.description}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {(rationale.suggested_probes?.length ?? 0) > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Suggested probes</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Channels</TableHead>
                      <TableHead>Rationale</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rationale.suggested_probes?.map((probe, index) => (
                      <TableRow key={`${probe.channels.join('-')}-${index}`}>
                        <TableCell className="font-medium">{probe.channels.join(', ')}</TableCell>
                        <TableCell>{probe.rationale}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          ) : null}
        </div>
      ) : null}

      {(report.supersedes || report.superseded_by) && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-base">Decision chain (INV-013)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {report.supersedes ? (
              <p>
                Supersedes:{' '}
                <Link
                  to={`/decommission/${encodeURIComponent(report.supersedes)}`}
                  className="font-mono text-primary hover:underline"
                >
                  {report.supersedes}
                </Link>
              </p>
            ) : null}
            {report.superseded_by ? (
              <p>
                Superseded by:{' '}
                <Link
                  to={`/decommission/${encodeURIComponent(report.superseded_by)}`}
                  className="font-mono text-primary hover:underline"
                >
                  {report.superseded_by}
                </Link>
              </p>
            ) : null}
          </CardContent>
        </Card>
      )}

      <LimitationsFooter text={report.limitations_footer} />
    </div>
  );
}
