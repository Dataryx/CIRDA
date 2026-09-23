import { Link, useParams } from 'react-router-dom';
import { useEntity } from '@/api/queries/use-entities';
import { useDecisionsByEntity } from '@/api/queries/use-decisions';
import { VerdictBadge } from '@/components/data-display/verdict-badge';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatDateTime } from '@/lib/datetime';
import { titleCase } from '@/lib/format';

export function EntityDetailPage() {
  const { entityId = '' } = useParams();
  const entity = useEntity(entityId);
  const decisions = useDecisionsByEntity(entityId, { limit: 10 });

  if (entity.isLoading) return <LoadingSpinner />;
  if (entity.error) return <ErrorAlert error={entity.error} />;
  if (!entity.data) return null;

  return (
    <div>
      <PageHeader
        title={entity.data.name}
        description={entity.data.entity_id}
        actions={
          <Button asChild variant="brand">
            <Link to={`/decommission?entity=${encodeURIComponent(entityId)}`}>Evaluate decommission</Link>
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Entity details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>
              <span className="text-muted-foreground">Type:</span> {titleCase(String(entity.data.entity_type))}
            </p>
            <p>
              <span className="text-muted-foreground">Criticality:</span>{' '}
              {titleCase(entity.data.criticality ?? 'unknown')}
            </p>
            {entity.data.aliases && entity.data.aliases.length > 0 ? (
              <p>
                <span className="text-muted-foreground">Aliases:</span> {entity.data.aliases.join(', ')}
              </p>
            ) : null}
            {entity.data.created_at ? (
              <p>
                <span className="text-muted-foreground">Created:</span> {formatDateTime(entity.data.created_at)}
              </p>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Decision history</CardTitle>
          </CardHeader>
          <CardContent>
            {decisions.isLoading ? <LoadingSpinner label="Loading decisions…" /> : null}
            {decisions.error ? <ErrorAlert error={decisions.error} /> : null}
            {decisions.data && decisions.data.items.length === 0 ? (
              <p className="text-sm text-muted-foreground">No decisions recorded for this entity.</p>
            ) : null}
            {decisions.data && decisions.data.items.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Verdict</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {decisions.data.items.map((d) => (
                    <TableRow key={d.decision_id}>
                      <TableCell>
                        <VerdictBadge verdict={d.verdict} size="sm" />
                      </TableCell>
                      <TableCell className="text-sm">{formatDateTime(d.as_of)}</TableCell>
                      <TableCell>
                        <Link
                          to={`/decommission/${encodeURIComponent(d.decision_id)}`}
                          className="text-sm text-primary hover:underline"
                        >
                          View report
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
