"""
Registre central du legacy résiduel hors périmètre nominal (Story 66.40).

Source de vérité versionnée : ``data/legacy_residual_registry.json``.
Le runtime consomme une projection via ``FallbackGovernanceRegistry`` — pas de matrice parallèle.
"""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, Field, field_validator

from app.llm_orchestration.feature_taxonomy import (
    LEGACY_DAILY_FEATURE,
    LEGACY_NATAL_FEATURE,
    NATAL_SUBFEATURE_MAPPING,
)
from app.llm_orchestration.models import FallbackStatus, FallbackType
from app.prompts.catalog import DEPRECATED_USE_CASE_MAPPING

_CANONICAL_REGISTRY_PATH: Final[Path] = (
    Path(__file__).resolve().parents[1]
    / "domain"
    / "llm"
    / "governance"
    / "data"
    / "legacy_residual_registry.json"
)
_LEGACY_REGISTRY_PATH: Final[Path] = (
    Path(__file__).resolve().parent / "data" / "legacy_residual_registry.json"
)
_REGISTRY_PATH: Final[Path] = (
    _CANONICAL_REGISTRY_PATH if _CANONICAL_REGISTRY_PATH.is_file() else _LEGACY_REGISTRY_PATH
)

_SCHEMA_LINE_PATTERN = re.compile(
    r"^\s*-\s*\*\*Version registre résiduel\*\*\s*:\s*`([^`]+)`\s*$", re.MULTILINE
)


class LegacyFallbackPathRecord(BaseModel):
    """Entrée de gouvernance pour un FallbackType."""

    stable_id: str
    path_kind: str
    fallback_type: FallbackType
    registry_status: str
    fallback_status: FallbackStatus
    owner: str
    justification: str
    perimeter: str
    review_or_extinction_date: str
    forbidden_families: frozenset[str] = Field(default_factory=frozenset)

    @field_validator("registry_status")
    @classmethod
    def _allowed_registry_status(cls, v: str) -> str:
        allowed = {"allowed", "deprecated", "blocked", "removal_candidate"}
        if v not in allowed:
            raise ValueError(f"registry_status must be one of {allowed}, got {v!r}")
        return v

    @field_validator("forbidden_families", mode="before")
    @classmethod
    def _families_to_frozenset(cls, v: Any) -> frozenset[str]:
        if v is None:
            return frozenset()
        if isinstance(v, frozenset):
            return v
        return frozenset(str(x) for x in v)

    @field_validator("owner", "justification", "perimeter", "review_or_extinction_date")
    @classmethod
    def _non_empty_str(cls, v: str) -> str:
        if not str(v).strip():
            raise ValueError("Champ obligatoire vide dans le registre legacy (AC8).")
        return str(v).strip()


class GovernedAliasRecord(BaseModel):
    stable_id: str
    path_kind: str = "alias"
    alias_kind: str
    from_value: str
    to_value: str
    registry_status: str
    owner: str
    justification: str
    perimeter: str
    review_or_extinction_date: str

    @field_validator("alias_kind")
    @classmethod
    def _alias_kind(cls, v: str) -> str:
        if v not in {"feature", "subfeature", "use_case"}:
            raise ValueError("alias_kind must be feature, subfeature or use_case")
        return v

    @field_validator("owner", "justification", "perimeter", "review_or_extinction_date")
    @classmethod
    def _non_empty_str(cls, v: str) -> str:
        if not str(v).strip():
            raise ValueError("Champ obligatoire vide dans le registre legacy (AC8).")
        return str(v).strip()


class DeprecatedUseCaseRecord(BaseModel):
    stable_id: str
    use_case_key: str
    registry_status: str
    owner: str
    justification: str
    perimeter: str
    review_or_extinction_date: str

    @field_validator("owner", "justification", "perimeter", "review_or_extinction_date")
    @classmethod
    def _non_empty_str(cls, v: str) -> str:
        if not str(v).strip():
            raise ValueError("Champ obligatoire vide dans le registre legacy (AC8).")
        return str(v).strip()


class LegacyResidualRegistryRoot(BaseModel):
    schema_version: str
    registry_title: str
    deny_by_default_statement: str
    progressive_blocklist_stable_ids: list[str] = Field(default_factory=list)
    fallback_paths: list[LegacyFallbackPathRecord]
    governed_aliases: list[GovernedAliasRecord]
    deprecated_use_cases: list[DeprecatedUseCaseRecord]


def _parse_fallback_status(raw: str) -> FallbackStatus:
    raw = raw.strip()
    for member in FallbackStatus:
        if member.value == raw:
            return member
    raise ValueError(f"Unknown fallback_status value: {raw!r}")


def _coerce_fallback_paths(raw_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw_list:
        row = dict(row)
        row["fallback_type"] = FallbackType(row["fallback_type"])
        row["fallback_status"] = _parse_fallback_status(row["fallback_status"])
        out.append(row)
    return out


@lru_cache(maxsize=1)
def load_legacy_residual_registry() -> LegacyResidualRegistryRoot:
    if not _REGISTRY_PATH.is_file():
        raise RuntimeError(f"Legacy residual registry file missing: {_REGISTRY_PATH}")

    raw = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    raw["fallback_paths"] = _coerce_fallback_paths(raw["fallback_paths"])
    root = LegacyResidualRegistryRoot.model_validate(raw)
    validate_registry_integrity(root)
    return root


def get_registry_schema_version() -> str:
    return load_legacy_residual_registry().schema_version


def get_fallback_path_record(fallback_type: FallbackType) -> LegacyFallbackPathRecord:
    root = load_legacy_residual_registry()
    for rec in root.fallback_paths:
        if rec.fallback_type == fallback_type:
            return rec
    raise KeyError(f"No legacy registry entry for fallback_type={fallback_type!s}")


def build_governance_matrix_projection() -> dict[FallbackType, dict[str, Any]]:
    """
    Projection consommée par FallbackGovernanceRegistry (AC2).
    Clés alignées sur l'ancienne GOVERNANCE_MATRIX pour minimiser le delta runtime.
    """
    root = load_legacy_residual_registry()
    matrix: dict[FallbackType, dict[str, Any]] = {}
    for rec in root.fallback_paths:
        matrix[rec.fallback_type] = {
            "stable_id": rec.stable_id,
            "registry_status": rec.registry_status,
            "path_kind": rec.path_kind,
            "status": rec.fallback_status,
            "justification": rec.justification,
            "perimeter": rec.perimeter,
            "extinction_criteria": f"Revue / extinction cible : {rec.review_or_extinction_date}",
            "review_or_extinction_date": rec.review_or_extinction_date,
            "owner": rec.owner,
            "forbidden_families": set(rec.forbidden_families),
        }
    if set(matrix.keys()) != set(FallbackType):
        missing = set(FallbackType) - set(matrix.keys())
        extra = set(matrix.keys()) - set(FallbackType)
        raise RuntimeError(
            f"Registry fallback_paths must cover exactly all FallbackType values. "
            f"missing={missing!r} extra={extra!r}"
        )
    return matrix


def parse_progressive_blocklist_env(raw: str | None) -> frozenset[str]:
    if not raw or not str(raw).strip():
        return frozenset()
    parts = [p.strip() for p in str(raw).split(",")]
    return frozenset(p for p in parts if p)


def effective_progressive_blocklist(
    root: LegacyResidualRegistryRoot | None = None,
    env_value: str | None = None,
) -> frozenset[str]:
    root = root or load_legacy_residual_registry()
    merged: set[str] = set(root.progressive_blocklist_stable_ids)
    merged.update(
        parse_progressive_blocklist_env(
            env_value if env_value is not None else os.getenv("LLM_LEGACY_PROGRESSIVE_BLOCKLIST")
        )
    )
    return frozenset(merged)


def validate_registry_integrity(root: LegacyResidualRegistryRoot) -> None:
    """
    Valide le registre résiduel (chargement runtime et tests).
    Les stable_id sont uniques sur l'ensemble fallback_paths, governed_aliases et
    deprecated_use_cases.
    """
    # AC1 / AC8 : champs obligatoires via Pydantic ; couverture FallbackType ci-dessus.

    catalog_keys = frozenset(DEPRECATED_USE_CASE_MAPPING.keys())
    registry_uc = frozenset(x.use_case_key for x in root.deprecated_use_cases)
    if catalog_keys != registry_uc:
        raise RuntimeError(
            "deprecated_use_cases keys must match DEPRECATED_USE_CASE_MAPPING exactly. "
            f"only_in_catalog={sorted(catalog_keys - registry_uc)!r} "
            f"only_in_registry={sorted(registry_uc - catalog_keys)!r}"
        )

    alias_pairs = {(a.alias_kind, a.from_value, a.to_value) for a in root.governed_aliases}
    expected_feature_aliases = {
        ("feature", LEGACY_DAILY_FEATURE, "horoscope_daily"),
        ("feature", LEGACY_NATAL_FEATURE, "natal"),
    }
    missing_fa = expected_feature_aliases - alias_pairs
    if missing_fa:
        raise RuntimeError(f"governed_aliases missing required feature alias rows: {missing_fa!r}")

    for legacy_sf, canonical in NATAL_SUBFEATURE_MAPPING.items():
        if ("subfeature", legacy_sf, canonical) not in alias_pairs:
            raise RuntimeError(
                "governed_aliases must document NATAL_SUBFEATURE_MAPPING entries: "
                f"missing {legacy_sf!r} -> {canonical!r}"
            )

    sections: list[tuple[str, str]] = []
    for fp in root.fallback_paths:
        sections.append((fp.stable_id, "fallback_paths"))
    for ga in root.governed_aliases:
        sections.append((ga.stable_id, "governed_aliases"))
    for du in root.deprecated_use_cases:
        sections.append((du.stable_id, "deprecated_use_cases"))

    seen: dict[str, str] = {}
    for stable_id, section in sections:
        if stable_id in seen:
            raise RuntimeError(
                "stable_id doit être unique dans tout le registre legacy résiduel "
                f"(doublon {stable_id!r}: {seen[stable_id]!r} et {section!r})."
            )
        seen[stable_id] = section


def assert_deprecated_use_case_registered(use_case_key: str) -> DeprecatedUseCaseRecord:
    root = load_legacy_residual_registry()
    for rec in root.deprecated_use_cases:
        if rec.use_case_key == use_case_key:
            return rec
    raise KeyError(f"use_case_key {use_case_key!r} not in legacy residual registry")


def render_maintenance_report() -> str:
    """
    Rapport texte pour maintenance / extinction par lots (AC11).
    """
    root = load_legacy_residual_registry()
    lines: list[str] = [
        f"# Rapport registre legacy résiduel (schema_version={root.schema_version})",
        "",
        "## Chemins fallback",
    ]
    for rec in sorted(root.fallback_paths, key=lambda r: r.stable_id):
        lines.append(
            f"- `{rec.stable_id}` | type={rec.path_kind} | fallback={rec.fallback_type.value} | "
            f"statut_registre={rec.registry_status} | statut_exec={rec.fallback_status.value} | "
            f"périmètre={rec.perimeter}"
        )
    lines.extend(["", "## Aliases gouvernés"])
    for rec in sorted(root.governed_aliases, key=lambda r: r.stable_id):
        lines.append(
            f"- `{rec.stable_id}` | {rec.alias_kind} `{rec.from_value}` -> `{rec.to_value}` | "
            f"{rec.registry_status}"
        )
    lines.extend(["", "## Use cases dépréciés (bindings)"])
    for rec in sorted(root.deprecated_use_cases, key=lambda r: r.use_case_key):
        lines.append(f"- `{rec.use_case_key}` -> `{rec.stable_id}` | {rec.registry_status}")
    blocked = effective_progressive_blocklist(root=root)
    lines.extend(
        [
            "",
            "## Blocage progressif effectif",
            f"- ids: {', '.join(sorted(blocked)) or '(aucun)'}",
            "",
            "## Violations",
            "- (aucune à la génération ; exécuter les tests registre pour validation)",
        ]
    )
    return "\n".join(lines) + "\n"


def extract_doc_registry_version(doc_markdown: str) -> str | None:
    m = _SCHEMA_LINE_PATTERN.search(doc_markdown)
    return m.group(1).strip() if m else None


def validate_doc_registry_version(doc_markdown: str) -> list[str]:
    errors: list[str] = []
    expected = get_registry_schema_version()
    found = extract_doc_registry_version(doc_markdown)
    if not found:
        errors.append(
            "Documentation: ligne obligatoire manquante "
            "('- **Version registre résiduel** : `...`') pour alignement AC9/AC10."
        )
    elif found != expected:
        errors.append(
            f"Documentation: version registre résiduel doc={found!r} != code={expected!r}."
        )
    return errors
