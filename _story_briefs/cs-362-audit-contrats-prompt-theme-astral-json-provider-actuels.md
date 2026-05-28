# CS-362 - Audit Contrats Prompt Theme Astral JSON Provider Actuels

<!-- Commentaire global: ce brief cadre l'audit des structures JSON actuelles envoyees au provider LLM pour le theme astral. -->

## Resume

Auditer les JSON provider actuels du theme astral pour verifier les divergences structurelles entre `free`, `basic` et `premium`, la duplication des donnees, l'exposition du plan commercial et les instructions incoherentes comme des consignes premium dans un payload basic.

## Contexte

Les exemples actuels montrent:

- un squelette top-level proche;
- des messages differents selon le plan;
- une persona absente en `free` et presente en `basic/premium`;
- des schemas de sortie differents;
- des quantites de donnees differentes;
- le plan commercial visible dans le payload;
- une duplication des donnees dans `developer` et `user`;
- des consignes premium dans le prompt basic.

Il faut transformer ces constats en audit source-aligne avant architecture cible.

## Objectif

Produire un diagnostic de contrat:

- ce qui est stable;
- ce qui diverge;
- ce qui doit rester variable par plan;
- ce qui doit devenir backend-only;
- ce qui doit etre supprime du payload;
- ce qui doit etre preserve dans le nouveau contrat.

## Perimetre inclus

1. Comparer les fichiers `free-provider-payload.json`, `basic-provider-payload.json`, `premium-provider-payload.json`.
2. Comparer le top-level, les `messages`, le `user` payload, `response_format`, `provider_parameters`.
3. Extraire les divergences de structure et les divergences de valeur.
4. Identifier les donnees inutiles au LLM: `plan`, metadata runtime, audit, hashes, traces, debug.
5. Identifier les donnees indispensables au LLM: delivery profile, feature context, astrologer voice, interpretation material, output contract.
6. Produire une matrice "keep / move backend-only / replace / remove".

## Hors perimetre

- Modifier les JSON.
- Modifier le runtime.
- Redefinir l'architecture cible en detail; cela appartient a CS-363.
- Faire un appel provider.

## Sources obligatoires

- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json`
- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/intermediate-data.json`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py`
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py`

## Livrable attendu

Creer:

```text
_condamad/audits/theme-astral-prompt-contract/<YYYY-MM-DD-HHMM>/02-audit-json-provider-theme-astral-actuels.md
```

Le rapport doit contenir:

1. Executive summary.
2. Tableau comparatif `free/basic/premium`.
3. Divergences structurelles.
4. Divergences de quantite de donnees.
5. Donnees inutiles ou backend-only.
6. Donnees manquantes pour la redaction.
7. Incoherences de prompt.
8. Recommandations pour CS-363.

## Criteres d'acceptation

1. Les trois payloads sont compares de maniere mecanique et narrative.
2. Le rapport distingue structure et valeurs.
3. Le rapport valide ou invalide explicitement le constat de structure non stable.
4. Le rapport indique que le plan commercial ne doit pas etre visible au LLM.
5. Le rapport identifie la duplication `developer` / `user`.
6. Le rapport identifie les consignes premium dans basic si elles sont confirmees.
7. Aucun fichier JSON ou runtime n'est modifie.

## Validation attendue

```powershell
rg -n "free|basic|premium|structure|developer|user|response_format|provider_parameters|backend-only|plan commercial" _condamad/audits/theme-astral-prompt-contract
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json | ConvertFrom-Json | Out-Null
```

## Risques

Le risque principal est de conclure trop vite que toute divergence est mauvaise. Certaines valeurs doivent varier par plan; ce sont les cles et la forme de feature qui doivent rester stables.
