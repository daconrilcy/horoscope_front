# CS-358 - Generer Exemples JSON Prompts Theme Astral Par Plan

<!-- Commentaire global: ce brief cadre la generation d'exemples JSON finaux de prompts de theme astral sans appel au moteur LLM. -->

## Resume

Generer un exemple complet de donnees, interpretations intermediaires, prompts et JSON final pour une personne nee le 24 avril 1974 a 11h00 du matin a Paris en France, pour les plans `free`, `basic` et `premium`.

Le livrable doit montrer ce qui serait envoye au moteur LLM, mais ne doit jamais appeler le provider LLM.

## Contexte

CS-356 doit expliquer la construction des prompts. CS-357 doit fournir les diagrammes. Cette story produit un exemple concret et auditable afin de verifier que la documentation est comprehensible et que la difference entre plans se voit dans un payload final.

Cas exemple impose:

- date de naissance: `1974-04-24`;
- heure de naissance: `11:00:00`;
- lieu: `Paris, France`;
- timezone attendue: `Europe/Paris`;
- plans: `free`, `basic`, `premium`;
- aucun appel au moteur LLM.

## Decision obligatoire sur l'heure de naissance

La demande fournit maintenant l'heure de naissance. Le livrable doit donc:

- utiliser `11:00:00` heure locale `Europe/Paris`;
- normaliser l'instant en UTC dans les donnees intermediaires;
- calculer ou fixture explicitement les maisons, l'Ascendant et le MC a partir de cette heure;
- ne pas conserver l'ancien fallback documentaire sans heure.

## Objectif

Produire des exemples qui montrent:

- les donnees d'entree normalisees;
- les donnees astrologiques calculees ou fixturees;
- les interpretations/signaux utilises pour le prompt;
- les limites et incertitudes;
- les differences `free`, `basic`, `premium`;
- les messages finaux `system`, `developer`, persona, `user`;
- le JSON final pret pour le moteur LLM;
- l'absence d'appel provider.

## Perimetre inclus

1. Lire CS-356 et CS-357 si disponibles.
2. Inspecter les tests ou fixtures existants permettant de generer un payload local sans provider.
3. Si possible, utiliser le runtime local ou des builders existants avec provider double/local pour produire les donnees.
4. Si le runtime local exige trop de configuration, produire des fixtures documentaires synthetiques mais les marquer explicitement comme exemples.
5. Generer trois exemples: `free`, `basic`, `premium`.
6. Inclure les interpretations/signaux intermediaires avant prompt final.
7. Inclure le JSON final provider-handoff attendu, sans credentials et sans reponse provider.
8. Ajouter une validation qui prouve qu'aucun appel externe n'a ete effectue.

## Hors perimetre

- Appeler OpenAI, un autre LLM ou tout provider externe.
- Persister une vraie interpretation utilisateur.
- Creer une nouvelle branche Git.
- Modifier les prompts de production.
- Changer les calculs astrologiques.
- Inventer une heure de naissance sans la declarer comme convention de demonstration.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` si CS-356 existe
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py`
- `backend/tests/evaluation/test_differentiation.py`

## Livrables attendus

Creer un dossier:

```text
_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/
```

Avec au minimum:

```text
README.md
free-provider-payload.json
basic-provider-payload.json
premium-provider-payload.json
intermediate-data.json
```

Le `README.md` doit expliquer comment les fichiers ont ete produits et confirmer qu'aucun appel provider n'a ete fait.

## Structure obligatoire des JSON finaux

Chaque fichier `*-provider-payload.json` doit representer le payload final juste avant handoff provider et contenir au minimum:

```json
{
  "use_case": "natal_*",
  "plan": "free|basic|premium",
  "mode": "structured",
  "provider_call_performed": false,
  "model": "<model configured or placeholder documented>",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "developer", "content": "..."},
    {"role": "developer", "content": "<persona astrologue si active>"},
    {"role": "user", "content": "{...json prompt-visible...}"}
  ],
  "response_format": {
    "type": "json_schema",
    "json_schema": {}
  },
  "provider_parameters": {
    "max_tokens": 0,
    "temperature": 0,
    "reasoning_effort": null,
    "verbosity": null
  },
  "audit_excluded_from_prompt": [
    "evidence",
    "provenance",
    "projection_hash",
    "llm_input_hash",
    "provider_response",
    "observability"
  ]
}
```

Adapter les valeurs aux contrats reels si le runtime local permet de les extraire. Ne pas inclure de secret, token API ou reponse provider.

## Structure obligatoire de `intermediate-data.json`

Le fichier doit contenir:

- `birth_input`;
- `normalization`;
- `calculation_assumptions`;
- `structured_facts_v1_sample`;
- `narrative_signals_sample`;
- `client_projection_sample`;
- `llm_astrology_input_v1_by_plan`;
- `plan_differences`;
- `limits`;
- `data_quality_warnings`;
- `generation_method`;
- `provider_call_performed: false`.

## Contraintes d'exactitude

- Si les positions astrologiques sont calculees par le runtime existant, citer la commande et le test de non-appel provider.
- Si les positions sont synthetiques, les etiqueter clairement comme exemple non verifie et ne pas les presenter comme ephemerides reelles.
- Si les positions sont calculees localement, documenter le moteur, la timezone, l'UTC, les coordonnees et le systeme de maisons.
- Ne pas mettre de donnees audit-only dans le message `user`.
- Les champs `evidence` peuvent exister dans `intermediate-data.json`, mais doivent etre absents des messages provider.
- Les trois plans doivent montrer des differences reelles de contenu ou de budget.
- Les exemples doivent rester lisibles et versionnables.

## Criteres d'acceptation

1. Les quatre fichiers attendus existent.
2. Les JSON sont valides.
3. Les trois plans ont un payload distinct.
4. Chaque payload contient les messages finaux dans l'ordre runtime attendu.
5. Chaque payload indique explicitement `provider_call_performed: false`.
6. Le message `user` ne contient que les blocs prompt-visibles.
7. Les donnees exclues sont listees hors prompt.
8. L'heure de naissance manquante est traitee comme hypothese documentee.
9. Le README explique si les donnees sont runtime-generated ou synthetiques.
10. Aucune cle API, reponse provider ou secret n'est present.

## Validation attendue

Documentation et JSON:

```powershell
rg -n "provider_call_performed|1974-04-24|11:00:00|Paris|free|basic|premium|runtime_generated" _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json | ConvertFrom-Json | Out-Null
Get-Content _condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/intermediate-data.json | ConvertFrom-Json | Out-Null
```

Si une commande Python est necessaire pour produire ou verifier les donnees, activer le venv avant toute commande:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/llm_orchestration/test_llm_astrology_input_boundaries.py --tb=short
```

## Risques

Le risque principal est de laisser croire que l'exemple est une prediction ou une interpretation LLM reelle. Le livrable doit rester un exemple de payload de prompt, sans reponse provider et sans promesse d'exactitude astrologique lorsque l'heure est une convention de demonstration.
