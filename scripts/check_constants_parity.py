#!/usr/bin/env python3
"""Verify normative constants match across cirda-core and service settings."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "cirda-core" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "ingest-worker" / "src"))

from cirda_core.config.constants import C_MIN, THETA_C, THETA_P  # noqa: E402
from cirda_api.settings import Settings as ApiSettings  # noqa: E402
from cirda_ingest.settings import Settings as IngestSettings  # noqa: E402


def _check(name: str, expected: float, actual: float) -> list[str]:
    if expected != actual:
        return [f"{name}: core={expected}, service={actual}"]
    return []


def main() -> int:
    errors: list[str] = []
    api = ApiSettings()
    ingest = IngestSettings()

    for label, svc in [("api", api), ("ingest", ingest)]:
        errors.extend(_check(f"{label}.theta_c", THETA_C, svc.theta_c))
        errors.extend(_check(f"{label}.theta_p", THETA_P, svc.theta_p))
        errors.extend(_check(f"{label}.c_min", C_MIN, svc.c_min))

    if errors:
        print("Constants parity check FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Constants parity check OK (THETA_C, THETA_P, C_MIN aligned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
