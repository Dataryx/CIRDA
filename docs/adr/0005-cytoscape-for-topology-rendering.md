# ADR 0005: Cytoscape for Topology Rendering

## Status

Accepted

## Context

The web dashboard must render dependency graphs with hundreds of nodes, layer
styling (confirmed vs possible), and interactive blast-radius highlighting.

## Decision

Use **Cytoscape.js** (via the web app graph component) for client-side topology
rendering. Server returns entity/edge JSON; layout runs in the browser.

## Consequences

- **Positive:** Mature graph UX, layer/style plugins, fits SPA architecture
- **Negative:** Very large estates (>3000 nodes) need clustering / filtering
- **Neutral:** Export and snapshot APIs remain graph-library agnostic
