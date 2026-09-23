# Data Model

CIRDA maintains a **temporal dependency graph** whose edges represent inferred
relationships between estate entities.

## Entities

| Field | Description |
|-------|-------------|
| `entity_id` | Stable identifier (may have aliases) |
| `entity_type` | agent, tool, service, data, queue, credential, model |
| `criticality` | critical, high, medium, low, unknown |
| `metadata` | Operator-defined tags |

Entity resolution merges aliases when similarity exceeds configured thresholds
(`cirda_core.resolution`).

## Edges

| Field | Description |
|-------|-------------|
| `relation` | delegates, calls, reads, writes, publishes, consumes, … |
| `layer` | `confirmed` or `possible` |
| `confidence` | Fused support S ∈ (0, 1] after decay |
| `necessity` | required, optional, redundant, fallback, unknown |

### Layer thresholds

- **Confirmed (G_c):** S ≥ θ_c (0.62) with direct-evidence policy
- **Possible (G_p):** θ_p ≤ S < θ_c (θ_p = 0.28), or confirmed edges (confirmed ⊆ possible)

## Temporal decay

Each evidence channel has a half-life (`HALF_LIFE` in `cirda_core.config.constants`).
Confidence decays exponentially from observation time to evaluation time `as_of`.
Edges are retained for audit; they are not deleted when stale.

See [diagrams/graph-model.mmd](diagrams/graph-model.mmd).
