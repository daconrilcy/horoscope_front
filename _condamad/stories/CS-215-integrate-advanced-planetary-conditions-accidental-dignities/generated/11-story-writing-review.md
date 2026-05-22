<!-- Revue redactionnelle CONDAMAD de la story CS-215. -->

# CS-215 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- La section Domain Boundary autorisait un nom equivalent pour
  `advanced_condition_modifier_profiles.py`, alors que la section 19, le
  Validation Plan, `$profiles` et les guardrails attendent ce chemin exact.
- La liste des deltas par defaut exigeait deux modificateurs
  `oriental_superior_bonus` et `occidental_superior_penalty`, mais ne donnait
  pas leurs valeurs V1.
- La fonction publique retournait seulement `tuple`, ce qui affaiblissait le
  contrat de forme de `AccidentalDignityModifier`.
- La regle lunaire disait "uniquement la Lune" sans preciser le code canonique
  `bundle.planet_key == "moon"`.
- La visibilite pouvait double compter `UNDER_BEAMS`: la story exigeait deja un
  `under_beams_penalty` depuis la proximite solaire, mais ne disait pas quoi
  faire de `PlanetVisibilityKey.UNDER_BEAMS`.
- AC16 prouvait seulement les imports interdits via `$forbidden_deps`; il ne
  couvrait pas explicitement les termes d'interpretation, API/DB/frontend,
  `json_builder` ni le diff adjacent pourtant exiges par le Validation Plan.
- L'evidence d'etat courant indiquait encore que CS-214 etait la derniere story
  numerotee, alors que `story-status.md` contient maintenant CS-215.
- Quelques formulations reduisaient la precision ou la lisibilite:
  `modificateurs additives`, `avancent le score final`, et l'absence de
  tolerance explicite pour `moon_phase=None`.

Fixes applied:

- Le chemin `advanced_condition_modifier_profiles.py` est maintenant obligatoire
  comme source unique des deltas V1.
- La signature attendue retourne
  `tuple[AccidentalDignityModifier, ...]`.
- Les deltas V1 sont explicites: `oriental_superior_bonus` vaut `+1` et
  `occidental_superior_penalty` vaut `-1`.
- Les regles de proximite solaire precisent `is_active=False`, `NONE`, cazimi,
  combustion hors Soleil et under beams.
- La regle de visibilite V1 couvre `INVISIBLE` et `EMERGING`, puis exclut
  `UNDER_BEAMS` et `CONJUNCT_SOLAR` pour eviter le double comptage.
- La regle oriental/occidental liste les planetes superieures V1
  `mars`, `jupiter`, `saturn`, les planetes inferieures V1 `mercury`, `venus`
  et les cas sans effet V1.
- La regle lunaire cible explicitement `bundle.planet_key == "moon"` et accepte
  `moon_phase=None`.
- AC9, AC10, AC11, AC16 et les taches de tests ont ete ajustes pour refleter
  les regles contractuelles corrigees.
- Le Validation Plan ajoute `$forbidden_surface_terms` et le scan associe.
- L'evidence 1 mentionne CS-215 comme story `ready-to-dev` apres CS-214 `done`.
- Les formulations fautives ont ete corrigees.

Validation after fixes:

- Premier rerun: `condamad_story_validate.py` PASS et
  `condamad_story_validate.py --explain-contracts` PASS; lint strict FAIL
  parce qu'AC16 depassait 180 caracteres, puis parce qu'AC16 melangeait deux
  invariants.
- Follow-up fix: AC16 a ete separe en AC16 surfaces interdites, AC17 diff
  adjacent, AC18 duplication des calculateurs et AC19 validation complete.
- Deuxieme rerun: validation PASS, explain-contracts PASS, lint PASS et lint
  strict PASS.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- La story utilisait le libelle `AST guard` pour des tests cibles et des scans
  `rg`, alors qu'aucune analyse AST n'est exigee. Le libelle pouvait conduire
  le dev agent a documenter une preuve differente de la preuve attendue.

Fixes applied:

- Le libelle runtime est devenu `AST guard evidence` pour satisfaire le contrat
  CONDAMAD tout en gardant les commandes ciblees explicites.
- AC16 ne mentionne plus `AST guard` et cite uniquement le scan concret
  `$forbidden_surface_terms`.

Validation after fixes:

- Premier rerun apres correction: validation FAIL parce que le contrat
  `Runtime Source of Truth` exige explicitement un artefact de type
  `AST guard`.
- Follow-up fix: le libelle `AST guard evidence` a ete conserve dans la
  section runtime avec les commandes pytest ciblees, tandis qu'AC16 reste
  limite au scan concret.
- Deuxieme rerun: validation PASS, explain-contracts PASS, lint PASS et lint
  strict PASS.

## Iteration 3 - Clean Review

Verdict: clean.

Checks:

- La story est self-contained pour les deltas V1, y compris
  `oriental_superior_bonus` et `occidental_superior_penalty`.
- Les regles de proximite solaire, visibilite V1, phase solaire V1 et phase
  lunaire indiquent les sources, les cas sans effet et les conditions de
  non-double-comptage.
- Les AC separent les invariants: surfaces interdites, diff adjacent,
  duplication des calculateurs et validation complete.
- Les chemins de modules attendus, variables de validation et preuves AC sont
  alignes.
- L'evidence d'etat courant correspond au registre `story-status.md`.
- Aucun wording restant ne permet API, DB, frontend, LLM, interpretation,
  fallback silencieux, shim, alias, duplication des calculateurs CS-209 a
  CS-214 ou double comptage `UNDER_BEAMS`.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 4 - Brief Alignment Review

Verdict: changes requested, then clean after correction.

Findings:

- Le brief de depart explicitait le pipeline cible
  `positions -> aspects -> advanced planetary conditions -> accidental dignity modifiers -> accidental dignity score`,
  mais la story ne le nommait pas directement. Le contrat etait implicitement
  correct, mais moins traçable face au brief.
- Le brief demandait d'enrichir les "signaux de dignite". Le code actuel expose
  `PlanetDignityResult` avec scores et breakdowns, pas avec un champ `signals`.
  La story devait donc expliciter la decision de traduction: signaux de dignite
  = modificateurs accidentels factuels visibles dans le breakdown ou dans un
  champ minimal dedie, sans passer par `interpretation_adapters`.
- Le brief precise que la stationnarite V1 peut etre `+2`, mais que son sens
  reel dependra plus tard de l'interpretation. La story avait le delta `+2`,
  mais pas la limite "convention V1 configurable, pas verite absolue".
- Le brief annonce CS-216 comme prochaine story interpretative; la story
  interdisait bien l'interpretation, mais ne posait pas explicitement cette
  frontiere de handoff.

Fixes applied:

- Ajout de `Brief pipeline alignment` en section 2.
- Ajout de `Brief dignity-signals resolution` en section 2.
- Ajout de `Pipeline source of truth` en section 4b.
- Ajout d'une `Stationary V1 note` en section 4f.
- Ajout d'une phrase Target State sur les signaux de dignite representes par
  les modificateurs accidentels.
- Ajout de `interpretation_adapters` aux surfaces hors scope et au diff
  adjacent.
- Ajout de `24a. Follow-up Story` pour borner CS-216.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

Clean alignment check:

- La story couvre l'objectif du brief: les conditions avancees existantes
  influencent maintenant le score accidentel via des modificateurs.
- Les etats listes par le brief sont couverts: combustion, cazimi, under beams,
  retrogradation, stationnarite, vitesse, visibilite, relation
  oriental/occidental et phase lunaire.
- Les modificateurs attendus et leurs deltas V1 sont explicites.
- Les breakdowns et "signaux de dignite" sont resolus comme preuves factuelles
  de score, sans texte narratif.
- Les cas particuliers du brief sont couverts: cazimi prioritaire,
  stationnaire+retrograde, conditions absentes et Soleil sans penalite de
  combustion.
- Les hors-perimetres du brief restent bloques: interpretation, rendering, UI,
  LLM, API, DB, migrations, seeders, dignites essentielles, nouveaux
  calculateurs et visibilite astronomique reelle.
