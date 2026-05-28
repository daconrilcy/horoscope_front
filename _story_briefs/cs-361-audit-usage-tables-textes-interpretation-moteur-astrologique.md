# CS-361 - Audit Usage Tables Textes Interpretation Moteur Astrologique

<!-- Commentaire global: ce brief cadre l'audit des textes d'interpretation disponibles et de leur usage reel par le moteur astrologique. -->

## Resume

Auditer si les tables, fichiers, seeds et modeles contenant des textes ou logiques d'interpretation astrologique sont effectivement utilises par le moteur astrologique et par la construction actuelle des inputs LLM.

L'objectif est de verifier le constat produit: les payloads envoyes au LLM contiennent beaucoup de donnees factuelles, mais peu de matiere interpretative controlee issue des tables metier.

## Contexte

Les exemples JSON de theme astral montrent un flux techniquement coherent mais insuffisant editorialement:

- positions, maisons, angles, aspects et dominantes sont presents;
- les `interpretation_hints` sont courts et partiels;
- les textes riches potentiellement presents en base ou dans les references ne semblent pas injectes;
- le LLM doit donc inferer l'interpretation depuis sa connaissance generale.

Avant de modifier le moteur, il faut inventorier les sources existantes et prouver leur usage ou non-usage.

## Objectif

Produire une preuve claire:

- quelles tables et fichiers contiennent du texte interpretatif;
- quels builders/services les utilisent deja;
- quelles donnees arrivent jusqu'aux projections, inputs LLM et payload provider;
- quelles sources sont dormantes, legacy, test-only ou admin-only;
- quels gaps doivent etre corriges dans les stories suivantes.

## Perimetre inclus

1. Inventorier les modeles DB, migrations, repositories, seeds et fichiers de references contenant des textes astrologiques.
2. Classer les contenus par famille: signe, planete, maison, aspect, dominante, dignite, rulership, condition avancee, profil structurel, pattern.
3. Tracer les appels depuis le moteur natal, les builders de projections et les builders LLM.
4. Comparer ce qui existe en base/reference avec ce qui arrive dans les JSON provider.
5. Identifier les tables ou textes non utilises.
6. Identifier les textes utilises mais perdus avant le LLM.
7. Produire un registre de findings avec severite et story candidate.

## Hors perimetre

- Modifier le code.
- Modifier la base ou les migrations.
- Changer les prompts.
- Appeler un provider LLM.
- Redefinir le nouveau contrat cible; cela appartient a CS-363.

## Sources obligatoires

- `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/*.json`
- `_condamad/examples/prompt-generation-cartography/1973-04-24-paris/*.json`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `backend/app/domain/astrology/**`
- `backend/app/services/**`
- `backend/app/infra/db/models/**`
- `backend/app/infra/db/repositories/**`
- `backend/app/ops/**`
- `backend/migrations/versions/**`
- `docs/recherches astro/**`
- `backend/tests/**`

## Livrable attendu

Creer:

```text
_condamad/audits/theme-astral-prompt-contract/<YYYY-MM-DD-HHMM>/01-audit-usage-tables-textes-interpretation.md
```

Le rapport doit contenir:

1. Executive summary.
2. Inventaire des sources de textes.
3. Matrice source -> owner -> usage runtime.
4. Trace d'appel vers projections et LLM.
5. Comparaison avec les JSON provider actuels.
6. Tables/textes utilises.
7. Tables/textes non utilises.
8. Gaps et risques.
9. Story candidates.

## Criteres d'acceptation

1. Chaque source de texte interpretatif identifiee a un statut: used, unused, legacy, test-only, seed-only, admin-only, unknown.
2. Le rapport prouve si les textes riches atteignent ou non le payload LLM.
3. Les chemins de code et symboles owners sont cites.
4. Les JSON `free/basic/premium` sont cites comme evidence.
5. Les gaps sont convertis en candidates pour CS-363 a CS-368.
6. Aucun changement applicatif n'est effectue.

## Validation attendue

```powershell
rg -n "interpret|keyword|texte|description|meaning|profile|dignit|rulership|condition|aspect|dominant" backend/app docs backend/migrations
rg -n "audit-usage-tables-textes-interpretation|used|unused|legacy|test-only|provider payload|story candidates" _condamad/audits/theme-astral-prompt-contract
```

Si une commande Python est necessaire, activer le venv:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -c "print('audit read-only')"
```

## Risques

Le risque principal est de confondre existence de donnees et usage effectif. Le rapport doit prouver le chemin d'appel, pas seulement lister des tables.
