# Tests de l'API publique transit_client_projection_v1 proof-gated.
"""Couvre la route transit publique, le proof gate et la segmentation B2C."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.dependencies.auth import require_authenticated_user
from app.api.v1.routers.public.transit_projection import (
    get_transit_client_projection_service,
    get_transit_projection_access_resolver,
    get_transit_projection_proof_gate,
)
from app.core.auth_context import AuthenticatedUser
from app.main import app
from app.services.entitlement.feature_scope_registry import FEATURE_SCOPE_REGISTRY, FeatureScope
from app.services.transit_projection.access_gate import (
    TRANSIT_PROJECTION_FEATURE_CODE,
    TransitProjectionAccessDenied,
)
from app.services.transit_projection.client_projection import TransitClientProjectionService
from app.services.transit_projection.proof_gate import (
    TransitProjectionProofGate,
    TransitProjectionProofGateUnavailable,
    TransitProjectionProofResult,
)

CLIENT = TestClient(app)


class _ValidProofGate:
    """Proof gate de test validant les preuves attendues."""

    def validate(self) -> TransitProjectionProofResult:
        """Retourne des refs publiques sans payload interne."""
        return TransitProjectionProofResult(
            is_valid=True,
            public_refs=("CS-280:final-evidence", "CS-281:final-evidence"),
        )


class _MissingProofGate:
    """Proof gate de test simulant une preuve manquante."""

    def validate(self) -> TransitProjectionProofResult:
        """Retourne le blocage attendu quand une preuve manque."""
        return TransitProjectionProofResult(
            is_valid=False,
            public_refs=(),
            missing_paths=("missing-proof.md",),
        )


class _UnavailableProofGate:
    """Proof gate de test simulant une preuve illisible."""

    def validate(self) -> TransitProjectionProofResult:
        """Leve l'indisponibilite attendue par le handler HTTP."""
        raise TransitProjectionProofGateUnavailable("proof_evidence_unavailable:test")


class _DegradedProjectionService(TransitClientProjectionService):
    """Service de test qui force un état dégradé explicite."""

    def build(self, *, plan_code: str, proof_refs: tuple[str, ...], degraded_reason=None):
        """Retourne la projection avec une raison de degradation contrôlée."""
        return super().build(
            plan_code=plan_code,
            proof_refs=proof_refs,
            degraded_reason="data_incomplete",
        )


class _AllowedAccessResolver:
    """Resolver B2C de test pour un plan autorise."""

    def __init__(self, plan_code: str) -> None:
        self._plan_code = plan_code

    def resolve(self, current_user):
        """Retourne le plan attendu sans acceder a la DB."""
        return SimpleNamespace(plan_code=self._plan_code)


class _DeniedAccessResolver:
    """Resolver B2C de test pour un refus d'acces."""

    def resolve(self, current_user):
        """Leve le refus attendu par le handler HTTP."""
        raise TransitProjectionAccessDenied(
            "feature_not_in_plan",
            "active",
            "free",
            "feature_not_in_plan",
        )


def test_transit_projection_blocks_missing_proof_gate() -> None:
    """La route refuse l'exposition si le proof gate n'est pas valide."""
    _override_user()
    app.dependency_overrides[get_transit_projection_proof_gate] = lambda: _MissingProofGate()
    _override_access("premium")

    response = CLIENT.get("/v1/transit/projection")

    app.dependency_overrides.clear()
    assert response.status_code == 409
    payload = response.json()
    assert payload["projection_id"] == "transit_client_projection_v1"
    assert payload["status"] == "proof_blocked"
    assert payload["degraded_reason"] == "proof_gate_missing_evidence"
    assert payload["content"]["sections"] == {}


def test_transit_projection_proof_gate_blocks_invalid_dependency_evidence(
    tmp_path: Path,
) -> None:
    """Le proof gate refuse une preuve presente mais sans marqueur PASS attendu."""
    _write_required_proofs(tmp_path)
    invalid_validation = (
        tmp_path
        / "_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt"
    )
    invalid_validation.write_text("Result: FAIL\n", encoding="utf-8")

    result = TransitProjectionProofGate(repo_root=tmp_path).validate()

    assert result.is_valid is False
    assert result.missing_paths == ()
    assert result.invalid_paths == (
        str(
            Path(
                "_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt"
            )
        ),
    )


def test_transit_projection_returns_unavailable_when_proof_service_is_unavailable() -> None:
    """Une preuve illisible produit un état indisponible explicite."""
    _override_user()
    app.dependency_overrides[get_transit_projection_proof_gate] = lambda: _UnavailableProofGate()
    _override_access("premium")

    response = CLIENT.get("/v1/transit/projection")

    app.dependency_overrides.clear()
    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "unavailable"
    assert payload["degraded_reason"] == "proof_evidence_unavailable:test"
    assert payload["content"]["sections"] == {}


def test_transit_projection_success_payload_is_client_safe() -> None:
    """Le payload expose la projection client sans champs runtime internes."""
    _override_user()
    _override_valid_proof_gate()
    _override_access("premium")

    response = CLIENT.get("/v1/transit/projection")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    serialized = str(payload)
    assert payload["projection_id"] == "transit_client_projection_v1"
    assert payload["status"] == "available"
    assert payload["plan_code"] == "premium"
    assert payload["proof_refs"] == ["CS-280:final-evidence", "CS-281:final-evidence"]
    assert payload["projection_hash"]
    assert "sequence_temporelle" in payload["content"]["sections"]
    assert "transit_chart_v1" not in serialized
    assert "TransitChartRuntime" not in serialized
    assert "execution_trace" not in serialized
    assert "debug_payload" not in serialized


def test_transit_projection_enforces_plan_depth() -> None:
    """Les plans free, basic et premium ne voient que leur profondeur."""
    _override_user()
    _override_valid_proof_gate()

    free_payload = _call_for_plan("free")
    basic_payload = _call_for_plan("basic")
    premium_payload = _call_for_plan("premium")

    app.dependency_overrides.clear()
    assert "orientation_generale" in free_payload["content"]["sections"]
    assert "fenetres_de_timing" not in free_payload["content"]["sections"]
    assert free_payload["upgrade_hint"] == "basic_unlocks_timing_windows"
    assert "fenetres_de_timing" in basic_payload["content"]["sections"]
    assert "sequence_temporelle" not in basic_payload["content"]["sections"]
    assert basic_payload["upgrade_hint"] == "premium_unlocks_sequence_and_cycles"
    assert "sequence_temporelle" in premium_payload["content"]["sections"]
    assert premium_payload["upgrade_hint"] is None


def test_transit_projection_returns_unauthorized_state() -> None:
    """Un refus B2C produit un état client unauthorized explicite."""
    _override_user()
    _override_valid_proof_gate()
    app.dependency_overrides[get_transit_projection_access_resolver] = lambda: (
        _DeniedAccessResolver()
    )

    response = CLIENT.get("/v1/transit/projection")

    app.dependency_overrides.clear()
    assert response.status_code == 403
    payload = response.json()
    assert payload["status"] == "unauthorized"
    assert payload["degraded_reason"] == "feature_not_in_plan"


def test_transit_projection_returns_degraded_state() -> None:
    """Un état dégradé reste explicite et conserve un hash stable."""
    _override_user()
    _override_valid_proof_gate()
    app.dependency_overrides[get_transit_client_projection_service] = lambda: (
        _DegradedProjectionService()
    )
    _override_access("basic")

    response = CLIENT.get("/v1/transit/projection")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["degraded_reason"] == "data_incomplete"
    assert payload["projection_hash"]


def test_transit_projection_route_registered_once_and_openapi_is_controlled() -> None:
    """Le runtime FastAPI expose une seule route transit client contrôlée."""
    route_paths = [route.path for route in app.routes]
    openapi = app.openapi()
    serialized_openapi = str(openapi)

    assert route_paths.count("/v1/transit/projection") == 1
    assert "/v1/transit/projection" in openapi["paths"]
    assert "transit_client_projection_v1" in serialized_openapi
    assert "TransitChartRuntime" not in serialized_openapi
    assert "transit_chart_v1" not in serialized_openapi
    assert "execution_trace" not in serialized_openapi
    assert "debug_payload" not in serialized_openapi


def test_transit_projection_feature_code_is_registered_for_real_b2c_gate() -> None:
    """Le feature code utilise par le gate runtime existe dans le registre B2C."""
    assert FEATURE_SCOPE_REGISTRY[TRANSIT_PROJECTION_FEATURE_CODE] == FeatureScope.B2C


def _override_user(role: str = "user") -> None:
    """Installe un utilisateur authentifié de test."""
    app.dependency_overrides[require_authenticated_user] = lambda: AuthenticatedUser(
        id=1,
        role=role,
        email="client@example.test",
        created_at=datetime(2026, 1, 1),
    )


def _override_valid_proof_gate() -> None:
    """Installe le proof gate valide de test."""
    app.dependency_overrides[get_transit_projection_proof_gate] = lambda: _ValidProofGate()


def _override_access(plan_code: str) -> None:
    """Installe un resolver B2C minimal pour un plan donne."""
    app.dependency_overrides[get_transit_projection_access_resolver] = lambda: (
        _AllowedAccessResolver(plan_code)
    )


def _call_for_plan(plan_code: str) -> dict:
    """Appelle la route avec un resolver B2C force sur un plan."""
    _override_access(plan_code)
    response = CLIENT.get("/v1/transit/projection")
    assert response.status_code == 200
    return response.json()


def _write_required_proofs(repo_root: Path) -> None:
    """Crée les preuves minimales valides pour le proof gate de test."""
    proof_payloads = {
        "_condamad/stories/CS-280-internal-transit-runtime/generated/10-final-evidence.md": (
            "Validation outcome: PASS\n"
        ),
        "_condamad/stories/CS-280-internal-transit-runtime/evidence/validation.txt": (
            "PASS: pytest\n"
        ),
        (
            "_condamad/stories/CS-281-transit-client-projection-by-plan/"
            "generated/10-final-evidence.md"
        ): "Validation outcome: PASS\n",
        "_condamad/stories/CS-281-transit-client-projection-by-plan/evidence/validation.txt": (
            "Result: PASS\n"
        ),
        "docs/architecture/transit-client-projection-v1-contract.md": (
            "transit_client_projection_v1\n"
        ),
    }
    for relative_path, content in proof_payloads.items():
        path = repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
