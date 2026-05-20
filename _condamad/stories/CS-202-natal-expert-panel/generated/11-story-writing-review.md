<!-- Revue redactionnelle CONDAMAD de la story CS-202. -->

# CS-202 Story Writing Review

Date: 2026-05-20

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- La story mélangeait français et anglais dans des phrases normatives
  destinées au dev agent (`must`, `display`, `This story`, `Static scans`),
  ce qui augmentait le risque d'interprétation non uniforme des obligations.
- Le terme `adapter` était utilisé seul dans le scope, les tâches et AC8 alors
  que le contrat public s'appelle `interpretation_adapter`; cette ambiguïté
  pouvait mener à une surface UI ou à un type mal nommé.
- La numérotation passait de `15. External Usage Blocker` à
  `17. Generated Contract Check`, ce qui rendait les références de sections
  fragiles pour une implémentation assistée.
- AC8 ne scannait que `OpenAI`, ce qui ne couvrait pas assez la dérive
  narrative ou personnalisée depuis `interpretation_adapter`.
- AC12 scannait tout `_condamad/stories` et cherchait uniquement la formulation
  anglaise `no astrology calculation`, ce qui pouvait donner un faux positif
  hors story ou manquer l'evidence rédigée en français.

Fixes applied:

- Reformulation en français des phrases normatives et des lignes de tableau qui
  guidaient l'implémentation.
- Remplacement des usages ambigus de `adapter` par `interpretation_adapter` ou
  `adaptateur interprétatif` selon le contexte.
- Renumérotation des sections finales de 16 à 23.
- Renforcement d'AC8 avec un scan plus ciblé sur `OpenAI`, `AIEngineAdapter`,
  `prompt_hint`, `personalized` et `conseil`.
- Restriction d'AC12 et du plan de validation au dossier d'evidence CS-202, avec
  acceptation des formulations française et anglaise.

Validation after fixes:

- `condamad_story_validate.py`: FAIL.
- `condamad_story_lint.py --strict`: FAIL.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- Les corrections françaises avaient supprimé des marqueurs exacts consommés
  par les validateurs CONDAMAD: `Static scans alone`, `AST guard` et
  `If an AC cannot be satisfied`.
- La story contenait encore deux résidus anglais dans des zones de prose/tableau:
  `This story belongs to exactly one domain` et `display factual fields`.

Fixes applied:

- Réintroduction des marqueurs exacts attendus par les validateurs, avec une
  explication française accolée lorsque nécessaire.
- Traduction des résidus anglais non requis par les validateurs.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: FAIL.

## Iteration 3 - Issues Found

Verdict: changes requested.

Findings:

- Le lint strict signalait trois lignes de tableau Markdown au-delà de 180
  caractères, sur l'artefact de validation et AC8/AC12.

Fixes applied:

- Raccourcissement des cellules de tableau sans affaiblir les exigences.
- Conservation de la commande de scan AC8 complète dans le plan de validation.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: FAIL.

## Iteration 4 - Issues Found

Verdict: changes requested.

Findings:

- AC12 utilisait `Test-Path`, que le validateur ne reconnaissait pas comme
  evidence concrète attendue dans la table d'acceptance criteria.
- AC3, AC8 et AC12 restaient trop longs après ajout de commandes concrètes.

Fixes applied:

- Remplacement de l'evidence AC12 par un scan `rg` ciblé sur le dossier
  d'evidence CS-202.
- Raccourcissement des cellules AC3, AC8 et AC12; les commandes complètes
  restent dans le plan de validation.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: FAIL.

## Iteration 5 - Issues Found

Verdict: changes requested.

Findings:

- AC3 et AC8 avaient été trop raccourcis: les validateurs ne reconnaissaient
  plus de commande concrète dans ces lignes.
- AC12 dépassait encore la limite de longueur stricte.

Fixes applied:

- Réintroduction de commandes concrètes `npm test` et `rg` dans AC3 et AC8.
- Raccourcissement du libellé AC12 pour rester sous la limite de ligne.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: FAIL.

## Iteration 6 - Issues Found

Verdict: changes requested.

Findings:

- AC3 et AC12 restaient au-dessus de 180 caractères malgré les corrections
  précédentes.

Fixes applied:

- Raccourcissement des libellés AC3 et AC12 sans retirer les commandes
  concrètes requises par le validateur.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: FAIL.

## Iteration 7 - Issues Found

Verdict: changes requested.

Findings:

- Le plan de validation faisait `cd frontend`, puis conservait des scans avec
  chemins `frontend/...`, ce que le lint strict signale comme incohérent.

Fixes applied:

- Remplacement du bloc frontend par des commandes `npm --prefix frontend ...`
  exécutables depuis la racine, cohérentes avec les scans suivants.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 8 - Clean Review

Verdict: clean.

Checks:

- Le périmètre frontend reste clair et ne permet pas de modification backend.
- Les contrats publics à consommer sont nommés explicitement.
- Les critères d'acceptation restent atomiques et reliés à une evidence
  vérifiable.
- Les états absent, vide, indisponible et ancien payload restent distingués.
- Les guardrails RG-108, RG-112 et RG-118 à RG-129 restent cités et reliés aux
  scans/tests attendus.
- Aucun libellé restant ne crée d'autorisation implicite de fallback doctrinal,
  alias legacy, calcul frontend, appel LLM ou compatibilité transitoire.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
