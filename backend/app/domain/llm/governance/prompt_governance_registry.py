"""
Registre central versionné — taxonomie canonique, aliases et placeholders (Story 66.42).

Source de vérité exécutable : `data/prompt_governance_registry.json`.
Toute évolution volontaire passe par ce fichier et les validations associées.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.llm.prompting.placeholder_policy import PlaceholderDef

logger = logging.getLogger(__name__)

_DATA_FILE: Final[Path] = (
    Path(__file__).resolve().parent / "data" / "prompt_governance_registry.json"
)

NATAL_CANONICAL_FEATURE: Final[str] = "natal"
LEGACY_NATAL_FEATURE: Final[str] = "natal_interpretation"
LEGACY_DAILY_FEATURE: Final[str] = "daily_prediction"
SUPPORTED_EXCEPTION_RULE_IDS: Final[frozenset[str]] = frozenset(
    {
        "GOV_PH_NOT_IN_REGISTRY",
        "GOV_PH_FAMILY_UNKNOWN",
    }
)


class UseCaseDeprecationTarget(BaseModel):
    feature: str
    subfeature: str
    plan: str


class PlaceholderEntry(BaseModel):
    name: str
    classification: Literal["required", "optional", "optional_with_fallback"]
    fallback: str | None = None


class GovernedExceptionEntry(BaseModel):
    """Exception taxonomique ou placeholder : métadonnées obligatoires (AC5)."""

    id: str
    owner: str = Field(min_length=1)
    justification: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    status: Literal["active", "revoked"]
    review_by: str = Field(min_length=1)


def _parse_scope_tokens(scope: str) -> dict[str, str]:
    """
    Strict parser for governed exception scope:
    - keys allowed: placeholder, family, rule
    - format: key:value;key:value
    """
    allowed_keys = {"placeholder", "family", "rule"}
    tokens: dict[str, str] = {}
    for raw in scope.split(";"):
        chunk = raw.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise ValueError(f"Invalid exception scope token (missing ':'): '{chunk}'")
        k, v = chunk.split(":", 1)
        key = k.strip().lower()
        val = v.strip()
        if key not in allowed_keys:
            raise ValueError(
                f"Unknown exception scope key '{key}' (allowed: {sorted(allowed_keys)})"
            )
        if not val:
            raise ValueError(f"Empty value for exception scope key '{key}'")
        if key in tokens:
            raise ValueError(f"Duplicate exception scope key '{key}'")
        tokens[key] = val
    return tokens


class PromptGovernanceRegistryData(BaseModel):
    schema_version: str
    canonical_families: list[str]
    universal_placeholders: list[str]
    legacy_nominal_feature_aliases: dict[str, str]
    legacy_subfeature_aliases_by_domain: dict[str, dict[str, str]]
    natal_subfeatures_canonical: list[str]
    deprecated_use_case_mapping: dict[str, UseCaseDeprecationTarget]
    placeholders_by_family: dict[str, list[PlaceholderEntry]]
    governed_exceptions: list[GovernedExceptionEntry]

    @model_validator(mode="after")
    def validate_governed_exception_scopes(self) -> "PromptGovernanceRegistryData":
        """
        Fail-closed: malformed scope => invalid registry at load time.
        Required scope keys: placeholder + family.
        """
        canonical_families = set(self.canonical_families)
        aliases = dict(self.legacy_nominal_feature_aliases)
        for exc in self.governed_exceptions:
            tokens = _parse_scope_tokens(exc.scope)
            if "placeholder" not in tokens:
                raise ValueError(
                    f"Governed exception '{exc.id}' missing required scope key 'placeholder'"
                )
            if "family" not in tokens:
                raise ValueError(
                    f"Governed exception '{exc.id}' missing required scope key 'family'"
                )

            raw_family = tokens["family"]
            normalized_family = aliases.get(raw_family, raw_family)
            if normalized_family not in canonical_families:
                raise ValueError(
                    f"Governed exception '{exc.id}' has non-canonical family '{raw_family}' "
                    f"(resolved: '{normalized_family}')"
                )

            if "rule" in tokens and not tokens["rule"].strip():
                raise ValueError(f"Governed exception '{exc.id}' has empty rule in scope")
            if "rule" in tokens:
                normalized_rule = tokens["rule"].strip().upper()
                if normalized_rule not in SUPPORTED_EXCEPTION_RULE_IDS:
                    raise ValueError(
                        f"Governed exception '{exc.id}' has unsupported rule '{tokens['rule']}' "
                        f"(allowed: {sorted(SUPPORTED_EXCEPTION_RULE_IDS)})"
                    )

        return self


@dataclass(frozen=True)
class PlaceholderGovernanceViolation:
    """Rapport structuré pour AC7 (placeholder non gouverné)."""

    rule_id: str
    placeholder: str
    family_key_resolved: str
    message: str
    source: str
    exception_id: str | None = None


class PromptGovernanceRegistry:
    """Facade chargée depuis le JSON — point d’accès runtime unique."""

    def __init__(self, data: PromptGovernanceRegistryData) -> None:
        self._data = data
        self.canonical_families: frozenset[str] = frozenset(data.canonical_families)
        self.universal_placeholders: frozenset[str] = frozenset(data.universal_placeholders)
        self._placeholder_defs_by_family: dict[str, list[PlaceholderDef]] = {
            fam: [
                PlaceholderDef(
                    name=p.name,
                    classification=p.classification,
                    fallback=p.fallback,
                )
                for p in defs
            ]
            for fam, defs in data.placeholders_by_family.items()
        }

    @classmethod
    def load(cls, path: Path | None = None) -> PromptGovernanceRegistry:
        p = path or _DATA_FILE
        raw = json.loads(p.read_text(encoding="utf-8"))
        data = PromptGovernanceRegistryData.model_validate(raw)
        reg = cls(data)
        logger.info(
            "prompt_governance_registry_loaded schema=%s families=%s",
            data.schema_version,
            sorted(data.canonical_families),
        )
        return reg

    def normalize_feature(self, feature: str) -> str:
        if not feature:
            return feature
        s = feature.strip()
        mapped = self._data.legacy_nominal_feature_aliases.get(s)
        if mapped:
            return mapped
        return s

    def normalize_subfeature(self, feature: str, subfeature: str | None) -> str | None:
        if subfeature is None:
            return None
        fn = self.normalize_feature(feature)
        domain_map = self._data.legacy_subfeature_aliases_by_domain.get(fn, {})
        return domain_map.get(subfeature, subfeature)

    def resolve_placeholder_family(self, feature: str) -> str:
        """
        Résout la clé de famille pour les placeholders (corrige horoscope_daily vs split abusif).
        """
        if not feature:
            return "unknown"
        f = self.normalize_feature(feature.strip())
        if f in self.canonical_families:
            return f
        if "_" in f:
            head = f.split("_", 1)[0]
            if head in self.canonical_families:
                return head
        return f

    def get_placeholder_defs(self, feature: str) -> list[PlaceholderDef]:
        key = self.resolve_placeholder_family(feature)
        return list(self._placeholder_defs_by_family.get(key, []))

    def natal_subfeatures_canonical_list(self) -> list[str]:
        return list(self._data.natal_subfeatures_canonical)

    def natal_subfeature_legacy_mapping(self) -> dict[str, str]:
        return dict(self._data.legacy_subfeature_aliases_by_domain.get(NATAL_CANONICAL_FEATURE, {}))

    def legacy_nominal_feature_aliases_map(self) -> dict[str, str]:
        return dict(self._data.legacy_nominal_feature_aliases)

    def _find_active_exception_for_placeholder(
        self, *, placeholder: str, family_key: str, rule_id: str
    ) -> GovernedExceptionEntry | None:
        """
        Best-effort matching via `scope` tokenized grammar:
        - "placeholder:<name>"
        - "family:<family>"
        - "rule:<rule_id>"
        Tokens are separated by ';'. Missing token = wildcard.
        """
        for exc in self._data.governed_exceptions:
            if exc.status != "active":
                continue
            tokens = _parse_scope_tokens(exc.scope)

            family_scope = tokens.get("family")
            if family_scope:
                family_scope = self.normalize_feature(family_scope)

            rule_scope = tokens.get("rule")
            if rule_scope:
                rule_scope = rule_scope.upper()

            if tokens.get("placeholder") and tokens["placeholder"] != placeholder:
                continue
            if family_scope and family_scope != family_key:
                continue
            if rule_scope and rule_scope != rule_id.upper():
                continue
            return exc
        return None

    def is_placeholder_governed_for_feature(
        self,
        *,
        placeholder: str,
        feature: str,
        rule_id: str = "GOV_PH_NOT_IN_REGISTRY",
    ) -> tuple[bool, str | None]:
        """
        Runtime-safe check used by PromptRenderer to keep publish/runtime aligned.
        Returns (is_allowed, exception_id_if_any).
        """
        family_key = self.resolve_placeholder_family(feature)
        allowed_names = {d.name for d in self.get_placeholder_defs(feature)}
        if placeholder in allowed_names or placeholder in self.universal_placeholders:
            return True, None

        exc = self._find_active_exception_for_placeholder(
            placeholder=placeholder,
            family_key=family_key,
            rule_id=rule_id,
        )
        if exc is not None:
            return True, exc.id
        return False, None

    def validate_placeholders_in_template(
        self, template: str, feature: str, *, source: str = "template"
    ) -> tuple[list[str], list[PlaceholderGovernanceViolation]]:
        """
        Valide les placeholders d’un template contre le registre central (AC2, AC4, AC7).
        Retourne (liste noms non autorisés, violations détaillées).
        """
        found = _extract_placeholders(template)
        family_key = self.resolve_placeholder_family(feature)
        violations: list[PlaceholderGovernanceViolation] = []
        invalid_names: list[str] = []

        if family_key not in self.canonical_families and family_key != "unknown":
            for p in found:
                if p in self.universal_placeholders:
                    continue
                rule_id = "GOV_PH_FAMILY_UNKNOWN"
                msg = (
                    f"Famille '{feature}' (résolu: '{family_key}') hors périmètre canonique "
                    f"({sorted(self.canonical_families)})."
                )
                violations.append(
                    PlaceholderGovernanceViolation(
                        rule_id=rule_id,
                        placeholder=p,
                        family_key_resolved=family_key,
                        message=msg,
                        source=source,
                    )
                )
                invalid_names.append(p)
            return invalid_names, violations

        for p in found:
            rule_id = "GOV_PH_NOT_IN_REGISTRY"
            is_allowed, exception_id = self.is_placeholder_governed_for_feature(
                placeholder=p,
                feature=feature,
                rule_id=rule_id,
            )
            if is_allowed:
                if exception_id:
                    logger.warning(
                        (
                            "prompt_governance_exception_applied "
                            "id=%s placeholder=%s family=%s source=%s"
                        ),
                        exception_id,
                        p,
                        family_key,
                        source,
                    )
                continue
            msg = (
                f"Placeholder '{{{{{p}}}}}' non enregistré pour la famille '{family_key}'. "
                f"Ajoutez-le au registre central (placeholders_by_family.{family_key}) "
                f"ou utilisez un placeholder universel autorisé."
            )
            violations.append(
                PlaceholderGovernanceViolation(
                    rule_id=rule_id,
                    placeholder=p,
                    family_key_resolved=family_key,
                    message=msg,
                    source=source,
                )
            )
            invalid_names.append(p)

        return invalid_names, violations


def _extract_placeholders(template: str) -> list[str]:
    if not template:
        return []
    matches = re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template)
    return list(dict.fromkeys(matches))


@lru_cache(maxsize=1)
def get_prompt_governance_registry() -> PromptGovernanceRegistry:
    return PromptGovernanceRegistry.load()


def format_placeholder_violation_report(violations: list[PlaceholderGovernanceViolation]) -> str:
    lines = []
    for v in violations:
        lines.append(
            f"[{v.rule_id}] placeholder={v.placeholder} family={v.family_key_resolved} "
            f"source={v.source} — {v.message}"
        )
    return "\n".join(lines)


def get_deprecated_use_case_mapping() -> dict[str, dict[str, str]]:
    reg = get_prompt_governance_registry()
    return {k: v.model_dump() for k, v in reg._data.deprecated_use_case_mapping.items()}


DEPRECATED_USE_CASE_MAPPING: dict[str, dict[str, str]] = {}
PLACEHOLDER_ALLOWLIST: dict[str, list[PlaceholderDef]] = {}


def _sync_derived_exports() -> None:
    global DEPRECATED_USE_CASE_MAPPING, PLACEHOLDER_ALLOWLIST
    reg = get_prompt_governance_registry()
    DEPRECATED_USE_CASE_MAPPING = {
        k: v.model_dump() for k, v in reg._data.deprecated_use_case_mapping.items()
    }
    PLACEHOLDER_ALLOWLIST = {
        fam: list(defs) for fam, defs in reg._placeholder_defs_by_family.items()
    }


_sync_derived_exports()
