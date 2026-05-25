# CS-297 — Expose Internal Admin replay_snapshot_v1 API

## Résumé

Exposer une API admin interne protégée pour consulter les métadonnées, lancer une tentative de replay contrôlée et purger un `replay_snapshot_v1`.

## Contexte

Le runtime replay ne doit pas être public, client-facing, frontend-first ni généré dans des clients publics. L'API doit rester dans un namespace admin/interne cohérent avec les routes existantes.

## Objectif

Ajouter une surface admin minimale, protégée, auditée et non publique pour le runtime replay snapshot.

## Préalable obligatoire

Avant de créer un routeur, relire :

- `backend/app/api/v1/routers/admin/**`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/services/api_contracts/admin/**`
- contrats admin existants d'audit et LLM observability
- CS-270/CS-271 rôles et permissions

## Périmètre inclus

1. Choisir le namespace canonique : `admin/audit` ou `admin/llm` selon owner existant.
2. Ajouter `GET` metadata snapshot.
3. Ajouter `POST` replay attempt contrôlée.
4. Ajouter `DELETE` purge manuelle auditée.
5. Protéger par rôle admin approuvé.
6. Refuser user/public/support non autorisé.
7. Vérifier l'absence de route publique/client.

## Hors périmètre

- Ajouter frontend.
- Ajouter exposition OpenAPI publique.
- Ajouter export massif.
- Ajouter replay libre ou listing global non borné.

## Critères d'acceptation

1. Les routes sont uniquement admin/interne.
2. Les utilisateurs non admin reçoivent 401/403.
3. Les réponses ne contiennent pas de payload sensible.
4. OpenAPI ne contient aucune route publique/client replay.
5. Les tests couvrent autorisé, refusé, introuvable, expiré et purgé.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests\api\admin tests\architecture --tb=short
```

## Dépendances

- CS-296 service applicatif.
- CS-270/CS-271 rôles et permissions.

## Risques

Le risque principal est d'exposer le replay comme une fonctionnalité client ou un debug libre. La surface doit rester minimale, admin, tracée et sans payload brut.
