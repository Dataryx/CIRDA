import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCreateEntity, useEntities } from '@/api/queries/use-entities';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { EmptyState } from '@/components/feedback/empty-state';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { useDebounce } from '@/hooks/use-debounce';
import { DEFAULT_PAGE_SIZE } from '@/lib/constants';
import { titleCase } from '@/lib/format';

const ENTITY_TYPES = ['agent', 'service', 'data', 'queue', 'tool', 'credential', 'model'] as const;
const CRITICALITIES = ['unknown', 'low', 'medium', 'high', 'critical'] as const;

export function EntitiesPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search);
  const entities = useEntities({ limit: DEFAULT_PAGE_SIZE });
  const create = useCreateEntity();

  const [entityId, setEntityId] = useState('');
  const [name, setName] = useState('');
  const [entityType, setEntityType] = useState<string>('agent');
  const [criticality, setCriticality] = useState<string>('unknown');
  const [aliasesRaw, setAliasesRaw] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const filtered =
    entities.data?.items.filter(
      (e) =>
        !debouncedSearch ||
        e.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        e.entity_id.toLowerCase().includes(debouncedSearch.toLowerCase()),
    ) ?? [];

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!entityId.trim() || !name.trim()) {
      setFormError('Entity ID and name are required.');
      return;
    }
    const aliases = aliasesRaw
      .split(',')
      .map((a) => a.trim())
      .filter(Boolean);
    try {
      await create.mutateAsync({
        entity_id: entityId.trim(),
        name: name.trim(),
        entity_type: entityType,
        criticality,
        aliases,
      });
      setEntityId('');
      setName('');
      setAliasesRaw('');
      setCriticality('unknown');
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to create entity');
    }
  }

  return (
    <div>
      <PageHeader
        title="Entities"
        description="Browse registered agents, services, tools, and data assets in the dependency graph."
        actions={
          <Input
            placeholder="Search entities…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-64"
          />
        }
      />

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">Register entity</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-3 md:grid-cols-2 lg:grid-cols-3" onSubmit={onCreate}>
            <Input
              placeholder="entity_id"
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              className="font-mono text-sm"
            />
            <Input placeholder="Display name" value={name} onChange={(e) => setName(e.target.value)} />
            <Select value={entityType} onValueChange={setEntityType}>
              <SelectTrigger>
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                {ENTITY_TYPES.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={criticality} onValueChange={setCriticality}>
              <SelectTrigger>
                <SelectValue placeholder="Criticality" />
              </SelectTrigger>
              <SelectContent>
                {CRITICALITIES.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              placeholder="Aliases (comma-separated)"
              value={aliasesRaw}
              onChange={(e) => setAliasesRaw(e.target.value)}
              className="md:col-span-2"
            />
            <div className="flex items-center gap-3">
              <Button type="submit" disabled={create.isPending}>
                Create
              </Button>
              {formError ? <span className="text-sm text-destructive">{formError}</span> : null}
            </div>
          </form>
        </CardContent>
      </Card>

      {entities.isLoading ? <LoadingSpinner /> : null}
      {entities.error ? <ErrorAlert error={entities.error} /> : null}
      {entities.data && filtered.length === 0 ? (
        <EmptyState
          title="No entities found"
          description="Try adjusting your search or ingest evidence first."
        />
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
                <TableHead>Aliases</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((entity) => (
                <TableRow key={entity.entity_id}>
                  <TableCell>
                    <Link
                      to={`/entities/${encodeURIComponent(entity.entity_id)}`}
                      className="font-medium hover:underline"
                    >
                      {entity.name}
                    </Link>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{entity.entity_id}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{titleCase(String(entity.entity_type))}</Badge>
                  </TableCell>
                  <TableCell>{titleCase(entity.criticality ?? 'unknown')}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {(entity.aliases ?? []).join(', ') || '—'}
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
