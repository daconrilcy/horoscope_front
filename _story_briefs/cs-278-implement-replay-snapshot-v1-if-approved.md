# CS-278 — Implement replay_snapshot_v1 If Approved

## Résumé

Implémenter `replay_snapshot_v1` uniquement si le modèle de stockage et sécurité est approuvé.

## Contexte

Le replay est un chantier séparé, plus sensible que le diagnostic redigé. Il ne doit être implémenté qu'après validation de la politique de stockage, accès, redaction et rétention.

## Objectif

Ajouter le replay contrôlé des calculs ou générations selon le contrat approuvé.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Implémenter le stockage du snapshot approuvé.
2. Ajouter les permissions et logs.
3. Ajouter les tests de redaction et accès.
4. Ajouter les tests de reproductibilité.
5. Documenter les limites de replay.

## Hors périmètre

- Implémenter si CS-277 n'est pas approuvée.
- Exposer au client.
- Stocker des secrets.
- Contourner la politique de rétention.

## Critères d'acceptation

1. L'implémentation est conditionnée à l'approbation explicite de CS-277.
2. Les snapshots ne contiennent pas de secrets.
3. Les accès sont journalisés.
4. Les tests prouvent le replay ou documentent les limites non déterministes.
5. La purge/rétention est prise en compte.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-277 approuvée.

## Risques

Le risque principal est de considérer le replay comme simple debug. C'est une surface sensible qui doit rester optionnelle et gouvernée.



