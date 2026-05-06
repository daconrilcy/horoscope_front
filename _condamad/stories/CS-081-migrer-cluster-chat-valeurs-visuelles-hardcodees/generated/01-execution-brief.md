# Execution Brief - CS-081

## Objectif

Migrer le cluster chat frontend vers des tokens existants, roles typographiques
et variables semantiques `--chat-*` documentees, sans modifier le comportement
React, les routes, les hooks ou les contrats API.

## Bornes

- Scope code: `frontend/src/pages/ChatPage.css` et les CSS sous
  `frontend/src/features/chat/components`.
- Scope garde: `frontend/src/tests/design-system-guards.test.ts`.
- Scope registre: `frontend/src/styles/token-namespace-registry.md` uniquement
  pour documenter `--chat-*`.
- Artefacts: `hardcoded-values-before.md`, `hardcoded-values-after.md` et
  fichiers `generated/`.

## Non-objectifs

- Ne pas migrer les autres fichiers de l'inventaire F-002.
- Ne pas toucher aux hooks, API, stores, routes ou composants React chat.
- Ne pas creer de dependance, d'exception large ou de chemin transitoire.
- Ne pas affaiblir les guardrails `RG-044` a `RG-050` et `RG-058`.

## Regles d'ecriture

- Reutiliser les tokens existants quand ils couvrent le role.
- Declarer les decisions chat durables sous un namespace `--chat-*` unique.
- Documenter tout nouveau namespace dans le registre de tokens.
- Ajouter une garde deterministe contre le retour des valeurs migrees hors de
  leur owner.

## Definition de fin

- Les sept AC ont une preuve code et validation.
- Les tests design-system, theme-tokens, css-fallback, inline-style,
  legacy-style et visual-smoke passent.
- `npm run lint` et `npm run build` passent.
- Les scans cibles sont classes dans l'artefact after.
- La story est revue et le registre de statut est synchronise.

## Halt conditions

- Une valeur visuelle ne peut pas etre classee sans decision produit.
- Une validation obligatoire echoue sans correction sure.
- Le scope devrait toucher le runtime chat ou une autre surface hors story.
