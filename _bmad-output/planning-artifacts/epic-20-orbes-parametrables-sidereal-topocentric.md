# Epic 20 (extension): Orbes paramétrables + options sidéral/topocentrique via ruleset

## Objectif

Rendre le moteur natal accurate configurable par ruleset pour les aspects (orbes par aspect/objet), et verrouiller les options de calcul `zodiac`/`frame` (tropical/sidéral, géocentrique/topocentrique) avec traçabilité et tests de non-régression.

## Décisions d'architecture verrouillées

- Les aspects restent calculés sur les positions SwissEph, mais l'orbe n'est plus global fixe.
- L'orbe est résolu par priorité: `orb_pair_override` > `orb_luminaries` > `default_orb`.
- `zodiac=tropical` reste le défaut produit.
- `zodiac=sidereal` nécessite une ayanamsa explicite ou un défaut ruleset (`lahiri`).
- `frame=geocentric` reste le défaut produit.
- `frame=topocentric` utilise altitude fournie, sinon `altitude_m=0`.
- Les champs de traçabilité de calcul doivent rester cohérents entre `result` et `metadata`.

## Stories du chapitre 20 (suite)

### Story 20.9 — Modèle de règles d'aspects paramétrables

- Fichier: `_bmad-output/implementation-artifacts/20-9-modelisation-regles-orbes-parametrables.md`
- Scope:
  - enrichir le référentiel aspects avec `default_orb_deg`
  - ajouter support d'overrides ciblés (luminaires/paires)
  - sérialiser les règles effectives utilisées pour audit

**Acceptance Criteria:**

- **Given** une version de référence seedée
  **When** les aspects sont chargés
  **Then** chaque aspect majeur contient `angle` et `default_orb_deg`
  **And** les codes attendus existent (`conjunction`, `sextile`, `square`, `trine`, `opposition`).

- **Given** une configuration d'override d'orbe
  **When** elle est validée au chargement
  **Then** les valeurs invalides (orb <= 0, orb > 15) sont rejetées avec erreur explicite.

### Story 20.10 — Calcul des aspects avec résolution d'orbe hiérarchique

- Fichier: `_bmad-output/implementation-artifacts/20-10-calcul-aspects-orbes-hierarchiques.md`
- Scope:
  - remplacer `max_orb` global par résolution par règle
  - exposer `orb_used` dans chaque aspect calculé
  - conserver tri déterministe et stabilité des sorties

**Acceptance Criteria:**

- **Given** un aspect défini avec `default_orb_deg=6`
  **When** deux planètes forment un angle à `|delta|=5.5`
  **Then** l'aspect est présent
  **And** `orb=5.5` et `orb_used=6`.

- **Given** un override luminaires plus large (`orb_luminaries=8`)
  **When** Soleil-Lune est à `|delta|=7`
  **Then** l'aspect est conservé
  **And** `orb_used=8`.

- **Given** un override paire spécifique (`sun-mercury=9`)
  **When** Soleil-Mercure est à `|delta|=8.5`
  **Then** l'aspect est conservé même si `default_orb` plus strict
  **And** `orb_used=9`.

### Story 20.11 — Contrat API et traçabilité des options zodiac/frame

- Fichier: `_bmad-output/implementation-artifacts/20-11-contrat-api-zodiac-frame-ayanamsa.md`
- Scope:
  - expliciter les options acceptées côté API (`zodiac`, `ayanamsa`, `frame`, `altitude_m`)
  - exposer les paramètres effectifs en sortie
  - normaliser les erreurs de validation

**Acceptance Criteria:**

- **Given** une requête `zodiac=sidereal` sans ayanamsa
  **When** la règle par défaut s'applique
  **Then** la réponse inclut `zodiac=sidereal` et `ayanamsa=lahiri` (ou valeur ruleset).

- **Given** une requête `frame=topocentric` sans altitude
  **When** le calcul est exécuté
  **Then** l'altitude effective est `0`
  **And** `frame=topocentric` est visible dans le résultat/metadata.

- **Given** une valeur invalide (`zodiac=foo` ou `frame=bar`)
  **When** la requête est soumise
  **Then** l'API retourne `422` avec code d'erreur métier explicite.

### Story 20.12 — Golden tests zodiac/frame et invariants metadata

- Fichier: `_bmad-output/implementation-artifacts/20-12-golden-tests-zodiac-frame-invariants.md`
- Scope:
  - golden tests comparatifs tropical vs sidereal
  - golden tests géocentrique vs topocentrique (ASC/MC)
  - invariants de cohérence `result.* == metadata.*` pour champs dupliqués

**Acceptance Criteria:**

- **Given** un cas golden fixe
  **When** calculé en tropical puis sidéral
  **Then** au moins une longitude planétaire diffère au-delà d'un epsilon minimal
  **And** les métadonnées reflètent bien le mode sidéral/ayanamsa.

- **Given** un cas golden fixe
  **When** calculé en géocentrique puis topocentrique
  **Then** ASC et/ou MC diffèrent dans une tolérance attendue
  **And** les autres champs de traçabilité restent cohérents.

- **Given** un résultat API `natal-chart/latest`
  **When** on compare `result.engine/zodiac/frame/ayanamsa` et `metadata.*`
  **Then** les valeurs sont identiques.

### Story 20.13 — UI natal: affichage avancé des aspects/retrograde

- Fichier: `_bmad-output/implementation-artifacts/20-13-ui-aspects-orb-used-retrograde.md`
- Scope:
  - afficher `orb` et `orb_used` de façon lisible
  - conserver l'indicateur rétrograde `℞`
  - gérer proprement les états vides/non configurés

**Acceptance Criteria:**

- **Given** un thème avec aspects calculés
  **When** l'utilisateur ouvre la page natal
  **Then** chaque aspect affiche `code`, planètes, `orb`, et `orb_used`.

- **Given** un thème sans aspects
  **When** la page s'affiche
  **Then** un état vide explicite est rendu sans erreur UI.

## Ordonnancement recommandé

1. Story 20.9
2. Story 20.10
3. Story 20.11
4. Story 20.12
5. Story 20.13

## Plan de tests global

- Unit:
  - résolution de priorité d'orbe (`pair > luminaries > default`)
  - validation des règles d'orbe
  - cohérence des codes aspects retournés
- Integration:
  - endpoint de génération natal avec options zodiac/frame
  - endpoint latest avec cohérence `result`/`metadata`
- Golden:
  - tropical vs sidereal (Sun/Moon/Mercury)
  - geocentric vs topocentric (ASC/MC)
  - stabilité `ephemeris_path_version`

## Checklist globale de Done

- [ ] Orbes paramétrables actives via référence/ruleset.
- [ ] API zodiac/frame/ayanamsa validée et documentée.
- [ ] Invariants metadata/result couverts par tests.
- [ ] Golden tests comparatifs verts (tropical/sidereal, geo/topo).
- [ ] UI natal affiche aspects enrichis (`orb_used`) et rétrograde.
