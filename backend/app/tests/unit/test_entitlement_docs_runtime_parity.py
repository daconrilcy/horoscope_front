# Garde de statut doc/runtime pour la documentation entitlement.
"""Verifie que la documentation entitlement ne derive pas des contrats runtime."""

from __future__ import annotations

from pathlib import Path

from app.infra.db.base import Base
from app.infra.db.models.canonical_entitlement_mutation_audit import (
    CanonicalEntitlementMutationAuditModel,
)
from app.infra.db.models.entitlement_mutation.alert.alert_event import (
    CanonicalEntitlementMutationAlertEventModel,
)
from app.infra.db.models.entitlement_mutation.audit.review import (
    CanonicalEntitlementMutationAuditReviewModel,
)
from app.infra.db.models.product_entitlements import FeatureUsageCounterModel
from app.main import app

BACKEND_ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = BACKEND_ROOT / "docs" / "entitlements-canonical-platform.md"
OWNERSHIP_INDEX = BACKEND_ROOT / "docs" / "ownership-index.md"

EXPECTED_OPENAPI_PATHS = {
    "/v1/entitlements/me": {"get"},
    "/v1/entitlements/plans": {"get"},
    "/v1/admin/entitlements/matrix": {"get"},
    "/v1/ops/entitlements/mutation-audits": {"get"},
    "/v1/ops/entitlements/mutation-audits/alerts": {"get"},
    "/v1/ops/entitlements/mutation-audits/alerts/summary": {"get"},
}
EXPECTED_TABLES = {
    FeatureUsageCounterModel.__tablename__,
    CanonicalEntitlementMutationAuditModel.__tablename__,
    CanonicalEntitlementMutationAuditReviewModel.__tablename__,
    CanonicalEntitlementMutationAlertEventModel.__tablename__,
}


def test_entitlement_doc_has_explicit_historical_status() -> None:
    """Le document doit annoncer qu'il n'est pas la source runtime active."""
    content = DOC_PATH.read_text(encoding="utf-8")
    ownership = OWNERSHIP_INDEX.read_text(encoding="utf-8")

    assert "Document status: historical-note." in content
    assert "Do not treat this prose as the source of truth" in content
    assert "`backend/docs/entitlements-canonical-platform.md`" in ownership
    assert "Entitlement runtime documentation | historical-note | historical-note" in ownership


def test_entitlement_documented_routes_exist_in_openapi() -> None:
    """Les routes entitlement critiques doivent rester observables via OpenAPI."""
    openapi_paths = app.openapi()["paths"]
    missing: list[str] = []
    for path, methods in EXPECTED_OPENAPI_PATHS.items():
        if path not in openapi_paths:
            missing.append(f"{path}: missing path")
            continue
        available_methods = set(openapi_paths[path])
        for method in methods:
            if method not in available_methods:
                missing.append(f"{method.upper()} {path}: missing method")

    assert missing == []


def test_entitlement_documented_tables_exist_in_sqlalchemy_metadata() -> None:
    """Les tables entitlement citees par la doc doivent rester chargees en metadata."""
    metadata_tables = set(Base.metadata.tables)

    assert EXPECTED_TABLES <= metadata_tables


def test_entitlement_review_alert_security_claims_are_guarded_or_historical() -> None:
    """Les claims review, alert et security doivent etre explicitement declasses ou gardes."""
    content = DOC_PATH.read_text(encoding="utf-8")
    for term in ("review", "alert", "security", "source of truth"):
        assert term in content.lower()
    assert "historical-note" in content
