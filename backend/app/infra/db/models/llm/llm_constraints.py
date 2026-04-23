# Contraintes SQL partagees par les modeles LLM.
"""Centralise les contraintes simples de domaines finis pour les tables LLM."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import CheckConstraint


def allowed_values_check(name: str, column_name: str, values: Iterable[str]) -> CheckConstraint:
    """Construit une contrainte CHECK pour un champ texte a valeurs fermees."""
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return CheckConstraint(f"{column_name} IN ({quoted_values})", name=name)
