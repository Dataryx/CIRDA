import { useState } from 'react';
import { useGraph } from '@/api/queries/use-graph';
import { GraphViewer } from '@/components/charts/graph-viewer';
import { ErrorAlert } from '@/components/feedback/error-alert';
import { LoadingSpinner } from '@/components/feedback/loading-spinner';
import { PageHeader } from '@/components/layout/page-header';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { GRAPH_LAYERS, LAYER_LABELS } from '@/lib/constants';
import type { GraphLayer } from '@/api/generated/schema.d';
import { formatDateTime } from '@/lib/datetime';

export function TopologyPage() {
  const [layer, setLayer] = useState<GraphLayer>('all');
  const graph = useGraph({ layer });

  return (
    <div>
      <PageHeader
        title="Topology"
        description="Dependency graph visualization. Confirmed edges are solid; possible edges are dashed (INV-014)."
        actions={
          <Select value={layer} onValueChange={(v) => setLayer(v as GraphLayer)}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {GRAPH_LAYERS.map((l) => (
                <SelectItem key={l} value={l}>
                  {LAYER_LABELS[l]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        }
      />

      {graph.isLoading ? <LoadingSpinner label="Loading graph…" /> : null}
      {graph.error ? <ErrorAlert error={graph.error} /> : null}
      {graph.data ? (
        <div className="space-y-4">
          <div className="flex gap-4 text-sm text-muted-foreground">
            <span>{graph.data.nodes.length} nodes</span>
            <span>{graph.data.edges.length} edges</span>
            <span>Engine {graph.data.engine_version}</span>
            {graph.data.as_of ? <span>As of {formatDateTime(graph.data.as_of)}</span> : null}
          </div>
          <GraphViewer nodes={graph.data.nodes} edges={graph.data.edges} />
          <div className="flex gap-6 text-sm">
            <div className="flex items-center gap-2">
              <span className="inline-block h-0.5 w-8 bg-layer-confirmed" />
              Confirmed (solid)
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-block h-0.5 w-8 border-t-2 border-dashed border-layer-possible" />
              Possible (dashed)
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
