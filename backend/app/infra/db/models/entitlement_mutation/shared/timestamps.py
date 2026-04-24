# Horloge partagée du sous-domaine entitlement mutation.
"""Centralise les helpers de timestamp du sous-domaine en s'appuyant sur `datetime_provider`."""

from __future__ import annotations

from datetime import datetime

from app.core.datetime_provider import datetime_provider


def now_utc() -> datetime:
    """Retourne l'instant UTC courant via le provider backend canonique."""

    return datetime_provider.utcnow()
