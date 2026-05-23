"""Tests du contrat natal expose apres adaptation interpretative."""

from __future__ import annotations

from app.domain.astrology.dignities.contracts import ChartSectResult
from app.domain.astrology.interpretation_adapters.contracts import InterpretationAdapterResult
from app.domain.astrology.natal_calculation import NatalResult
from app.main import app


def test_natal_result_exposes_interpretation_adapter_after_dominance() -> None:
    """Le contrat natal expose le resultat d'adaptation sans remplacer les dominantes."""
    fields = list(NatalResult.model_fields)

    assert "dominant_planets" in fields
    assert "interpretation_adapter" in fields
    assert "dignity_sect" in fields
    assert fields.index("interpretation_adapter") > fields.index("dominant_planets")
    assert NatalResult.model_fields["interpretation_adapter"].annotation == (
        InterpretationAdapterResult | None
    )
    assert NatalResult.model_fields["dignity_sect"].annotation == (ChartSectResult | None)


def test_public_schema_excludes_fixed_star_runtime_payloads() -> None:
    """Les nouveaux payloads chart-object restent hors schema public."""
    schemas = app.openapi().get("components", {}).get("schemas", {})
    serialized_schemas = str(schemas)

    assert "FixedStarRuntimePayload" not in serialized_schemas
    assert "FixedStarConjunctionRuntimePayload" not in serialized_schemas
