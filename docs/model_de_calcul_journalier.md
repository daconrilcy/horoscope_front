# Modèle de calcul pour un moteur de prédiction astrologique quotidienne

## Résumé exécutif
Ce rapport spécifie un **socle de calcul** (sans code) pour produire, à partir d’un **thème natal** et d’une **journée utilisateur** (date/heure, fuseau, localisation), une prédiction structurée en **signaux astrologiques**, **scores par catégories**, **découpage temporel intrajournalier** et **synthèse textuelle**.

Les décisions structurantes sont les suivantes :  
- **Conventions figées (V1)** : zodiaque **tropical**, positions **géocentriques** (topocentrique optionnel), système de maisons **Placidus** avec mécanisme de repli en cas de latitudes extrêmes (géré par Swiss Ephemeris), et **aspects majeurs ptolemaïques** (conjonction, sextile, carré, trigone, opposition). Swiss Ephemeris fournit le calcul des positions/speeds, des maisons (Asc/MC) et des levers/couchers nécessaires au découpage temporel (positions en UT, vitesses en deg/day, maisons via `swe_houses`, lever/coucher via `swe_rise_trans`). citeturn3view0turn3view1turn3view2turn3view4turn4view4turn0search34  
- **Orbes “moteur du jour”** : pas de norme universelle ; on fige des orbes **serrées** compatibles avec l’objectif intraday, en s’appuyant sur l’idée que la fenêtre la plus “potente” d’un transit se situe à ~1° (et que 2–3° peuvent rester opérants selon les pratiques). citeturn0search6turn0search2  
- **Architecture de scoring** : chaque événement produit une **Contribution(e,c,t)** (valencée ±, bornée et normalisée), agrégée en **RawDay(c)**, puis convertie en **Note(c) 1–20** via une **calibration percentile par catégorie**.  
- **Référentiel DB** : votre schéma de référence actuel est minimal (planètes/maisons = code/nom) et extensible via une table EAV `astro_characteristics` ; cette table est déjà utilisée pour des traits d’aspects (orbes personnalisées). fileciteturn0file0 fileciteturn0file1  
  → Recommandation : conserver la logique “référence versionnée + traits”, et ajouter seulement quelques colonnes “cœur” si besoin de performance, tout le reste en **traits JSON**.  
- **Stockage quotidien** : ajout d’une table `daily_scores` (et champs associés) pour enregistrer notes, puissance/volatilité, points de bascule, timeline UX, et synthèse.

---

## Hypothèses et conventions à figer
### Référentiel astronomique et temporalité
**Temps de référence** : Swiss Ephemeris distingue UT et TT ; `swe_calc_ut()` prend un **Julian Day en UT** et retourne notamment **positions + vitesses** (longitude/latitude/distance + vitesses associées). citeturn3view0turn3view1  
**Règle** : toutes les dates/heures utilisateur (Europe/Paris ou autre fuseau) sont converties en UT pour le calcul, puis reconverties en local pour l’affichage.

### Géocentrique vs topocentrique
Swiss Ephemeris documente la différence **géocentrique vs topocentrique**, pouvant dépasser **un degré pour la Lune**, et précise que le topocentrique exige latitude/longitude et, pour de la précision, l’altitude. citeturn2view0turn3view3  

**Recommandation V1 (simplicité + stabilité produit)**  
- **Positions géocentriques** (par défaut) : cohérentes avec la majorité des éphémérides “astrologiques standard”, plus simples à opérer (moins de données requises).  
- **Option V2** : topocentrique activable par profil (données géo complètes + altitude), avec flag `SEFLG_TOPOCTR` après `swe_set_topo()`. citeturn3view3turn2view0  

### Système de maisons
Swiss Ephemeris implémente de nombreux systèmes de maisons (dont Placidus, Koch, Regiomontanus, Campanus, Whole Sign) et documente leurs propriétés ; il indique aussi des comportements en latitudes élevées (limitations/solutions). citeturn4view4turn4view3turn3view2  

**Recommandation V1**  
- **Placidus** comme système principal (cohérence avec un usage large et disponibilité dans Swiss Ephemeris). citeturn4view4  
- **Règle de repli** : si Swiss Ephemeris signale une non-convergence / latitudes extrêmes, enregistrer le repli (p.ex. Porphyry) comme “house_system_effective” dans le résultat (important pour l’audit et la reproductibilité). Swiss Ephemeris décrit explicitement des mécanismes de correction/itération et de bascule. citeturn4view1turn4view4  

### Périmètre V1 : pas de calculs exotiques
**Inclus (V1)**  
- Corps : Soleil, Lune, Mercure, Vénus, Mars, Jupiter, Saturne, Uranus, Neptune, Pluton.  
- Points : Ascendant, MC (issus de `swe_houses`), cuspides. citeturn3view2turn1search0  
- Aspects : 5 majeurs ptolemaïques (conjonction, sextile, carré, trigone, opposition). citeturn0search34turn0search2  
- États : vitesse (direct/rétrograde via signe de la vitesse en longitude), applying/separating, entrées/sorties d’orbe. citeturn3view1turn0search37  

**Exclus (V1)** : étoiles fixes, parts arabes, antisces, astéroïdes multiples, aspects mineurs, techniques avancées (directions primaires, progressions secondaires, révolutions solaires), etc. (Non interdits, mais non nécessaires au moteur quotidien “lisible et stable”.)

### Orbes par planète et fenêtre d’exactitude
The Astrology Podcast souligne qu’il n’existe **pas de standard unique d’orbes** et suggère qu’une proximité d’environ **1°** autour d’un transit est souvent vécue comme “pic” d’intensité (avec une opérativité pouvant s’étendre à ~2–3° selon les approches). citeturn0search2turn0search6  

**Convention V1 recommandée (moteur du jour, serré)**  
- Définir deux seuils :  
  - `orb_peak_deg` (fenêtre “bascule/peak”) = **1.0°** (générique, modulable par planète)  
  - `orb_active_deg` (fenêtre d’activité) = dépend de la planète transitante (table ci-dessous)

**Table recommandée `orb_active_deg` (par planète transitante)**  
| Planète (code) | orb_active_deg | orb_peak_deg | Justification produit |
|---|---:|---:|---|
| moon | 1.5 | 1.0 | Variation intraday forte, mais on reste serré |
| sun | 2.0 | 1.0 | Climat du jour, mais pas trop large |
| mercury | 2.0 | 1.0 | Intraday significatif (communication/rythme mental) |
| venus | 2.0 | 1.0 | Affectif/social, variations perceptibles |
| mars | 2.0 | 1.0 | Énergie/conflit, variations perceptibles |
| jupiter | 1.5 | 1.0 | Plus lent, on resserre pour éviter du “bruit permanent” |
| saturn | 1.5 | 1.0 | Même logique (structure/lenteur) |
| uranus | 1.0 | 0.7 | Très lent : signal du jour uniquement très serré |
| neptune | 1.0 | 0.7 | Idem |
| pluto | 1.0 | 0.7 | Idem |

**Modulation par aspect (multiplicateur)**  
On introduit `mult_aspect_orb(A)` : conjonction 1.00, opposition 0.95, carré 0.90, trigone 0.90, sextile 0.80.  
Donc :  
`orb_max(P, A) = orb_active_deg(P) × mult_aspect_orb(A)`  
et la “zone peak” :  
`orb_exact(P, A) = min(orb_peak_deg(P), 0.5 × orb_max(P,A))`

---

## Référentiel et données de référence à stocker
### État actuel de la DB de référence
Vos modèles SQLAlchemy montrent :  
- `planets` : id, reference_version_id, code, name  
- `houses` : id, reference_version_id, number, name  
- `aspects` : angle + `default_orb_deg`  
- `astro_characteristics` : table EAV (entity_type, entity_code, trait, value) déjà utilisée pour des traits d’aspects (ex. orbes spécifiques).  
- Références versionnées et **verrouillables** (`reference_versions.is_locked`), empêchant la mutation une fois figées. fileciteturn0file0 fileciteturn0file1  

**Implication** : toutes les valeurs métier décrites ci-dessous doivent être rattachées à une **reference_version** (reproductibilité), et idéalement injectées via un “seed” de version.

### Stratégie de stockage recommandée
Vous avez deux voies. La plus cohérente avec l’existant est la voie A.

**Voie A (recommandée) : attributs en “traits” dans `astro_characteristics`**  
- Avantages : très flexible (pas de migration lourde), aligné avec l’existant, versionnable naturellement. fileciteturn0file1  
- Inconvénient : moins performant pour requêtes analytiques SQL pures (mais acceptable en SQLite si vous chargez en mémoire au runtime).

**Voie B (option) : colonnes supplémentaires dans `planets` et `houses`**  
- Avantage : requêtes directes.  
- Inconvénient : migrations/évolution plus coûteuses, rigidité.

Dans ce rapport, je fournis :  
1) les **attributs métier** à définir (indépendamment de la voie A/B),  
2) une proposition de **types SQLite** si vous choisissez des colonnes,  
3) la représentation en **traits** (clé/valeur JSON) si vous choisissez la voie A.

### Attributs métier pour chaque planète
#### Schéma des attributs (à ajouter)
| Attribut | Type SQLite (si colonne) | Trait recommandé (Voie A) | Domaine | Description / règle |
|---|---|---|---|---|
| class | TEXT | planet.class | moteur | `luminary` / `personal` / `social` / `transpersonal` |
| speed_rank | INTEGER | planet.speed_rank | moteur | ordre relatif (1 = plus rapide) ; utile UX/validation |
| speed_class | TEXT | planet.speed_class | moteur | `fast` / `medium` / `slow` (pilotage intraday) |
| weight_intraday | FLOAT | planet.weight_intraday | scoring | poids de variation horaire (0–1) |
| weight_day_climate | FLOAT | planet.weight_day_climate | scoring | poids “climat du jour” (0–1) |
| typical_polarity | FLOAT | planet.typical_polarity | scoring | tendance ± (−1..+1) ; n’inverse pas un aspect mais module la valence |
| orb_active_deg | FLOAT | planet.orb_active_deg | events | orbe max de détection (degrés) |
| orb_peak_deg | FLOAT | planet.orb_peak_deg | events | zone “pic” (ex. 1°) |
| ui_category_weights_json | TEXT (JSON) | planet.ui_category_weights | routage | matrice planète→catégories (vecteur normalisé) |
| keywords_json | TEXT (JSON) | planet.keywords | éditorial | mots-clés pour templates (3–8 mots) |
| micro_notes | TEXT | planet.micro_notes | éditorial | note courte (≤140 caractères) |

#### Valeurs recommandées par planète (V1)
| code | class | speed_rank | speed_class | weight_intraday | weight_day_climate | typical_polarity | orb_active_deg | micro_notes |
|---|---|---:|---|---:|---:|---:|---:|---|
| sun | luminary | 4 | medium | 0.50 | 0.70 | +0.20 | 2.0 | “Identité, direction du jour, mise en lumière.” |
| moon | luminary | 1 | fast | 1.00 | 0.50 | +0.00 | 1.5 | “Humeur, besoins, rythme, réactivité.” |
| mercury | personal | 2 | fast | 0.70 | 0.40 | +0.00 | 2.0 | “Pensée, échanges, arbitrages, timing.” |
| venus | personal | 3 | medium | 0.60 | 0.35 | +0.60 | 2.0 | “Lien, attractivité, plaisir, harmonie.” |
| mars | personal | 5 | medium | 0.40 | 0.40 | −0.10 | 2.0 | “Élan, action, friction, sexualité.” |
| jupiter | social | 7 | slow | 0.20 | 0.55 | +0.50 | 1.5 | “Expansion, opportunité, confiance.” |
| saturn | social | 8 | slow | 0.15 | 0.60 | −0.50 | 1.5 | “Structure, devoir, délais, maturité.” |
| uranus | transpersonal | 6 | slow | 0.05 | 0.45 | +0.00 | 1.0 | “Rupture, surprise, besoin de liberté.” |
| neptune | transpersonal | 9 | slow | 0.05 | 0.40 | +0.00 | 1.0 | “Inspiration, flou, idéalisation.” |
| pluto | transpersonal | 10 | slow | 0.05 | 0.45 | −0.20 | 1.0 | “Intensité, transformation, pouvoir.” |

### Attributs métier pour chaque maison
#### Schéma des attributs (à ajouter)
| Attribut | Type SQLite (si colonne) | Trait recommandé (Voie A) | Domaine | Description |
|---|---|---|---|---|
| ui_domains_json | TEXT (JSON) | house.ui_domains | éditorial | libellés UX (1–3 domaines) |
| ui_primary_category | TEXT | house.ui_primary_category | UX | code catégorie principale |
| ui_category_weights_json | TEXT (JSON) | house.ui_category_weights | routage | maison→catégories (vecteur normalisé) |
| base_priority | INTEGER | house.base_priority | scoring | maison angulaire souvent plus “visible” (convention moteur) |
| keywords_json | TEXT (JSON) | house.keywords | éditorial | mots-clés (5–12) utiles pour synthèse |
| micro_notes | TEXT | house.micro_notes | éditorial | note courte explicative |

#### Valeurs recommandées par maison (V1)
Les significations des maisons sont documentées par Astro.com (introduction) et par The Astrology Podcast (série sur les 12 maisons). citeturn1search0turn1search1turn1search5  

| maison | name (actuel) | ui_domains (exemples) | ui_primary_category | base_priority | micro_notes |
|---:|---|---|---|---:|---|
| 1 | Self | énergie, corps, initiative | energie | 5 | “Élan, présence, ton de départ.” |
| 2 | Resources | argent, sécurité, ressources | argent | 4 | “Ressources personnelles et stabilité.” |
| 3 | Communication | échanges, trajets, mental | communication | 3 | “Flux d’infos, coordination, micro-choix.” |
| 4 | Home | foyer, famille, base émotionnelle | famille_foyer | 5 | “Ancrage, intimité, besoin de sécurité.” |
| 5 | Creativity | plaisir, créativité, romance | plaisir_creativite | 3 | “Joie, désir, expression et jeu.” |
| 6 | Health | santé, routines, travail quotidien | sante | 4 | “Hygiène de vie, méthodes, rendement.” |
| 7 | Partnership | couple, associés, contrats | amour | 5 | “Relation directe, miroir, négociation.” |
| 8 | Transformation | intimité, intensité, partagé | sexe_intimite | 4 | “Fusion, secrets, ressources partagées.” |
| 9 | Beliefs | sens, apprentissage, horizon | plaisir_creativite | 2 | “Perspective, exploration, sens.” |
| 10 | Career | objectifs, statut, visibilité | carriere | 5 | “Direction, ambition, exposition publique.” |
| 11 | Community | amis, réseau, projets | social_reseau | 3 | “Collectif, opportunités via réseau.” |
| 12 | Subconscious | repos, retrait, récupération | humeur | 2 | “Ralentir, digérer, se ressourcer.” |

### Matrices de routage
#### Définition des catégories UI (codes)
| code | libellé UX | périmètre |
|---|---|---|
| energie | Énergie | ton d’action, vitalité, drive |
| humeur | Humeur | émotions, sensibilité, stabilité interne |
| sante | Santé | hygiène de vie, corps, récupération |
| travail | Travail | productivité, organisation, tâches |
| carriere | Carrière | visibilité, objectifs, image publique |
| argent | Argent | ressources, dépenses, sécurité matérielle |
| amour | Amour | relation, couple, harmonie relationnelle |
| sexe_intimite | Sexualité & intimité | désir, intensité, fusion, partages |
| famille_foyer | Famille & foyer | home, proches, base affective |
| social_reseau | Social & réseau | amis, communauté, collectif |
| communication | Communication | échanges, décisions, coordination |
| plaisir_creativite | Plaisir & créativité | joie, inspiration, romance, jeu |

#### Matrice planète → catégories (poids de couleur)
Ces poids servent à “colorer” un signal et à alimenter les templates ; ils ne doivent pas annihiler un événement routé par maison (voir formule Contribution).  

| planète | energie | humeur | sante | travail | carriere | argent | amour | sexe_intimite | famille_foyer | social_reseau | communication | plaisir_creativite |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sun | 0.25 | 0.05 | 0.10 | 0.10 | 0.25 | 0.05 | 0.05 | 0.05 | 0.00 | 0.05 | 0.00 | 0.05 |
| moon | 0.10 | 0.30 | 0.15 | 0.05 | 0.00 | 0.05 | 0.10 | 0.05 | 0.20 | 0.05 | 0.00 | 0.00 |
| mercury | 0.05 | 0.10 | 0.05 | 0.25 | 0.10 | 0.05 | 0.00 | 0.00 | 0.00 | 0.15 | 0.35 | 0.05 |
| venus | 0.05 | 0.10 | 0.05 | 0.00 | 0.00 | 0.15 | 0.30 | 0.15 | 0.00 | 0.10 | 0.00 | 0.15 |
| mars | 0.25 | 0.10 | 0.05 | 0.20 | 0.15 | 0.00 | 0.00 | 0.20 | 0.00 | 0.05 | 0.05 | 0.00 |
| jupiter | 0.10 | 0.10 | 0.05 | 0.05 | 0.20 | 0.15 | 0.10 | 0.00 | 0.00 | 0.15 | 0.05 | 0.05 |
| saturn | 0.05 | 0.10 | 0.10 | 0.20 | 0.25 | 0.15 | 0.00 | 0.00 | 0.05 | 0.05 | 0.05 | 0.00 |
| uranus | 0.10 | 0.15 | 0.00 | 0.10 | 0.15 | 0.05 | 0.00 | 0.00 | 0.00 | 0.20 | 0.20 | 0.05 |
| neptune | 0.05 | 0.25 | 0.10 | 0.00 | 0.00 | 0.00 | 0.15 | 0.05 | 0.00 | 0.10 | 0.05 | 0.25 |
| pluto | 0.10 | 0.20 | 0.00 | 0.00 | 0.15 | 0.15 | 0.10 | 0.25 | 0.00 | 0.05 | 0.00 | 0.00 |

#### Matrice maison → catégories (routage principal)
| maison | energie | humeur | sante | travail | carriere | argent | amour | sexe_intimite | famille_foyer | social_reseau | communication | plaisir_creativite |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.55 | 0.10 | 0.25 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2 | 0.00 | 0.00 | 0.05 | 0.00 | 0.10 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 |
| 3 | 0.00 | 0.05 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.70 | 0.00 |
| 4 | 0.00 | 0.20 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.70 | 0.00 | 0.00 | 0.00 |
| 5 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.10 | 0.00 | 0.00 | 0.00 | 0.55 |
| 6 | 0.10 | 0.10 | 0.45 | 0.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| 7 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.45 | 0.00 | 0.00 | 0.30 | 0.15 | 0.00 |
| 8 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.25 | 0.10 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 |
| 9 | 0.00 | 0.10 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.15 | 0.30 | 0.20 |
| 10 | 0.10 | 0.00 | 0.00 | 0.00 | 0.70 | 0.15 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 |
| 11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.15 | 0.10 | 0.00 | 0.00 | 0.00 | 0.65 | 0.00 | 0.10 |
| 12 | 0.10 | 0.40 | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.15 |

---

## Signaux à calculer et règles de priorité
### Calculs de base à chaque pas de temps
**Pas temporel interne** : 15 minutes (Δt = 900 s).  
À chaque pas t :  
1) Calculer positions/vitesses des planètes (longitude et vitesse en longitude) via Swiss Ephemeris. `swe_calc_ut()` retourne vitesses en deg/day, permettant d’identifier direct/rétrograde et d’estimer applying/separating. citeturn3view0turn3view1  
2) Calculer maisons/angles (Asc/MC) via `swe_houses()` (nécessite latitude/longitude). citeturn3view2  
3) Calculer lever/coucher du Soleil (et éventuellement autres) via `swe_rise_trans()` afin de supporter heures planétaires et fenêtres jour/nuit. citeturn3view4  

### Définition formelle des événements (events)
On note :  
- λ(P,t) : longitude écliptique (0..360) de la planète transitante P au temps t  
- λ(X) : longitude du point natal X (planète/angle natal)  
- A ∈ {0,60,90,120,180} (angles des aspects majeurs) citeturn0search34  
- Δλ = wrap180( λ(P,t) − λ(X) ) ∈ [−180, +180]  
- orb(A) = | |Δλ| − A |  

**Événement “AspectTransitActive”**  
- Déclenché si `orb(A) ≤ orb_max(P,A)`.

**Sous-événements d’activation**  
- `enter_orb` : orb traverse de >orb_max à ≤orb_max entre deux pas.  
- `exact` : orb ≤ orb_exact (fenêtre “peak”) OU minimum local d’orb (selon mode).  
- `exit_orb` : orb traverse de ≤orb_max à >orb_max.

**Applying vs separating**  
Applying/separating est défini par la variation de l’orbe :  
- applying si `orb(t+Δt) < orb(t)`  
- separating si `orb(t+Δt) > orb(t)`  
Cette définition correspond à l’idée que l’aspect est “plus fort” quand il se forme (applying) que lorsqu’il s’éloigne (separating). citeturn0search37  

### Événements non-aspects (pivots intraday)
**Changement de signe de la Lune**  
- `moon_sign_ingress` si `sign(λ(moon,t)) ≠ sign(λ(moon,t+Δt))`.  

**Changement de signe de l’Ascendant (du moment)**  
- `asc_sign_change` si `sign(Asc(t)) ≠ sign(Asc(t+Δt))` (Asc via `swe_houses`). citeturn3view2  

**Heures planétaires** (modulateur léger)  
Les “heures planétaires” divisent le jour (lever→coucher) en 12 parts et la nuit (coucher→lever) en 12 parts, et attribuent à chaque segment un maître selon un ordre (souvent dit “chaldéen”). citeturn1search14turn1search6  
- `planetary_hour_change` à chaque début de segment.  
- Données requises : lever/coucher exacts (Swiss Ephemeris `swe_rise_trans`). citeturn3view4  

### Table de priorité et poids d’événements
| Event type | Condition | Priorité | Poids base `w_event` | Remarque produit |
|---|---|---:|---:|---|
| aspect_exact_to_angle | exact & cible = angle natal | 100 | 1.00 | Pivot majeur du jour |
| aspect_exact_to_luminary | exact & cible = Sun/Moon natal | 95 | 0.95 | Très structurant |
| aspect_exact_to_personal | exact & cible = planète perso natale | 85 | 0.85 | Très perceptible |
| aspect_enter_orb | enter_orb | 70 | 0.60 | Début de “phase” |
| asc_sign_change | changement signe Asc | 65 | 0.55 | Changement de “cadre” |
| moon_sign_ingress | changement signe Lune | 60 | 0.50 | Changement d’humeur/rythme |
| aspect_exit_orb | exit_orb | 55 | 0.45 | Fin de “phase” |
| planetary_hour_change | début heure planétaire | 20 | 0.15 | Modulateur léger (ne renverse pas) |

---

## Modèle mathématique de scoring
### Fonction Contribution(e,c,t)
Chaque event e au temps t contribue à chaque catégorie c via une contribution bornée.

#### Étape de routage (dominante de domaine)
On calcule d’abord un **poids de domaine** vers les maisons, puis vers les catégories UI :

1) **Vecteur maison** `H_e` (dimension 12) :  
- si l’event cible un point natal X situé en maison h(X) :  
  - `H_e[h(X)] = 0.70`  
- si la planète transitante P se trouve (au temps t) dans la maison natale h(P,t) :  
  - `H_e[h(P,t)] += 0.30`  
Puis normaliser H_e pour sommer à 1 (si cas particuliers).

2) **Vecteur catégories issues des maisons** :  
`W_house_to_cat` est la matrice maison→catégories (table plus haut).  
Donc :  
`D_house(e,c) = Σ_h H_e[h] × W_house_to_cat[h,c]`

3) **Couleur planétaire**  
`W_planet_to_cat[P,c]` est la matrice planète→catégories.  
On l’utilise comme **blend**, pour éviter qu’elle annule totalement un événement routé par maison :  
`D_planet(P,c) = 0.50 + 0.50 × W_planet_to_cat[P,c]`  
Ainsi, `D_planet ∈ [0.50, 1.00]`.

4) **Routage total**  
`D(e,c) = D_house(e,c) × D_planet(P,c)`

#### Intensité, temporalité, valence
On définit ensuite :

- `w_planet(P)` = `weight_intraday` (table planètes)  
- `w_aspect(A)` (intensité géométrique) : conjonction 1.00, opposition 0.90, carré 0.85, trigone 0.75, sextile 0.60.  
- `f_orb` (0..1) :  
  - si orb > orb_max alors 0  
  - sinon : `f_orb = 1 − (orb / orb_max)^p` avec p=2 (courbe accentuant le “near exact”)  
- `f_phase` : applying 1.05, exact 1.15, separating 0.95 (convention moteur alignée avec l’idée applying > separating). citeturn0search37turn0search6  
- `f_target` (importance de la cible) : angle 1.30 ; luminaire 1.20 ; planète personnelle 1.10 ; planète sociale 1.00 ; transpersonnelle 0.90.  
- `NS(c)` : sensibilité natale (section suivante), bornée [0.75, 1.25].  
- `Pol(e,c)` : valence ∈ [−1,+1]  
  - Base aspect : trigone/sextile +1 ; carré/opposition −1 ; conjonction = moyenne des polarités typiques des deux corps (bornée).  
  - `Pol_final = clamp(−1,+1, base_aspect × (1 + 0.3×typical_polarity(P)) )`  
  - Pour la conjonction : `Pol_final = clamp(−1,+1, 0.5×typical_polarity(P) + 0.5×typical_polarity(target))`

#### Formule finale
\[
Contribution(e,c,t)= w\_event(e)\times w\_{planet}(P)\times w\_{aspect}(A)\times f\_{orb}\times f\_{phase}\times f\_{target}\times NS(c)\times D(e,c)\times Pol(e,c)
\]

**Bornes recommandées (anti-explosion)**  
- Après calcul : `Contribution = clamp(−1.0, +1.0, Contribution)`  
- Puis `RawStep(c,t) = Σ_e Contribution(e,c,t)` avec `RawStep` clampé à [−3,+3] (sécurité).

### Exemples numériques illustratifs
Les exemples ci-dessous illustrent le mécanisme (les chiffres suivent les conventions de ce rapport).

#### Cas type A : trigone Lune transitante → Soleil natal en Maison X (effet carrière)
Hypothèses :  
- P = moon ; A = trigone ; orb = 0.3° ; orb_max = 1.5×0.90=1.35° ; applying  
- cible = luminaire ; NS(carriere)=1.05  
- routage (cible maison X + transit maison VI) puis mapping maison→catégorie donne `D_house≈0.59` ; `D_planet(moon,carriere)=0.55` ; donc `D≈0.3245`  
- w_event(exact) non, supposons “active” : w_event = 0.60 (enter_orb/active) ou 0.85 (exact perso). Ici : event “active” standard : 0.60.

Calcul :  
- `f_orb = 1 − (0.3/1.35)^2 ≈ 0.9506`  
- `w_planet=1.00` ; `w_aspect=0.75` ; `f_phase=1.05` ; `f_target=1.20` ; `Pol=+1`

On obtient une contribution positive modérée (~ +0.19 à +0.31 selon `w_event`). Interprétation UX : **fenêtre porteuse** orientée visibilité/élan.

#### Cas type B : carré Mars transitant → Mercure natal (tension sur travail/communication)
Hypothèses :  
- P = mars ; A = carré ; orb = 0.8° ; orb_max = 2.0×0.90=1.8° ; applying  
- cible = planète personnelle ; NS(travail)=1.00  
- routage donne D(travail) ~ 0.27 ; `D_planet(mars,travail)=0.80` → D ~ 0.216  
- `Pol = −1` (carré)

La contribution est négative (tension) mais quantifiée et localisée temporellement : utile pour détecter un **pivot** et produire une consigne éditoriale (“ralentir, clarifier, éviter l’impulsivité”).

#### Cas type C : conjonction Saturne transitant → MC natal (exigeant mais structurant)
Hypothèses :  
- P = saturn ; A = conjonction ; orb = 0.5° ; orb_max = 1.5×1.0=1.5° ; separating  
- cible = angle ; NS(carriere)=1.10  
- routage fortement carriere ; `Pol` conjonction ≈ moyenne polarités (saturn −0.5, MC 0) = −0.25

La contribution est négative faible à moyenne : pas “mauvaise” mais “coûteuse/structurante”. C’est typiquement un signal de **discipline / responsabilités**, à refléter dans l’éditorial.

---

## Sensibilité natale NS(c) et normalisations
### NS(c) : définition et barèmes proposés
Objectif : amplifier une catégorie si le natal rend le sujet plus réactif sur ce domaine, sans sur-déterminer.

NS(c) est composée de 4 composantes :  
- `Occ(c)` : occupation des maisons liées à la catégorie  
- `Rul(c)` : force des maîtres de maisons (via règles de maîtrise des signes)  
- `Ang(c)` : présence de liens vers angles (Asc/MC)  
- `Dom(c)` : dominante élémentaire / répétitions (optionnel V1)

**Règle de maîtrise des signes** : Astrodienst documente les “sign rulers” (ex. Mars gouverne Bélier et Scorpion). citeturn6search0  

#### Barèmes
1) **Occupation**  
Définir un poids natal par planète : luminaire 0.08, personnelle 0.06, sociale 0.04, transpersonnelle 0.02.  
Pour chaque catégorie c, définir un ensemble de maisons `H(c)` (exemples ci-dessous).  
`Occ(c) = Σ_{planètes natales X dans maisons H(c)} w_natal_planet(X)`  
Puis re-scinder : `Occ_norm(c) = min(1.0, Occ(c) / 0.25)` (0.25 ≈ “maison bien occupée”).

2) **Maîtres de maisons**  
Pour chaque maison h ∈ H(c), identifier le maître `ruler(sign_on_cusp(h))`. citeturn6search0  
Score de force simple (V1) du maître R :  
- +0.06 si R est en maison angulaire (1/4/7/10)  
- +0.03 si succédente (2/5/8/11)  
- +0.01 si cadente (3/6/9/12)  
- +0.05 si R aspecte (orb ≤ 3°) Asc ou MC (natal)  
Puis `Rul_norm(c) = min(1.0, moyenne_h score(R_h) / 0.10)`.

3) **Angles**  
`Ang_norm(c)` : +1 si la catégorie implique une maison angulaire primaire (carriere→10, amour→7, famille→4, energie→1), sinon 0.

4) **Dominante (optionnel)**  
`Dom_norm(c)` : 0..1 selon la répétition d’éléments/significateurs liés (V1 peut ignorer).

#### Formule NS(c)
\[
NS(c)= clamp(0.75,1.25, 1.0 + 0.12\times Occ\_{norm}(c) + 0.10\times Rul\_{norm}(c) + 0.05\times Ang\_{norm}(c) + 0.03\times Dom\_{norm}(c))
\]

### Normalisation par catégorie
Avant calibration percentile, on calcule `RawDay(c)` de façon comparable :

1) `RawStep(c,t)` (toutes les 15 min)  
2) Agrégation journalière :
- `Mean(c) = moyenne_t RawStep(c,t)`  
- `Peak90(c) = max des moyennes glissantes (90 min)`  
- `Close(c) = moyenne des 2 dernières heures de la journée`

\[
RawDay(c) = 0.70\times Mean(c) + 0.20\times Peak90(c) + 0.10\times Close(c)
\]

Puis clamp global : `RawDay(c) ∈ [−2, +2]` (stabilité).

---

## Temporalité, bascules, calibration et stockage
### Méthode temporelle et détection de points de bascule
**Grille interne** : pas de 15 minutes.  
**Raffinement** : si un changement est détecté entre t et t+15 min (ex. Moon sign ingress, asc sign change, enter/exit orb), on recherche un temps `t*` à précision cible (p.ex. ≤ 1 min) par dichotomie/logique de raffinement.

**Définition d’un “point de bascule”**  
Un instant ou intervalle est déclaré pivot si au moins une condition est vraie :  
- une catégorie c change de note estimée (après calibration) de **≥ 2 points** entre deux blocs UX ;  
- le **top 3** des catégories du jour change (ordre ou composition) ;  
- un événement prioritaire ≥ 65 (table des priorités) survient (exact to angle/luminary, asc change, etc.).

### Agrégation en blocs UX
- Blocs “stables” d’**une heure** par défaut.  
- Si bascule : découper en blocs adaptatifs (ex. 09:00–10:15, 10:15–11:30) centrés autour du pivot détecté.  
- Pour chaque bloc : stocker catégories dominantes, et event(s) responsable(s) (traçabilité).

### Calibration percentile : RawDay → Note 1–20
La conversion 1–20 doit être **calibrée par catégorie** afin d’éviter qu’une catégorie “naturellement bruyante” (ex. humeur) écrase une catégorie “rare” (ex. argent).

#### Dataset requis
- Un ensemble de thèmes natals “divers” (au minimum : distribution de latitudes/fuseaux, profils d’angles variés).  
- Une fenêtre temporelle **≥ 365 jours** (idéal 2–3 ans) pour capturer saisons et cycles.  
- Même convention (reference_version + règles) pour tout le dataset.

#### Étapes
1) Calculer `RawDay(c)` pour chaque jour et chaque catégorie.  
2) Pour chaque catégorie c, estimer la distribution empirique et extraire : **P5, P25, P50, P75, P95**.  
3) Définir une échelle cible :  
- P5 → note 2  
- P25 → note 6  
- P50 → note 10  
- P75 → note 14  
- P95 → note 19  
(en dessous de P5 → 1 ; au-dessus de P95 → 20)

#### Fonction de conversion (piecewise linéaire)
Soit x = RawDay(c).  
- Si x ≤ P5 : Note = 1 ou 2 (selon politique)  
- Entre P5..P25 : interpoler linéairement 2→6  
- Entre P25..P50 : 6→10  
- Entre P50..P75 : 10→14  
- Entre P75..P95 : 14→19  
- Si x ≥ P95 : Note = 20

Cette approche produit une note interprétable et stable, indépendante des amplitudes internes.

#### Métriques additionnelles à stocker
- **Puissance** `Power(c)` : somme des |RawStep|, normalisée (mesure “charge”)  
- **Volatilité** `Vol(c)` : écart-type de RawStep (mesure “instabilité”)  
- **Pivot_count** : nombre de pivots détectés

### Schéma de stockage recommandé
#### Champs supplémentaires (référence)
Vous pouvez ne rien ajouter à `planets/houses` et tout stocker dans `astro_characteristics` (Voie A). Si vous ajoutez des colonnes (Voie B), limiter aux champs “recherche rapide” :

**Planets (colonnes optionnelles)** : `weight_intraday`, `weight_day_climate`, `typical_polarity`, `orb_active_deg`, `orb_peak_deg`, `ui_category_weights_json`, `keywords_json`, `micro_notes`.  
**Houses (colonnes optionnelles)** : `ui_primary_category`, `ui_category_weights_json`, `base_priority`, `keywords_json`, `micro_notes`.

Rappel : votre système de référence est versionné et verrouillé ; les attributs doivent donc être liés à la version. fileciteturn0file0

#### Nouvelle table `daily_scores`
**Objectif** : persister la sortie calculée (et les éléments nécessaires à l’explicabilité).  

| Champ | Type SQLite | Contraintes | Description |
|---|---|---|---|
| id | INTEGER | PK | |
| user_id | INTEGER | index | lien utilisateur |
| date_local | DATE | index | date de la prédiction (jour local) |
| timezone | TEXT | not null | ex. `Europe/Paris` |
| location_lat | FLOAT | nullable | lat du jour (si dispo) |
| location_lon | FLOAT | nullable | lon du jour (si dispo) |
| reference_version | TEXT | not null | version des tables de référence |
| ruleset_version | TEXT | not null | version des règles (scoring) |
| input_hash | TEXT | index | hash des inputs (natal+jour+lieu+versions) |
| computed_at | DATETIME | not null | timestamp calcul |
| scores_json | TEXT (JSON) | not null | notes 1–20, raw, power, vol par catégorie |
| timeline_json | TEXT (JSON) | not null | blocs UX + événements pivots |
| turning_points_json | TEXT (JSON) | not null | liste pivots (heure, cause, catégories affectées) |
| summary_text | TEXT | not null | synthèse écrite |
| debug_events_json | TEXT (JSON) | nullable | audit détaillé (optionnel) |

Contrainte conseillée : `UNIQUE(user_id, date_local, reference_version, ruleset_version)`.

#### ERD (Mermaid)
```mermaid
erDiagram
  REFERENCE_VERSIONS ||--o{ PLANETS : contains
  REFERENCE_VERSIONS ||--o{ HOUSES : contains
  REFERENCE_VERSIONS ||--o{ ASPECTS : contains
  REFERENCE_VERSIONS ||--o{ ASTRO_CHARACTERISTICS : has_traits

  USERS ||--o{ DAILY_SCORES : has

  PLANETS {
    int id
    int reference_version_id
    string code
    string name
    // optional columns: weight_intraday, ...
  }

  HOUSES {
    int id
    int reference_version_id
    int number
    string name
    // optional columns: ui_primary_category, ...
  }

  ASTRO_CHARACTERISTICS {
    int id
    int reference_version_id
    string entity_type
    string entity_code
    string trait
    string value
  }

  DAILY_SCORES {
    int id
    int user_id
    date date_local
    string timezone
    string reference_version
    string ruleset_version
    string input_hash
    datetime computed_at
    json scores_json
    json timeline_json
    json turning_points_json
    text summary_text
  }
```

#### Exemple JSON d’enregistrement (dans `daily_scores.scores_json` et `timeline_json`)
```json
{
  "date_local": "2026-03-07",
  "timezone": "Europe/Paris",
  "notes_1_20": {
    "energie": 13,
    "humeur": 9,
    "sante": 11,
    "travail": 14,
    "carriere": 16,
    "argent": 10,
    "amour": 12,
    "sexe_intimite": 15,
    "famille_foyer": 8,
    "social_reseau": 13,
    "communication": 12,
    "plaisir_creativite": 14
  },
  "rawday": {
    "energie": 0.42,
    "humeur": -0.18
  },
  "metrics": {
    "power": {"energie": 1.8, "humeur": 2.4},
    "volatility": {"energie": 0.35, "humeur": 0.70},
    "pivot_count": 2
  }
}
```

```json
{
  "blocks": [
    {
      "start_local": "07:00",
      "end_local": "09:00",
      "dominant_categories": ["travail", "communication"],
      "tone": "structurer",
      "turning_point": false
    },
    {
      "start_local": "10:15",
      "end_local": "11:30",
      "dominant_categories": ["carriere", "energie"],
      "turning_point": true,
      "drivers": [
        {"type": "aspect_exact_to_luminary", "planet": "moon", "aspect": "trine", "target": "sun"}
      ]
    }
  ],
  "turning_points": [
    {"at_local": "10:15", "reason": "exact_orb", "delta_note_min": 2}
  ]
}
```

### Règles éditoriales pour la synthèse textuelle
**Principe** : le texte est dérivé des scores, métriques et pivots, pas “inventé”.  
Cadre épistémologique : Britannica qualifie l’astrologie de **divination** ; donc rédaction en registres “tendances / vigilance / fenêtres favorables” (notamment santé/argent). citeturn0search3turn0search23  

#### Éléments obligatoires dans la synthèse
- **Top 3 catégories** (notes les plus élevées) : “où ça porte”.  
- **Top 2 exigeants** (notes basses ou forte puissance négative) : “où ça coûte”.  
- **Pivot principal** : heure + explication courte (event prioritaire).  
- **Période porteuse** : bloc avec Peak90 le plus haut.  
- **Prudence santé/argent** : formulations non prescriptives (pas de diagnostic médical / injonction financière).

#### Templates paramétrables (exemples)
- Intro : “Climat du jour : {tone_global}. Priorités : {top3}. Vigilance : {bottom2}.”  
- Pivot : “Point de bascule vers {hh:mm} : {event_driver} → impact {categories_impacted}.”  
- Santé : “Tendance : {note}/20. Ajustement conseillé : {micro_action}.” (micro_action = règles éditoriales statiques, non médicales)  
- Argent : “Tendance : {note}/20. Axe du jour : {prudence}.”  

### Diagramme flux (Mermaid)
```mermaid
flowchart TD
  A[Inputs: thème natal + date/heure locale + fuseau + localisation] --> B[Conversion en UT]
  B --> C[Positions & vitesses: swe_calc_ut]
  B --> D[Maisons & angles: swe_houses]
  B --> E[Lever/coucher: swe_rise_trans]
  C --> F[Détection aspects + orbes + applying/separating]
  D --> G[Changements Asc + routage maisons]
  C --> H[Changements de signe Lune]
  E --> I[Heures planétaires]
  F --> J[Contribution(e,c,t)]
  G --> J
  H --> J
  I --> J
  J --> K[RawStep(c,t) -> RawDay(c)]
  K --> L[Calibration percentile -> Note 1-20]
  L --> M[Blocs UX + points de bascule]
  M --> N[Synthèse textuelle]
  N --> O[Persist: daily_scores]
```

### Plan de tests unitaires et jeux de données
Objectif : valider chaque règle indépendamment (déterminisme, bornes, stabilité).

#### Jeux de données minimaux (≥ 10 cas types)
| Cas | Entrée (pattern) | Règle testée | Attendu |
|---|---|---|---|
| 1 | Aspect conjonction exact (orb→0) | `exact` + f_orb monotone | maximum local, event “exact” détecté |
| 2 | orb franchit seuil entre t et t+15 | `enter_orb` / `exit_orb` | event généré + temps raffiné |
| 3 | orb diminue sur 4 pas | applying | flag applying vrai citeturn0search37 |
| 4 | orb augmente sur 4 pas | separating | flag separating vrai citeturn0search37 |
| 5 | vitesse < 0 (rétrograde) | robustesse applying/separating | classification correcte malgré inversion |
| 6 | Lune change de signe entre deux pas | `moon_sign_ingress` | pivot détecté + raffinement |
| 7 | Asc change de signe | `asc_sign_change` | event + pivot potentiel citeturn3view2 |
| 8 | Heures planétaires | découpage lever/coucher | 24 segments (12 jour/12 nuit) cohérents citeturn1search14turn3view4 |
| 9 | Contribution hors orbe | f_orb=0 | Contribution = 0 |
| 10 | Saturation | clamp | Contribution bornée, RawStep borné |
| 11 | NS(c) bornes | clamp NS | NS ∈ [0.75,1.25] |
| 12 | pivot threshold | ΔNote≥2 ou top3 change | pivot_count cohérent |

#### Tests de cohérence globale (non-régression)
- Somme des poids matrices = 1 (planète→cat, maison→cat).  
- Stabilité : à inputs identiques, sortie identique (hash + versions).  
- Audit : pour chaque note, possibilité de remonter aux 3 principaux événements contributeurs (si `debug_events_json` activé).  

---

**Note de conformité épistémologique** : ce moteur produit une lecture symbolique et probabiliste ; l’écriture (et l’UI) doit éviter les formulations causales strictes ou prescriptives, en particulier pour la santé et l’argent. citeturn0search3turn0search23