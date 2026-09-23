"""OpenTelemetry tracing setup."""

from __future__ import annotations

from cirda_api.settings import Settings


def configure_tracing(settings: Settings) -> None:
    if not settings.otel_enabled:
        return
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    provider = TracerProvider(resource=Resource.create({"service.name": "cirda-api"}))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
