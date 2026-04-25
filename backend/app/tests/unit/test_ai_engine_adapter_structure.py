"""Verifie les garde-fous structurels autour de la facade publique LLM."""

from __future__ import annotations

from pathlib import Path

import app.domain.llm.runtime as runtime_llm

REPO_ROOT = Path(__file__).resolve().parents[4]
BACKEND_ROOT = REPO_ROOT / "backend"
APPLICATION_ROOT = BACKEND_ROOT / "app" / "application"
ADAPTER_FILE = BACKEND_ROOT / "app" / "domain" / "llm" / "runtime" / "adapter.py"


def test_runtime_public_surface_is_minimal() -> None:
    """La couche publique `app.domain.llm.runtime` ne doit exposer que la facade utile."""
    assert runtime_llm.__all__ == ["AIEngineAdapter", "AIEngineAdapterError"]
    assert runtime_llm.AIEngineAdapter.__name__ == "AIEngineAdapter"
    assert runtime_llm.AIEngineAdapterError.__name__ == "AIEngineAdapterError"


def test_application_folder_has_been_removed() -> None:
    """Empeche la recreation du dossier `app/application` apres la migration."""
    assert not APPLICATION_ROOT.exists()


def test_legacy_services_adapter_file_does_not_exist() -> None:
    """Empêche la réintroduction du chemin legacy `app.services.ai_engine_adapter`."""
    assert not (BACKEND_ROOT / "app" / "services" / "ai_engine_adapter.py").exists()


def test_backend_code_does_not_import_legacy_adapter_path() -> None:
    """Empêche tout import nominal du chemin legacy dans le backend et les tests."""
    forbidden_markers = ["app.services.ai_engine_adapter", "app.application.llm"]
    offenders: list[str] = []
    for path in BACKEND_ROOT.rglob("*.py"):
        if ".venv" in path.parts:
            continue
        if path == Path(__file__).resolve():
            continue
        content = path.read_text(encoding="utf-8")
        if any(marker in content for marker in forbidden_markers):
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []


def test_production_adapter_keeps_no_test_hook() -> None:
    """Empêche le retour des hooks de test dans le module de production nominal."""
    content = ADAPTER_FILE.read_text(encoding="utf-8")
    forbidden_markers = [
        "set_test_chat_generator",
        "set_test_guidance_generator",
        "reset_test_generators",
        "_test_chat_generator",
        "_test_guidance_generator",
    ]
    for marker in forbidden_markers:
        assert marker not in content


def test_production_code_does_not_depend_on_test_helpers() -> None:
    """Empêche les imports de helpers de test depuis le code de production."""
    offenders: list[str] = []
    for path in (BACKEND_ROOT / "app").rglob("*.py"):
        if "tests" in path.parts:
            continue
        content = path.read_text(encoding="utf-8")
        if "app.tests.helpers" in content:
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []
