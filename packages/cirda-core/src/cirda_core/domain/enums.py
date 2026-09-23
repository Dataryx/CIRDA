"""Domain enumerations for CIRDA."""

from __future__ import annotations

from enum import StrEnum


class EntityType(StrEnum):
    AGENT = "agent"
    TOOL = "tool"
    SERVICE = "service"
    DATA = "data"
    QUEUE = "queue"
    CREDENTIAL = "credential"
    MODEL = "model"


class Relation(StrEnum):
    DELEGATES = "delegates"
    CALLS = "calls"
    READS = "reads"
    WRITES = "writes"
    PUBLISHES = "publishes"
    CONSUMES = "consumes"
    AUTHENTICATES = "authenticates"
    USES_MODEL = "uses_model"


class EvidenceChannel(StrEnum):
    TRACE = "trace"
    DATABASE = "database"
    MESSAGING = "messaging"
    IAM = "iam"
    AGENT_FRAMEWORK = "agent_framework"
    TEMPORAL_CORRELATION = "temporal_correlation"
    SHARED_RESOURCE = "shared_resource"
    WORKFLOW_WINDOW = "workflow_window"
    STATIC_DECLARED = "static_declared"


class ChannelClass(StrEnum):
    DIRECT = "direct"
    WEAK = "weak"
    DECLARED = "declared"


class GraphLayer(StrEnum):
    CONFIRMED = "confirmed"
    POSSIBLE = "possible"


class Criticality(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Verdict(StrEnum):
    UNSAFE = "UNSAFE"
    SAFE = "SAFE"
    INDETERMINATE = "INDETERMINATE"


class Necessity(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    REDUNDANT = "redundant"
    FALLBACK = "fallback"
    UNKNOWN = "unknown"


class ChangeType(StrEnum):
    RETIREMENT = "retirement"
    MODEL_UPGRADE = "model_upgrade"
    CREDENTIAL_ROTATION = "credential_rotation"
    TOOL_SCHEMA_CHANGE = "tool_schema_change"
    DATA_CONTRACT_MIGRATION = "data_contract_migration"


class RunbookStage(StrEnum):
    REPORT_AND_REMEDIATE = "report_and_remediate"
    DISABLE_NEW_WORK = "disable_new_work"
    OBSERVE_DOWNSTREAM = "observe_downstream"
    REVOKE_CREDENTIALS = "revoke_credentials"
    DELETE_IDENTITY = "delete_identity"
