# CS-329 — Rapport Synthese Transition Injection Prompts LLM

## Résumé

Produire un rapport `.md` complet, precis et exploitable qui resume la situation apres les audits CS-324 a CS-327 et le rapport d'architecture CS-328.

Ce rapport doit permettre de rediger ensuite des briefs de stories de refactor pour la bascule :

```text
calculs astrologiques + interpretations pre-narratives
-> injection structuree dans les prompts LLM
```

## Contexte

L'objectif final est de supprimer le legacy et de faire des injections qualitatives dans les prompts LLM :

- plus riches ;
- plus factuelles ;
- plus structurees ;
- basees sur des calculs et interpretations existants ;
- auditables ;
- sans laisser de place a l'invention astrologique.

Cette story ne refactorise rien. Elle produit le rapport de synthese qui transforme les audits et l'architecture en base de travail pour les futures stories.

## Objectif

Generer un document de synthese final :

```text
_condamad/reports/calculs-interpretations-vers-prompts-llm/<YYYY-MM-DD-HHMM>/rapport-transition-injection-prompts-llm.md
```

Le rapport doit etre suffisamment complet pour servir de source aux briefs de refactor suivants.

## Sources obligatoires

Lire et citer explicitement :

- livrables CS-324 ;
- livrables CS-325 ;
- livrables CS-326 ;
- livrables CS-327 ;
- livrables CS-328.

Relire les fichiers code les plus critiques si un point des audits semble contradictoire :

- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/services/chart/json_builder.py`

## Structure obligatoire du rapport

Le rapport final doit contenir :

1. Executive summary.
2. Etat actuel de l'injection LLM.
3. Carte des surfaces legacy.
4. Carte des surfaces issues de la refonte recente.
5. Carte des donnees disponibles mais non exploitees.
6. Architecture cible recommandee.
7. Contrat cible d'injection LLM recommande.
8. Strategie de retrait du legacy.
9. Priorisation des refactors.
10. Liste des futures stories recommandees.
11. Risques et limites.
12. Annexes de preuves.

## Questions obligatoires

1. Quel est le diagnostic final sur la transition calculs/interpretion vers prompt LLM ?
2. Quelles donnees sont injectees aujourd'hui et par quel chemin ?
3. Quelles donnees devraient etre injectees demain ?
4. Quels elements legacy faut-il retirer, remplacer ou confiner ?
5. Quel contrat cible doit guider les futures stories ?
6. Quelle sequence de refactor est la plus pragmatique ?
7. Quels tests ou guardrails seront necessaires dans les futures stories ?

## Périmètre inclus

1. Consolider les audits et l'architecture.
2. Rediger un rapport unique, complet et precis.
3. Proposer une roadmap de refactor par stories candidates.
4. Decrire les validations attendues pour les futures stories.
5. Identifier les inconnues restantes qui necessitent decision produit/technique.

## Hors périmètre

- Implementer les refactors.
- Modifier les prompts.
- Modifier les generateurs LLM.
- Modifier la securite, le CI ou les astrologues.
- Modifier les endpoints publics.
- Executer des appels LLM reels.

## Livrable attendu

Créer :

```text
_condamad/reports/calculs-interpretations-vers-prompts-llm/<YYYY-MM-DD-HHMM>/rapport-transition-injection-prompts-llm.md
```

Le rapport doit inclure une section finale `Stories de refactor recommandees` avec au minimum :

- une story de definition du contrat cible d'injection ;
- une story de branchement du contrat cible dans `NatalExecutionInput` / `ExecutionContext` ;
- une story de migration des use cases natals hors `chart_json` legacy ;
- une story de preservation hash/audit/evidence ;
- une story de tests de non-invention et de non-regression ;
- une story de retrait progressif des surfaces legacy.

## Critères d'acceptation

1. Le rapport final existe au chemin attendu.
2. Le rapport cite les audits et l'architecture.
3. Le rapport distingue clairement `legacy`, `recent-refonte`, `a conserver`, `a refactoriser`, `a supprimer`.
4. Le rapport contient une architecture cible et une sequence de refactor.
5. Le rapport permet de rediger directement les prochains briefs de stories.
6. Aucune modification applicative n'est realisee.

## Validation attendue

```powershell
Test-Path .\_condamad\reports\calculs-interpretations-vers-prompts-llm
rg -n "legacy|recent-refonte|contrat cible|chart_json|structured_facts_v1|AINarrativeInput|NatalExecutionInput|ExecutionContext|Stories de refactor recommandees" .\_condamad\reports\calculs-interpretations-vers-prompts-llm
git status --short -- _condamad _story_briefs backend/app backend/tests
```

## Risques

Le risque principal est de produire une synthese trop generale. Le rapport doit rester ancre dans les preuves des audits et aboutir a des stories de refactor concretes.
