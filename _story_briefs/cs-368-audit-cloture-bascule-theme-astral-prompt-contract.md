# CS-368 - Audit Cloture Bascule Theme Astral Prompt Contract

<!-- Commentaire global: ce brief cadre l'audit final de cloture apres bascule bigbang du contrat prompt theme astral. -->

## Resume

Auditer la cloture de la bascule `theme_astral` apres CS-361 a CS-367 afin de verifier que le nouveau contrat est bien unique, versionne, enrichi par les tables d'interpretation, et que le legacy a ete supprime.

## Contexte

La chaine doit aboutir a:

- un squelette provider stable par feature;
- des valeurs et quantites pilotees par delivery profile;
- aucun `plan` commercial dans le payload LLM;
- un `astrologer_voice` preponderant sur le style;
- un `interpretation_material` issu des tables;
- une persistence/versioning DB;
- une suppression complete du legacy theme astral.

## Objectif

Donner un verdict:

- valide;
- valide avec risques residuels acceptes;
- invalide tant que certains gaps restent.

## Perimetre inclus

1. Lire les livrables CS-361 a CS-367.
2. Relire le code final.
3. Verifier les migrations/seeds/versioning.
4. Verifier les tests et guardrails.
5. Verifier les exemples JSON.
6. Verifier l'absence de legacy runtime actif.
7. Produire un rapport court de cloture.

## Hors perimetre

- Modifier le code.
- Modifier les migrations.
- Ajouter des tests.
- Redecider l'architecture.
- Appeler un provider LLM.

## Sources obligatoires

- `_condamad/audits/theme-astral-prompt-contract/**`
- `_condamad/architecture/theme-astral-prompt-contract/**`
- `_condamad/examples/prompt-generation-cartography/**`
- `backend/app/domain/llm/**`
- `backend/app/domain/astrology/interpretation/**`
- `backend/app/services/llm_generation/natal/**`
- `backend/app/ops/llm/bootstrap/**`
- `backend/tests/**`
- `backend/migrations/versions/**`

## Livrable attendu

Creer:

```text
_condamad/audits/theme-astral-prompt-contract/<YYYY-MM-DD-HHMM>/03-audit-cloture-bascule-theme-astral-prompt-contract.md
```

Le rapport doit contenir:

1. Verdict.
2. Statut des criteres CS-361 a CS-367.
3. Preuve d'utilisation des textes d'interpretation.
4. Preuve de structure stable entre delivery profiles.
5. Preuve de non-exposition du plan commercial.
6. Preuve de persistence/versioning DB.
7. Preuve de suppression legacy.
8. Commandes executees.
9. Risques residuels.

## Criteres d'acceptation

1. Le rapport donne un verdict non ambigu.
2. Chaque critere majeur est prouve par fichier, symbole, test ou commande.
3. Le rapport montre que les textes metier atteignent le payload LLM.
4. Le rapport montre que la structure provider est identique entre profils.
5. Le rapport montre que le plan commercial reste backend-only.
6. Le rapport montre que le legacy theme astral n'a plus de chemin actif.
7. Les risques residuels sont explicitement acceptes ou convertis en stories.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
pytest -q tests --tb=short
rg -n "audit-cloture-bascule-theme-astral|Verdict|interpretation_material|delivery_profile|legacy|backend-only" ..\_condamad\audits\theme-astral-prompt-contract
```

## Risques

Le risque principal est de cloturer alors qu'un chemin legacy subsiste dans un fallback ou un seed. Tout chemin residuel doit etre nomme, justifie ou bloque.
