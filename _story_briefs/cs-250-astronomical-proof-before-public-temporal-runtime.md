# CS-250 — Harden Astronomical Proof Before Public Temporal Runtime

## Résumé

Durcir la preuve astronomique avant toute ouverture de technique temporelle publique.

Cette story remappe `SC-ARCH-006A` et doit être traitée avant `CS-253`, sauf acceptation explicite du risque par le produit.

## Contexte

CS-241 signale que la preuve astronomique reste incomplète pour les cas sensibles et que le chemin simplifié est encore callable. CS-245 impose donc un gate : aucune story de technique temporelle publique ne doit s'ouvrir tant que cette preuve n'est pas traitée ou risk-accepted.

## Objectif

Installer une baseline de confiance pour les calculs astronomiques :

- preuve du mode production `swisseph` ou équivalent autorisé ;
- suite golden sur cas sensibles ;
- trace de version, hash ou configuration d'éphémérides ;
- politique de tolérance ;
- garde contre l'utilisation publique d'un mode simplifié non qualifié.

## Périmètre inclus

1. Identifier les chemins simplifiés encore accessibles.
2. Ajouter ou renforcer les guards de mode production.
3. Créer une suite golden minimale pour les cas sensibles retenus.
4. Capturer la version/configuration d'éphémérides dans les preuves de test.
5. Documenter les tolérances et les limites connues.
6. Bloquer explicitement CS-253 si la preuve n'est pas fermée.

## Hors périmètre

- Implémenter transits, synastrie, returns, progressions ou profections.
- Modifier le frontend.
- Ajouter une API publique.
- Corriger toute doctrine astrologique non liée à la précision astronomique.

## Critères d'acceptation

1. Les tests prouvent le mode astronomique de production attendu.
2. Les cas golden sensibles couvrent au minimum les dates/lieux/maisons identifiés par CS-241 ou par la story.
3. Les tolérances sont explicites et justifiées.
4. Le mode simplifié ne peut pas porter une surface temporelle publique.
5. La trace de version/configuration d'éphémérides est disponible dans les preuves.
6. CS-253 reste bloquée sauf preuve terminée ou risk acceptance documentée.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

Ajouter les tests golden ciblés. Si certains cas nécessitent une dépendance locale d'éphémérides, documenter le prérequis exact.

## Dépendances

- CS-246 pour classer les familles temporelles bloquées.
- Doit précéder CS-253.

## Risk acceptance

Une acceptation de risque ne peut autoriser qu'une expérimentation non publique. Elle doit citer :

- le périmètre exact autorisé ;
- la surface interdite au public ;
- les écarts astronomiques connus ;
- la date ou story de fermeture.

## Risques

Le risque principal est de confondre "tests qui passent" avec "preuve astronomique suffisante". Les cas golden doivent être reliés à des références externes ou à une source d'éphémérides explicite.
