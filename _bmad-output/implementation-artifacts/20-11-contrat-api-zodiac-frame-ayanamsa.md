# Story 20.11: Contrat API zodiac/frame/ayanamsa

Status: ready-for-dev

## Story

As a API consumer,
I want un contrat explicite pour `zodiac`, `frame`, `ayanamsa` et `altitude_m`,
so that je peux piloter le calcul natal sans ambiguïté et diagnostiquer les erreurs proprement.

## Acceptance Criteria

1. **Given** `zodiac=sidereal` sans ayanamsa **When** la requête est traitée **Then** l'ayanamsa effective (`lahiri` ruleset par défaut) est visible dans la réponse.
2. **Given** `frame=topocentric` sans altitude **When** la requête est traitée **Then** l'altitude effective est `0`.
3. **Given** des paramètres invalides (`zodiac`/`frame`) **When** la requête est soumise **Then** l'API retourne `422` avec code métier explicite.
4. **Given** un résultat retourné **When** on lit `result` et `metadata` **Then** les champs dupliqués de configuration de calcul sont cohérents.

## Tasks / Subtasks

- [ ] Task 1 (AC: 1-3) Durcir la validation des entrées API natal
  - [ ] Enum stricte `zodiac`, `frame`
  - [ ] Gestion explicite ayanamsa par défaut en sidéral
- [ ] Task 2 (AC: 1, 2, 4) Exposer les paramètres effectifs
  - [ ] Garantir la traçabilité des valeurs effectives dans `result` et `metadata`
- [ ] Task 3 (AC: 3) Normaliser les erreurs
  - [ ] Codes d'erreur stables (`invalid_*`) avec détail actionnable
- [ ] Task 4 (AC: 1-4) Couverture tests API/integration
  - [ ] Cas sidéral sans ayanamsa
  - [ ] Cas topocentric sans altitude
  - [ ] Cas paramètres invalides
  - [ ] Invariant cohérence `result`/`metadata`

## Dev Notes

- Endpoint concerné: `/v1/users/me/natal-chart` et lecture `/v1/users/me/natal-chart/latest`.
- La logique centrale passe par `NatalCalculationService.calculate(...)`.
- Vérifier la non-régression de `accurate=False` et des payloads existants frontend.

### Project Structure Notes

- Backend API + services.
- Impacts: routers `users`, modèles de requête/réponse, `natal_calculation_service`, tests d'intégration.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2011--contrat-api-et-traçabilité-des-options-zodiacframe]
- [Source: backend/app/services/natal_calculation_service.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
