# Garde des assets locaux de validation du webhook Stripe.
"""Verifie que le listener Stripe local reste PowerShell-only et dev-only."""

from __future__ import annotations

import inspect
import re
from pathlib import Path

from app.services.billing.stripe_webhook_events import (
    LOCAL_LISTENER_EVENT_TYPES,
    SUPPORTED_WEBHOOK_EVENT_TYPES,
)
from app.services.billing.stripe_webhook_service import StripeWebhookService

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_PATH = REPO_ROOT / "docs" / "billing-webhook-local-testing.md"
LEGACY_DOC_PATH = REPO_ROOT / "docs" / "stripe-webhook-dev.md"
POWERSHELL_SCRIPT_PATH = REPO_ROOT / "scripts" / "stripe-listen-webhook.ps1"

SUPPORTED_EVENTS = set(SUPPORTED_WEBHOOK_EVENT_TYPES)
UNSUPPORTED_DOCUMENTED_EVENT_TYPES = {"invoice.payment_succeeded"}


def _extract_events(script_content: str) -> list[str]:
    match = re.search(r"--events\s+([^\r\n]+)", script_content)
    assert match is not None, "Unable to locate --events option in script"
    cleaned = match.group(1).replace("\\", "").replace("`", "").strip()
    return [event.strip() for event in cleaned.split(",")]


def _extract_markdown_events(content: str) -> set[str]:
    return set(
        re.findall(
            r"("
            r"checkout\.session\.[a-z_]+"
            r"|customer(?:\.subscription)?\.[a-z_]+"
            r"|subscription_schedule\.[a-z_]+"
            r"|invoice\.[a-z_]+"
            r")",
            content,
        )
    )


def _extract_markdown_event_statuses(content: str) -> dict[str, str]:
    """Extrait le statut de traitement annonce dans les tableaux Markdown."""
    return {
        event_type: status.strip()
        for event_type, status in re.findall(
            r"^\|\s+`([^`]+)`\s+\|\s+([^|]+?)\s+\|",
            content,
            flags=re.MULTILINE,
        )
    }


def test_runbook_covers_required_local_webhook_validation_steps() -> None:
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

    required_snippets = [
        "runbook canonique local",
        "stripe login",
        "stripe listen --forward-to http://localhost:8001/v1/billing/stripe-webhook",
        "--load-from-webhooks-api",
        ".env.local",
        "Le secret de développement local vient explicitement de `stripe listen`.",
        "Résultat attendu : rejet HTTP 400 avec le code `invalid_signature`.",
        "Résultat attendu : l'événement est accepté et retourne un statut HTTP 200",
        "stripe events resend evt_123456 --webhook-endpoint=we_123456",
        "`duplicate_ignored`",
    ]

    for snippet in required_snippets:
        assert snippet in runbook


def test_powershell_listener_uses_standardized_event_list_and_target() -> None:
    """Le script PowerShell reste l'unique listener local canonique."""
    powershell_content = POWERSHELL_SCRIPT_PATH.read_text(encoding="utf-8")
    powershell_events = _extract_events(POWERSHELL_SCRIPT_PATH.read_text(encoding="utf-8"))

    assert "--forward-to http://localhost:8001/v1/billing/stripe-webhook" in powershell_content
    assert powershell_events == list(LOCAL_LISTENER_EVENT_TYPES)


def test_bash_listener_is_not_supported_as_local_dev_asset() -> None:
    """Bloque la reintroduction du listener Bash Stripe local."""
    bash_script_path = REPO_ROOT / "scripts" / ("stripe-listen-webhook" + ".sh")

    assert not bash_script_path.exists()


def test_runbook_does_not_expose_bash_or_wsl_listener_support() -> None:
    """La documentation active doit rester limitee a Windows / PowerShell."""
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

    forbidden_snippets = [
        "stripe-listen-webhook" + ".sh",
        "Git " + "Bash",
        "W" + "SL",
        "```bash",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in runbook

    assert "Windows / PowerShell" in runbook
    assert "outil de développement local" in runbook
    assert "surface CI, production ou déploiement" in runbook


def test_docs_are_aligned_with_supported_backend_webhook_perimeter() -> None:
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    legacy_doc = LEGACY_DOC_PATH.read_text(encoding="utf-8")

    runbook_events = _extract_markdown_events(runbook)
    legacy_events = _extract_markdown_events(legacy_doc)
    legacy_statuses = _extract_markdown_event_statuses(legacy_doc)

    assert SUPPORTED_EVENTS.issubset(runbook_events)
    assert SUPPORTED_EVENTS.issubset(legacy_events)
    assert SUPPORTED_EVENTS.issubset(legacy_statuses)

    assert "runbook canonique" in runbook
    assert "rationale historique" in legacy_doc
    assert "runbook canonique" in legacy_doc
    assert "sous-ensemble standardisé" in legacy_doc
    assert "périmètre backend élargi" in legacy_doc

    assert "| `customer.subscription.trial_will_end` | ❌ Non traité |" not in legacy_doc, (
        "Legacy documentation must not mark a handled event as non traité"
    )
    for event_type in SUPPORTED_EVENTS:
        assert legacy_statuses[event_type].startswith("✅"), (
            f"{event_type} must be documented as supported"
        )
    for event_type in UNSUPPORTED_DOCUMENTED_EVENT_TYPES:
        assert event_type not in runbook_events
        assert not legacy_statuses[event_type].startswith("✅")
    assert "`invoice.payment_succeeded` | ❌ Remplacé" in legacy_doc
    assert "Désormais traité comme `event_ignored`" in legacy_doc


def test_runtime_dispatch_and_resolver_use_canonical_registry() -> None:
    """Bloque le retour de listes locales concurrentes dans le service runtime."""
    handle_source = inspect.getsource(StripeWebhookService.handle_event)
    resolver_source = inspect.getsource(StripeWebhookService._resolve_user_id)

    assert "is_supported_webhook_event(event_type)" in handle_source
    assert "CHECKOUT_UPGRADE_EVENT_TYPES" in handle_source
    assert "CHECKOUT_CLIENT_REFERENCE_EVENT_TYPES" in resolver_source
    assert "CUSTOMER_LOOKUP_EVENT_TYPES" in resolver_source
    assert "CUSTOMER_OBJECT_ID_LOOKUP_EVENT_TYPES" in resolver_source

    forbidden_events = [
        "checkout.session.async_payment_succeeded",
        "subscription_schedule.created",
    ]
    for event_type in forbidden_events:
        assert event_type not in handle_source
        assert event_type not in resolver_source
