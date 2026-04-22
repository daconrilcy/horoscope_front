from __future__ import annotations

import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest

_TMP_ROOT = Path(__file__).resolve().parent / ".tmp-pytest" / "fixture-tmp"
_TMP_ROOT.mkdir(parents=True, exist_ok=True)


@dataclass
class WorkspaceTmpPathFactory:
    base_temp: Path

    def getbasetemp(self) -> Path:
        return self.base_temp

    def mktemp(self, basename: str, numbered: bool = True) -> Path:
        suffix = f"-{uuid.uuid4().hex}" if numbered else ""
        path = self.base_temp / f"{basename}{suffix}"
        path.mkdir(parents=True, exist_ok=False)
        return path


@pytest.fixture(scope="session")
def tmp_path_factory() -> WorkspaceTmpPathFactory:
    try:
        yield WorkspaceTmpPathFactory(base_temp=_TMP_ROOT)
    finally:
        shutil.rmtree(_TMP_ROOT, ignore_errors=True)


@pytest.fixture
def tmp_path(tmp_path_factory: WorkspaceTmpPathFactory) -> Path:
    path = tmp_path_factory.mktemp("test")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
