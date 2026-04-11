# Story 66.26: Durcissement de la discipline de maintenance documentaire du pipeline LLM

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want to rendre obligatoire, traçable et opératoire la maintenance du document de référence du pipeline de génération de prompts LLM à chaque évolution structurelle du gateway,
so that la documentation d'architecture reste alignée sur le code réel, avec une preuve explicite de vérification sur un commit ou tag déterminé, et qu'aucune modification structurelle de `_resolve_plan()`, de la composition textuelle canonique, des providers ou des fallbacks ne puisse être mergée sans mise à jour documentaire associée.

## Contexte

Le document [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) est désormais la source de vérité pratique décrivant le pipeline canonique de résolution, de composition, d'exécution provider et de gouvernance des fallbacks. Il formalise déjà :

- l'ordre réel de résolution dans le gateway ;
- les responsabilités de `PromptAssemblyConfig`, `ExecutionProfile`, `PromptRenderer` et `ResolvedExecutionPlan` ;
- la taxonomie `feature/subfeature/plan` ;
- le statut des fallbacks ;
- le support runtime effectif des providers ;
- l'observabilité et la matrice d'évaluation.

Les stories 66.21 à 66.25 ont durci le fond de la doctrine :

- **66.21** a fermé et classé les fallbacks encore tolérés ;
- **66.22** a verrouillé les providers nominalement supportés ;
- **66.23** a normalisé la taxonomie canonique natal ;
- **66.24** a étendu le gating d'évaluation aux chemins encore transitoires ;
- **66.25** a rendu explicites les discriminants structurels de runtime dans l'observabilité.

Le document d'architecture a suivi cette convergence, mais il reste un angle mort de gouvernance opérationnelle :

- la preuve de fraîcheur documentaire est encore `HEAD`, donc non stable pour un audit ;
- la section "Maintenance de cette documentation" formule une attente, pas encore une obligation de contribution contrôlable ;
- les zones de code qui déclenchent une revue documentaire ne sont pas encore bornées avec assez de précision ;
- le repository ne porte pas encore de règle PR visible imposant soit la mise à jour documentaire, soit une justification explicite d'absence de changement.

La story 66.26 ne change donc pas la doctrine technique du pipeline. Elle transforme la maintenance du document en règle d'ingénierie explicite et traçable.

## Acceptance Criteria

1. **AC1 — Référence de vérification non flottante** : La section "Dernière vérification manuelle contre le pipeline réel du gateway" ne doit plus accepter de référence flottante comme `HEAD`, `main`, `master`, "branche courante" ou équivalent. Elle exige une référence stable : commit SHA, tag, ou les deux.
2. **AC2 — Politique documentaire explicitée dans le document** : La section "Maintenance de cette documentation" doit exprimer comme obligation d'ingénierie qu'une PR modifiant la structure du pipeline mette à jour le document dans le même change set, ou justifie explicitement pourquoi le document reste valide sans changement.
3. **AC3 — Zones à impact documentaire obligatoire bornées** : Le document doit lister explicitement les zones de code ou catégories de composants qui déclenchent au minimum une revue documentaire obligatoire : `_resolve_plan()`, `_build_messages()` lorsque l'ordre canonique change, renderer / `PromptRenderer`, `_call_provider()`, `ProviderParameterMapper`, `FallbackGovernanceRegistry`, taxonomie canonique, résolution `ExecutionProfile`, `context_quality` / `ContextQualityInjector`, et toute logique modifiant la source de vérité décrite dans le document.
4. **AC4 — Règle de PR ajoutée au workflow de contribution** : Le repository doit exposer, dans une surface visible au moment de la review PR, une règle de contribution indiquant explicitement que toute modification de `_resolve_plan()`, de la composition textuelle canonique, des providers ou des fallbacks doit mettre à jour [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md), ou justifier explicitement l'absence de changement documentaire.
5. **AC5 — Cohérence entre règle documentaire et règle PR** : La règle présente dans le document et celle du workflow PR doivent porter le même périmètre de déclenchement et la même exigence de justification explicite.
6. **AC6 — Traçabilité de la dernière vérification** : Le document doit continuer d'exposer une date de dernière vérification, mais cette date doit être associée à une preuve exploitable de la version auditée afin qu'un reviewer puisse retrouver sans ambiguïté le code examiné.
7. **AC7 — Pas de pseudo-automatisation mensongère** : La story ne doit pas introduire un mécanisme déclarant automatiquement que la documentation est à jour sans revue humaine réelle. Toute mention de vérification doit correspondre à une revue manuelle effective.
8. **AC8 — Compatibilité avec les stories précédentes** : La story ne modifie pas la doctrine fonctionnelle issue des stories 66.21 à 66.25. Elle renforce uniquement la discipline de maintenance et de traçabilité documentaire autour de cette doctrine.
9. **AC9 — Format de preuve documentaire homogène** : Le bloc final de vérification dans [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) doit utiliser un format stable et répétable permettant la lecture humaine et une assertion légère en test.

## Tasks / Subtasks

- [x] Task 1: Durcir la politique de maintenance dans le document d'architecture (AC1, AC2, AC3, AC6, AC7)
  - [x] Mettre à jour [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) pour remplacer la formulation actuelle par une obligation explicite de mise à jour documentaire ou de justification d'absence de changement.
  - [x] Remplacer le bloc de vérification manuel afin d'interdire explicitement les références flottantes (`HEAD`, branche courante, alias implicite).
  - [x] Introduire un format normatif minimal du bloc final, par exemple `date`, `commit`, `tag` optionnel.
  - [x] S'assurer que la formulation ne laisse pas croire à une auto-certification mécanique de fraîcheur documentaire.

- [x] Task 2: Borner explicitement les zones à impact documentaire obligatoire (AC2, AC3, AC5)
  - [x] Lister dans le document les composants, étapes ou catégories de logique qui déclenchent une revue documentaire obligatoire.
  - [x] Couvrir au minimum `_resolve_plan()`, `_build_messages()` si l'ordre canonique change, le renderer / la composition textuelle canonique, `ProviderParameterMapper`, `_call_provider()`, `FallbackGovernanceRegistry`, la taxonomie `feature/subfeature/plan`, la résolution `ExecutionProfile`, `context_quality` et `ContextQualityInjector`.
  - [x] Préciser qu'un refactoring purement local ou cosmétique peut ne pas exiger une mise à jour documentaire, mais qu'il doit alors être justifié explicitement dans la PR.

- [x] Task 3: Ajouter la règle normative au workflow de contribution (AC4, AC5, AC7)
  - [x] Identifier la surface de contribution la plus adaptée dans le dépôt : template PR sous `.github/`, checklist de review existante, ou documentation dédiée si aucun template PR n'existe encore.
  - [x] Ajouter une formulation normative et actionnable imposant soit la mise à jour documentaire, soit une justification explicite.
  - [x] Prévoir un champ libre ou équivalent pour la référence commit/tag auditée par la documentation si la surface choisie s'y prête.
  - [x] Éviter toute formulation laissant entendre qu'une simple case cochée remplace la revue humaine effective.

- [x] Task 4: Garantir la cohérence entre document et workflow PR (AC4, AC5, AC8)
  - [x] Vérifier que le périmètre de déclenchement décrit dans le document et celui du workflow de contribution sont alignés.
  - [x] Vérifier que les deux surfaces emploient une sémantique cohérente sur la justification explicite en cas d'absence de mise à jour documentaire.
  - [x] Vérifier que la story ne réécrit pas la doctrine canonique du pipeline, mais uniquement sa gouvernance documentaire.

- [x] Task 5: Ajouter les tests de gouvernance légère (AC1 à AC7)
  - [x] Ajouter une suite dédiée, par exemple `backend/tests/integration/test_story_66_26_documentation_governance.py`, ou une suite documentaire équivalente si le dépôt dispose déjà d'un emplacement plus approprié pour ce type de garde-fou.
  - [x] Vérifier que [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) ne contient plus `commit / tag : HEAD`.
  - [x] Vérifier que la règle de contribution mentionne au minimum `_resolve_plan()`, composition textuelle canonique, providers et fallbacks.
  - [x] Vérifier que la surface de contribution choisie explicite les deux issues autorisées : mise à jour documentaire dans le même change set, ou justification explicite de l'absence de changement.

## Dev Notes

### Objectif exact

Cette story est une story de gouvernance documentaire opérationnelle. Elle ne vise pas à revoir le fond du pipeline, mais à rendre sa documentation :

- obligatoire à maintenir ;
- traçable par référence de code stable ;
- contrôlable dans le workflow de contribution ;
- cohérente avec le niveau de durcissement déjà atteint dans les stories 66.21 à 66.25.

### État actuel observé dans le dépôt

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) contient déjà une section "Maintenance de cette documentation", mais la formulation actuelle reste de l'ordre de l'attente plus que de l'obligation.
- Le bloc "Dernière vérification manuelle contre le pipeline réel du gateway" utilise encore `commit / tag : HEAD`, ce qui n'est pas exploitable comme preuve d'audit stable.
- Si aucun template PR adapté n'existe déjà, il faudra créer une surface de contribution visible sous `.github/` ou équivalent.
- Une documentation de contribution existe déjà dans le dépôt, mais elle n'est pas aujourd'hui la source explicite d'une règle PR dédiée au pipeline LLM.

### Fichiers à inspecter en priorité

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/gateway.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/gateway.py)
- [backend/app/llm_orchestration/services/prompt_renderer.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/prompt_renderer.py)
- [backend/app/llm_orchestration/services/provider_parameter_mapper.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/provider_parameter_mapper.py)
- [backend/app/llm_orchestration/services/fallback_governance.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/fallback_governance.py)
- [docs/agent/story-34-2-contribution.md](/c:/dev/horoscope_front/docs/agent/story-34-2-contribution.md) comme exemple d'artefact de contribution/documentation déjà présent dans le dépôt

### Contraintes d'implémentation

- Ne pas réécrire massivement le document : le plus petit delta cohérent est attendu.
- Ne pas introduire d'automatisation qui déclare le document "à jour" sans revue humaine.
- Ne pas dupliquer la règle dans plusieurs surfaces divergentes ; choisir une source de contribution visible et la garder alignée avec le document d'architecture.
- Si un template PR est créé, il doit rester sobre, ciblé et centré sur la règle de gouvernance documentaire concernée par cette story.
- La règle de contribution doit porter sur les changements **structurels** du pipeline, pas sur toute retouche locale ou purement cosmétique.

### Testing Requirements

- Ajouter un garde-fou qui vérifie que le document n'accepte plus de référence flottante comme `HEAD`.
- Vérifier que la surface de contribution choisie contient bien une règle normative mentionnant au minimum `_resolve_plan()`, la composition textuelle canonique, providers et fallbacks.
- Vérifier que la formulation autorise une justification explicite lorsque le document reste valide sans modification.
- Vérifier qu'aucune assertion de test n'implique une auto-vérification documentaire purement mécanique.
- Commandes backend/documentaires à exécuter après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `pytest -q`
  - si une suite dédiée est ajoutée : `pytest tests/integration/test_story_66_26_documentation_governance.py -q`

### Previous Story Intelligence

- **66.21** a déjà montré le pattern attendu : une règle de gouvernance doit être explicitement classée, bornée et observable, pas laissée implicite.
- **66.22** a illustré l'importance d'une source de vérité unique et d'un verrou appliqué à plusieurs surfaces (admin, publication, runtime). Cette story reprend ce pattern pour la discipline documentaire.
- **66.23** a durci la taxonomie canonique via une source de vérité centrale et des tests de non-régression ; le même niveau de rigueur est attendu ici, mais appliqué à la maintenance documentaire.
- **66.24** a étendu le gating d'évaluation et a montré l'intérêt d'une cohérence stricte entre doctrine, reporting et tests.
- **66.25** a encore renforcé la valeur stratégique du document [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md), ce qui justifie qu'il devienne un artefact maintenu sous discipline explicite.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [epic-66-llm-orchestration-contrats-explicites.md](/c:/dev/horoscope_front/_bmad-output/planning-artifacts/epic-66-llm-orchestration-contrats-explicites.md)
- [66-21.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-21.md)
- [66-22.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-22.md)
- [66-23.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-23.md)
- [66-24.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-24.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

- Mise à jour de `docs/llm-prompt-generation-by-feature.md` avec une politique de maintenance durcie et des zones d'impact explicites.
- Remplacement de `HEAD` par le commit SHA actuel dans le document d'architecture.
- Création du dossier `.github/` et du fichier `pull_request_template.md` avec la règle de gouvernance LLM.
- Ajout de tests d'intégration pour vérifier la conformité de la documentation et du template PR.
- Durcissement post-review du périmètre documentaire pour inclure explicitement `context_quality` dans le document et dans le template PR.
- Renforcement du garde-fou d'intégration sur le bloc de preuve documentaire avec validation d'un format stable et répétable (date ISO + référence stable non flottante).

### File List

- `docs/llm-prompt-generation-by-feature.md`
- `.github/pull_request_template.md`
- `backend/tests/integration/test_story_66_26_documentation_governance.py`

### Change Log

- 2026-04-11: Implémentation de la story 66.26 (Gouvernance documentaire LLM)
- 2026-04-11: Correctif post-review sur `context_quality` et durcissement du test AC9.

### Review Findings

- [x] [Review][Patch] Link format in PR template [.github/pull_request_template.md] — remove leading slash for relative links.
- [x] [Review][Patch] Ajouter `context_quality` au périmètre explicite de revue documentaire dans le document et le template PR.
- [x] [Review][Patch] Rendre le garde-fou AC9 moins dépendant d'un wording exact et plus robuste sur le format de preuve documentaire.
