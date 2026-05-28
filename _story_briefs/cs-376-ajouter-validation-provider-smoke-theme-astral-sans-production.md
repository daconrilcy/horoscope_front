# CS-376 - Ajouter Validation Provider Smoke Theme Astral Sans Production

<!-- Commentaire global: ce brief cadre une validation optionnelle non production du payload theme astral jusqu'au provider LLM. -->

## Resume

Ajouter une validation de type smoke/evaluation non production pour verifier qu'un provider LLM accepte le nouveau payload `theme_astral_llm_input_v1` et respecte globalement le contrat de sortie, sans utiliser ce test comme dependance obligatoire de la CI standard.

## Contexte

Les audits CS-368 et CS-369 acceptent un risque residuel: aucun appel provider LLM reel n'a ete effectue. Le code prouve le builder, le gateway, les exemples et les tests, mais pas le comportement provider.

Pour une implementation "parfaite", il faut au moins un chemin explicite de validation manuelle ou semi-automatique qui exerce le provider en environnement non production.

## Objectif

Creer une validation non production qui:

- prend un payload exemple `theme_astral`;
- appelle le provider configure uniquement si les secrets/env vars existent;
- valide que la reponse respecte `theme_astral_response_contract_v1`;
- n'est jamais obligatoire sans credentials;
- documente clairement les couts, preconditions et limites.

## Perimetre inclus

1. Lire les pratiques existantes d'appel provider et de validation schema.
2. Ajouter un script ou test marque `provider_smoke` si une convention existe.
3. Declarer le marker pytest si un nouveau marker est ajoute.
4. Proteger l'execution par variable d'environnement explicite.
5. Ajouter un timeout, un plafond de cout implicite et une unique tentative par run.
6. Ne jamais exposer de secret.
7. Utiliser le payload exemple premium ou basic.
8. Valider le JSON de sortie contre le contrat.
9. Documenter la commande dans un fichier de preuve ou README.

## Hors perimetre

- Rendre le test obligatoire en CI standard.
- Changer le provider par defaut.
- Stocker des reponses LLM contenant des donnees sensibles.
- Ameliorer le contenu redactionnel par prompt engineering non demande.

## Sources obligatoires

- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/tests/**`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/**`
- `backend/pyproject.toml`
- docs OpenAI officielles si un usage API doit etre confirme

## Criteres d'acceptation

1. Le smoke provider est documente et desactive par defaut.
2. Sans credentials ou variable explicite, il skip proprement.
3. Avec credentials, il appelle le provider une seule fois sur un payload non production.
4. La reponse est validee contre `theme_astral_response_contract_v1`.
5. Aucun secret n'est affiche ou persiste.
6. Le rapport explique que ce test complete les preuves runtime sans remplacer les tests deterministes.
7. Le marker `provider_smoke` est declare ou une convention existante est reutilisee.
8. Le test ne sauvegarde pas la reponse complete du LLM par defaut; seules les metadonnees non sensibles et le verdict schema peuvent etre journalises.
9. Le test est skip par defaut sur CI standard et en local sans opt-in.

## Commandes de validation minimales

Sans provider:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests --tb=short -m "not provider_smoke"
```

Avec provider, seulement si explicitement autorise:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
$env:RUN_THEME_ASTRAL_PROVIDER_SMOKE='1'
python -B -m pytest -q tests -m provider_smoke --tb=short
```

Verification de non-execution accidentelle:

```powershell
rg -n "provider_smoke|RUN_THEME_ASTRAL_PROVIDER_SMOKE|OPENAI_API_KEY" tests pyproject.toml
```

## Risques

Le risque principal est de rendre la CI fragile, couteuse ou dependante d'un service externe. Le smoke doit etre opt-in, documente, et strictement separe des validations deterministes.
