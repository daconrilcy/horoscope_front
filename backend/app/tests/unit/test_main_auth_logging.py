# Commentaire global: couvre les diagnostics d'authentification sans fuite de secret.
"""Tests des helpers de journalisation d'authentification."""

from __future__ import annotations

from app.main import _classify_authorization_header


def test_classify_authorization_header_never_returns_token_value() -> None:
    """Classe le header Authorization sans exposer le bearer token."""
    assert _classify_authorization_header(None) == "missing"
    assert _classify_authorization_header("") == "blank"
    assert _classify_authorization_header("Basic abc") == "non_bearer_present"
    assert _classify_authorization_header("Bearer ") == "bearer_empty"
    assert _classify_authorization_header("Bearer secret-token-value") == "bearer_present"
