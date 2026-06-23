# Commentaire global: garde-fous de l'externalisation Astral du runtime backend.
"""Vérifie que le backend reste une façade applicative vers Astral."""

from __future__ import annotations

from pathlib import Path

from starlette.responses import StreamingResponse

from app.main import app


def test_removed_legacy_product_routes_are_not_mounted() -> None:
    """Vérifie que les anciennes surfaces produit ne sont plus exposées."""
    paths = {getattr(route, "path", "") for route in app.routes}

    forbidden_prefixes = (
        "/v1/astrology",
        "/v1/astrology-engine",
        "/v1/astrologers",
        "/v1/chat",
        "/v1/consultations",
        "/v1/ephemeris",
        "/v1/guidance",
        "/v1/predictions",
        "/v1/projections",
        "/v1/transit",
        "/v1/theme-natal",
        "/v1/admin/llm",
        "/v1/admin/pdf-templates",
        "/v1/internal/llm",
        "/v1/ops/monitoring-llm",
        "/v1/ops/persona",
        "/v1/b2b/editorial",
    )

    assert "/v1/astral/jobs" in paths
    assert not [
        path for path in paths if any(path.startswith(prefix) for prefix in forbidden_prefixes)
    ]


def test_legacy_runtime_packages_are_removed() -> None:
    """Vérifie que les packages locaux de calcul et d'interprétation ont disparu."""
    app_root = Path(__file__).resolve().parents[2]
    forbidden_paths = (
        app_root / "domain" / "astrology",
        app_root / "domain" / "llm",
        app_root / "domain" / "prediction",
        app_root / "domain" / "theme_natal",
        app_root / "services" / "llm_generation",
        app_root / "services" / "llm_observability",
        app_root / "services" / "prediction",
        app_root / "services" / "natal",
        app_root / "services" / "projections",
        app_root / "services" / "transit_projection",
        app_root / "services" / "chart",
        app_root / "core" / "ephemeris.py",
        app_root / "ops" / "llm",
    )

    assert [str(path) for path in forbidden_paths if path.exists()] == []


def test_astral_events_endpoint_is_backend_sse_proxy() -> None:
    """Vérifie que le endpoint events ne publie plus une URL Mercure au navigateur."""
    events_route = next(
        route
        for route in app.routes
        if getattr(route, "path", "") == "/v1/astral/jobs/{run_id}/events"
    )

    assert getattr(events_route, "response_class", None) is StreamingResponse


def test_forbidden_runtime_dependencies_are_absent_from_pyproject() -> None:
    """Vérifie que le backend applicatif ne dépend plus des moteurs locaux."""
    pyproject = Path(__file__).resolve().parents[3] / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()
    forbidden_dependencies = ("op" + "enai", "pys" + "wisseph", "timezone" + "finder")

    assert not [dependency for dependency in forbidden_dependencies if dependency in content]
    assert "httpx==0.28.1" in content


def test_frontend_does_not_call_astral_docker_directly() -> None:
    """Vérifie que le navigateur passe uniquement par le backend."""
    frontend_src = Path(__file__).resolve().parents[4] / "frontend" / "src"
    forbidden = ("localhost:8081", "localhost:8082", "localhost:3000")
    violations: list[str] = []

    for path in frontend_src.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        content = path.read_text(encoding="utf-8")
        if any(pattern in content for pattern in forbidden):
            violations.append(str(path.relative_to(frontend_src)))

    assert violations == []
