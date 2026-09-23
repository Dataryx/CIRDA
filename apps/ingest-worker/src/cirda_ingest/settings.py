"""Ingest worker settings from CIRDA_* environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from cirda_core.config.constants import C_MIN, THETA_C, THETA_P


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CIRDA_", env_file=".env", extra="ignore")

    app_env: Literal["development", "staging", "production"] = "development"
    host: str = "0.0.0.0"
    port: int = 8081

    event_bus: Literal["kafka", "inmemory", "otlp", "file"] = "inmemory"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "cirda.evidence.raw"
    kafka_group_id: str = "cirda-ingest"
    kafka_dlq_topic: str = "cirda.evidence.dlq"
    kafka_auto_fallback: bool = True

    otlp_listen_host: str = "0.0.0.0"
    otlp_listen_port: int = 4318
    file_replay_path: str = "data/replay.jsonl"
    file_replay_loop: bool = False

    database_url: str | None = None
    memory_store: bool = False
    redis_url: str = "redis://localhost:6379/1"

    batch_max_events: int = 500
    batch_max_wait_ms: int = 200

    theta_c: float = Field(default=THETA_C, alias="THETA_C")
    theta_p: float = Field(default=THETA_P, alias="THETA_P")
    c_min: float = Field(default=C_MIN, alias="C_MIN")
    confirmed_requires_direct_evidence: bool = True
    min_trace_observations_for_confirmed: int = 3

    log_level: str = "INFO"
    log_json: bool = False
    metrics_enabled: bool = True
    health_check_kafka: bool = True

    @model_validator(mode="after")
    def validate_calibration(self) -> Settings:
        if self.theta_p >= self.theta_c:
            raise ValueError("CIRDA_THETA_P must be strictly less than CIRDA_THETA_C")
        return self

    @property
    def batch_max_wait_seconds(self) -> float:
        return self.batch_max_wait_ms / 1000.0

    @property
    def use_memory_store(self) -> bool:
        return self.memory_store or self.database_url is None

    @property
    def effective_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return "sqlite+aiosqlite:///:memory:"


@lru_cache
def get_settings() -> Settings:
    return Settings()
