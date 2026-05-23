"""Resolve a local guardrail subset from the global CONDAMAD registry.

The registry is global, but story execution is local. This helper selects a
short, deterministic subset from a story scope so agents do not print or reason
over the full guardrail registry during story writing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


GuardrailRows = dict[str, dict[str, str]]

UNIVERSAL_IDS = ("RG-047", "RG-052")


def parse_guardrail_rows(text: str) -> GuardrailRows:
    rows: GuardrailRows = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("| RG-"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        guardrail_id, source, surface, invariant, guard = cells[:5]
        rows[guardrail_id] = {
            "source": source,
            "surface": surface,
            "invariant": invariant,
            "guard": guard,
        }
    return rows


def normalize_scope(values: list[str]) -> str:
    return " ".join(values).lower()


def select_guardrail_ids(scope_text: str, rows: GuardrailRows) -> dict[str, list[str]]:
    selected = {
        "universal": [
            guardrail_id for guardrail_id in UNIVERSAL_IDS if guardrail_id in rows
        ],
        "applicable": [],
        "needs_investigation": [],
        "non_applicable_examples": [],
    }

    def add_applicable(guardrail_id: str) -> None:
        if guardrail_id in rows and guardrail_id not in selected["applicable"]:
            selected["applicable"].append(guardrail_id)

    backend = any(token in scope_text for token in ("backend", "python", "fastapi"))
    api = any(
        token in scope_text for token in ("api", "route", "http", "openapi", "endpoint")
    )
    tests = any(token in scope_text for token in ("test", "pytest", "backend/tests"))
    health = any(token in scope_text for token in ("/health", "health"))
    frontend = any(
        token in scope_text for token in ("frontend", "react", "vite", "tsx")
    )
    auth = any(token in scope_text for token in ("auth", "protected", "permission"))

    if backend:
        add_applicable("RG-002")
    if backend and api:
        add_applicable("RG-003")
    if api or "openapi" in scope_text:
        add_applicable("RG-007")
    if backend and tests:
        add_applicable("RG-022")
    if health:
        add_applicable("RG-053")

    if frontend:
        add_applicable("RG-027")
        add_applicable("RG-041")
        add_applicable("RG-042")
    elif "RG-041" in rows:
        selected["non_applicable_examples"].append("RG-041")

    if auth:
        add_applicable("RG-020")
    elif health and "RG-020" in rows:
        selected["non_applicable_examples"].append("RG-020")

    for guardrail_id in selected["universal"]:
        if guardrail_id in selected["applicable"]:
            selected["applicable"].remove(guardrail_id)

    return selected


def reason_for(guardrail_id: str, bucket: str, scope_text: str) -> str:
    if bucket == "universal":
        return "universal local validation/no-legacy guardrail"
    if bucket == "non_applicable_examples" and guardrail_id == "RG-020":
        return "auth is not in scope for the public health route"
    if bucket == "non_applicable_examples" and guardrail_id == "RG-041":
        return "frontend build is not in scope because no frontend surface is touched"
    if guardrail_id == "RG-002":
        return "scope touches backend layout or backend app paths"
    if guardrail_id == "RG-003":
        return "scope touches backend API routing boundary"
    if guardrail_id == "RG-007":
        return "scope touches API/OpenAPI contract behavior"
    if guardrail_id == "RG-022":
        return "scope includes backend tests"
    if guardrail_id == "RG-053":
        return "scope touches GET /health"
    if guardrail_id == "RG-020":
        return "scope touches protected/auth route behavior"
    if guardrail_id in {"RG-027", "RG-041", "RG-042"}:
        return "scope touches frontend surfaces"
    return f"matched scope: {scope_text[:80]}"


def format_selection(
    selection: dict[str, list[str]], rows: GuardrailRows, scope_text: str
) -> str:
    lines = ["# Guardrail Selection", ""]
    for bucket in (
        "universal",
        "applicable",
        "needs_investigation",
        "non_applicable_examples",
    ):
        lines.append(f"## {bucket.replace('_', ' ').title()}")
        ids = selection[bucket]
        if not ids:
            lines.append("- none")
        for guardrail_id in ids:
            surface = rows.get(guardrail_id, {}).get("surface", "unknown surface")
            reason = reason_for(guardrail_id, bucket, scope_text)
            lines.append(f"- `{guardrail_id}` - {surface}; {reason}.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve applicable CONDAMAD guardrails."
    )
    parser.add_argument(
        "--registry",
        default="_condamad/stories/regression-guardrails.md",
        help="Path to regression-guardrails.md.",
    )
    parser.add_argument(
        "--operation", action="append", default=[], help="Story operation type."
    )
    parser.add_argument("--domain", action="append", default=[], help="Story domain.")
    parser.add_argument(
        "--path", action="append", default=[], help="Route, file, or directory path."
    )
    parser.add_argument(
        "--contract", action="append", default=[], help="Contract type."
    )
    parser.add_argument(
        "--forbidden",
        action="append",
        default=[],
        help="Forbidden/out-of-scope surface.",
    )
    parser.add_argument(
        "--ids-only",
        action="store_true",
        help="Print only selected guardrail IDs, one per line.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"Guardrail registry not found: {registry_path}", file=sys.stderr)
        return 1

    rows = parse_guardrail_rows(registry_path.read_text(encoding="utf-8"))
    scope_values = args.operation + args.domain + args.path + args.contract
    scope_text = normalize_scope(scope_values)
    selection = select_guardrail_ids(scope_text, rows)

    selected_ids = []
    for bucket in ("universal", "applicable", "needs_investigation"):
        selected_ids.extend(selection[bucket])

    if args.ids_only:
        print("\n".join(selected_ids))
    else:
        print(format_selection(selection, rows, scope_text), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
