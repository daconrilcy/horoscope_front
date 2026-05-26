# CS-328 — Architecture Transition Calculs Interpretations Injection LLM

## Résumé

Produire un rapport d'architecture intermediaire qui consolide les audits CS-324 a CS-327 et propose la cible de transition entre calculs + interpretations et injection LLM.

Le rapport doit definir quelle surface devient l'entree LLM canonique, quelles surfaces legacy doivent etre retirees ou confinees, et quelles stories de refactor seront necessaires ensuite.

## Contexte

Les audits doivent clarifier trois zones :

- les donnees astrologiques disponibles apres refonte ;
- le pipeline LLM natal effectif ;
- les contrats/projections recents potentiellement injectables ;
- la capacite des prompts/assemblies/input schemas a recevoir une entree plus riche.

Cette story transforme ces constats en architecture cible, sans encore refactoriser.

## Objectif

Produire une architecture cible pour la bascule :

```text
CalculationGraph / ChartObjectRuntimeData
-> ChartInterpretationInput
-> contrat interne d'injection LLM
-> prompt runtime
-> audit narrative answer
```

avec une strategie explicite de retrait du legacy.

## Sources obligatoires

Lire et citer explicitement les livrables des stories :

- CS-324
- CS-325
- CS-326
- CS-327

Relire aussi :

- `_story_briefs/cs-245-archi-canonical-astrology-runtime-transition.md`
- `_story_briefs/cs-254-ai-scoring-narrative-input-contract.md`
- `_story_briefs/cs-256-define-structured-facts-v1-stable-hashable-fact-projection.md`
- `_story_briefs/cs-258-define-client-interpretation-projection-v1-by-plan.md`
- `_story_briefs/cs-259-define-narrative-answer-audit-v1.md`
- `_story_briefs/cs-287-implement-client-interpretation-projection-v1-builder-by-plan.md`
- `_story_briefs/cs-291-implement-generic-projection-endpoint.md`

## Questions obligatoires

1. Quelle surface doit devenir l'entree interne canonique des prompts LLM ?
2. Faut-il utiliser directement `AINarrativeInputContract`, etendre `structured_facts_v1`, ou creer un contrat dedie ?
3. Quelles donnees doivent rester dans un bloc factuel, un bloc de signaux interpretatifs, un bloc de limites/missing data, un bloc evidence et un bloc shaping editorial ?
4. Comment eviter que le prompt devienne source de verite astrologique ?
5. Quelles surfaces legacy doivent etre confinees pendant transition ?
6. Comment conserver l'audit `projection_hash` / `llm_input_hash` / `evidence_refs` ?
7. Quel ordre de refactor minimise le risque produit ?

## Périmètre inclus

1. Produire un diagramme textuel de flux cible.
2. Definir les owners cibles par couche.
3. Definir les surfaces de compatibilite legacy et leur date/condition de retrait.
4. Proposer un contrat cible d'injection LLM au niveau conceptuel, sans implementation.
5. Proposer une strategie de mapping vers `NatalExecutionInput` / `ExecutionContext`.
6. Proposer une liste de stories candidates de refactor, priorisees.

## Hors périmètre

- Implementer le contrat cible.
- Modifier les prompts.
- Modifier les providers.
- Modifier la securite, le CI ou les astrologues.
- Modifier les endpoints publics.
- Supprimer du code legacy.

## Livrable attendu

Créer un dossier d'architecture :

```text
_condamad/architecture/calculs-interpretations-injection-llm/<YYYY-MM-DD-HHMM>/
```

avec :

- `00-architecture.md` : architecture cible ;
- `01-evidence-map.md` : mapping des audits vers decisions ;
- `02-target-contract.md` : contrat cible conceptuel ;
- `03-legacy-transition.md` : plan de confinement/retrait legacy ;
- `04-story-candidates.md` : candidates de refactor priorisees ;
- `05-risk-register.md` : risques et mitigations.

## Matrices obligatoires

### Matrice 1 — Surfaces

| Surface | Statut actuel | Statut cible | Owner actuel | Owner cible | LLM input | Public | Legacy | Action recommandee |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Surfaces minimales :

- `chart_json`
- `natal_data`
- `astro_context`
- `evidence_catalog`
- `ChartObjectRuntimeData`
- `ChartInterpretationInputRuntimeData`
- `structured_facts_v1`
- `client_interpretation_projection_v1`
- `AINarrativeInputContract`
- `narrative_answer_audit_v1`

### Matrice 2 — Blocs cible d'injection

| Bloc | Contenu | Source canonique | Source interdite | Hashable | Prompt-visible | Audit-visible | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |

Blocs minimaux :

- faits structurels ;
- signaux interpretatifs ;
- limites et donnees manquantes ;
- preuves / evidence refs ;
- shaping editorial par plan ;
- provenance et versions ;
- exclusions explicites.

### Matrice 3 — Stories candidates

| Priorite | Story candidate | But | Prerequis | Risque | Validation attendue |
| --- | --- | --- | --- | --- | --- |

## Critères d'acceptation

1. Les decisions d'architecture sont rattachees aux audits.
2. La cible separe calcul, interpretation pre-narrative, injection LLM et prompt final.
3. Les surfaces legacy a confiner sont listees.
4. Le contrat cible est assez precis pour rediger des stories de refactor.
5. Les stories candidates n'incluent pas de modification de prompt redactionnel.
6. Aucune modification applicative n'est realisee.

## Validation attendue

```powershell
Test-Path .\_condamad\audits\calculs-interpretations-vers-llm
Test-Path .\_condamad\audits\pipeline-prompt-llm-natal
Test-Path .\_condamad\audits\projections-interpretatives-llm-input-readiness
Test-Path .\_condamad\audits\configuration-prompts-placeholders-input-schema
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## Risques

Le risque principal est de produire une architecture qui melange projection produit et entree LLM interne. La cible doit rester orientee owner canonique, auditabilite et retrait progressif du legacy.
