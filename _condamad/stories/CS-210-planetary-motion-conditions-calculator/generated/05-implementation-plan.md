# Implementation Plan - CS-210

## Architecture Finding

`planetary_conditions` contient les contrats CS-208 et le calculateur solaire CS-209. Aucun calculateur de mouvement ni catalogue de profils n'existe avant cette story.

## Plan

1. Ajouter `PlanetaryMotionProfile` dans `contracts.py`.
2. Ajouter un catalogue immutable de dix profils par defaut.
3. Ajouter le calculateur pur avec direction, ratio, etat de vitesse et batch.
4. Exporter les nouveaux symboles publics.
5. Ajouter les tests unitaires du calculateur et etendre les tests de contrats.
6. Executer tests, scans, lint et evidence.

## No Legacy

Aucun shim, alias, fallback, integration adjacente ou second owner n'est autorise.
