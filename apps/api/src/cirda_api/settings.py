"""Application settings loaded from CIRDA_* environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from cirda_core.config.constants import C_MIN, THETA_C, THETA_P
from cirda_core.domain.enums import Criticality


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CIRDA_", env_file=".env", extra="ignore")

    app_env: Literal["development", "staging", "production"] = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    memory_store: bool = False
    event_bus: Literal["redis", "inmemory"] = "inmemory"

    theta_c: float = Field(default=THETA_C, alias="THETA_C")
    theta_p: float = Field(default=THETA_P, alias="THETA_P")
    c_min: float = Field(default=C_MIN, alias="C_MIN")
    confirmed_requires_direct_evidence: bool = True
    min_trace_observations_for_confirmed: int = 3
    max_ingest_lag_seconds: float = 3600.0
    critical_threshold: Criticality = Criticality.HIGH
    hard_blocks: str = ""
    probe_planning_enabled: bool = False
    probe_execution_enabled: bool = False

    auth_mode: Literal["dev", "jwt", "api_key"] = "dev"
    jwt_secret: str = "dev-secret-change-me"
    jwt_issuer: str = "cirda"
    jwt_audience: str = "cirda-api"

    log_level: str = "INFO"
    log_json: bool = False
    otel_enabled: bool = False
    otel_endpoint: str = "http://localhost:4317"
    metrics_enabled: bool = True
    rate_limit_rpm: int = 600

    scheduler_enabled: bool = True
    decay_job_interval_seconds: int = 3600
    coverage_job_interval_seconds: int = 900
    snapshot_job_interval_seconds: int = 86400
    recalibration_job_interval_seconds: int = 604800

    decision_limitations_footer: str = (
        "Limitations (§X): CIRDA decisions reflect observability coverage and inferred "
        "dependency structure at the evaluation timestamp. S denotes calibrated support, "
        "not causal probability. Absence of evidence is not evidence of absence. "
        "INDETERMINATE outcomes require additional probes before irreversible action."
    )

    @field_validator("theta_c", "theta_p", "c_min")
    @classmethod
    def validate_unit_interval(cls, v: float, info: object) -> float:
        if not 0.0 < v <= 1.0:
            msg = f"{getattr(info, 'field_name', 'value')} must be in (0, 1]"
            raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_calibration(self) -> Settings:
        if self.theta_p >= self.theta_c:
            raise ValueError("CIRDA_THETA_P must be strictly less than CIRDA_THETA_C")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def hard_block_set(self) -> frozenset[str]:
        if not self.hard_blocks.strip():
            return frozenset()
        return frozenset(b.strip() for b in self.hard_blocks.split(",") if b.strip())

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
