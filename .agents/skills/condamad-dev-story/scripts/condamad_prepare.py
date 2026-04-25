#!/usr/bin/env python3
"""Genere une capsule de story CONDAMAD depuis un fichier markdown.

Ce helper reste volontairement sans dependance. Il cree la structure canonique
utilisee par le skill `condamad-dev-story` et ecrit des fichiers de depart
conservateurs que Codex doit affiner avant implementation.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_GENERATED = [
    "01-execution-brief.md",
    "03-acceptance-traceability.md",
    "04-target-files.md",
    "06-validation-plan.md",
    "07-no-legacy-dry-guardrails.md",
    "10-final-evidence.md",
]

OPTIONAL_GENERATED = [
    "05-implementation-plan.md",
    "09-dev-log.md",
]

HEADING_RE = re.compile(r"^#{1,6}\s+")
AC_HEADING_RE = re.compile(r"acceptance criteria|crit[eè]res d.?acceptation|ac\b", re.I)
AC_LABEL_RE = re.compile(r"^(AC\s*\d+)\s*[:.-]\s*(.*)$", re.I)
LIST_MARKER_RE = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+)")


def slugify(value: str) -> str:
    """Convertit une valeur libre en cle de chemin stable."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or datetime.now(timezone.utc).strftime("%Y-%m-%d-generated-story")


def infer_story_key(story_path: Path, story_text: str, explicit: str | None) -> str:
    """Deduit une cle de story depuis l'option CLI, le fichier ou le titre."""
    if explicit:
        return slugify(explicit)
    if story_path.name:
        stem = story_path.stem
        if stem and stem.lower() not in {"story", "00-story"}:
            return slugify(stem)
    title = next(
        (
            line.lstrip("# ").strip()
            for line in story_text.splitlines()
            if line.lstrip().startswith("#")
        ),
        "",
    )
    return slugify(title)


def strip_list_marker(value: str) -> str:
    """Retire un marqueur de liste markdown sans toucher au texte metier."""
    value = re.sub(r"^\s*[-*]\s+", "", value)
    return re.sub(r"^\s*\d+[.)]\s+", "", value)


def collect_acceptance_candidates(story_text: str) -> list[str]:
    """Regroupe les criteres d'acceptation extraits de la section markdown."""
    in_ac = False
    candidates: list[str] = []
    current: list[str] = []

    def flush_current() -> None:
        if current:
            candidates.append(" ".join(current).strip())
            current.clear()

    for line in story_text.splitlines():
        stripped = line.strip()
        if HEADING_RE.match(stripped):
            flush_current()
            in_ac = bool(AC_HEADING_RE.search(stripped))
            continue
        if not in_ac or not stripped or stripped.startswith("|"):
            continue

        starts_new_criterion = bool(LIST_MARKER_RE.match(line)) or bool(
            AC_LABEL_RE.match(strip_list_marker(stripped))
        )
        if starts_new_criterion:
            flush_current()
            current.append(strip_list_marker(stripped))
        elif current:
            current.append(stripped)
        else:
            current.append(stripped)

    flush_current()
    return candidates


def normalize_acceptance_candidate(criterion: str) -> tuple[str | None, str]:
    """Normalise un critere brut en label optionnel et texte nettoye."""
    normalized = re.sub(r"\s+", " ", strip_list_marker(criterion)).strip()
    label_match = AC_LABEL_RE.match(normalized)
    if not label_match:
        return None, normalized
    label = label_match.group(1).replace(" ", "").upper()
    text = label_match.group(2).strip() or normalized
    return label, text


def next_unlabeled_ac(existing_labels: set[str]) -> str:
    """Retourne le prochain label AC non deja utilise."""
    index = 1
    while f"AC{index}" in existing_labels:
        index += 1
    return f"AC{index}"


def extract_acceptance_criteria(story_text: str) -> list[tuple[str, str]]:
    """Extrait au mieux les criteres d'acceptation depuis une story markdown.

    Le fichier de tracabilite genere reste un point de depart: Codex doit
    l'affiner apres lecture de la story et du contexte du depot.
    """
    candidates = collect_acceptance_candidates(story_text)

    for match in re.finditer(
        r"(?im)^\s*(?:[-*]\s*)?(AC\s*\d+)\s*[:.-]\s*(.+)$", story_text
    ):
        candidates.append(
            f"{match.group(1).replace(' ', '')}: {match.group(2).strip()}"
        )

    existing_labels: set[str] = set()
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for criterion in candidates:
        explicit_label, text = normalize_acceptance_candidate(criterion)
        if not text:
            continue
        label = explicit_label or next_unlabeled_ac(existing_labels)
        key = (label.lower(), re.sub(r"\s+", " ", text).casefold())
        if key in seen:
            continue
        seen.add(key)
        existing_labels.add(label)
        result.append((label, text))

    if not result:
        result.append(("AC1", "Implement the story scope as defined in 00-story.md."))
    return result


def write_if_missing(path: Path, content: str, overwrite: bool) -> None:
    """Ecrit un fichier genere sans ecraser par defaut le travail existant."""
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_execution_brief(story_key: str) -> str:
    """Rend le brief d'execution initial."""
    return f"""# Execution Brief — {story_key}

## Primary objective

Implement story `{story_key}` exactly as defined in `../00-story.md`.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.
"""


def render_traceability(criteria: list[tuple[str, str]]) -> str:
    """Rend la table de tracabilite initiale des criteres d'acceptation."""
    rows = [
        "# Acceptance Traceability",
        "",
        "| AC | Requirement | Expected code impact | Required validation evidence | Status |",
        "|---|---|---|---|---|",
    ]
    for label, text in criteria:
        rows.append(
            f"| {label} | {text.replace('|', '\\|')} | TBD after repository inspection | TBD after validation planning | PENDING |"
        )
    rows.extend(
        [
            "",
            "Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.",
        ]
    )
    return "\n".join(rows)


def render_target_files() -> str:
    """Rend les hypotheses initiales de fichiers cibles."""
    return """# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg "<main symbol or feature name>" .
rg "legacy|compat|shim|fallback|deprecated|alias" .
```

Adapt searches to the story and repository layout.

## Likely modified files

- TBD after repository inspection

## Forbidden or high-risk files

- TBD after repository inspection
"""


def render_validation_plan() -> str:
    """Rend le plan de validation initial."""
    return """# Validation Plan

## Targeted checks

```bash
# Replace with the smallest relevant test command after repository inspection.
pytest -q
```

## Architecture / negative scans

```bash
rg "legacy|compat|shim|fallback|deprecated|alias" .
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
pytest -q
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
"""


def render_guardrails() -> str:
    """Rend les garde-fous No Legacy / DRY generiques."""
    return """# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
"""


def render_final_evidence(story_key: str) -> str:
    """Rend le squelette de preuve finale."""
    return f"""# Final Evidence — {story_key}

## Story status

- Validation outcome: TBD
- Ready for review: no
- Story key: {story_key}
- Source story: `00-story.md`
- Capsule path: TBD

## Preflight

- Repository root: TBD
- Story source: `00-story.md`
- Initial `git status --short`: TBD
- Pre-existing dirty files: TBD
- AGENTS.md files considered: TBD
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | TBD | |
| `generated/01-execution-brief.md` | yes | yes | TBD | |
| `generated/03-acceptance-traceability.md` | yes | yes | TBD | |
| `generated/04-target-files.md` | yes | yes | TBD | |
| `generated/06-validation-plan.md` | yes | yes | TBD | |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | TBD | |
| `generated/10-final-evidence.md` | yes | yes | TBD | |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| TBD | TBD | TBD | PENDING | |

## Files changed

- TBD

## Files deleted

- TBD

## Tests added or updated

- TBD

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| TBD | TBD | TBD | TBD | TBD |

## Commands skipped or blocked

- TBD

## DRY / No Legacy evidence

- TBD

## Diff review

- `git diff --stat`: TBD
- `git diff --check`: TBD

## Final worktree status

- TBD

## Remaining risks

- TBD

## Suggested reviewer focus

- TBD
"""


def render_dev_log() -> str:
    """Rend le journal de developpement optionnel."""
    return """# Dev Log

## Preflight

- Initial `git status --short`:
- Current branch:
- Existing dirty files:

## Search evidence

## Implementation notes

## Commands run

| Command | Result | Notes |
|---|---|---|

## Issues encountered

## Decisions made

## Final `git status --short`
"""


def render_implementation_plan() -> str:
    """Rend le plan d'implementation optionnel."""
    return """# Implementation Plan

## Initial repository findings

- TBD

## Proposed changes

- TBD

## Files to modify

- TBD

## Files to delete

- TBD

## Tests to add or update

- TBD

## Risk assessment

- TBD

## Rollback strategy

- TBD
"""


def build_templates(
    story_key: str, criteria: list[tuple[str, str]], with_optional: bool
) -> dict[str, str]:
    """Construit les contenus generes dans l'ordre canonique."""
    templates = {
        "01-execution-brief.md": render_execution_brief(story_key),
        "03-acceptance-traceability.md": render_traceability(criteria),
        "04-target-files.md": render_target_files(),
        "06-validation-plan.md": render_validation_plan(),
        "07-no-legacy-dry-guardrails.md": render_guardrails(),
        "10-final-evidence.md": render_final_evidence(story_key),
    }
    if with_optional:
        templates.update(
            {
                "05-implementation-plan.md": render_implementation_plan(),
                "09-dev-log.md": render_dev_log(),
            }
        )
    return templates


def main() -> int:
    """Execute la generation de capsule depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Generate a CONDAMAD story capsule.")
    parser.add_argument(
        "story", type=Path, help="Path to the source story markdown file."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--story-key", help="Explicit story key. Defaults to story filename or title."
    )
    parser.add_argument(
        "--capsules-dir",
        type=Path,
        default=Path("_condamad/stories"),
        help="Capsule base directory relative to root unless absolute.",
    )
    parser.add_argument(
        "--overwrite-generated",
        action="store_true",
        help="Overwrite existing generated files.",
    )
    parser.add_argument(
        "--overwrite-story",
        action="store_true",
        help="Overwrite an existing 00-story.md when it differs from the source story.",
    )
    parser.add_argument(
        "--with-optional",
        action="store_true",
        help="Generate optional implementation/dev-log files.",
    )
    args = parser.parse_args()

    story_path = args.story.expanduser().resolve()
    if not story_path.exists():
        raise SystemExit(f"Story file not found: {story_path}")
    if not story_path.is_file():
        raise SystemExit(f"Story path is not a file: {story_path}")

    story_text = story_path.read_text(encoding="utf-8")
    story_key = infer_story_key(story_path, story_text, args.story_key)
    root = args.root.expanduser().resolve()
    base = (
        args.capsules_dir
        if args.capsules_dir.is_absolute()
        else root / args.capsules_dir
    )
    capsule = base / story_key
    generated = capsule / "generated"
    generated.mkdir(parents=True, exist_ok=True)

    target_story = capsule / "00-story.md"
    if target_story.exists():
        target_story_text = target_story.read_text(encoding="utf-8")
        if target_story_text != story_text:
            if not args.overwrite_story:
                raise SystemExit(
                    "Existing capsule story differs from source story. "
                    "Use --overwrite-story to replace 00-story.md."
                )
            target_story.write_text(story_text, encoding="utf-8")
            print(f"Overwrote existing capsule story: {target_story}", file=sys.stderr)
    else:
        shutil.copyfile(story_path, target_story)

    criteria = extract_acceptance_criteria(story_text)
    templates = build_templates(story_key, criteria, args.with_optional)

    expected_files = REQUIRED_GENERATED + (
        OPTIONAL_GENERATED if args.with_optional else []
    )
    for name in expected_files:
        content = templates[name]
        write_if_missing(generated / name, content, args.overwrite_generated)

    print(f"CONDAMAD capsule ready: {capsule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
