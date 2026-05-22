<!-- Revue redactionnelle CONDAMAD de la story CS-216. -->

# CS-216 Story Writing Review

## Iteration 1 - Issues Found

Verdict: changes requested.

Findings:

- La story autorisait soit `NatalResult`, soit
  `AdvancedPlanetaryConditionsResult` comme surface runtime des profils, alors
  que le domaine, les fichiers attendus et les tests ciblent `NatalResult`.
- La formulation "fallback generique" pouvait etre confondue avec le fallback
  silencieux explicitement interdit par la story.
- Les cles de conditions a extraire depuis `PlanetaryConditionsBundle` et
  `MoonPhaseCondition` n'etaient pas listees dans le contrat de forme, ce qui
  laissait trop d'inference au dev agent.
- Les sections finales etaient numerotees `24a` puis `24`, ce qui rendait les
  references moins nettes.

Fixes applied:

- `NatalResult.interpretation_profiles_by_planet` est maintenant la seule
  surface runtime interne autorisee.
- Le wording "fallback generique" a ete remplace par "resolution generique
  statique" et la regle de resolution est explicite: priorites du catalogue,
  aucune generation dynamique.
- La section 4f liste les extractions attendues depuis proximite solaire,
  mouvement, visibilite, relation solaire et phase lunaire.
- `Follow-up Story` est devenu section 24 et `References` section 25.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 2 - Issues Found

Verdict: changes requested.

Findings:

- Les tests demandes couvraient combust, retrograde et phases lunaires, mais ne
  forcaient pas explicitement l'extraction `stationary`, visibilite et
  oriental/occidental.
- `under_beams` peut etre produit par proximite solaire et par visibilite; la
  story ne disait pas si le runtime devait dedupliquer cette cle.
- La section des invariants non applicables disait `RG-001` a `RG-142`, alors
  que `RG-135` a `RG-142` sont applicables a la story.

Fixes applied:

- AC3 demande maintenant l'extraction depuis chaque famille contractuelle.
- La tache de tests couvre `stationary`, visibilite, solar phase, moon phases
  et la deduplication `under_beams`.
- La section 4f ajoute l'ordre de collecte et la deduplication des cles.
- Le libelle des invariants non applicables ne contredit plus la liste des
  invariants applicables.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 3 - Clean Review

Verdict: changes requested after brief-alignment check.

Findings:

- Le brief indique que les profils preparent aussi de futurs prompts LLM, mais
  la story disait que CS-216 ne prepare aucun prompt. La limite correcte est:
  aucun prompt n'est cree dans CS-216, mais les blocs symboliques restent
  exploitables par de futurs prompts.
- La signature publique retournait seulement `tuple`, alors que le brief attend
  `tuple[AdvancedConditionInterpretationProfile, ...]`.
- Le brief demande des profils specifiques a une polarite; la story portait
  bien `polarity`, mais ne disait pas explicitement que la polarite est une
  propriete de profil et non un filtre runtime.
- La vision pipeline du brief et le choix repo-informed `NatalResult` au lieu
  de `AdvancedPlanetaryConditionsResult` meritaient une trace explicite.

Fixes applied:

- Ajout de `Brief pipeline alignment` et `Brief target-file resolution` en
  section 2.
- La signature reste compatible avec le linter CONDAMAD et une regle de retour
  exige un tuple homogene de `AdvancedConditionInterpretationProfile`.
- Ajout d'une `Polarity rule` en section 4f.
- Les taches et AC demandent maintenant polarite/intensite explicites et des
  tests des champs de polarite.
- La section follow-up precise que CS-216 ne cree aucun prompt, tout en
  preparant des blocs exploitables par de futurs prompts.

Validation after fixes:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.

## Iteration 4 - Clean Review

Verdict: clean.

Checks:

- La story est self-contained pour la surface runtime, les contrats, les cles de
  catalogue minimales, la priorite de resolution et la collecte des cles.
- La story est alignee avec les enjeux du brief: couche symbolique
  intermediaire, pipeline apres dignites, preparation future des moteurs
  narratifs/prompts/renderers sans implementation de ces couches.
- Les AC et taches forcent les familles factuelles attendues: proximite solaire,
  mouvement, visibilite, relation solaire et phase lunaire.
- La polarite est explicitement modelee comme donnee de profil, sans devenir un
  filtre runtime ni une interpretation finale.
- Les guardrails restent alignes: pas de scoring, prompt/LLM, API, DB,
  frontend, projection publique, recalcul des conditions ou texte final
  utilisateur.
- Les commandes CONDAMAD de validation et lint passent sous venv.

Validation:

- `condamad_story_validate.py`: PASS.
- `condamad_story_validate.py --explain-contracts`: PASS.
- `condamad_story_lint.py`: PASS.
- `condamad_story_lint.py --strict`: PASS.
