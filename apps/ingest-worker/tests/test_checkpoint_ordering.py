"""Checkpoint ordering — offsets commit only after durable write."""

from __future__ import annotations

import pytest

from cirda_ingest.pipeline.checkpoint import CheckpointManager, InMemoryCommitter, OffsetToken
from cirda_ingest.pipeline.stages import InboundMessage, sample_trace_raw


@pytest.mark.asyncio
async def test_checkpoint_not_committed_before_durable(pipeline, checkpoint) -> None:
    committer = InMemoryCommitter()
    checkpoint = CheckpointManager(committer)

    msg = InboundMessage(
        raw=sample_trace_raw("cp-1"),
        message_id="kafka:0:42",
        source="kafka",
        topic="cirda.evidence.raw",
        partition=0,
        offset=42,
    )
    checkpoint.register(
        OffsetToken(
            message_id=msg.message_id,
            topic=msg.topic,
            partition=msg.partition,
            offset=msg.offset,
        )
    )

    assert committer.committed == []

    await pipeline.process_batch([msg])
    assert committer.committed == []

    checkpoint.mark_durable([msg.message_id])
    committed = await checkpoint.commit_durable()
    assert committed == 1
    assert committer.committed == [msg.message_id]


@pytest.mark.asyncio
async def test_deduped_event_still_checkpoints(pipeline, checkpoint) -> None:
    committer = InMemoryCommitter()
    checkpoint = CheckpointManager(committer)
    raw = sample_trace_raw("cp-dup")

    msg1 = InboundMessage(raw=raw, message_id="m1", source="test")
    msg2 = InboundMessage(raw=raw, message_id="m2", source="test")

    checkpoint.register(OffsetToken(message_id="m1"))
    await pipeline.process_batch([msg1])
    checkpoint.mark_durable(["m1"])
    await checkpoint.commit_durable()

    checkpoint.register(OffsetToken(message_id="m2"))
    await pipeline.process_batch([msg2])
    checkpoint.mark_durable(["m2"])
    await checkpoint.commit_durable()

    assert committer.committed == ["m1", "m2"]
