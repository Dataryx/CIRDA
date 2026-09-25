"""CIRDA core domain library."""

from cirda_core import domain
from cirda_core.analysis.blast_radius import BlastRadius, compute_blast_radius
from cirda_core.config.calibration import CalibrationParams, validate_calibration
from cirda_core.config.channels import CHANNEL_PROFILES, ChannelProfile, get_channel_profile
from cirda_core.config.constants import C_MIN, HALF_LIFE, THETA_C, THETA_P, half_life_seconds
from cirda_core.config.policy import DEFAULT_POLICY, PolicyConfig
from cirda_core.coverage.benchmark_estimator import benchmark_coverage
from cirda_core.coverage.estimator import estimate_coverage, meets_coverage_threshold
from cirda_core.decision.explanation import explain_decision
from cirda_core.decision.gate import evaluate_gate, evaluate_gate_from_layers
from cirda_core.decision.probe_planner import ProbePlan, estimate_probe_delta_c, plan_probes
from cirda_core.decision.runbook import STANDARD_RUNBOOK, default_runbook_for_verdict
from cirda_core.graph.layers import classify_layer
from cirda_core.graph.necessity_suggester import NecessityHint, suggest_necessity
from cirda_core.graph.reachability import ReachabilityResult, critical_descendants, descendants_within_depth
from cirda_core.graph.snapshot import GraphSnapshot
from cirda_core.graph.temporal_graph import TemporalGraph
from cirda_core.inference.direction import RETAINED, REVERSED, translate_to_dependency_edge
from cirda_core.inference.fusion import ChannelObservation, channel_strength, fuse_channels, has_direct_evidence
from cirda_core.inference.weak_signals import can_confirm_layer, weak_only_observations
from cirda_core.normalization.adapters import ALL_ADAPTERS
from cirda_core.normalization.normalizer import Normalizer
from cirda_core.resolution.entity_resolver import EntityResolver
from cirda_core.version import ENGINE_VERSION

__all__ = [
    "ALL_ADAPTERS",
    "BlastRadius",
    "CHANNEL_PROFILES",
    "C_MIN",
    "CalibrationParams",
    "ChannelObservation",
    "ChannelProfile",
    "DEFAULT_POLICY",
    "ENGINE_VERSION",
    "EntityResolver",
    "GraphSnapshot",
    "HALF_LIFE",
    "NecessityHint",
    "Normalizer",
    "PolicyConfig",
    "ProbePlan",
    "ReachabilityResult",
    "RETAINED",
    "REVERSED",
    "STANDARD_RUNBOOK",
    "THETA_C",
    "THETA_P",
    "TemporalGraph",
    "benchmark_coverage",
    "can_confirm_layer",
    "channel_strength",
    "classify_layer",
    "compute_blast_radius",
    "critical_descendants",
    "default_runbook_for_verdict",
    "descendants_within_depth",
    "domain",
    "estimate_coverage",
    "estimate_probe_delta_c",
    "evaluate_gate",
    "evaluate_gate_from_layers",
    "explain_decision",
    "fuse_channels",
    "get_channel_profile",
    "half_life_seconds",
    "has_direct_evidence",
    "meets_coverage_threshold",
    "plan_probes",
    "suggest_necessity",
    "translate_to_dependency_edge",
    "validate_calibration",
    "weak_only_observations",
]
