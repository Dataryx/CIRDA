import { useAuditLog } from '@/api/queries/use-audit';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { EmptyState } from '@/components/feedback/empty-state';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DEFAULT_PAGE_SIZE } from '@/lib/constants';
import { formatDateTime } from '@/lib/datetime';

export function AuditPage() {
  const audit = useAuditLog({ limit: DEFAULT_PAGE_SIZE });

  return (
    <div>
      <PageHeader title="Audit Log" description="Administrative actions and configuration changes." />

      {audit.isLoading ? <LoadingSpinner /> : null}
      {audit.error ? <ErrorAlert error={audit.error} /> : null}
      {audit.data && audit.data.items.length === 0 ? (
        <EmptyState title="No audit entries" description="Administrative actions will appear here." />
      ) : null}
      {audit.data && audit.data.items.length > 0 ? (
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Principal</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Resource</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {audit.data.items.map((entry) => (
                <TableRow key={entry.log_id}>
                  <TableCell className="text-sm">{formatDateTime(String(entry.created_at))}</TableCell>
                  <TableCell className="font-mono text-xs">{entry.principal_id ?? '—'}</TableCell>
                  <TableCell>{entry.action}</TableCell>
                  <TableCell className="text-sm">
                    {entry.resource_type}
                    {entry.resource_id ? `: ${entry.resource_id}` : ''}
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
