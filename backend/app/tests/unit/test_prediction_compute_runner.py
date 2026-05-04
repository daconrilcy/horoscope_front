"""Tests unitaires du runner de calcul prediction threade."""

from __future__ import annotations

import ast
import inspect
import textwrap
import threading
import time
from datetime import date
from unittest.mock import MagicMock

import pytest

from app.core.config import DailyEngineMode
from app.services.prediction import compute_runner
from app.services.prediction.compute_runner import PredictionComputeRunner
from app.services.prediction.types import DailyPredictionServiceError


class _InstrumentedContextLoader:
    """Observe le thread et la session utilises pour charger le contexte."""

    def __init__(self, loaded_context: object) -> None:
        self.loaded_context = loaded_context
        self.calls: list[tuple[object, int]] = []

    def load(self, db: object, _ref: str, _rule: str, _dt: date) -> object:
        """Memorise la session et le thread du chargement."""
        self.calls.append((db, threading.get_ident()))
        return self.loaded_context


class _CapturingOrchestrator:
    """Orchestrateur de test qui capture le loader injecte au worker."""

    def __init__(self, *, block: bool = False) -> None:
        self.block = block
        self.last_bound: _CapturingOrchestrator | None = None
        self.prediction_context_loader = None
        self.worker_thread_id: int | None = None
        self.loaded_context = None

    def with_context_loader(self, prediction_context_loader):
        """Retourne un clone configure comme le ferait l'orchestrateur reel."""
        clone = _CapturingOrchestrator(block=self.block)
        clone.prediction_context_loader = prediction_context_loader
        self.last_bound = clone
        return clone

    def run(self, *, engine_input, include_editorial_text, engine_mode=None):
        """Execute le loader dans le worker puis retourne ou bloque selon le test."""
        self.worker_thread_id = threading.get_ident()
        self.loaded_context = self.prediction_context_loader(
            engine_input.reference_version,
            engine_input.ruleset_version,
            engine_input.local_date,
        )
        if self.block:
            time.sleep(0.2)
        bundle = MagicMock()
        bundle.to_engine_output.return_value = "engine-output"
        return bundle


def _engine_input() -> MagicMock:
    """Construit une entree moteur minimale pour le runner."""
    engine_input = MagicMock()
    engine_input.reference_version = "2.0.0"
    engine_input.ruleset_version = "2.0.0"
    engine_input.local_date = date(2026, 5, 4)
    return engine_input


def test_run_preloads_prediction_context_before_worker_thread() -> None:
    """Verifie que la session appelante n'est pas capturee par le worker."""
    caller_thread_id = threading.get_ident()
    db = object()
    loaded_context = object()
    context_loader = _InstrumentedContextLoader(loaded_context)
    orchestrator = _CapturingOrchestrator()
    runner = PredictionComputeRunner(context_loader, orchestrator)

    result = runner.run_with_timeout(
        db,
        _engine_input(),
        engine_mode=DailyEngineMode.V3,
    )

    assert result.engine_output == "engine-output"
    assert context_loader.calls == [(db, caller_thread_id)]
    assert orchestrator.last_bound is not None
    assert orchestrator.last_bound.loaded_context is loaded_context
    assert orchestrator.last_bound.worker_thread_id != caller_thread_id


def test_ctx_loader_does_not_capture_caller_db_session() -> None:
    """Garde AST contre la reintroduction de `db` dans le loader du worker."""
    source = textwrap.dedent(
        inspect.getsource(compute_runner.PredictionComputeRunner.run_with_timeout)
    )
    tree = ast.parse(source)
    ctx_loader = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "ctx_loader"
    )

    db_references = [
        node for node in ast.walk(ctx_loader) if isinstance(node, ast.Name) and node.id == "db"
    ]

    assert db_references == []


def test_timeout_returns_controlled_error_without_reusing_caller_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prouve que le timeout n'entraine pas d'acces worker a la session DB."""
    db = MagicMock()
    loaded_context = object()
    context_loader = _InstrumentedContextLoader(loaded_context)
    orchestrator = _CapturingOrchestrator(block=True)
    runner = PredictionComputeRunner(context_loader, orchestrator)
    monkeypatch.setattr(
        "app.services.prediction.compute_runner._COMPUTE_TIMEOUT_SECONDS",
        0.01,
    )

    with pytest.raises(DailyPredictionServiceError) as excinfo:
        runner.run_with_timeout(db, _engine_input())

    assert excinfo.value.code == "timeout"
    assert context_loader.calls == [(db, threading.get_ident())]
    db.expire_all.assert_not_called()
