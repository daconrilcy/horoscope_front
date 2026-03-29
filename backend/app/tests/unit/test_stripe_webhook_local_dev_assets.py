import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RUNBOOK_PATH = REPO_ROOT / "docs" / "billing-webhook-local-testing.md"
POWERSHELL_SCRIPT_PATH = REPO_ROOT / "scripts" / "stripe-listen-webhook.ps1"
BASH_SCRIPT_PATH = REPO_ROOT / "scripts" / "stripe-listen-webhook.sh"


def _extract_events(script_content: str) -> list[str]:
    match = re.search(r"--events\s+([^\r\n]+)", script_content)
    assert match is not None, "Unable to locate --events option in script"
    cleaned = match.group(1).replace("\\", "").replace("`", "").strip()
    return [event.strip() for event in cleaned.split(",")]


def test_runbook_covers_required_local_webhook_validation_steps() -> None:
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

    required_snippets = [
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
    assert bash_events == [
        "checkout.session.completed",
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.paid",
        "invoice.payment_failed",
        "invoice.payment_action_required",
    ]
