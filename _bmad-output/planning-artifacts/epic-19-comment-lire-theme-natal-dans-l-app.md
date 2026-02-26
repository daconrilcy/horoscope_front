# Epic 19: Comment lire ton thème natal dans l'app

## Objectif

Fournir une lecture pédagogique, traçable et cohérente du thème natal dans l'application, en expliquant clairement les signes, les maisons, les planètes, les conventions de calcul, et les métadonnées affichées.

Étendre le chapitre 19 avec un axe backend robuste pour le géocodage: proxy Nominatim côté API + persistance canonique du lieu résolu (`PlaceResolved`) afin de préparer les futurs calculs d'éphémérides réelles et d'ascendant/maisons précis.

## Portée

- Harmoniser le contenu de lecture entre liste des planètes et roue des maisons.
- Clarifier les conventions de conversion de longitude (0-360) vers signe + degré dans le signe.
- Expliquer la logique d'appartenance aux maisons, y compris le cas de wrap 360->0 et la convention `[debut, fin)`.
- Rendre explicites les règles "Signe solaire", "Ascendant" et le mode dégradé sans heure de naissance.
- Afficher les métadonnées de calcul pour la traçabilité.
- Remplacer l'appel direct frontend vers Nominatim par des endpoints backend.
- Persister un lieu canonique résolu (provider ids, coordonnées, hiérarchie géo, timezone optionnelle) comme source-of-truth.
- Distinguer cache de requêtes de géocodage (TTL) et stockage durable des lieux résolus.
- Rattacher explicitement le profil de naissance utilisateur à `geo_place_resolved` via FK.

## Story du chapitre 19

### Story 19.1 — Guide de lecture du thème natal dans l'app

- Fichier: `_bmad-output/implementation-artifacts/19-1-comment-lire-ton-theme-natal-dans-l-app.md`
- Scope:
  - section de contenu "Comment lire ton thème natal dans l'app" intégrée à la page thème natal
  - explications signes/maisons/planètes avec exemples chiffrés cohérents
  - convention explicite des intervalles de maisons `[debut, fin)` et gestion du wrap
  - affichage explicite du mode sans heure de naissance (ascendant non calculé)
  - affichage des métadonnées: date/heure génération, version référentiel, version ruleset, système de maisons

### Story 19.2 — Backend Geocoding Search Proxy (Nominatim)

- Fichier: `_bmad-output/implementation-artifacts/19-2-backend-geocoding-search-proxy-nominatim.md`
- Scope:
  - nouvel endpoint backend de recherche de lieux
  - retour des champs complets exploitables pour persister `geo_place_resolved`
  - arrêt de l'appel direct à Nominatim depuis le frontend

### Story 19.3 — Cache DB `geocoding_query_cache` séparé du canonique

- Fichier: `_bmad-output/implementation-artifacts/19-3-cache-db-geocoding-query.md`
- Scope:
  - cache de requêtes avec TTL pour performance
  - séparation stricte cache temporaire vs vérité terrain durable
  - réutilisation backend pour limiter la pression upstream

### Story 19.4 — Modèle DB `geo_place_resolved` (canonique)

- Fichier: `_bmad-output/implementation-artifacts/19-4-modele-db-geo-place-resolved.md`
- Scope:
  - table canonique des lieux résolus + contraintes d'unicité/index
  - stratégie de déduplication et traçabilité provider
  - coordonnées et timezone optionnelle prêtes pour moteurs accurate

### Story 19.5 — Endpoint backend de confirmation de sélection

- Fichier: `_bmad-output/implementation-artifacts/19-5-geocoding-resolve-confirm-selection.md`
- Scope:
  - endpoint `POST /api/v1/geocoding/resolve`
  - persistance via `snapshot` ou récupération upstream (`lookup/details`)
  - retour objet `PlaceResolved` avec id interne

### Story 19.6 — Rattachement profil de naissance à `geo_place_resolved`

- Fichier: `_bmad-output/implementation-artifacts/19-6-rattachement-birth-profile-place-resolved.md`
- Scope:
  - ajout FK `birth_place_resolved_id` sur profil de naissance
  - conservation éventuelle de `birth_place_text` pour UX
  - exposition API d'un objet `birth_place_resolved` complet

## Ordonnancement recommandé

1. Story 19.2 — Backend Geocoding Search Proxy (Nominatim)
2. Story 19.3 — Cache DB `geocoding_query_cache`
3. Story 19.4 — Modèle DB `geo_place_resolved`
4. Story 19.5 — Endpoint `POST /geocoding/resolve`
5. Story 19.6 — Rattachement profil + lecture pipeline natal via FK

Justification: le frontend peut migrer vers 19.2+19.3 rapidement, puis la persistance canonique et le rattachement profil se branchent sans bloquer la transition UX.

## Acceptance checklist global

- [ ] Le guide explique les 3 briques: signes, maisons, planètes.
- [ ] Un exemple de conversion longitude -> signe + degré est affiché et exact.
- [ ] La convention d'intervalle de maison `[debut, fin)` est documentée clairement.
- [ ] Le cas de wrap 360->0 est illustré avec un exemple.
- [ ] Le mode sans heure de naissance est explicite (ascendant non calculé).
- [ ] Les métadonnées de traçabilité sont visibles en haut de page.
- [ ] Le frontend n'appelle plus directement Nominatim.
- [ ] Le backend expose un endpoint de recherche de lieux avec champs persistables complets.
- [ ] La table `geo_place_resolved` existe avec contraintes d'unicité/index recommandées.
- [ ] Le profil de naissance stocke un FK `birth_place_resolved_id`.
- [ ] L'API profil renvoie `birth_place_text` + `birth_place_resolved` (ids provider, display_name, lat/lon, timezone si connue).
- [ ] Le cache `geocoding_query_cache` (TTL) est distinct du stockage canonique `geo_place_resolved` (sans TTL).
- [ ] L'endpoint `POST /api/v1/geocoding/resolve` persiste et retourne un `PlaceResolved`.
- [ ] Les tests couvrent persistance, réutilisation via contrainte unique, et stabilité inter-sessions des coordonnées.
