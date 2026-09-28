import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useBlastRadius, useCriticalPaths, useReachability } from '@/api/queries/use-analysis';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatConfidence } from '@/lib/format';

export function AnalysisPage() {
  const [params, setParams] = useSearchParams();
  const initial = params.get('source_id') ?? '';
  const [sourceId, setSourceId] = useState(initial);
  const [submitted, setSubmitted] = useState(initial);

  const blast = useBlastRadius();
  const reach = useReachability();
  const paths = useCriticalPaths({
    source_id: submitted,
    enabled: Boolean(submitted),
  });

  function runAnalysis() {
    const id = sourceId.trim();
    if (!id) return;
    setSubmitted(id);
    setParams({ source_id: id });
    blast.mutate({ source_id: id });
    reach.mutate({ source_id: id });
  }

  const error = blast.error ?? reach.error ?? paths.error;

  return (
    <div>
      <PageHeader
        title="Analysis"
        description="Blast radius, reachability, and critical paths on G_p (possible layer)."
      />

      <Card className="mb-6">
        <CardContent className="flex flex-wrap items-end gap-3 pt-6">
          <div className="min-w-[16rem] flex-1">
            <label className="mb-1 block text-sm text-muted-foreground">Source entity ID</label>
            <Input
              value={sourceId}
              onChange={(e) => setSourceId(e.target.value)}
              placeholder="e.g. invoice-reconciler-agent"
              className="font-mono text-sm"
            />
          </div>
          <Button onClick={runAnalysis} disabled={!sourceId.trim() || blast.isPending}>
            Analyze
          </Button>
        </CardContent>
      </Card>

      {error ? <ErrorAlert error={error} /> : null}

      {submitted ? (
        <Tabs defaultValue="blast">
          <TabsList>
            <TabsTrigger value="blast">Blast radius</TabsTrigger>
            <TabsTrigger value="reachability">Reachability</TabsTrigger>
            <TabsTrigger value="paths">Critical paths</TabsTrigger>
          </TabsList>

          <TabsContent value="blast" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Blast radius (G_p)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {blast.isPending ? <p className="text-muted-foreground">Computing…</p> : null}
                {blast.data ? (
                  <>
                    <p>
                      All reachable:{' '}
                      <span className="font-mono font-medium">{blast.data.all_reachable.length}</span>
                    </p>
                    <p>
                      Critical:{' '}
                      <span className="font-mono font-medium">
                        {blast.data.critical_reachable.length}
                      </span>
                      {blast.data.truncated ? ' (truncated)' : null}
                    </p>
                    <ul className="max-h-64 overflow-auto font-mono text-xs text-muted-foreground">
                      {blast.data.critical_reachable.map((id) => (
                        <li key={id}>{id}</li>
                      ))}
                    </ul>
                  </>
                ) : null}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reachability" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Reachability</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {reach.isPending ? <p className="text-muted-foreground">Computing…</p> : null}
                {reach.data ? (
                  <>
                    <p>
                      Reachable nodes:{' '}
                      <span className="font-mono font-medium">{reach.data.reachable.length}</span>
                      {reach.data.truncated ? ' (truncated)' : null}
                    </p>
                    <ul className="max-h-64 overflow-auto font-mono text-xs text-muted-foreground">
                      {reach.data.reachable.map((id) => (
                        <li key={id}>{id}</li>
                      ))}
                    </ul>
                  </>
                ) : null}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="paths" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Critical paths</CardTitle>
              </CardHeader>
              <CardContent>
                {paths.isLoading ? <p className="text-sm text-muted-foreground">Loading…</p> : null}
                {paths.data && paths.data.paths.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No critical paths from this source.</p>
                ) : null}
                {paths.data && paths.data.paths.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Path</TableHead>
                        <TableHead>Confidence</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {paths.data.paths.map((path) => (
                        <TableRow key={path.path_nodes.join('>')}>
                          <TableCell className="font-mono text-xs">
                            {path.path_nodes.join(' → ')}
                          </TableCell>
                          <TableCell>{formatConfidence(path.path_confidence)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : null}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      ) : null}
    </div>
  );
}
