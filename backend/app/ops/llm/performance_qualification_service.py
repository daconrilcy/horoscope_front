import uuid
from collections.abc import Mapping
from typing import Literal, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.datetime_provider import datetime_provider
from app.domain.llm.runtime.contracts import (
    PerformanceQualificationReport,
    PerformanceSLA,
    PerformanceSLO,
)
from app.ops.llm.performance_registry import (
    PERFORMANCE_SLA_REGISTRY,
    PERFORMANCE_SLO_REGISTRY,
)


class PerformanceQualificationService:
    @staticmethod
    def _resolve_manifest_entry_id(manifest: object, manifest_entry_id: Optional[str]) -> str:
        if manifest_entry_id:
            return manifest_entry_id

        if not isinstance(manifest, Mapping):
            raise ValueError("Qualification rejected: active snapshot manifest is invalid.")

        targets = manifest.get("targets")
        if not isinstance(targets, Mapping) or not targets:
            raise ValueError(
                "Qualification rejected: active snapshot manifest does not expose targets."
            )

        if len(targets) == 1:
            return str(next(iter(targets)))

        raise ValueError(
            "Qualification rejected: manifest_entry_id is required for multi-target snapshots."
        )

    @staticmethod
    async def evaluate_run_async(
        family: str,
        profile: str,
        total_requests: int,
        success_count: int,
        protection_count: int,
        error_count: int,
        latency_p50_ms: float,
        latency_p95_ms: float,
        latency_p99_ms: float,
        throughput_rps: float,
        db: Optional[Session] = None,
        active_snapshot_id: Optional[uuid.UUID] = None,
        active_snapshot_version: Optional[str] = None,
        manifest_entry_id: Optional[str] = None,
        environment: str = "local",
    ) -> PerformanceQualificationReport:
        """
        Évalue un run de charge par rapport aux SLO et SLA (Story 66.35) - Version Async.
        """
        if db and not active_snapshot_id:
            from app.domain.llm.configuration.active_release import get_active_release_id

            active_snapshot_id = await get_active_release_id(db)

        if not active_snapshot_id:
            raise ValueError("Qualification rejected: No active snapshot ID could be resolved.")

        snapshot = None
        if db and active_snapshot_id and (not active_snapshot_version or not manifest_entry_id):
            from app.infra.db.models.llm.llm_release import LlmReleaseSnapshotModel

            stmt = select(LlmReleaseSnapshotModel).where(
                LlmReleaseSnapshotModel.id == active_snapshot_id
            )
            snapshot = db.execute(stmt).scalar_one_or_none()
            if snapshot:
                active_snapshot_version = snapshot.version

        if not active_snapshot_version:
            raise ValueError(
                "Qualification rejected: No active snapshot version could be resolved."
            )

        manifest_entry_id = PerformanceQualificationService._resolve_manifest_entry_id(
            snapshot.manifest if snapshot is not None else None,
            manifest_entry_id,
        )

        return PerformanceQualificationService.evaluate_run(
            family=family,
            profile=profile,
            total_requests=total_requests,
            success_count=success_count,
            protection_count=protection_count,
            error_count=error_count,
            latency_p50_ms=latency_p50_ms,
            latency_p95_ms=latency_p95_ms,
            latency_p99_ms=latency_p99_ms,
            throughput_rps=throughput_rps,
            active_snapshot_id=active_snapshot_id,
            active_snapshot_version=active_snapshot_version,
            manifest_entry_id=manifest_entry_id,
            environment=environment,
        )

    @staticmethod
    def evaluate_run(
        family: str,
        profile: str,
        total_requests: int,
        success_count: int,
        protection_count: int,
        error_count: int,
        latency_p50_ms: float,
        latency_p95_ms: float,
        latency_p99_ms: float,
        throughput_rps: float,
        active_snapshot_id: Optional[uuid.UUID] = None,
        active_snapshot_version: Optional[str] = None,
        manifest_entry_id: Optional[str] = None,
        environment: str = "local",
    ) -> PerformanceQualificationReport:
        """
        Évalue un run de charge par rapport aux SLO et SLA (Story 66.35).
        Retourne un rapport de qualification complet avec verdict automatisé.
        """
        slo = PERFORMANCE_SLO_REGISTRY.get(family)
        sla = PERFORMANCE_SLA_REGISTRY.get(family)

        if not slo or not sla:
            # Default strict for unknown families
            slo = PerformanceSLO(
                p95_latency_ms=2000.0,
                p99_latency_ms=4000.0,
                min_success_rate=0.99,
                max_protection_rate=0.01,
                max_error_rate=0.0,
            )
            sla = PerformanceSLA(p95_latency_max_ms=10000.0, max_error_rate_threshold=0.05)

        error_rate = error_count / total_requests if total_requests > 0 else 0.0
        protection_rate = protection_count / total_requests if total_requests > 0 else 0.0

        constraints = []
        verdict: Literal["go", "no-go", "go-with-constraints"] = "go"

        # 1. Check SLA (Seuils critiques -> No-Go)
        if latency_p95_ms > sla.p95_latency_max_ms:
            verdict = "no-go"
            constraints.append(
                f"SLA Violation: p95 latency {latency_p95_ms}ms > {sla.p95_latency_max_ms}ms"
            )

        if error_rate > sla.max_error_rate_threshold:
            verdict = "no-go"
            constraints.append(
                f"SLA Violation: error rate {error_rate:.2%} > {sla.max_error_rate_threshold:.2%}"
            )

        # 2. Check SLO (Objectifs -> Go with constraints)
        if verdict != "no-go":
            if latency_p95_ms > slo.p95_latency_ms:
                verdict = "go-with-constraints"
                constraints.append(
                    f"SLO Warning: p95 latency {latency_p95_ms}ms > {slo.p95_latency_ms}ms"
                )

            if error_rate > slo.max_error_rate:
                verdict = "go-with-constraints"
                constraints.append(
                    f"SLO Warning: error rate {error_rate:.2%} > {slo.max_error_rate:.2%}"
                )

            if protection_rate > slo.max_protection_rate:
                verdict = "go-with-constraints"
                constraints.append(
                    f"SLO Warning: protection rate {protection_rate:.2%} > "
                    f"{slo.max_protection_rate:.2%}"
                )

        # 3. Budget remaining calculation
        if slo.max_error_rate > 0:
            budget_remaining = max(0.0, 1.0 - (error_rate / slo.max_error_rate))
        else:
            budget_remaining = 1.0 if error_rate == 0 else 0.0

        return PerformanceQualificationReport(
            active_snapshot_id=active_snapshot_id,
            active_snapshot_version=active_snapshot_version,
            manifest_entry_id=manifest_entry_id,
            environment=environment,
            family=family,
            profile=profile,
            total_requests=total_requests,
            success_count=success_count,
            protection_count=protection_count,
            error_count=error_count,
            error_rate=error_rate,
            latency_p50_ms=latency_p50_ms,
            latency_p95_ms=latency_p95_ms,
            latency_p99_ms=latency_p99_ms,
            throughput_rps=throughput_rps,
            budget_remaining=budget_remaining,
            verdict=verdict,
            constraints=constraints,
            generated_at=datetime_provider.utcnow(),
        )
