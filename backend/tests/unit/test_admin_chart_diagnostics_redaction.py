# Commentaire global: ces tests verrouillent le masquage du diagnostic admin de calcul.
"""Tests unitaires de redaction pour `admin_chart_diagnostics_v1`."""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.auth_context import AuthenticatedUser
from app.infra.db.models.chart_result import ChartResultModel
from app.services.ops.admin_chart_diagnostics import (
    AdminChartDiagnosticsService,
    _masked_chart_reference,
)


class _FakeChartResultRepository:
    """Repository de test minimal pour isoler l'assemblage du diagnostic."""

    def __init__(self, _db: object) -> None:
        self._db = _db

    def get_by_chart_id(self, chart_id: str) -> ChartResultModel:
        """Retourne une source persistante sans acces base."""
        return ChartResultModel(
            chart_id=chart_id,
            reference_version="ref-v1",
            ruleset_version="rules-v1",
            input_hash="b" * 64,
            result_payload={"status": "persisted"},
        )


class _FakeAuditService:
    """Capture l'appel d'audit sans ecrire en base."""

    payload = None

    @staticmethod
    def record_event(_db: object, *, payload: object) -> None:
        """Memorise le payload d'audit pour assertion."""
        _FakeAuditService.payload = payload


def test_chart_reference_is_hashed_not_returned_raw() -> None:
    """Le champ de reference expose un hash tronque, pas la valeur source."""
    raw_reference = "chart-sensitive-reference"

    masked = _masked_chart_reference(raw_reference)

    assert masked != raw_reference
    assert masked.endswith("...")
    assert len(masked) < len(raw_reference)


def test_response_omits_raw_sensitive_payload(monkeypatch) -> None:
    """Le diagnostic contient seulement des metadonnees de graphe et la politique."""
    monkeypatch.setattr(
        "app.services.ops.admin_chart_diagnostics.ChartResultRepository",
        _FakeChartResultRepository,
    )
    monkeypatch.setattr(
        "app.services.ops.admin_chart_diagnostics.AuditService",
        _FakeAuditService,
    )

    response = AdminChartDiagnosticsService.get_chart_diagnostics(
        object(),
        chart_reference="chart-sensitive-reference",
        request_id="rid-redaction",
        current_user=AuthenticatedUser(
            id=1,
            role="admin",
            email="admin@example.com",
            created_at=datetime(2026, 5, 24, tzinfo=UTC),
        ),
    )
    serialized = response.model_dump(mode="json")

    assert serialized["chart_reference"] != "chart-sensitive-reference"
    assert serialized["redaction"]["applied"] == [
        "chart_reference_hashed",
        "raw_birth_fields_omitted",
    ]
    assert "chart-sensitive-reference" not in str(serialized)
    assert "result_payload" not in str(serialized)
    assert "raw_birth_data" in serialized["redaction"]["omitted_raw_field_categories"]
