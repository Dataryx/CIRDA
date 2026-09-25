import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  useEdge,
  useEdgeEvidence,
  useNecessitySuggestions,
  usePatchEdgeNecessity,
} from '@/api/queries/use-edges';
import { FusionBreakdownCard } from '@/components/data-display/fusion-breakdown-card';
import { SupportTooltip } from '@/components/data-display/support-tooltip';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import type { FusionBreakdown } from '@/api/generated/schema.d';
import { formatDateTime } from '@/lib/datetime';
import { formatConfidence } from '@/lib/format';

export function EdgeEvidencePage() {
  const { edgeId = '' } = useParams();
  const edge = useEdge(edgeId);
  const evidence = useEdgeEvidence(edgeId);
  const hints = useNecessitySuggestions(edge.data?.source_id ?? '');
  const patchNecessity = usePatchEdgeNecessity();

  const fusionBreakdown = useMemo((): FusionBreakdown | null => {
    if (!edge.data || !evidence.data) return null;
    const channelCounts = new Map<string, number>();
    for (const event of evidence.data.events) {
      channelCounts.set(event.channel, (channelCounts.get(event.channel) ?? 0) + 1);
    }
    const channels = [...channelCounts.entries()].map(([channel, count]) => ({
      channel,
      count,
      strength: 0,
    }));
    return {
      fused_support: edge.data.confidence,
      channels,
    };
  }, [edge.data, evidence.data]);

  const hintForEdge = hints.data?.items.find((item) => item.edge_id === edge.data?.edge_id);

  const isLoading = edge.isLoading || evidence.isLoading;
  const error = edge.error ?? evidence.error;

  if (isLoading) return <LoadingSpinner label="Loading edge evidence…" />;
  if (error) return <ErrorAlert error={error} />;
  if (!edge.data) return null;

  return (
    <div>
      <PageHeader
        title="Edge Evidence"
        description={edge.data.edge_id}
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="outline">{edge.data.necessity ?? 'unknown'}</Badge>
            <Badge variant={edge.data.layer === 'confirmed' ? 'default' : 'secondary'}>
              {edge.data.layer}
            </Badge>
          </div>
        }
      />

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Fused support <SupportTooltip />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="font-mono text-2xl font-bold">{formatConfidence(edge.data.confidence)}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Relation</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-lg font-medium">{edge.data.relation}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Evidence count</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="font-mono text-2xl font-bold">{edge.data.evidence_count ?? 0}</span>
          </CardContent>
        </Card>
      </div>

      {hintForEdge ? (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-base">Necessity suggestion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>
              Suggested:{' '}
              <span className="font-mono font-medium">{hintForEdge.suggested_necessity}</span>
              {' '}(confidence {formatConfidence(hintForEdge.confidence)})
            </p>
            <p className="text-muted-foreground">{hintForEdge.rationale}</p>
            <p className="text-xs text-muted-foreground">
              Suggest-only heuristic — accepting writes an operator annotation via PATCH; nothing is
              auto-mutated.
            </p>
            <Button
              size="sm"
              disabled={patchNecessity.isPending}
              onClick={() =>
                patchNecessity.mutate({
                  edgeId: hintForEdge.edge_id,
                  necessity: hintForEdge.suggested_necessity,
                })
              }
            >
              Accept suggestion
            </Button>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        {fusionBreakdown ? <FusionBreakdownCard breakdown={fusionBreakdown} /> : null}

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Endpoint entities</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>
              Source:{' '}
              <Link to={`/entities/${encodeURIComponent(edge.data.source_id)}`} className="font-mono text-primary hover:underline">
                {edge.data.source_id}
              </Link>
            </p>
            <p>
              Target:{' '}
              <Link to={`/entities/${encodeURIComponent(edge.data.target_id)}`} className="font-mono text-primary hover:underline">
                {edge.data.target_id}
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base">Evidence events</CardTitle>
        </CardHeader>
        <CardContent>
          {evidence.data && evidence.data.events.length === 0 ? (
            <p className="text-sm text-muted-foreground">No evidence events linked to this edge.</p>
          ) : null}
          {evidence.data && evidence.data.events.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Event ID</TableHead>
                  <TableHead>Channel</TableHead>
                  <TableHead>Observed</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {evidence.data.events.map((event) => (
                  <TableRow key={event.event_id}>
                    <TableCell className="font-mono text-xs">{event.event_id}</TableCell>
                    <TableCell>{event.channel}</TableCell>
                    <TableCell>{formatDateTime(event.observed_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
