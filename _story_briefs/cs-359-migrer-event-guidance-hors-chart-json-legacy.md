# CS-359 - Migrer Event Guidance Hors Chart Json Legacy

<!-- Commentaire global: ce brief cadre la migration obligatoire de event_guidance hors du carrier legacy chart_json. -->

## Resume

Migrer ou supprimer `event_guidance` afin qu'aucune dette legacy `chart_json` ne reste dans les contrats, seeds ou chemins provider-capable.

Decision produit: on ne conserve aucune dette. Cette story doit choisir l'option techniquement correcte apres inspection: migrer `event_guidance` vers un input canonique non legacy, ou supprimer le use case si aucun trigger produit supporte n'existe.

## Contexte

CS-353 et CS-354 ont montre que `event_guidance` existe dans `canonical_use_case_registry.py`, `AIEngineAdapter` et les seeds guidance avec `chart_json` et `event_description`, sans trigger public audite. CS-350 corrige maintenant la documentation en classant `event_guidance` comme migration obligatoire.

## Objectif

Eliminer la dependance legacy `chart_json` de `event_guidance` ou supprimer completement la surface si elle n'a pas de contrat produit actif.

## Perimetre inclus

1. Auditer les references code, tests, seeds et docs a `event_guidance`.
2. Verifier s'il existe un trigger produit reel ou seulement des seeds/tests/contrats dormants.
3. Si le use case est conserve:
   - definir l'input canonique attendu;
   - retirer `chart_json` des placeholders et schemas;
   - brancher un input non legacy compatible avec la gouvernance LLM;
   - ajouter les tests de frontiere prompt-visible.
4. Si le use case est supprime:
   - retirer le contrat canonique dormant;
   - retirer les seeds et mappings associes;
   - adapter les tests et docs.
5. Mettre a jour CS-350 et les guardrails si la classification change.

## Hors perimetre

- Conserver `event_guidance` comme dette.
- Reintroduire `chart_json` ou `natal_data` comme prompt-visible moderne.
- Modifier des flux guidance actifs non lies.
- Faire un appel provider reel.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/audits/prompt-generation-document-review/2026-05-27-2246/03-parallel-legacy-processes-audit.md`
- `_condamad/architecture/prompt-generation-document-review/2026-05-27-2338/archi-parallel-legacy-prompt-generation-report.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/tests/**`

## Livrable attendu

Implementation code + tests, ou suppression code + tests, avec evidence sous:

```text
_condamad/stories/CS-359-migrer-event-guidance-hors-chart-json-legacy/evidence/
```

## Criteres d'acceptation

1. Aucun contrat runtime `event_guidance` ne requiert `chart_json`.
2. Si `event_guidance` est conserve, son input est canonique, versionne et teste.
3. Si `event_guidance` est supprime, aucun seed ou mapping runtime ne le conserve.
4. `chart_json` et `natal_data` restent exclus du prompt-visible natal moderne.
5. CS-350 et RG-149 sont mis a jour si la classification change.

## Validation attendue

```powershell
rg -n "event_guidance|chart_json|natal_data" backend/app backend/tests _condamad
rg -n "event_guidance.*migration obligatoire|event_guidance" _condamad/docs/prompt-generation-cartography _condamad/stories/regression-guardrails.md
```

Les commandes Python doivent etre executees apres activation du venv.

## Risques

Le risque principal est de supprimer ou migrer un contrat dormant sans verifier s'il est encore attendu par un flux produit ou admin.
