import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useEntities } from '@/api/queries/use-entities';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { EmptyState } from '@/components/feedback/empty-state';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { useDebounce } from '@/hooks/use-debounce';
import { DEFAULT_PAGE_SIZE } from '@/lib/constants';
import { titleCase } from '@/lib/format';

export function EntitiesPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search);
  const entities = useEntities({ limit: DEFAULT_PAGE_SIZE });

  const filtered =
    entities.data?.items.filter(
      (e) =>
        !debouncedSearch ||
        e.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        e.entity_id.toLowerCase().includes(debouncedSearch.toLowerCase()),
    ) ?? [];

  return (
    <div>
      <PageHeader
        title="Entities"
        description="Browse registered agents, services, tools, and data assets in the dependency graph."
        actions={<Input placeholder="Search entities…" value={search} onChange={(e) => setSearch(e.target.value)} className="w-64" />}
      />

      {entities.isLoading ? <LoadingSpinner /> : null}
      {entities.error ? <ErrorAlert error={entities.error} /> : null}
      {entities.data && filtered.length === 0 ? (
        <EmptyState title="No entities found" description="Try adjusting your search or ingest evidence first." />
      ) : null}
      {filtered.length > 0 ? (
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>ID</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Criticality</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((entity) => (
                <TableRow key={entity.entity_id}>
                  <TableCell>
                    <Link to={`/entities/${encodeURIComponent(entity.entity_id)}`} className="font-medium hover:underline">
                      {entity.name}
                    </Link>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{entity.entity_id}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{titleCase(String(entity.entity_type))}</Badge>
                  </TableCell>
                  <TableCell>{titleCase(entity.criticality ?? 'unknown')}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}
    </div>
  );
}
