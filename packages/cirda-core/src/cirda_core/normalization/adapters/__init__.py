"""Evidence source adapters."""

from cirda_core.normalization.adapters.agent_framework_adapter import AgentFrameworkAdapter
from cirda_core.normalization.adapters.database_adapter import DatabaseAdapter
from cirda_core.normalization.adapters.iam_adapter import IamAdapter
from cirda_core.normalization.adapters.messaging_adapter import MessagingAdapter
from cirda_core.normalization.adapters.static_adapter import StaticAdapter
from cirda_core.normalization.adapters.trace_adapter import TraceAdapter

ALL_ADAPTERS = [
    TraceAdapter(),
    DatabaseAdapter(),
    MessagingAdapter(),
    IamAdapter(),
    AgentFrameworkAdapter(),
    StaticAdapter(),
]

__all__ = [
    "AgentFrameworkAdapter",
    "DatabaseAdapter",
    "IamAdapter",
    "MessagingAdapter",
    "StaticAdapter",
    "TraceAdapter",
    "ALL_ADAPTERS",
]
