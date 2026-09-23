"""API v1 router aggregation."""

from fastapi import APIRouter

from cirda_api.api.v1.routes import (
    admin,
    analysis,
    audit,
    benchmarks,
    calibration,
    coverage,
    decisions,
    edges,
    entities,
    evidence,
    graph,
    health,
    ingest,
    stream,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(ingest.router)
api_router.include_router(entities.router)
api_router.include_router(graph.router)
api_router.include_router(edges.router)
api_router.include_router(evidence.router)
api_router.include_router(analysis.router)
api_router.include_router(decisions.router)
api_router.include_router(coverage.router)
api_router.include_router(calibration.router)
api_router.include_router(benchmarks.router)
api_router.include_router(audit.router)
api_router.include_router(admin.router)
api_router.include_router(stream.router)
