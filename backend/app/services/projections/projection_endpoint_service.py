# Orchestration applicative du endpoint generique de projections B2C.
"""Resolve la source de theme, les droits B2C, les builders publics et la persistance."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.auth_context import AuthenticatedUser
from app.domain.astrology.interpretation.beginner_summary_v1_builder import (
    BeginnerSummaryV1Builder,
)
from app.domain.astrology.interpretation.client_interpretation_projection_v1_builder import (
    ClientInterpretationProjectionV1Builder,
)
from app.domain.astrology.interpretation.structured_facts_v1_builder import (
    STRUCTURED_FACTS_V1_CONTRACT_VERSION,
    StructuredFactsV1Builder,
)
from app.domain.astrology.natal_calculation import NatalCalculationError, NatalResult
from app.domain.astrology.natal_preparation import BirthInput, BirthPreparationError
from app.domain.astrology.projections.projection_hash import compute_projection_hash
from app.infra.db.repositories.chart_result_repository import ChartResultRepository
from app.infra.db.repositories.projection_repository import ProjectionRepository
from app.services.api_contracts.public.astrology_engine import NatalCalculateRequest
from app.services.api_contracts.public.projections import (
    ProjectionCommandMetadata,
    ProjectionCommandRequest,
    ProjectionCommandResponse,
)
from app.services.chart.result_service import ChartResultService, ChartResultServiceError
from app.services.entitlement.effective_entitlement_resolver_service import (
    EffectiveEntitlementResolverService,
)
from app.services.entitlement.entitlement_types import EffectiveEntitlementsSnapshot
from app.services.natal.calculation_service import NatalCalculationService
from app.services.projection_persistence_service import (
    ProjectionBuilderUnavailableError,
    ProjectionPersistenceService,
)

PUBLIC_PROJECTION_VERSION = "v1"
SUPPORTED_PROJECTION_TYPES = frozenset(
    {
        "structured_facts_v1",
        "beginner_summary_v1",
        "client_interpretation_projection_v1",
    }
)
_SUPPORTED_PLAN_CODES = frozenset({"free", "basic", "premium"})


class ProjectionEndpointServiceError(Exception):
    """Erreur controlee que le routeur convertit en reponse HTTP."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Initialise une erreur applicative sans payload technique interne."""
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ChartCalculationService(Protocol):
    """Contrat minimal du service de calcul natal reutilise par l'orchestrateur."""

    @staticmethod
    def calculate(**kwargs: Any) -> NatalResult:
        """Calcule un theme natal depuis les arguments publics deja valides."""


class ChartTraceService(Protocol):
    """Contrat minimal du service de trace chart existant."""

    @staticmethod
    def persist_trace(
        db: Session,
        birth_input: BirthInput,
        natal_result: NatalResult,
        user_id: int | None = None,
    ) -> str:
        """Persiste la trace de theme et retourne le chart_id canonique."""


@dataclass(frozen=True)
class _ResolvedChart:
    """Theme natal resolu avec sa provenance publique."""

    chart_id: str
    natal_result: NatalResult
    source: str


@dataclass(frozen=True)
class _BuiltProjection:
    """Projection publique construite avec le builder reel utilise."""

    payload: dict[str, Any]
    builder: Any
    builder_args: tuple[Any, ...]
    builder_kwargs: dict[str, Any]
    source_versions: dict[str, Any]


class ProjectionEndpointService:
    """Orchestre la commande publique sans dupliquer les owners metier."""

    def __init__(
        self,
        db: Session,
        *,
        chart_repository: ChartResultRepository | None = None,
        persistence_service: ProjectionPersistenceService | None = None,
        entitlement_resolver: Callable[[Session, int], EffectiveEntitlementsSnapshot] | None = None,
        calculation_service: type[ChartCalculationService] = NatalCalculationService,
        chart_trace_service: type[ChartTraceService] = ChartResultService,
    ) -> None:
        """Initialise les dependances canoniques, injectables en tests."""
        self.db = db
        self.chart_repository = chart_repository or ChartResultRepository(db)
        self.persistence_service = persistence_service or ProjectionPersistenceService(
            ProjectionRepository(db)
        )
        self.entitlement_resolver = entitlement_resolver or _resolve_b2c_snapshot
        self.calculation_service = calculation_service
        self.chart_trace_service = chart_trace_service
        self.structured_builder = StructuredFactsV1Builder()
        self.beginner_builder = BeginnerSummaryV1Builder()
        self.client_builder = ClientInterpretationProjectionV1Builder()

    def generate(
        self,
        *,
        request: ProjectionCommandRequest,
        current_user: AuthenticatedUser,
        request_id: str,
    ) -> ProjectionCommandResponse:
        """Genere la projection publique demandee ou leve un refus controle."""
        if current_user.role not in {"user", "admin"}:
            raise ProjectionEndpointServiceError(
                code="projection.unauthorized",
                message="projection command is reserved to B2C users",
                details={"actual_role": current_user.role},
            )

        self._validate_projection_contract(request)
        chart = self._resolve_chart(request=request, current_user=current_user)
        plan_code = self._resolve_plan_code(current_user.id)
        built = self._build_projection(request, chart, plan_code=plan_code)
        projection_hash = compute_projection_hash(built.payload)
        persisted_id: int | None = None

        if request.persist:
            try:
                persisted = self.persistence_service.persist_from_builder(
                    builder=built.builder,
                    projection_type=request.projection_type,
                    projection_version=request.projection_version,
                    chart_id=chart.chart_id,
                    user_id=current_user.id,
                    source_versions=built.source_versions,
                    source=chart.source,
                    builder_args=built.builder_args,
                    builder_kwargs=built.builder_kwargs,
                )
            except (ProjectionBuilderUnavailableError, ValueError) as exc:
                raise ProjectionEndpointServiceError(
                    code="projection.dependency_unavailable",
                    message="projection persistence dependency is unavailable",
                    details={"reason": exc.__class__.__name__},
                ) from exc
            projection_hash = persisted.projection_hash
            persisted_id = int(persisted.id)

        return ProjectionCommandResponse(
            chart_id=chart.chart_id,
            projection_type=request.projection_type,  # type: ignore[arg-type]
            projection_version=request.projection_version,
            persisted=request.persist,
            projection_hash=projection_hash,
            payload=built.payload,
            metadata=ProjectionCommandMetadata(
                source="chart_id" if chart.source == "chart_result" else "birth_input",
                plan_code=plan_code,  # type: ignore[arg-type]
                request_id=request_id,
                persisted_id=persisted_id,
            ),
        )

    def _validate_projection_contract(self, request: ProjectionCommandRequest) -> None:
        """Verifie type public et version explicite sans resolution implicite."""
        if request.projection_type not in SUPPORTED_PROJECTION_TYPES:
            raise ProjectionEndpointServiceError(
                code="projection.unauthorized",
                message="projection type is not authorized for B2C clients",
                details={"projection_type": request.projection_type},
            )
        if request.projection_version != PUBLIC_PROJECTION_VERSION:
            raise ProjectionEndpointServiceError(
                code="projection.invalid_payload",
                message="projection version is unsupported",
                details={
                    "projection_type": request.projection_type,
                    "projection_version": request.projection_version,
                },
            )

    def _resolve_chart(
        self,
        *,
        request: ProjectionCommandRequest,
        current_user: AuthenticatedUser,
    ) -> _ResolvedChart:
        """Choisit exactement une source chart_id ou birth_input."""
        has_chart_id = request.chart_id is not None
        has_birth_input = request.birth_input is not None
        if has_chart_id == has_birth_input:
            raise ProjectionEndpointServiceError(
                code="projection.invalid_chart_source",
                message="provide exactly one chart source",
                details={"chart_id": has_chart_id, "birth_input": has_birth_input},
            )
        if request.chart_id is not None:
            return self._resolve_existing_chart(request.chart_id, current_user)
        if request.birth_input is None:
            raise AssertionError("birth_input source should be selected")
        return self._calculate_chart(request.birth_input, current_user)

    def _resolve_existing_chart(
        self,
        chart_id: str,
        current_user: AuthenticatedUser,
    ) -> _ResolvedChart:
        """Retrouve un theme existant appartenant a l'utilisateur authentifie."""
        model = self.chart_repository.get_by_chart_id(chart_id)
        if model is None or model.user_id != current_user.id:
            raise ProjectionEndpointServiceError(
                code="projection.chart_not_found",
                message="chart result was not found for this user",
                details={"chart_id": chart_id},
            )
        try:
            natal_result = NatalResult.model_validate(model.result_payload)
        except ValidationError as exc:
            raise ProjectionEndpointServiceError(
                code="projection.dependency_unavailable",
                message="stored chart result cannot be used",
                details={"chart_id": chart_id},
            ) from exc
        return _ResolvedChart(chart_id=chart_id, natal_result=natal_result, source="chart_result")

    def _calculate_chart(
        self,
        payload: NatalCalculateRequest,
        current_user: AuthenticatedUser,
    ) -> _ResolvedChart:
        """Calcule un theme natal depuis birth_input puis reutilise la trace chart."""
        birth_input = BirthInput(
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            birth_place=payload.birth_place,
            birth_timezone=payload.birth_timezone,
            birth_lat=payload.birth_lat,
            birth_lon=payload.birth_lon,
            place_resolved_id=payload.place_resolved_id,
        )
        try:
            natal_result = self.calculation_service.calculate(
                db=self.db,
                birth_input=birth_input,
                reference_version=payload.reference_version,
                accurate=payload.accurate,
                zodiac=payload.zodiac,
                ayanamsa=payload.ayanamsa,
                frame=payload.frame,
                house_system=payload.house_system,
                altitude_m=payload.altitude_m,
                request_id=None,
                tt_enabled=payload.tt_enabled,
                derive_enabled=True,
                include_points_in_aspects=payload.include_points_in_aspects,
            )
            chart_id = self.chart_trace_service.persist_trace(
                self.db,
                birth_input,
                natal_result,
                user_id=current_user.id,
            )
        except BirthPreparationError as exc:
            raise ProjectionEndpointServiceError(
                code="projection.invalid_payload",
                message="birth input validation failed",
                details=exc.details,
            ) from exc
        except (NatalCalculationError, ChartResultServiceError) as exc:
            raise ProjectionEndpointServiceError(
                code="projection.dependency_unavailable",
                message="chart calculation dependency is unavailable",
                details={"reason": getattr(exc, "code", exc.__class__.__name__)},
            ) from exc
        return _ResolvedChart(chart_id=chart_id, natal_result=natal_result, source="birth_input")

    def _resolve_plan_code(self, user_id: int) -> str:
        """Lit le plan B2C courant depuis le resolver entitlement canonique."""
        snapshot = self.entitlement_resolver(self.db, user_id)
        if snapshot.plan_code not in _SUPPORTED_PLAN_CODES:
            raise ProjectionEndpointServiceError(
                code="projection.unauthorized",
                message="user plan is not authorized for public projections",
                details={"current_plan": snapshot.plan_code},
            )
        return snapshot.plan_code

    def _build_projection(
        self,
        request: ProjectionCommandRequest,
        chart: _ResolvedChart,
        *,
        plan_code: str,
    ) -> _BuiltProjection:
        """Dispatche uniquement vers les builders publics livres."""
        structured_payload = self.structured_builder.build(
            chart.natal_result,
            chart_id=chart.chart_id,
        )
        structured_source_versions = _source_versions(structured_payload)
        if request.projection_type == "structured_facts_v1":
            return _BuiltProjection(
                payload=structured_payload,
                builder=self.structured_builder,
                builder_args=(chart.natal_result,),
                builder_kwargs={"chart_id": chart.chart_id},
                source_versions=structured_source_versions,
            )
        if request.projection_type == "beginner_summary_v1":
            payload = self.beginner_builder.build(structured_payload)
            return _BuiltProjection(
                payload=payload,
                builder=self.beginner_builder,
                builder_args=(structured_payload,),
                builder_kwargs={},
                source_versions={
                    "projection_contract": PUBLIC_PROJECTION_VERSION,
                    "source_projection": "structured_facts_v1",
                    "source_versions": structured_source_versions,
                },
            )
        payload = self.client_builder.build(
            structured_payload,
            requested_plan=plan_code,
            current_plan=plan_code,
        )
        return _BuiltProjection(
            payload=payload,
            builder=self.client_builder,
            builder_args=(structured_payload,),
            builder_kwargs={"requested_plan": plan_code, "current_plan": plan_code},
            source_versions={
                "projection_contract": PUBLIC_PROJECTION_VERSION,
                "source_projection": "structured_facts_v1",
                "source_versions": structured_source_versions,
            },
        )


def _resolve_b2c_snapshot(db: Session, user_id: int) -> EffectiveEntitlementsSnapshot:
    """Adapte le resolver entitlement existant a une signature injectable."""
    return EffectiveEntitlementResolverService.resolve_b2c_user_snapshot(db, app_user_id=user_id)


def _source_versions(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Extrait une provenance JSON stable du payload structured_facts_v1."""
    source_versions = payload.get("source_versions")
    if isinstance(source_versions, dict):
        return source_versions
    return {"structured_facts_contract": STRUCTURED_FACTS_V1_CONTRACT_VERSION}
