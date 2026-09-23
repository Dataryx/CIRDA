#!/usr/bin/env python3
"""Generate OpenAPI 3.1 spec from the FastAPI application."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "cirda-core" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

# Minimal env for schema generation (no DB required)
os.environ.setdefault("CIRDA_MEMORY_STORE", "true")
os.environ.setdefault("CIRDA_EVENT_BUS", "inmemory")
os.environ.setdefault("CIRDA_AUTH_MODE", "dev")
os.environ.setdefault("CIRDA_SCHEDULER_ENABLED", "false")

OUTPUT = ROOT / "packages" / "contracts" / "openapi" / "cirda-v1.yaml"


def main() -> int:
    import yaml
    from cirda_api.main import create_app

    app = create_app()
    schema = app.openapi()
    schema["openapi"] = "3.1.0"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as fh:
        yaml.dump(schema, fh, sort_keys=False, allow_unicode=True, default_flow_style=False)

    json_path = OUTPUT.with_suffix(".json")
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(schema, fh, indent=2)

    print(f"Wrote {OUTPUT}")
    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("Installing PyYAML for OpenAPI export...")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    raise SystemExit(main())
