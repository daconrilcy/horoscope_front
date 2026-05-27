# CS-343 - Audit Inventaire Surfaces Generation Prompt LLM

<!-- Commentaire global: ce brief cadre l'audit d'inventaire des surfaces qui participent directement ou indirectement a la generation des prompts LLM. -->

## Resume

Produire un audit exhaustif des surfaces de code, configuration, seeds, tests et artefacts CONDAMAD qui participent a la generation des prompts LLM actuels.

Cette story ne modifie pas le runtime. Elle construit la carte source necessaire aux stories suivantes.

## Contexte

Les stories CS-324 a CS-342 ont traite plusieurs frontieres du prompt natal moderne: `llm_astrology_input_v1`, extinction des carriers legacy, separation prompt/audit, evidence hors prompt, validation et persistence. Il manque maintenant une cartographie complete et lisible du code effectivement en place pour generer les prompts.

## Objectif

Identifier toutes les surfaces actives ou historiques qui peuvent influencer:

- la selection de use case;
- la resolution d'assembly;
- le rendu du developer prompt;
- la composition des messages system/developer/persona/user;
- le payload utilisateur;
- le handoff provider;
- la validation et la persistence qui referencent prompt, input LLM ou audit.

## Perimetre inclus

1. Auditer les owners backend LLM sous `backend/app/domain/llm/**`.
2. Auditer les services de generation sous `backend/app/services/llm_generation/**`.
3. Auditer les builders astrologiques qui alimentent `llm_astrology_input_v1`.
4. Auditer les models, migrations, seeds et bootstrap LLM qui portent prompts, assemblies, personas, schemas et profils.
5. Auditer les routeurs admin/public/internal qui declenchent ou exposent la generation LLM.
6. Auditer les tests backend qui verrouillent la generation, la validation ou les gardes anti-legacy.
7. Produire un registre des surfaces avec statut: active runtime, active configuration, test guard, bootstrap/seed, observability/audit, historique, dette.

## Hors perimetre

- Modifier le code applicatif.
- Corriger les bugs decouverts.
- Reecrire les prompts.
- Produire la synthese architecture finale.
- Produire le rapport de livraison final.

## Sources a lire

- `_story_briefs/cs-324-audit-surfaces-calculs-interpretations-vers-llm.md`
- `_story_briefs/cs-325-audit-pipeline-prompt-llm-natal-legacy-vs-canonique.md`
- `_story_briefs/cs-327-audit-configuration-prompts-placeholders-input-schema.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-341-sortir-evidence-du-prompt-et-valider-redaction-llm-natale.md`
- `_story_briefs/cs-342-cloturer-process-evidence-hors-prompt-validation-redaction-llm-natale.md`
- `_condamad/stories/story-status.md`

## Fichiers a inspecter en priorite

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/chat/public_chat.py`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/**/test*llm*`
- `backend/tests/**/test*prompt*`

## Livrable attendu

Creer:

```text
_condamad/audits/prompt-generation-cartography/<YYYY-MM-DD-HHMM>/01-surface-inventory-audit.md
```

Le document doit contenir:

1. Resume executif.
2. Table des surfaces inspectees.
3. Statut de chaque surface.
4. Symboles ou fonctions clefs.
5. Preuves par chemin de fichier et nom de symbole.
6. Frontieres connues: prompt-visible, validation-only, audit-only, runtime-only.
7. Occurrences legacy classees.
8. Gaps pour les audits suivants.

## Criteres d'acceptation

1. Le rapport d'audit existe dans `_condamad/audits/prompt-generation-cartography/**`.
2. Chaque surface relevante a un statut explicite.
3. Les surfaces actives sont distinguees des seeds, tests, docs et artefacts historiques.
4. Les chemins vers `gateway.py`, `assembly_resolver.py`, `prompt_renderer.py`, `canonical_use_case_registry.py` et `llm_astrology_input_v1.py` sont couverts.
5. Les gaps sont convertis en questions ou dependances pour CS-344 a CS-350.

## Validation attendue

```powershell
rg -n "prompt|llm|assembly|persona|provider|llm_astrology_input_v1" backend/app backend/tests
rg -n "CS-343|surface-inventory-audit" _condamad _story_briefs
```

## Risques

Le risque principal est de confondre presence textuelle et influence runtime. L'audit doit classer les occurrences par role avant de conclure.

