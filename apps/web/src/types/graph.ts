import type { GraphEdge, GraphLayer, GraphNode, GraphPayload } from '@/api/generated/schema.d';

export type { GraphNode, GraphEdge, GraphPayload, GraphLayer };

export interface CytoscapeElement {
  data: {
    id: string;
    label?: string;
    source?: string;
    target?: string;
    layer?: string;
    entityType?: string;
    criticality?: string;
    confidence?: number;
  };
  classes?: string;
}

export interface GraphViewOptions {
  layer: GraphLayer;
  highlightEntityId?: string;
  showLabels: boolean;
}

export type RelationDirection = 'retained' | 'reversed';

export interface DirectedEdgeInput {
  actorId: string;
  counterpartId: string;
  relation: string;
}

export interface DirectedEdgeOutput {
  sourceId: string;
  targetId: string;
  relation: string;
  direction: RelationDirection;
}
