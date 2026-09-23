import cytoscape, { type Core, type ElementDefinition } from 'cytoscape';
import fcose from 'cytoscape-fcose';
import { useEffect, useRef } from 'react';
import type { GraphEdge, GraphNode } from '@/api/generated/schema.d';

cytoscape.use(fcose);

interface GraphViewerProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  highlightEntityId?: string;
  height?: number;
}

function toElements(nodes: GraphNode[], edges: GraphEdge[]): ElementDefinition[] {
  const nodeElements: ElementDefinition[] = nodes.map((node) => ({
    data: {
      id: node.entity_id,
      label: node.name,
      entityType: node.entity_type,
      criticality: node.criticality,
    },
  }));

  const edgeElements: ElementDefinition[] = edges.map((edge) => ({
    data: {
      id: edge.edge_id,
      source: edge.source_id,
      target: edge.target_id,
      label: edge.relation,
      layer: edge.layer,
      confidence: edge.confidence,
    },
    classes: edge.layer === 'possible' ? 'possible-edge' : 'confirmed-edge',
  }));

  return [...nodeElements, ...edgeElements];
}

export function GraphViewer({ nodes, edges, highlightEntityId, height = 520 }: GraphViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    cyRef.current?.destroy();
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements: toElements(nodes, edges),
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'background-color': '#0072B2',
            color: '#fff',
            'font-size': 10,
            'text-valign': 'bottom',
            'text-margin-y': 4,
            width: 24,
            height: 24,
          },
        },
        {
          selector: 'node[?criticality][criticality = "high"]',
          style: { 'background-color': '#D55E00', width: 32, height: 32 },
        },
        {
          selector: 'edge.confirmed-edge',
          style: {
            width: 2,
            'line-color': '#7c3aed',
            'target-arrow-color': '#7c3aed',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
        {
          selector: 'edge.possible-edge',
          style: {
            width: 2,
            'line-color': '#a78bfa',
            'line-style': 'dashed',
            'target-arrow-color': '#a78bfa',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
        {
          selector: '.highlighted',
          style: {
            'border-width': 3,
            'border-color': '#E69F00',
          },
        },
      ],
      layout: { name: 'fcose', randomize: true } as cytoscape.LayoutOptions,
    });

    if (highlightEntityId) {
      cyRef.current.$id(highlightEntityId).addClass('highlighted');
      cyRef.current.center(cyRef.current.$id(highlightEntityId));
    }

    return () => {
      cyRef.current?.destroy();
      cyRef.current = null;
    };
  }, [nodes, edges, highlightEntityId]);

  return (
    <div
      ref={containerRef}
      className="w-full rounded-lg border bg-card"
      style={{ height }}
      role="img"
      aria-label="Dependency graph visualization"
    />
  );
}
