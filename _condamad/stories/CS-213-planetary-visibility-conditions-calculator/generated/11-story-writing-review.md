<!-- Revue redactionnelle CONDAMAD de la story CS-213. -->

# CS-213 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- Quelques formulations contractuelles mélangeaient anglais et français dans
  une story majoritairement française, notamment `and the bounded`, `no public`
  et `otherwise`. Cela rendait les règles moins homogènes que le reste du
  document.
- AC16 ne couvrait pas toute la liste de dépendances interdites déjà exigée par
  le Validation Plan: `app.infrastructure`, `app.services`, `OpenAI` et
  `AIEngineAdapter` manquaient dans la preuve AC.
- AC19 ne couvrait pas toute la garde d'astronomie observationnelle et
  d'intégration globale déjà exigée par le Validation Plan: `NatalResult`,
  `topocentric`, `latitude`, `FastAPI` et `SQLAlchemy` manquaient dans la
  preuve AC.
- La section `New durable invariant` demandait seulement de verifier la
  presence de `RG-140`, alors que les sections 19 et 21 autorisent aussi son
  ajout si l'invariant n'existe pas encore.

Fixes applied:

- Reworded the mixed-language contract prose in French.
- Expanded AC16 evidence to match the forbidden dependency scan in the
  Validation Plan.
- Expanded AC19 evidence to match the observation/integration scan in the
  Validation Plan.
- Replaced `verifier la presence de RG-140` with `verifier ou ajouter RG-140`.

Validation after fixes:

- First rerun failed because the AC19 wording used `runtime`, which triggered
  the story linter's runtime-evidence rule for a static scan AC.

Follow-up fix:

- Reworded AC19 from `integration runtime globale` to `integration globale
  adjacente`, preserving the intended `NatalResult` guard without triggering
  the runtime-evidence rule.
- Added `$forbidden_deps` and `$forbidden_observation` variables in the
  Validation Plan so AC16 and AC19 keep concrete `rg` evidence without
  duplicating long regexes in the AC table.
- Split the strict-lint compound AC19 wording: AC19 now covers observation-only
  terms, while AC20 carries the adjacent/global integration scan.

Validation after follow-up fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- AC16 through AC20 still mixed English result wording (`expected zero hits`,
  `zero-hit`) into otherwise French acceptance criteria.

Fixes applied:

- Replaced the result wording with `aucun hit attendu` while preserving the
  concrete validation commands.
- Shortened AC20 after the translation pushed the row over the lint line limit.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS after shortening AC20.
- `condamad_story_lint.py --strict`: PASS after shortening AC20.

## Iteration 3 - Clean Review

Verdict: clean.

Checks:

- The story is self-contained for visibility priority, threshold ordering,
  cazimi/conjunction behavior, combustion, under beams, oriental-only
  emergence, default visibility, batch behavior and placeholders not produced
  by nominal cases.
- AC16 through AC20 now align with the detailed Validation Plan scans without
  losing concrete evidence.
- `RG-140` wording now matches the expected implementation path: verify it if
  present, add it if absent.
- No remaining wording permits scoring, interpretation, API/DB/frontend
  integration, compatibility shims, duplicate contracts, hidden fallbacks,
  heliacal astronomy reel or out-of-scope `NatalResult` integration.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 4 - Brief Alignment Review

Verdict: changes requested, then clean after correction.

Findings:

- The story implemented the brief's rules, but did not explicitly capture the
  brief's domain stakes: visibility as an expert astrological fact about a
  planet's visible manifestation, not as scoring or interpretation.
- The brief mentioned raw Sun/planet longitudes while also forbidding
  recalculation of solar distance and orientation. The story used CS-209 and
  CS-211 derived facts, but did not state this source-resolution decision.
- The brief listed "proche de l'emergence", while CS-208 has no
  `NEAR_EMERGENCE` visibility key. The story used the `EMERGING` 15-18 degree
  window but did not explicitly explain that this covers the brief's
  near-emergence intent without adding a local enum.

Fixes applied:

- Added `Brief-stakes alignment` to section 2.
- Added `Source ambiguity resolved` to section 2 and a matching operation rule
  forbidding raw longitude consumption in CS-213.
- Added `Near-emergence handling` to section 4f and the same target-state
  expectation in section 6.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

Clean alignment check:

- The story now covers the brief's functional states through the CS-208
  contract: `VISIBLE`, `INVISIBLE`, `UNDER_BEAMS`, `EMERGING`,
  `HELIACAL_RISING`, `HELIACAL_SETTING`, `CONJUNCT_SOLAR` and `UNKNOWN`, with
  heliacal values and `UNKNOWN` kept as non-produced placeholders for nominal
  CS-213 cases.
- The story explicitly resolves the raw longitude ambiguity by consuming
  CS-209/CS-211 derived facts instead of recalculating distance or orientation.
- The story explicitly maps the brief's "proche de l'emergence" intent to the
  simplified `EMERGING` threshold window because no separate
  `NEAR_EMERGENCE` key exists in CS-208.
