# Commentaire global: ce module porte le contrat interne du graphe factuel natal Basic.
"""Contrats immuables du graphe de faits natals Basic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class NatalFactFamily(StrEnum):
    """Familles factuelles minimales exposees par le graphe natal Basic."""

    LUMINARY = "luminary_fact"
    ANGLE = "angle_fact"
    PLANET_POSITION = "planet_position_fact"
    HOUSE_EMPHASIS = "house_emphasis_fact"
    SIGN_EMPHASIS = "sign_emphasis_fact"
    ELEMENT_BALANCE = "element_balance_fact"
    MODALITY_BALANCE = "modality_balance_fact"
    ASPECT = "aspect_fact"
    RULERSHIP = "rulership_fact"
    CONDITION = "condition_fact"
    NODE = "node_fact"


@dataclass(frozen=True, slots=True)
class NatalFact:
    """Fait atomique interne avec provenance runtime et statut editorial separe."""

    fact_id: str
    family: NatalFactFamily
    objects: tuple[str, ...]
    confidence: str
    requires_birth_time: bool
    source_paths: tuple[str, ...]
    editorial_candidate: bool

    def __post_init__(self) -> None:
        """Valide qu'un fait reste atomique, source et deterministe."""
        if not self.fact_id.strip():
            raise ValueError("natal fact requires fact_id")
        if any(not item.strip() for item in self.objects):
            raise ValueError("natal fact rejects empty object references")
        if not self.confidence.strip():
            raise ValueError("natal fact requires confidence")
        if not self.source_paths or any(not item.strip() for item in self.source_paths):
            raise ValueError("natal fact requires source paths")

    def to_internal_payload(self) -> dict[str, Any]:
        """Retourne la forme auditable avec chemins de source internes."""
        return {
            "fact_id": self.fact_id,
            "family": self.family.value,
            "objects": list(self.objects),
            "confidence": self.confidence,
            "requires_birth_time": self.requires_birth_time,
            "source_paths": list(self.source_paths),
            "editorial_candidate": self.editorial_candidate,
        }

    def to_editorial_candidate_payload(self) -> dict[str, Any]:
        """Projette un candidat aval sans chemins de source internes."""
        return {
            "fact_id": self.fact_id,
            "family": self.family.value,
            "objects": list(self.objects),
            "confidence": self.confidence,
            "requires_birth_time": self.requires_birth_time,
        }


@dataclass(frozen=True, slots=True)
class NatalFactGraph:
    """Graphe deterministe de faits internes issus des projections runtime."""

    graph_id: str
    facts: tuple[NatalFact, ...]

    def __post_init__(self) -> None:
        """Garantit l'unicite stable des identifiants de faits."""
        if not self.graph_id.strip():
            raise ValueError("natal fact graph requires graph_id")
        fact_ids = [fact.fact_id for fact in self.facts]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("natal fact graph rejects duplicate fact ids")

    @property
    def editorial_candidates(self) -> tuple[NatalFact, ...]:
        """Retourne uniquement les faits eligibles a la selection editoriale aval."""
        return tuple(fact for fact in self.facts if fact.editorial_candidate)

    def to_internal_payload(self) -> dict[str, Any]:
        """Retourne la forme interne complete du graphe factuel."""
        return {
            "graph_id": self.graph_id,
            "facts": [fact.to_internal_payload() for fact in self.facts],
        }

    def to_editorial_candidate_payload(self) -> dict[str, Any]:
        """Retourne une forme aval sans fuite des chemins de source internes."""
        return {
            "graph_id": self.graph_id,
            "facts": [fact.to_editorial_candidate_payload() for fact in self.editorial_candidates],
        }
