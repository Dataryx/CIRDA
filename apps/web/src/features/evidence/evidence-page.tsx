import { useEvidenceList } from '@/api/queries/use-evidence';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { EmptyState } from '@/components/feedback/empty-state';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { DEFAULT_PAGE_SIZE } from '@/lib/constants';
import { formatDateTime } from '@/lib/datetime';

export function EvidencePage() {
  const evidence = useEvidenceList({ limit: DEFAULT_PAGE_SIZE });

  return (
    <div>
      <PageHeader
        title="Evidence"
        description="Raw observability events that inform dependency edge inference."
      />

      {evidence.isLoading ? <LoadingSpinner /> : null}
      {evidence.error ? <ErrorAlert error={evidence.error} /> : null}
      {evidence.data && evidence.data.items.length === 0 ? (
        <EmptyState title="No evidence events" description="Ingest telemetry to populate the evidence store." />
      ) : null}
      {evidence.data && evidence.data.items.length > 0 ? (
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Event</TableHead>
                <TableHead>Source → Target</TableHead>
                <TableHead>Relation</TableHead>
                <TableHead>Channel</TableHead>
                <TableHead>Observed</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evidence.data.items.map((event) => (
                <TableRow key={event.event_id}>
                  <TableCell className="font-mono text-xs">{event.event_id}</TableCell>
                  <TableCell className="text-sm">
                    {event.source_id} → {event.target_id}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{event.relation}</Badge>
                  </TableCell>
                  <TableCell>{event.channel}</TableCell>
                  <TableCell className="text-sm">{formatDateTime(event.observed_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}
    </div>
  );
}
