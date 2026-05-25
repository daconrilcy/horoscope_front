# CS-293 — Close Astrology Disclaimer Projection Policy Evidence

## Résumé

Produire la politique et les preuves manquantes pour clôturer CS-284 sur les disclaimers des projections astrologiques B2C.

## Contexte

CS-284 est encore `Not evidenced` au sens strict : la capsule ne contient pas `generated/10-final-evidence.md`, le dossier `evidence/` attendu est absent, et `docs/architecture/astrology-disclaimer-projection-policy.md` n'existe pas.

Le code contient déjà des sources utiles : `disclaimer_registry.py`, l'injection applicative dans le service natal, et des comportements de guidance. La politique doit confirmer que les disclaimers sont contrôlés par l'application et non inventés par le LLM.

## Objectif

Créer l'inventaire et la politique canonique de rattachement des disclaimers aux projections B2C, puis produire les preuves CONDAMAD de clôture.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Inventorier les disclaimers existants dans backend, frontend, docs et story briefs.
2. Classer les usages : natal, prédiction, IA, mode dégradé, absence d'heure de naissance.
3. Définir `docs/architecture/astrology-disclaimer-projection-policy.md`.
4. Mapper les disclaimers applicatifs aux projections `beginner_summary_v1` et `client_interpretation_projection_v1` par plan free/basic/premium.
5. Documenter que le LLM ne crée, ne réécrit et ne mute jamais les disclaimers.
6. Produire les artefacts `evidence/` et `generated/10-final-evidence.md` de CS-284.

## Hors périmètre

- Créer une nouvelle politique juridique complète.
- Ajouter une route, une UI, une migration, un modèle ou un prompt.
- Exposer des avertissements techniques admin aux clients B2C.
- Modifier les textes existants sans écart d'inventaire justifié.

## Critères d'acceptation

1. Le document `docs/architecture/astrology-disclaimer-projection-policy.md` existe.
2. L'inventaire des disclaimers existants est persisté sous la capsule CS-284.
3. Les projections et plans B2C indiquent les disclaimers applicables.
4. Les cas mode dégradé et absence d'heure de naissance sont couverts ou déclarés comme gap produit.
5. La preuve finale CS-284 existe et démontre l'absence de drift API/runtime.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -c "from app.main import app; assert 'astrology_disclaimer_projection_policy' not in str(app.openapi())"
python -B -c "from app.main import app; assert all('disclaimer-policy' not in getattr(r, 'path', '') for r in app.routes)"
ruff check .
python -B -m pytest -q --tb=short
```

## Dépendances

- CS-257 pour `beginner_summary_v1`.
- CS-258 pour `client_interpretation_projection_v1`.
- CS-283 pour les entitlements B2C.
- CS-284 pour le contrat de story initial.

## Risques

Le risque principal est de laisser le LLM devenir propriétaire de mentions produit ou juridiques variables. Les disclaimers doivent rester statiques, applicatifs, documentés et rattachés explicitement aux projections.
