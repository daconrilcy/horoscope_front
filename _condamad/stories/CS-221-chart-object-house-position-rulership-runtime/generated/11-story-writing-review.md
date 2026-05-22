<!-- Revue redactionnelle CONDAMAD de la story CS-221. -->

# CS-221 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- La section `Current State Evidence` presentait encore `CS-221` comme le
  prochain numero disponible, alors que `story-status.md` contient deja
  l'enregistrement de la story en `ready-to-dev`.
- Les mentions `ajout de RG-148` pouvaient laisser croire que le guardrail
  devait toujours etre cree, alors que le registre contient deja l'invariant
  `RG-148` dans le worktree courant.
- `AC11` demandait `test_natal_result_contract.py`, mais ce test n'etait pas
  repris dans la liste executable des tests cibles du Validation Plan.

Corrections appliquees:

- Mise a jour de l'evidence d'etat courant pour decrire `CS-221` comme deja
  enregistree dans `story-status.md`.
- Remplacement des formulations d'ajout obligatoire de `RG-148` par une regle
  de verification ou d'ajout conditionnel si absent.
- Ajout de
  `backend/tests/unit/domain/astrology/test_natal_result_contract.py` aux tests
  cibles du Validation Plan.

Validation apres corrections:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- `AC17` exigeait la presence de `CS-221 Final Evidence`, mais le Validation
  Plan ne contenait pas le scan executable correspondant depuis la racine du
  repository.

Corrections appliquees:

- Ajout du scan
  `rg -n "CS-221 Final Evidence" _condamad/stories/CS-221-chart-object-house-position-rulership-runtime/evidence/validation.md`
  dans les scans anti-regression du Validation Plan.

Validation apres corrections:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 3 - Issues Found

Verdict: changes requested after brief-alignment check.

Findings:

- Le brief nomme `HousePositionRuntimePayload`, tandis que la story utilise
  `ChartObjectHousePositionPayload`. Le choix est correct pour le repo, mais il
  devait etre explicite pour ne pas ressembler a un oubli du payload demande.
- Le brief place CS-221 avant les fixed stars / CS-222. La story bornait bien le
  domaine astrology runtime, mais ne disait pas explicitement que les etoiles
  fixes restent pour une story ulterieure.

Corrections appliquees:

- Ajout d'une regle de nommage: `ChartObjectHousePositionPayload` est la
  surface house position canonique existante a enrichir, sans creer de doublon
  `HousePositionRuntimePayload`.
- Ajout des etoiles fixes / CS-222 comme hors scope explicite et comme decision
  d'alignement source.

Validation apres corrections:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 4 - Clean Review

Verdict: clean.

Checks:

- La story reste bornee au runtime backend astrology et n'elargit pas vers API,
  DB, migrations, frontend, interpretation ou projection JSON publique.
- Les contrats requis restent presents: runtime source of truth, baseline,
  ownership routing, allowlist exception, contract shape, reintroduction guard
  et evidence persistante.
- Les AC sont atomiques et les preuves attendues sont couvertes par le plan de
  validation ou par les scans explicites.
- Les taches couvrent baseline, contrats, projectors/enrichers, orchestration,
  tests, guards et preuve finale.
- Les guardrails interdisent toujours selection par `object_type`, second
  resolver, table locale de rulership, fallback silencieux et payload narratif.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
