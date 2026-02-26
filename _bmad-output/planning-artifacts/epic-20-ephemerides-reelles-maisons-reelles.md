# Epic 20: Éphémérides réelles + Maisons réelles (Swiss Ephemeris)

## Objectif

Introduire un moteur de calcul natal accurate basé sur Swiss Ephemeris (`pyswisseph`) comme source de vérité par défaut, tout en conservant le moteur simplified derrière feature flag pour comparaison/debug.

## Décisions d'architecture verrouillées

- `engine=swisseph` par défaut (accurate).
- `zodiac=tropical` par défaut.
- `frame=geocentric` par défaut.
- `house_system=placidus` par défaut.
- Si `zodiac=sidereal` et ayanamsa non fourni: `ayanamsa=lahiri` par défaut.
- Si `frame=topocentric` et altitude absente: `altitude_m=0` par défaut.

## Stories du chapitre 20

### Story 20.1 — Installation & configuration Swiss Ephemeris

- Fichier: `_bmad-output/implementation-artifacts/20-1-installation-configuration-swiss-ephemeris.md`
- Scope:
  - dépendance `pyswisseph`
  - path des fichiers d'éphémérides via settings/env
  - bootstrap de vérification au démarrage + erreurs normalisées

### Story 20.2 — Provider `ephemeris_provider` (planètes + speed + sidereal)

- Fichier: `_bmad-output/implementation-artifacts/20-2-ephemeris-provider-swiss-calc-ut.md`
- Scope:
  - `swe.calc_ut` pour Sun..Pluto
  - longitude/latitude/speed et détection rétrograde
  - support tropical/sidereal + ayanamsa

### Story 20.3 — Provider maisons SwissEph (Placidus défaut)

- Fichier: `_bmad-output/implementation-artifacts/20-3-houses-provider-swiss-placidus-extensible.md`
- Scope:
  - `houses_ex` (cuspides 1..12 + ASC/MC)
  - stratégie extensible pour Equal/Whole Sign
  - topocentrique optionnel

### Story 20.4 — Intégration pipeline natal existant

- Fichier: `_bmad-output/implementation-artifacts/20-4-integration-pipeline-natal-accurate-engine.md`
- Scope:
  - conversion `date+heure+timezone -> UTC -> JDUT`
  - sélection moteur via ruleset/feature flag
  - invariants et erreurs métier (`422`) vs techniques (`5xx`)

### Story 20.5 — Metadata API complète de calcul

- Fichier: `_bmad-output/implementation-artifacts/20-5-metadata-api-complete-calculation-params.md`
- Scope:
  - exposition complète des paramètres de calcul en metadata
  - traçabilité versionnée engine/ruleset/reference
  - timezone utilisée explicitement

### Story 20.6 — Golden tests de référence

- Fichier: `_bmad-output/implementation-artifacts/20-6-tests-golden-reference-swisseph.md`
- Scope:
  - 3 cas fixes (Sun/Moon/Mercury, tolérance `0.01°`)
  - timezone historique `Europe/Paris 1973`
  - cas rétrograde (`speed < 0`)

### Story 20.7 — Migration/compat moteur simplified

- Fichier: `_bmad-output/implementation-artifacts/20-7-migration-compat-engine-simplified-feature-flag.md`
- Scope:
  - SwissEph par défaut activable
  - simplified conservé derrière flag
  - endpoint/param interne dev-only de comparaison

### Story 20.8 — Impact UI minimal et non-régression

- Fichier: `_bmad-output/implementation-artifacts/20-8-ui-impact-retrograde-house-system.md`
- Scope:
  - afficher `℞` sur rétrograde
  - afficher `house_system=Placidus` dans l'en-tête
  - garantir la stabilité de la page natal chart

## Ordonnancement recommandé

1. Story 20.1
2. Story 20.2
3. Story 20.3
4. Story 20.4
5. Story 20.5
6. Story 20.6
7. Story 20.7
8. Story 20.8

## Checklist globale de Done

- [ ] Swiss Ephemeris intégré et activable.
- [ ] Résultats cohérents (invariants signe/longitude et maison/intervalle) + metadata complète.
- [ ] Tests unitaires, intégration et golden tests verts.
- [ ] UI stable avec rétrograde et house_system affichés.
- [ ] Observabilité en place (métriques latence/erreurs + logs structurés sans PII).
