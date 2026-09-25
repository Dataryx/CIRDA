#!/usr/bin/env python3
"""
Replay JSONL telemetry into the CIRDA ingest API or Kafka topic.

Usage:
  uv run python scripts/replay_telemetry.py data/replay.jsonl
  uv run python scripts/replay_telemetry.py data/replay.jsonl --target kafka
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

API_BASE = "http://localhost:8000"
AUTH_HEADERS = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}


def replay_http(path: Path, *, rate: float, dry_run: bool) -> int:
    sent = 0
    with httpx.Client(base_url=API_BASE, headers=AUTH_HEADERS, timeout=30.0) as client:
        with path.open(encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as exc:
                    print(f"Line {line_no}: invalid JSON — {exc}")
                    continue
                if dry_run:
                    print(f"[dry-run] would ingest event_id={raw.get('event_id', '?')}")
                else:
                    r = client.post("/api/v1/ingest/events", json={"raw": raw})
                    if r.status_code != 200:
                        print(f"Line {line_no}: HTTP {r.status_code} — {r.text[:200]}")
                        continue
                sent += 1
                if rate > 0:
                    time.sleep(1.0 / rate)
    return sent


def replay_kafka(path: Path, *, bootstrap: str, topic: str, rate: float) -> int:
    try:
        from aiokafka import AIOKafkaProducer
    except ImportError:
        print("ERROR: aiokafka required for kafka target. Install cirda-ingest deps.")
        return 0

    import asyncio

    async def _run() -> int:
        producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap,
            compression_type=None,
            value_serializer=lambda v: v if isinstance(v, (bytes, bytearray)) else str(v).encode("utf-8"),
        )
        await producer.start()
        sent = 0
        try:
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    await producer.send_and_wait(topic, line.encode("utf-8"))
                    sent += 1
                    if rate > 0:
                        await asyncio.sleep(1.0 / rate)
        finally:
            await producer.stop()
        return sent

    return asyncio.run(_run())


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay JSONL telemetry into CIRDA")
    parser.add_argument("file", type=Path, help="JSONL file with one event per line")
    parser.add_argument("--target", choices=["http", "kafka"], default="http")
    parser.add_argument("--rate", type=float, default=0, help="Events per second (0 = unlimited)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--kafka-bootstrap", default="localhost:19092")
    parser.add_argument("--kafka-topic", default="cirda.evidence.raw")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: file not found: {args.file}")
        return 1

    if args.target == "http":
        count = replay_http(args.file, rate=args.rate, dry_run=args.dry_run)
    else:
        count = replay_kafka(
            args.file,
            bootstrap=args.kafka_bootstrap,
            topic=args.kafka_topic,
            rate=args.rate,
        )

    print(f"Replayed {count} events via {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
