"""Centralise le cache process-local des statuts d abonnement."""

from __future__ import annotations

from threading import Lock
from time import monotonic

from app.core.config import settings
from app.services.billing.models import SubscriptionStatusData

MAX_SUBSCRIPTION_CACHE_ENTRIES = 10_000
SUBSCRIPTION_STATUS_CACHE: dict[int, tuple[float, SubscriptionStatusData]] = {}
SUBSCRIPTION_STATUS_CACHE_LOCK = Lock()


def subscription_cache_ttl_seconds() -> float:
    """Retourne la duree de vie du cache d abonnement."""
    return max(0.0, settings.billing_subscription_cache_ttl_seconds)


def get_cached_subscription_status(user_id: int) -> SubscriptionStatusData | None:
    """Retourne un statut d abonnement depuis le cache quand il est encore valide."""
    ttl = subscription_cache_ttl_seconds()
    if ttl <= 0:
        return None

    now = monotonic()
    with SUBSCRIPTION_STATUS_CACHE_LOCK:
        prune_subscription_cache_locked(now)
        cached = SUBSCRIPTION_STATUS_CACHE.get(user_id)
        if cached is None:
            return None
        expires_at, payload = cached
        if now >= expires_at:
            SUBSCRIPTION_STATUS_CACHE.pop(user_id, None)
            return None
        return payload.model_copy(deep=True)


def set_cached_subscription_status(user_id: int, payload: SubscriptionStatusData) -> None:
    """Met en cache le statut d abonnement d un utilisateur."""
    ttl = subscription_cache_ttl_seconds()
    if ttl <= 0:
        return

    now = monotonic()
    with SUBSCRIPTION_STATUS_CACHE_LOCK:
        prune_subscription_cache_locked(now)
        SUBSCRIPTION_STATUS_CACHE[user_id] = (now + ttl, payload.model_copy(deep=True))
        while len(SUBSCRIPTION_STATUS_CACHE) > MAX_SUBSCRIPTION_CACHE_ENTRIES:
            SUBSCRIPTION_STATUS_CACHE.pop(next(iter(SUBSCRIPTION_STATUS_CACHE)))


def prune_subscription_cache_locked(now: float) -> None:
    """Supprime les entrees expirees du cache sous verrou."""
    expired_keys = [
        user_id
        for user_id, (expires_at, _) in SUBSCRIPTION_STATUS_CACHE.items()
        if now >= expires_at
    ]
    for user_id in expired_keys:
        SUBSCRIPTION_STATUS_CACHE.pop(user_id, None)


def invalidate_cached_subscription_status(user_id: int) -> None:
    """Invalide le cache d abonnement d un utilisateur donne."""
    with SUBSCRIPTION_STATUS_CACHE_LOCK:
        SUBSCRIPTION_STATUS_CACHE.pop(user_id, None)


def reset_subscription_status_cache() -> None:
    """Vide completement le cache des statuts d abonnement."""
    with SUBSCRIPTION_STATUS_CACHE_LOCK:
        SUBSCRIPTION_STATUS_CACHE.clear()
