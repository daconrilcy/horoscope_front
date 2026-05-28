# CS-364 - Definir Persistence Versionnee Contrats Prompt Theme Astral

<!-- Commentaire global: ce brief cadre la mise en place des contrats et structures versionnees en base pour le prompt theme astral. -->

## Resume

Mettre en place la persistence versionnee des contrats de construction de prompt `theme_astral`: squelette provider, contrat d'entree, profil de livraison, contrat de sortie, prompt texts et liens vers astrologue/persona.

Cette story doit s'appuyer sur les mecanismes backend existants: use cases, prompt versions, output schemas, assemblies, personas, execution profiles et migrations LLM.

## Contexte

Le processus de generation de prompt doit devenir modifiable sans changement de code lourd:

- modifier le texte de prompt;
- modifier un output contract;
- changer une politique de delivery profile;
- choisir un astrologue;
- versionner et auditer les changements.

Le nouveau contrat ne doit pas etre hardcode hors des structures existantes si le backend fournit deja un registre versionne.

## Objectif

Creer ou adapter les modeles, schemas et seeds pour enregistrer en base:

- `theme_astral_prompt_contract_v1`;
- `theme_astral_llm_input_v1`;
- `theme_astral_response_contract_v1`;
- `delivery_profile` par profondeur resolue;
- `astrologer_voice` ou liens vers personas;
- prompt templates et assemblies associes.

## Perimetre inclus

1. Lire l'architecture CS-363.
2. Identifier les modeles DB LLM existants reutilisables.
3. Ajouter les migrations minimales si un champ/table manque.
4. Ajouter les schemas Pydantic/domain necessaires.
5. Ajouter les seeds idempotents.
6. Ajouter les tests de migration et de coherence.
7. Documenter comment modifier un contrat ou prompt versionne.

## Hors perimetre

- Construire `interpretation_material`.
- Changer le gateway provider.
- Supprimer le legacy.
- Appeler un provider LLM.
- Ajouter un nouveau dossier racine sous `backend/`.

## Sources obligatoires

- `_condamad/architecture/theme-astral-prompt-contract/**/archi-theme-astral-prompt-contract-v1.md`
- `backend/app/infra/db/models/llm/**`
- `backend/migrations/versions/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/app/domain/llm/configuration/**`
- `backend/tests/**llm**`

## Livrables attendus

Selon l'architecture retenue:

- migrations Alembic si necessaires;
- modeles ou champs DB;
- schemas/domain models;
- seeds idempotents;
- tests unitaires et integration ciblés;
- documentation courte si le mode de modification change.

## Criteres d'acceptation

1. Les contrats de prompt theme astral sont versionnes.
2. Le contrat d'entree, le contrat de sortie et le squelette provider ont un identifiant stable.
3. Les prompts associes sont modifiables via la registry/versioning existante.
4. Les profils de livraison resolus ne divulguent pas le plan commercial au LLM.
5. Les personas/astrologues sont lies sans porter la verite astrologique.
6. Les seeds sont idempotents.
7. Les tests prouvent la persistence, la lecture active et l'incompatibilite de versions invalides.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "theme_astral_prompt_contract|theme_astral_llm_input|theme_astral_response_contract|delivery_profile|astrologer_voice" app tests migrations
```

## Risques

Le risque principal est de dupliquer la registry LLM existante. Toute nouvelle table doit etre justifiee par un manque explicite; sinon reutiliser les surfaces existantes.
