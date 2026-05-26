# Rapport Transition Injection Prompts LLM

<!-- Commentaire global: ce rapport consolide CS-324 a CS-328 en base de cadrage pour les futures stories de refactor LLM. -->

## Executive summary

Diagnostic final: la transition `calculs astrologiques + interpretations pre-narratives -> injection structuree dans les prompts LLM`
est necessaire et non encore realisee dans le chemin natal audite.

Aujourd'hui, le chemin LLM natal reste centre sur `chart_json`, `natal_data`, `evidence_catalog` et `astro_context`.
Les audits CS-324 et CS-325 montrent que `chart_json` est le principal contenu prompt-visible, tandis que plusieurs champs
transportes au runtime ne deviennent pas automatiquement visibles dans le message utilisateur.

Les surfaces issues de la refonte recente existent: `structured_facts_v1`, `AINarrativeInputContract`,
`client_interpretation_projection_v1`, `ChartInterpretationInputRuntimeData`, `CalculationGraph` et `ChartObjectRuntimeData`.
CS-326 et CS-328 concluent que `AINarrativeInputContract` est le meilleur owner interne cible, avec `structured_facts_v1`
comme substrat factuel hashable et `llm_astrology_input_v1` comme wrapper/schema LLM versionne.

La roadmap doit donc d'abord formaliser le contrat cible, puis aligner hashes/preuves, schemas runtime, garde
prompt-visible/runtime-only et retrait progressif du legacy. Aucune modification applicative n'est realisee par CS-329.

## Etat actuel de l'injection LLM

| Surface | Statut observe | Visibilite LLM actuelle | Source |
|---|---|---|---|
| `chart_json` | legacy, projection publique/historique | prompt-visible par defaut ou via `{{chart_json}}` | CS-324, CS-325 |
| `natal_data` | legacy, meme projection en dict | runtime-only dans le chemin audite | CS-324, CS-325 |
| `evidence_catalog` | validation/evidence derivee de `chart_json` | validation-only dans les preuves CS-325 | CS-324, CS-325 |
| `astro_context` | transition, contexte astral-point etroit | runtime-only, pas owner global | CS-324, CS-325 |
| `plan`, `level`, `module`, `variant_code` | controle runtime/use-case | runtime-only | CS-325 |

Reponse aux questions 1 et 2 du brief: le diagnostic final est un decalage entre les donnees riches disponibles et l'injection
reelle. Les donnees injectees aujourd'hui passent par `NatalExecutionInput`, puis `ExecutionContext` et `LLMGateway`; seul
`chart_json` est prouve prompt-visible dans le chemin audite.

## Carte des surfaces legacy

| Surface legacy | Risque | Action cible | Source |
|---|---|---|---|
| `chart_json` | source de verite de facto alors que des facts recents existent | confiner en compatibilite de transition | CS-324 F-001/F-002, CS-327 F-001 |
| `natal_data` | duplication du meme payload que `chart_json` | supprimer ou borner apres contrat cible | CS-324 F-002, CS-327 F-002 |
| `evidence_catalog` derive de `chart_json` | confusion entre grounding prompt et validation output | redefinir en `evidence_refs` + role validation/audit | CS-324 F-003, CS-325 F-003 |
| `/users`, `free_short`, schemas v1/v2/v3 | compatibilites non classees | registre keep/remove/needs-user-decision | CS-325 F-004 |
| placeholders `chart_json` | schema/prompt plat historique | remplacer par schema structure sans wildcard | CS-327 F-001/F-003 |

Les elements a retirer, remplacer ou confiner sont donc `chart_json`, `natal_data`, les branches legacy natales, les fallbacks
schema/prompt et l'ambiguite `evidence_catalog`. Aucun retrait n'est fait dans cette story.

## Carte des surfaces issues de la refonte recente

| Surface recent-refonte | Role recommande | Restriction | Source |
|---|---|---|---|
| `CalculationGraph` | source de calcul interne | jamais payload prompt brut | CS-328 |
| `ChartObjectRuntimeData` | runtime riche interne | jamais provider/public/prompt brut | CS-324, CS-328 |
| `ChartInterpretationInputRuntimeData` | pont pre-narratif | alimente le contrat narratif, pas le prompt directement | CS-328 |
| `structured_facts_v1` | faits hashables, projection stable | source factuelle, pas contrat narratif complet | CS-326, CS-328 |
| `AINarrativeInputContract` | owner interne cible | doit etre mappe vers un schema LLM explicite | CS-326, CS-328 |
| `client_interpretation_projection_v1` | shaping B2C par plan | pas source factuelle canonique du prompt | CS-326, CS-328 |
| `narrative_answer_audit_v1` | audit/replay/hash apres generation | jamais input prompt | CS-326, CS-328 |

## Carte des donnees disponibles mais non exploitees

| Donnee disponible | Etat | Utilisation cible | Validation attendue |
|---|---|---|---|
| `structured_facts_v1` | available-not-injected | bloc `facts` hashable | tests de hash et scans owner |
| `AINarrativeInputContract` | available-not-injected | contrat interne facts/signals/readiness/provenance | tests de forme et mapping |
| `ChartInterpretationInputRuntimeData` | disponible en amont interpretation | source pre-narrative controlee | scan sans exposition brute |
| `projection_hash` | disponible cote projections/audit | hash de faits stables | tests de stabilite |
| `llm_input_hash` | cible audit LLM | hash de tous les blocs influencant le prompt | tests invalidation |
| `evidence_refs` | cible evidence | refs visibles/validables selon decision owner | tests validator/audit |

Reponse a la question 3: demain, l'injection devrait porter faits structurels, signaux interpretatifs, limites/donnees
manquantes, preuves, shaping par plan et provenance versionnee. Elle ne doit pas injecter le runtime brut ni les projections B2C
comme faits.

## Architecture cible recommandee

Flux cible recommande par CS-328:

```text
CalculationGraph / ChartObjectRuntimeData
  -> ChartInterpretationInputRuntimeData
  -> AINarrativeInputContract
  -> llm_astrology_input_v1
  -> prompt runtime
  -> narrative_answer_audit_v1
```

`NatalExecutionInput` doit recevoir le bloc structure `llm_astrology_input_v1` ou un champ equivalent explicitement versionne.
`ExecutionContext` doit porter l'identite de requete, use-case, plan/module, locale, prompt ref et donnees runtime de controle,
pas les faits astrologiques bruts comme source de verite cachee.

## Contrat cible d'injection LLM recommande

| Section | Source | Conclusion | Action | Validation attendue |
|---|---|---|---|---|
| `facts` | `structured_facts_v1` | faits stables et hashables | injecter via contrat cible | hash stability tests |
| `signals` | `AINarrativeInputContract` | signaux pre-narratifs | garder owner interpretation | contract shape tests |
| `limits` | facts + narrative input | missing data et exclusions | rendre prompt-visible si utile | tests non-invention |
| `evidence` | `evidence_refs` | refs et role validation/audit | decision visible vs validation-only | validator tests |
| `shaping` | projection client metadata | consignes produit, pas faits | separer des facts | tests de separation |
| `provenance` | audit narrative | versions et hashes | stocker apres generation | audit/replay tests |
| `exclusions` | architecture guards | sources interdites | scan raw runtime et legacy | reintroduction guard |

Reponse a la question 5: le contrat cible doit etre `llm_astrology_input_v1`, wrapper LLM autour de
`AINarrativeInputContract`, avec `structured_facts_v1` comme source factuelle et `narrative_answer_audit_v1` comme preuve
post-generation.

## Strategie de retrait du legacy

1. Declarer le contrat cible et la transition-condition pour `chart_json` / `natal_data`.
2. Aligner `projection_hash`, `llm_input_hash` et `evidence_refs`.
3. Faire declarer le schema moderne par les use cases natals.
4. Ajouter les tests prompt-visible/runtime-only/validation-only/audit-only.
5. Classer `/users`, `free_short`, schemas et fallbacks en `intentional`, `delete-candidate` ou `needs-user-decision`.
6. Retirer ou documenter definitivement `chart_json` / `natal_data` apres validation.

Reponse a la question 4: les surfaces legacy doivent etre retirees seulement apres contrat cible, tests et decisions owner.
Avant cela, elles restent confinees et nommees comme compatibilite.

## Priorisation des refactors

| Priorite | Refactor | Pourquoi maintenant | Dependances |
|---|---|---|---|
| P1 | Definition du contrat cible d'injection | bloque tout le reste | decision architecture owner |
| P2 | Preservation hash, audit et evidence | rend l'injection auditable | P1 + decision evidence role |
| P3 | Branchement runtime/config dans `NatalExecutionInput` et `ExecutionContext` | rend le contrat executable | P1/P2 |
| P4 | Tests prompt-visible/runtime-only | evite l'injection accidentelle | P3 |
| P5 | Migration hors `chart_json` legacy | retire le carrier historique | P1-P4 |
| P6 | Retrait progressif des surfaces historiques | nettoie branches et fallbacks | decisions product owner |

Reponse a la question 6: la sequence pragmatique est contrat -> preuves/hash -> schema runtime -> guards -> migration -> retrait.

## Liste des futures stories recommandees

### Stories de refactor recommandees

1. Definition du contrat cible d'injection.
   - Objectif: formaliser `llm_astrology_input_v1` autour de `AINarrativeInputContract`.
   - Sources: CS-324 F-001/F-003, CS-325 F-001, CS-326 F-001, CS-327 F-001, CS-328 P1.
   - Validation: contract shape tests, scan owner choisi, scan negatif `ChartObjectRuntimeData` dans prompt/provider.

2. Branchement du contrat cible dans `NatalExecutionInput` et `ExecutionContext`.
   - Objectif: mapper facts/signals/limits/evidence/shaping/provenance dans un champ schema-owned.
   - Sources: CS-328 `Target Layer Owners And Runtime Mapping`, CS-327 F-001/F-002.
   - Validation: tests gateway/service, absence de fallback silencieux vers `chart_json`.

3. Migration des use cases natals hors `chart_json` legacy.
   - Objectif: remplacer `chart_json` comme owner prompt moderne.
   - Sources: CS-324 F-002, CS-325 F-001, CS-327 F-001.
   - Validation: scans `input_schema`, placeholders, use-case registry, no new legacy alias.

4. Preservation hash, audit et evidence.
   - Objectif: aligner `projection_hash`, `llm_input_hash`, `evidence_refs` et workflow de rejet.
   - Sources: CS-324 F-003, CS-325 F-003, CS-326 F-003, CS-328 P2.
   - Validation: hash stability, invalidation, validator/audit tests.

5. Tests de non-invention et de non-regression.
   - Objectif: prouver la frontiere prompt-visible/runtime-only/validation-only/audit-only.
   - Sources: CS-325 F-002, CS-327 F-003, CS-328 P4.
   - Validation: tests `LLMGateway`, `PromptRenderer`, validation payload et assertions negatives.

6. Retrait progressif des surfaces historiques.
   - Objectif: classer puis retirer ou documenter `/users`, `free_short`, schemas, fallbacks, `chart_json`, `natal_data`.
   - Sources: CS-324 F-002/F-004, CS-325 F-004, CS-327 F-004, CS-328 P5.
   - Validation: registre de branches, tests cibles, scans `legacy|fallback|transition-condition`.

## Risques et limites

- Risque principal: produire des stories de refactor trop generales sans owner de contrat. Mitigation: P1 doit nommer owner,
  schema, champs, exclusions et stop condition.
- Risque de confusion B2C/prompt: `client_interpretation_projection_v1` doit rester shaping produit, pas facts.
- Risque de fausse auditabilite: `evidence_catalog` actuel prouve surtout la validation, pas le grounding prompt.
- Risque de casse produit: `/users`, `free_short` et schemas compatibilite doivent etre classes avant suppression.
- Limite CS-329: ce rapport ne modifie aucun code, prompt, endpoint, provider, frontend, DB ou migration.

Reponse a la question 7: les futures stories auront besoin de tests de contrat, hash, evidence refs, gateway message
composition, prompt renderer, validation payload, scans negatifs raw runtime et scans anti-fallback/anti-alias.

## Annexes de preuves

| Source | Chemin | Utilisation |
|---|---|---|
| CS-324 | `_condamad/audits/calculs-interpretations-vers-llm/2026-05-26-0000/**` | surfaces calculs/interpretes vs LLM |
| CS-325 | `_condamad/audits/pipeline-prompt-llm-natal/2026-05-26-0000/**` | pipeline prompt, visibilite et branches |
| CS-326 | `_condamad/audits/projections-interpretatives-llm-input-readiness/2026-05-26-0000/**` | readiness projections et contrat cible |
| CS-327 | `_condamad/audits/configuration-prompts-placeholders-input-schema/2026-05-26-0000/**` | schemas, placeholders et runtime validation |
| CS-328 | `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/**` | architecture cible et roadmap |

Les citations detaillees, contradictions et disponibilites sont conservees dans `evidence-sources.md`.
