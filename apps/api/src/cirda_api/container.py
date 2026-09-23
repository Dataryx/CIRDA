"""Dependency injection container."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.repositories.audit import AuditRepository
from cirda_api.db.repositories.benchmark import BenchmarkRepository
from cirda_api.db.repositories.calibration import CalibrationRepository
from cirda_api.db.repositories.coverage import CoverageRepository
from cirda_api.db.repositories.decision import DecisionRepository
from cirda_api.db.repositories.edge import EdgeRepository
from cirda_api.db.repositories.entity import EntityRepository
from cirda_api.db.repositories.evidence import EvidenceRepository
from cirda_api.db.repositories.principal import PrincipalRepository
from cirda_api.memory.store import MemoryStore
from cirda_api.services.analysis_service import AnalysisService
from cirda_api.services.audit_service import AuditService
from cirda_api.services.benchmark_service import BenchmarkService
from cirda_api.services.calibration_service import CalibrationService
from cirda_api.services.coverage_service import CoverageService
from cirda_api.services.decision_service import DecisionService
from cirda_api.services.edge_service import EdgeService
from cirda_api.services.entity_service import EntityService
from cirda_api.services.evidence_service import EvidenceService
from cirda_api.services.graph_service import GraphService
from cirda_api.services.ingest_service import IngestService
from cirda_api.services.policy import build_policy
from cirda_api.settings import Settings
from cirda_api.ws.manager import ConnectionManager
from cirda_api.ws.publisher import EventPublisher


@dataclass
class Container:
    settings: Settings
    memory: MemoryStore | None
    ws_manager: ConnectionManager
    publisher: EventPublisher
    entity_repo: EntityRepository
    evidence_repo: EvidenceRepository
    edge_repo: EdgeRepository
    decision_repo: DecisionRepository
    coverage_repo: CoverageRepository
    calibration_repo: CalibrationRepository
    benchmark_repo: BenchmarkRepository
    audit_repo: AuditRepository
    principal_repo: PrincipalRepository
    entity_service: EntityService
    evidence_service: EvidenceService
    edge_service: EdgeService
    graph_service: GraphService
    ingest_service: IngestService
    analysis_service: AnalysisService
    decision_service: DecisionService
    coverage_service: CoverageService
    calibration_service: CalibrationService
    benchmark_service: BenchmarkService
    audit_service: AuditService


def build_container(settings: Settings, session: AsyncSession | None = None) -> Container:
    memory = MemoryStore() if settings.use_memory_store else None
    entity_repo = EntityRepository(session=session, memory=memory)
    evidence_repo = EvidenceRepository(session=session, memory=memory)
    edge_repo = EdgeRepository(session=session, memory=memory)
    decision_repo = DecisionRepository(session=session, memory=memory)
    coverage_repo = CoverageRepository(session=session, memory=memory)
    calibration_repo = CalibrationRepository(session=session, memory=memory)
    benchmark_repo = BenchmarkRepository(session=session, memory=memory)
    audit_repo = AuditRepository(session=session, memory=memory)
    principal_repo = PrincipalRepository(session=session, memory=memory)

    ws_manager = ConnectionManager()
    publisher = EventPublisher(ws_manager)
    policy = build_policy(settings)

    entity_service = EntityService(entity_repo)
    evidence_service = EvidenceService(evidence_repo)
    edge_service = EdgeService(edge_repo, evidence_repo)
    graph_service = GraphService(entity_repo, edge_repo)
    coverage_service = CoverageService(entity_repo, evidence_repo, coverage_repo, settings)
    ingest_service = IngestService(evidence_repo, edge_repo, entity_repo, policy, publisher)
    analysis_service = AnalysisService(graph_service, entity_repo, settings)
    decision_service = DecisionService(decision_repo, graph_service, coverage_service, evidence_repo, settings)
    calibration_service = CalibrationService(calibration_repo, settings)
    benchmark_service = BenchmarkService(benchmark_repo)
    audit_service = AuditService(audit_repo)

    return Container(
        settings=settings,
        memory=memory,
        ws_manager=ws_manager,
        publisher=publisher,
        entity_repo=entity_repo,
        evidence_repo=evidence_repo,
        edge_repo=edge_repo,
        decision_repo=decision_repo,
        coverage_repo=coverage_repo,
        calibration_repo=calibration_repo,
        benchmark_repo=benchmark_repo,
        audit_repo=audit_repo,
        principal_repo=principal_repo,
        entity_service=entity_service,
        evidence_service=evidence_service,
        edge_service=edge_service,
        graph_service=graph_service,
        ingest_service=ingest_service,
        analysis_service=analysis_service,
        decision_service=decision_service,
        coverage_service=coverage_service,
        calibration_service=calibration_service,
        benchmark_service=benchmark_service,
        audit_service=audit_service,
    )
