"""Cross-dialect column types."""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# Prefer JSONB on PostgreSQL via JSON with none_as_null; ORM uses JSON for sqlite tests.
JsonColumn = JSON().with_variant(JSONB(), "postgresql")
