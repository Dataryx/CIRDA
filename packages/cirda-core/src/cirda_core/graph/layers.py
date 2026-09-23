"""Graph layer classification."""

from __future__ import annotations

from cirda_core.config.constants import THETA_C, THETA_P
from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.enums import GraphLayer
from cirda_core.inference.fusion import has_direct_evidence


def classify_layer(
    fused_confidence: float,
    observations_have_direct: bool,
    policy: PolicyConfig | None = None,
) -> GraphLayer | None:
    """
    Classify an edge into confirmed or possible layer based on fused confidence.

    Returns None if confidence is below possible threshold.
    """
    cfg = policy or PolicyConfig()
    if fused_confidence < cfg.theta_possible:
        return None
    if fused_confidence >= cfg.theta_confirmed:
        if cfg.confirmed_requires_direct_evidence and not observations_have_direct:
            return GraphLayer.POSSIBLE
        return GraphLayer.CONFIRMED
    return GraphLayer.POSSIBLE


def layer_threshold(layer: GraphLayer, policy: PolicyConfig | None = None) -> float:
    """Return confidence threshold for a layer."""
    cfg = policy or PolicyConfig()
    if layer == GraphLayer.CONFIRMED:
        return cfg.theta_confirmed
    return cfg.theta_possible


def meets_confirmed_threshold(fused_confidence: float, policy: PolicyConfig | None = None) -> bool:
    """Check if fused confidence meets confirmed threshold."""
    cfg = policy or PolicyConfig()
    return fused_confidence >= cfg.theta_confirmed


def meets_possible_threshold(fused_confidence: float, policy: PolicyConfig | None = None) -> bool:
    """Check if fused confidence meets possible threshold."""
    cfg = policy or PolicyConfig()
    return fused_confidence >= cfg.theta_possible
