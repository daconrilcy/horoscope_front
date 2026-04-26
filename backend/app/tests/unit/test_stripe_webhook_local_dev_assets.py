import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_PATH = REPO_ROOT / "docs" / "billing-webhook-local-testing.md"
LEGACY_DOC_PATH = REPO_ROOT / "docs" / "stripe-webhook-dev.md"
SERVICE_PATH = REPO_ROOT / "backend" / "app" / "services" / "billing" / "stripe_webhook_service.py"
POWERSHELL_SCRIPT_PATH = REPO_ROOT / "scripts" / "stripe-listen-webhook.ps1"
BASH_SCRIPT_PATH = REPO_ROOT / "scripts" / "stripe-listen-webhook.sh"

STANDARDIZED_EVENT_LIST = [
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",
    "invoice.payment_failed",
    "invoice.payment_action_required",
]
STANDARDIZED_EVENTS = set(STANDARDIZED_EVENT_LIST)

EXTENDED_EVENT_LIST = [
    "customer.updated",
    "customer.subscription.paused",
    "customer.subscription.resumed",
    "customer.subscription.trial_will_end",
]
EXTENDED_EVENTS = set(EXTENDED_EVENT_LIST)


def _extract_events(script_content: str) -> list[str]:
    match = re.search(r"--events\s+([^\r\n]+)", script_content)
    assert match is not None, "Unable to locate --events option in script"
    cleaned = match.group(1).replace("\\", "").replace("`", "").strip()
    return [event.strip() for event in cleaned.split(",")]


def _extract_markdown_events(content: str) -> set[str]:
    return set(
        re.findall(
            r"(checkout\.session\.completed|customer(?:\.subscription)?\.[a-z_]+|invoice\.[a-z_]+)",
            content,
        )
    )


def _extract_service_events(content: str) -> set[str]:
    return set(
        re.findall(
            r'"((?:checkout\.session\.completed|customer(?:\.subscription)?\.[a-z_]+|invoice\.[a-z_]+))"',
            content,
        )
    )


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


def test_listener_scripts_use_same_standardized_event_list_and_shell_script_has_no_bom() -> None:
    bash_bytes = BASH_SCRIPT_PATH.read_bytes()
    assert not bash_bytes.startswith(b"\xef\xbb\xbf")

    bash_events = _extract_events(bash_bytes.decode("utf-8"))
    powershell_events = _extract_events(POWERSHELL_SCRIPT_PATH.read_text(encoding="utf-8"))

    assert bash_events == powershell_events
    assert bash_events == STANDARDIZED_EVENT_LIST


def test_docs_are_aligned_with_supported_backend_webhook_perimeter() -> None:
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    legacy_doc = LEGACY_DOC_PATH.read_text(encoding="utf-8")
    service_content = SERVICE_PATH.read_text(encoding="utf-8")

    service_events = _extract_service_events(service_content)
    runbook_events = _extract_markdown_events(runbook)
    legacy_events = _extract_markdown_events(legacy_doc)

    assert STANDARDIZED_EVENTS.issubset(service_events)
    assert EXTENDED_EVENTS.issubset(service_events)

    assert STANDARDIZED_EVENTS.issubset(runbook_events)
    assert EXTENDED_EVENTS.issubset(runbook_events)

    assert "runbook canonique" in runbook
    assert "rationale historique" in legacy_doc
    assert "runbook canonique" in legacy_doc
    assert "sous-ensemble standardisé" in legacy_doc
    assert "périmètre backend élargi" in legacy_doc
    assert EXTENDED_EVENTS.issubset(legacy_events)

    assert "| `customer.subscription.trial_will_end` | ❌ Non traité |" not in legacy_doc, (
        "Legacy documentation must not mark a handled event as non traité"
    )
