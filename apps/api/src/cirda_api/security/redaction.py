"""Response redaction for lower-privilege roles."""

from __future__ import annotations

from typing import Any

from cirda_core.normalization.redaction import redact_value

from cirda_api.security.auth import PrincipalContext

SENSITIVE_KEYS = frozenset({"payload_hash", "api_key_hash", "metadata"})


def redact_for_principal(data: Any, principal: PrincipalContext) -> Any:
    if "admin" in principal.roles:
        return data
    if isinstance(data, dict):
        out: dict[str, Any] = {}
        for k, v in data.items():
            if k in SENSITIVE_KEYS and "approver" not in principal.roles:
                out[k] = "[REDACTED]"
            else:
                out[k] = redact_for_principal(v, principal)
        return out
    if isinstance(data, list):
        return [redact_for_principal(i, principal) for i in data]
    return redact_value(data) if "viewer" == next(iter(principal.roles), "viewer") and isinstance(data, dict) else data
