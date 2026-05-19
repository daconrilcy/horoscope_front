<!-- Revue redactionnelle CONDAMAD de la story CS-194. -->

# CS-194 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- `CS-194` depended on `CS-193` condition signals while `CS-193` was still
  `ready-to-dev`; the story did not define a hard implementation precondition
  and allowed an ambiguous partial execution path.
- The DB seed contract referenced "les lignes du brief" without listing the
  eight rows, so AC1 and the runtime evidence were not independently
  verifiable from the story file.
- The expected SQLAlchemy model owner allowed "un modèle astrology voisin",
  which left avoidable implementation drift around model placement and
  metadata registration.

Fixes applied:

- Added section `2a. Sequencing / Blocking Dependencies` with a hard stop when
  `CS-193` is not done or `condition_signals` is absent.
- Added section `4b.1 Dominance Factor Seed Contract` with the exact v1 rows,
  weights, ordering and deterministic scoring rule.
- Replaced ambiguous model ownership with `reference.py` plus explicit
  `models/__init__.py` export.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 2 - Clean Review

Verdict: clean.

Checks:

- The story is self-contained for the dominance factor seed contract.
- The dependency on CS-193 is explicit and blocks partial implementation.
- Acceptance criteria remain atomic and mapped to validation evidence.
- Runtime source of truth, baseline snapshot, ownership routing, contract shape,
  persistent evidence and reintroduction guard sections are present.
- No remaining wording permits compatibility shims, fallback behavior, broad
  allowlists, duplicate dominance engines, local dominance weights or LLM/UI
  scope creep.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
