# Epic 18: Astro Profile — Sun Sign + Ascendant + UI intégrée

## Objectif

Garantir le calcul et l'exposition robustes du signe solaire et de l'ascendant, avec règle explicite sur l'absence d'heure de naissance, puis intégrer ces données dans le front (Hero, Profil, Thème natal) sans duplication de route et avec cohérence CSS/tokens.

## Règle métier verrouillée

Si `birth_time` est null/absent => ascendant non calculé (`null`) + `missing_birth_time=true`.

Si `birth_time` est une string valide (y compris `"00:00"`) => `missing_birth_time=false` + calcul ascendant normal.

## Stories du chapitre 18

### Story 18.1 — Backend

- Fichier: `_bmad-output/implementation-artifacts/18-1-astro-profile-backend-sun-sign-ascendant-null-time.md`
- Scope:
  - BirthInput nullable pour `birth_time`
  - migration DB `birth_time` nullable
  - service `user_astro_profile_service`
  - exposition via routes existantes (`/v1/users/me/birth-data`, `/v1/users/me/natal-chart/latest`)
  - tests unit + integration (null, "14:30", "00:00")

### Story 18.2 — Front data flow (API/types/hooks)

- Fichier: `_bmad-output/implementation-artifacts/18-2-astro-profile-frontend-api-types-null-time.md`
- Scope:
  - audit routes/hooks existants et réutilisation sans duplication
  - suppression sentinelle front `"00:00"` automatique
  - stratégie unique payload: `birth_time: null` si heure manquante
  - `birth_time?: string | null`, `missing_birth_time: boolean` dans les types
  - tests front data non-régression

### Story 18.3 — UI + SVG + CSS

- Fichier: `_bmad-output/implementation-artifacts/18-3-astro-profile-ui-hero-profile-natal-svg-css.md`
- Scope:
  - Hero, Profile, Natal chart affichent signe/ascendant + fallback missing time
  - mapping signe -> SVG depuis `docs/interfaces/signes`
  - stratégie `currentColor` (`stroke`) + `fill` transparent
  - cohérence CSS dans `HeroHoroscopeCard.css` et `App.css` via variables
  - tests UI ciblés (Hero/Today/Natal/Profile)

## Acceptance checklist global

- [x] API retourne le bon signe solaire pour date connue.
- [x] API retourne ascendant non-null pour date + heure valide.
- [x] API retourne ascendant null + `missing_birth_time=true` pour heure absente/null.
- [x] `"00:00"` explicite reste une heure valide calculée.
- [x] Hero affiche signe réel + SVG correspondant.
- [x] SVG Hero hérite de la couleur texte (`currentColor`).
- [x] Aucun endpoint frontend dupliqué.
- [x] Couleurs pilotées par variables CSS (pas de hardcoded dans les zones modifiées).

## Corrections post-livraison

- Backend:
  - cohérence natale durcie (validation signe/longitude, validation intervalle maison avec wrap 360->0, assertions cuspides).
  - `metadata.house_system` ajouté dans la réponse natal chart, avec `metadata.reference_version` et `metadata.ruleset_version`.
  - observabilité ajoutée pour incohérences: log `natal_inconsistent_result_detected` (warning, sampling) + métriques compteur global et labelisé.
  - cache du référentiel consolidé dans `ReferenceDataService` (thread-safe).
- Frontend:
  - réduction du bruit de logs sur 404/422 attendus pour le natal chart.
  - politique de logs support alignée: 4xx fonctionnels non loggés, 5xx loggés avec request id.
  - typages `metadata` alignés (`reference_version`, `ruleset_version`, `house_system`).
