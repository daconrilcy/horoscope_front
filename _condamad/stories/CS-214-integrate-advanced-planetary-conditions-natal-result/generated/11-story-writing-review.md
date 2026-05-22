<!-- Revue redactionnelle CONDAMAD de la story CS-214. -->

# CS-214 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- AC20 demandait l'absence d'import interdit, mais la preuve attendue etait un
  test runtime. Cette preuve ne demontre pas l'absence d'import interdit dans
  les nouveaux modules.
- AC21 demandait que les surfaces adjacentes restent inchangees, mais la preuve
  attendue etait un test runtime. Cette preuve ne demontre pas que le diff des
  surfaces hors scope est vide.
- La story listait les signaux globaux `waxing_moon` et `waning_moon`, mais ne
  precisait pas leur source. Un dev agent pouvait les omettre, les rattacher au
  bundle Lune ou les produire depuis une logique non canonique.

Fixes applied:

- AC20 exige maintenant le scan `rg -n $forbidden_deps $new_modules` avec zero
  hit attendu.
- AC21 exige maintenant le `git diff -- ...` des surfaces adjacentes avec diff
  vide attendu.
- La section 4f contient une regle explicite de source des signaux: signaux des
  bundles pour les conditions planetaires, signaux globaux lunaires depuis
  `moon_phase`, puis aggregation dans `result.signals`.
- La tache 3 ajoute une sous-tache dediee aux signaux globaux
  `waxing_moon`/`waning_moon`.

Validation after fixes:

- `condamad_story_validate.py`: FAIL, AC21 evidence not recognized as
  concrete by the CONDAMAD validator.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: FAIL, AC21 evidence not recognized as concrete.
- `condamad_story_lint.py --strict`: FAIL, AC21 evidence not recognized as
  concrete.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- The Iteration 1 fix used a direct `git diff -- ...` evidence cell for AC21.
  The command is semantically correct, but the story validator only recognizes
  predefined command families or explicit manual checks as concrete AC
  evidence.

Fixes applied:

- Reworded AC21 as an explicit manual check that executes the same scoped
  `git diff -- ...` command and expects an empty diff.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS after shortening AC21 evidence through an
  evidence variable.
- `condamad_story_lint.py --strict`: PASS after shortening AC21 evidence
  through an evidence variable.

## Iteration 3 - Clean Review

Verdict: clean.

Checks:

- AC20 now requires the forbidden import scan and no longer relies on a runtime
  unit test to prove static import absence.
- AC21 now requires the scoped adjacent-surface diff check and remains accepted
  by the CONDAMAD story validator as concrete manual evidence.
- The source of `waxing_moon` and `waning_moon` is explicit: they come from the
  global `moon_phase`, not from ad hoc natal runtime logic or a planet bundle
  fallback.
- The implementation tasks now include a dedicated subtask for global lunar
  signals.
- Required contracts remain present: runtime source of truth, baseline
  snapshot, ownership routing, allowlist exception, contract shape,
  reintroduction guard and persistent evidence.
- No remaining wording permits scoring, interpretation, API/DB/frontend
  integration, compatibility shims, fallback behavior, duplicate contracts or
  out-of-scope JSON projection.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
