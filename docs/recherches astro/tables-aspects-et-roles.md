# Tables liées aux aspects astrologiques et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux aspects astrologiques dans l'état courant du schéma Alembic, après les migrations `20260218_0001_create_reference_tables.py`, `20260226_0027_add_default_orb_deg_to_aspects.py`, `20260307_0032_migration_a_prediction_reference_tables.py`, `20260512_0086_deversion_astrology_structures.py` et `20260514_0099_rename_astral_reference_tables.py`.

Deux catégories sont distinguées :

- Tables SQL qui décrivent le vocabulaire stable des aspects et leur paramétrage prédictif.
- Tables, payloads et objets runtime qui calculent, transportent ou restituent des aspects sous forme de JSON ou d'événements.

Point important : les aspects réels d'un thème ne sont pas stockés dans une table relationnelle dédiée. Ils sont calculés à l'exécution à partir des longitudes planétaires ou des états temporels, puis transportés dans `NatalResult.aspects`, `chart_results.result_payload.aspects`, les événements de prédiction et les payloads publics.

## Vue d'ensemble

| Table ou payload | Lien aux aspects | Rôle principal | Versionné |
| --- | --- | --- | --- |
| `astral_aspects` | Table canonique des cinq aspects majeurs | Vocabulaire stable : code, nom, angle exact et orbe natal par défaut | Non |
| `astral_aspect_profiles` | `aspect_id -> astral_aspects.id` | Paramétrage du moteur daily : intensité, valence, multiplicateur d'orbe, phase | Oui, via `reference_version_id` |
| `ruleset_event_types` | Codes d'événements d'aspect | Pondération et priorité des événements `aspect_*` | Indirectement via le ruleset |
| `ruleset_parameters` | Paramètres de phase/orbe | Multiplicateurs runtime applicables à certains événements | Indirectement via le ruleset |
| `chart_results` | JSON `result_payload.aspects` | Snapshot des aspects natals calculés pour un thème | Version texte dans payload et colonnes |
| `daily_prediction_category_scores` | JSON `contributors_json` | Historique des contributeurs pouvant inclure des événements d'aspect | Indirectement via le run |
| `daily_prediction_turning_points` | JSON `driver_json` | Historique des événements conducteurs, souvent des aspects exacts | Indirectement via le run |
| `user_prediction_baselines` | Pas de colonne aspect | Baselines calculées à partir de scores où les aspects sont déjà agrégés | Oui, via référence/ruleset |

## Tables de référence directes

### `astral_aspects`

Définie par `AspectModel` dans `backend/app/infra/db/models/reference.py`.

Historique :

- Créée par `20260218_0001_create_reference_tables.py` avec un `reference_version_id`.
- Enrichie par `20260226_0027_add_default_orb_deg_to_aspects.py` avec `default_orb_deg`.
- Déversionnée par `20260512_0086_deversion_astrology_structures.py`.
- Renommée en `astral_aspects` par `20260514_0099_rename_astral_reference_tables.py`.
- Depuis cette migration, `astral_aspects` est un vocabulaire stable, indépendant des versions de paramétrage.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique utilisé par les clés étrangères. |
| `code` | `String(32)` | Code applicatif stable, par exemple `trine` ou `square`. |
| `name` | `String(64)` | Nom lisible. |
| `angle` | `Integer` | Angle exact de référence sur le cercle zodiacal. |
| `default_orb_deg` | `Float` | Orbe natal par défaut utilisé par le calcul de thème. |

Contraintes :

- Unicité sur `code`.
- Index sur `code`.
- Plus de `reference_version_id` depuis `20260512_0086`.

Aspects seedés par `ReferenceRepository.seed_version_defaults` :

| Code | Nom SQL | Angle | Orbe natal par défaut |
| --- | --- | ---: | ---: |
| `conjunction` | `Conjunction` | 0 | 8.0 |
| `sextile` | `Sextile` | 60 | 4.0 |
| `square` | `Square` | 90 | 6.0 |
| `trine` | `Trine` | 120 | 6.0 |
| `opposition` | `Opposition` | 180 | 8.0 |

Rôle métier :

- Sert de dictionnaire canonique des aspects majeurs supportés.
- Alimente `ReferenceRepository.get_reference_data`, donc le calcul natal reçoit les aspects sous forme de contrats `code`, `name`, `angle`, `default_orb_deg`.
- Sert de cible relationnelle à `astral_aspect_profiles`.
- Ne stocke pas de planète, de paire planétaire, d'orbe observé, de phase applying/separating ou de résultat utilisateur.

## Table de paramétrage du moteur de prédiction quotidienne

### `astral_aspect_profiles`

Définie par `AspectProfileModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de configuration du moteur de prédiction quotidienne.
- Ne calcule aucun aspect : elle qualifie un aspect déjà identifié par le calcul natal ou par `EventDetector`.
- Versionnée par `reference_version_id`.
- Verrouillée via `_ensure_reference_version_is_mutable` quand la version de référence est verrouillée.

Historique :

- Créée par `20260307_0032_migration_a_prediction_reference_tables.py`.
- Initialement unique par `aspect_id`.
- Versionnée par `20260512_0086_deversion_astrology_structures.py`, avec unicité `(reference_version_id, aspect_id)`.
- Renommée en `astral_aspect_profiles` par `20260514_0099_rename_astral_reference_tables.py`.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence qui porte ce paramétrage prédictif. |
| `aspect_id` | Aspect canonique concerné. |
| `intensity_weight` | Poids d'intensité utilisé dans les contributions et certains calculs de sensibilité natale. |
| `default_valence` | Valence de base : `favorable`, `challenging`, `polarizing` ou `contextual` dans le seed actuel. |
| `orb_multiplier` | Multiplicateur appliqué à l'orbe actif de la planète transitante ou à certains orbes natals du moteur daily. |
| `phase_sensitive` | Indique si l'aspect doit être sensible à la phase. Actuellement chargé mais peu exploité directement. |
| `micro_note` | Note éditoriale optionnelle, non exposée dans `AspectProfileData` au moment de cette analyse. |

Valeurs seedées dans `run_prediction_reference_seed` :

| Aspect | Intensité | Valence | Multiplicateur d'orbe | Sensible phase |
| --- | ---: | --- | ---: | --- |
| `conjunction` | 1.5 | `contextual` | 1.0 | Non |
| `sextile` | 0.8 | `favorable` | 0.9 | Non |
| `square` | 1.2 | `challenging` | 1.0 | Non |
| `trine` | 1.0 | `favorable` | 1.0 | Non |
| `opposition` | 1.3 | `polarizing` | 1.0 | Oui |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_aspect_profiles`.
- Injectée dans `PredictionContext.aspect_profiles` sous forme de mapping `code -> AspectProfileData`.
- Figée par `PredictionContextLoader._freeze_aspect_profile`.
- Validée par le seed avec un comptage attendu de `5` profils par version de référence complète.
- Utilisée par :
  - `EventDetector._orb_max` pour moduler l'orbe actif planète x aspect ;
  - `ContributionCalculator._w_aspect` pour pondérer les contributions ;
  - `ContributionCalculator._pol` pour résoudre la polarité de l'événement ;
  - `IntradayActivationBuilder` pour construire les activations lunaires intraday ;
  - `TransitSignalBuilder` via les mêmes événements/contributions ;
  - `NatalSensitivityCalculator._compute_natal_aspects_contribution` pour moduler la sensibilité structurelle par thème ;
  - `EngineOrchestrator._compute_natal_aspects` pour enrichir le `NatalChart` interne du moteur daily.

Nuance importante :

- `astral_aspects.default_orb_deg` sert au calcul natal de `NatalResult.aspects`.
- `astral_aspect_profiles.orb_multiplier` sert au moteur de prédiction, combiné aux profils planétaires ou à des orbes internes.
- Les deux champs ne doivent pas être fusionnés : le premier décrit le référentiel astrologique de calcul natal, le second décrit une pondération produit de prédiction.

## Tables adjacentes nécessaires au fonctionnement

### `astral_reference_versions`

Rôle :

- Versionne les paramètres de prédiction, pas le vocabulaire stable `astral_aspects`.
- Verrouille les versions via `is_locked`.
- Les mises à jour de `astral_aspect_profiles` passent par `_ensure_reference_version_is_mutable`.

### `ruleset_event_types`

Rôle :

- Porte les priorités et poids de base des événements du moteur daily.
- Les événements d'aspect seedés sont :

| Code | Groupe | Priorité | Poids de base |
| --- | --- | ---: | ---: |
| `aspect_exact_to_angle` | `aspect` | 80 | 2.0 |
| `aspect_exact_to_luminary` | `aspect` | 75 | 1.8 |
| `aspect_exact_to_personal` | `aspect` | 68 | 1.5 |
| `aspect_enter_orb` | `aspect` | 40 | 1.0 |
| `aspect_exit_orb` | `aspect` | 25 | 0.5 |

Ces lignes ne définissent pas ce qu'est un trigone ou un carré. Elles qualifient les types d'événements produits quand un aspect entre en orbe, devient exact ou sort d'orbe.

### `ruleset_parameters`

Rôle :

- Porte les paramètres génériques du ruleset, dont `orb_multiplier_applying`, `orb_multiplier_exact` et `orb_multiplier_separating`.
- Ces paramètres relèvent du comportement moteur, pas du vocabulaire canonique des aspects.

### `prediction_categories`, `astral_planet_category_weights`, `astral_house_category_weights`

Rôle :

- Les aspects ne sont pas directement routés vers les catégories par une table `aspect_category_weights`.
- Le routage thématique passe surtout par les planètes impliquées, les maisons cible/transitée, les points astrologiques et la sensibilité natale.
- L'aspect module l'intensité et la polarité du signal ; il ne choisit pas seul la catégorie.

## Données de calcul et de résultat

### Calcul natal

Le calcul natal est porté par `build_natal_result` dans `backend/app/domain/astrology/natal_calculation.py`.

Flux :

1. `ReferenceRepository.get_reference_data` expose `aspects[]` depuis la table stable `astral_aspects`.
2. `build_natal_result` vérifie que `aspects[]` existe et que chaque entrée contient un `code`, un `angle` et un `default_orb_deg` valide.
3. Les éventuels champs `orb_luminaries_override_deg`, `orb_luminaries`, `orb_pair_overrides`, `orb_pairs` ou `orb_overrides` sont acceptés si présents dans la source de référence.
4. Les aspects sont triés par angle et code.
5. Le calcul filtre explicitement sur `MAJOR_ASPECT_CODES`, soit `conjunction`, `sextile`, `square`, `trine`, `opposition`.
6. `calculate_major_aspects` compare toutes les paires de positions planétaires et applique la résolution hiérarchique des orbes.
7. Les résultats sont convertis en `AspectResult`.

Contrat `AspectResult` :

| Champ | Rôle |
| --- | --- |
| `aspect_code` | Code canonique de l'aspect détecté. |
| `planet_a`, `planet_b` | Corps impliqués, triés pour stabilité de sortie. |
| `angle` | Angle théorique de l'aspect. |
| `orb` | Écart angulaire réel historique. |
| `orb_used` | Même écart réel, champ plus explicite ajouté pour compatibilité. |
| `orb_max` | Seuil d'orbe résolu pour cette paire. |

Le calcul d'orbe dans `calculate_major_aspects` suit cet ordre :

1. Override spécifique à la paire, par exemple `sun-mercury`.
2. Override luminaire si l'une des deux planètes est `sun` ou `moon`.
3. Orbe par défaut de l'aspect.

Le calcul produit des compteurs d'observabilité :

- `aspects_calculated_total_{aspect_school}`
- `aspects_rejected_orb_total`

Limite :

- Le champ `aspect_school` est présent dans `NatalResult` et la configuration (`modern`, `traditional`), mais les aspects relationnels ne référencent pas encore une table `astral_systems` ou une école d'aspects.
- Le calcul courant repose sur les cinq aspects majeurs déclarés dans `MAJOR_ASPECT_CODES`.

### `chart_results`

Définie par `ChartResultModel`.

Colonnes pertinentes :

| Colonne | Rôle |
| --- | --- |
| `reference_version` | Version du référentiel utilisée pour construire le thème. |
| `ruleset_version` | Version de règles utilisée. |
| `result_payload` | Snapshot JSON complet du résultat de thème. |

Rôle des aspects dans `result_payload` :

- `aspects[]` contient les aspects natals majeurs exposés publiquement.
- `chart_json_builder` filtre encore sur les aspects majeurs avant sérialisation.
- Chaque aspect public contient `type`, `planet_a`, `planet_b`, `angle`, `orb` et `applying`.
- `applying` vaut actuellement `null` pour le natal, car le statut applying/separating n'est pas connu dans ce contexte.

Exemple de projection publique :

```json
{
  "type": "trine",
  "planet_a": "moon",
  "planet_b": "sun",
  "angle": 120.0,
  "orb": 1.4,
  "applying": null
}
```

### Catalogue d'évidence

`build_enriched_evidence_catalog` transforme les aspects du JSON de thème en identifiants stables.

Format :

- `ASPECT_{PLANET_A}_{PLANET_B}_{TYPE}`
- `ASPECT_{PLANET_A}_{PLANET_B}_{TYPE}_ORB{orb_int}`

Exemples :

```text
ASPECT_MOON_SUN_TRINE
ASPECT_MOON_SUN_TRINE_ORB1
```

Les paires sont triées pour stabiliser les identifiants. Le validateur LLM accepte et canonicalise aussi certaines variantes historiques.

## Moteur de prédiction quotidienne

### Détection des aspects transit -> natal

`EventDetector` détecte les aspects à partir d'une séquence de `StepAstroState`.

Aspects supportés :

| Angle | Code |
| ---: | --- |
| 0 | `conjunction` |
| 60 | `sextile` |
| 90 | `square` |
| 120 | `trine` |
| 180 | `opposition` |

Cibles natales V1 :

- Planètes : `Sun`, `Moon`, `Mercury`, `Venus`, `Mars`, `Jupiter`, `Saturn`, `Uranus`, `Neptune`, `Pluto`.
- Angles : `Asc`, `MC`.

Événements produits :

- `aspect_enter_orb` quand l'orbe passe sous le seuil actif.
- `aspect_exit_orb` quand l'orbe sort du seuil actif.
- `aspect_exact_to_angle` pour un exact vers `Asc` ou `MC`.
- `aspect_exact_to_luminary` pour un exact vers `Sun` ou `Moon`.
- `aspect_exact_to_personal` pour les autres cibles.

Métadonnées principales :

| Métadonnée | Rôle |
| --- | --- |
| `natal_house_target` | Maison natale de la cible. |
| `natal_house_transited` | Maison natale traversée par la planète transitante. |
| `orb_max` | Seuil actif résolu via planète et profil d'aspect. |
| `phase` | `applying` ou `separating` selon l'évolution de l'orbe. |

### Contribution numérique

`ContributionCalculator` combine l'aspect avec les autres facteurs :

```text
w_event × w_planet × w_aspect × f_orb × f_phase × f_target × NS(c) × D(e,c) × Pol(e,c)
```

Rôle de l'aspect :

- `w_aspect` vient de `AspectProfileData.intensity_weight`.
- `f_orb` décroît selon l'écart à `orb_max`.
- `f_phase` dépend de `metadata.phase`.
- `Pol(e,c)` lit `AspectProfileData.default_valence`, puis éventuellement la polarité typique de la planète pour les valences contextuelles.

Point d'attention :

- Le code actuel de polarité reconnaît explicitement `positive`, `negative` et `neutral`, puis traite le reste comme contextuel.
- Les valeurs seedées `favorable`, `challenging` et `polarizing` passent donc par la branche contextuelle si aucune traduction dédiée n'est ajoutée.
- Ce comportement peut être voulu ou hérité, mais il doit être audité avant de s'en servir comme vocabulaire métier strict.

### Aspects natals internes au moteur daily

`EngineOrchestrator._compute_natal_aspects` reconstruit des aspects natals internes à partir des positions normalisées et du contexte de prédiction.

Caractéristiques :

- Produit des `AstroEvent(event_type="natal_aspect")`.
- Utilise les cinq aspects de `EventDetector.ASPECTS_V1`.
- Applique un `orb_max` interne de base `5.0`, multiplié par `AspectProfileData.orb_multiplier`.
- Injecte `default_valence`, `orb_max` et `is_natal` dans les métadonnées.

Ces événements ne remplacent pas `NatalResult.aspects`. Ils servent au moteur de prédiction, notamment à la sensibilité natale.

### Sensibilité natale

`NatalSensitivityCalculator._compute_natal_aspects_contribution` consomme `NatalChart.natal_aspects`.

Rôle :

- Identifie si les deux corps d'un aspect natal sont des significateurs d'une catégorie.
- Pondère par `intensity_weight`.
- Module par la valence d'aspect et l'orbe.
- Retourne une composante normalisée qui entre dans le score structurel par thème.

La valence y est résolue par `_aspect_valence`, avec fallback favorable pour `trine`, `sextile`, `conjunction` et challenging pour `square`, `opposition` si le profil ne fournit pas une valence exploitable.

### Aspects intraday lunaires

`IntradayActivationBuilder` parcourt les aspects V1 entre la Lune et les cibles natales.

Rôle :

- Produit des contributeurs de type `moon_aspect`.
- Réutilise l'orbe, la pondération d'aspect, la phase et la polarité via `EventDetector` et `ContributionCalculator`.
- Sert aux timelines et activations continues, pas au calcul natal public.

### Aspects enrichis

`EnrichedAstroEventsBuilder` ajoute des événements publics display-only :

- `sky_aspect` pour les aspects ciel -> ciel du jour, avec orbe fixe `<= 1.5°` et limite de quatre événements.
- `progression_aspect` pour les aspects de progressions secondaires vers le natal, avec orbe fixe `<= 1.0°`.
- Les conjonctions aux étoiles fixes utilisent aussi une logique angulaire, mais ne sont pas des aspects issus de la table `astral_aspects`.

Ces événements utilisent les mêmes codes d'aspect majeurs, mais ils ne sont pas alimentés directement par `astral_aspect_profiles` et ont `base_weight = 0.0` quand ils sont display-only.

## Restitution publique et frontend

### Projections publiques backend

`PublicAstroFoundationProjector` expose `dominant_aspects` :

- Prend les événements dont le type est dans `PUBLIC_ASTRO_ASPECT_EVENT_TYPES`.
- Exclut les self-aspects où `body == target`.
- Trie par orbe pour garder les quatre aspects dominants.
- Traduit les libellés via `public_astro_vocabulary`.

`PublicAstroDailyEventsProjector` expose :

- `aspects` pour les aspects transit -> natal publics.
- `sky_aspects` pour les aspects ciel -> ciel enrichis.
- `progressions` pour les aspects de progressions secondaires.

### Vocabulaire public

`public_astro_vocabulary.py` définit les libellés et tonalités :

| Aspect | Libellé FR | Tonalité |
| --- | --- | --- |
| `conjunction` | Conjonction | intensification |
| `sextile` | Sextile | fluidité |
| `square` | Carré | ajustement |
| `trine` | Trigone | fluidité |
| `opposition` | Opposition | ajustement |
| `quincunx` | Quinconce | adaptation |

Point d'attention :

- `quincunx` existe dans le vocabulaire public, mais n'est pas seedé dans `astral_aspects` et n'est pas dans `MAJOR_ASPECT_CODES`.
- Il peut donc être affiché si un événement enrichi ou externe l'émet, mais il ne fait pas partie du référentiel relationnel actif.

### Frontend

Le frontend consomme les aspects dans plusieurs zones :

- `frontend/src/api/natal-chart/index.ts` expose `AspectResult`.
- `NatalChartPage.tsx` affiche les aspects natals et l'état vide.
- `frontend/src/i18n/natalChart.ts` contient les descriptions pédagogiques et lectures rapides.
- `frontend/src/utils/predictionI18n.ts` traduit les aspects dans les drivers de prédiction.
- `AstroDailyEvents.tsx` et `AstroFoundationSection.tsx` affichent les aspects publics daily.
- `NatalInterpretationEvidence.tsx` catégorise les preuves `ASPECT_*` dans `major_aspects`.

Compatibilité :

- Certains chemins frontend manipulent `aspect_code` en majuscules (`TRINE`) alors que le backend canonique relationnel utilise des codes minuscules (`trine`).
- Les helpers de traduction normalisent généralement la casse, mais les nouveaux contrats doivent préciser la forme attendue.

## Étapes où les aspects interviennent dans les calculs

1. `ReferenceRepository.seed_version_defaults` garantit les cinq lignes de `astral_aspects`.
2. `ReferenceRepository.get_reference_data` expose les aspects stables au calcul natal.
3. `build_natal_result` valide les définitions d'aspect et filtre les aspects majeurs.
4. `calculate_major_aspects` compare toutes les paires de positions et résout les orbes.
5. `NatalResult.aspects` transporte les `AspectResult`.
6. `chart_json_builder` sérialise les aspects majeurs dans `result_payload.aspects`.
7. `build_enriched_evidence_catalog` produit les preuves `ASPECT_*`.
8. `run_prediction_reference_seed` alimente `astral_aspect_profiles` pour la version de référence active.
9. `PredictionReferenceRepository.get_aspect_profiles` charge les profils dans `PredictionContext`.
10. `PredictionContextLoader` fige les profils d'aspect dans le contexte chargé.
11. `EventDetector` détecte les entrées/sorties d'orbe et aspects exacts transit -> natal.
12. `ContributionCalculator` applique `w_aspect`, `f_orb`, `f_phase` et la polarité.
13. `EngineOrchestrator` reconstruit des `natal_aspect` internes pour la sensibilité daily.
14. `NatalSensitivityCalculator` intègre les aspects natals dans la sensibilité par catégorie.
15. `IntradayActivationBuilder` construit les activations lunaires par aspect.
16. `EnrichedAstroEventsBuilder` ajoute des aspects ciel -> ciel et progressions display-only.
17. `daily_prediction_*` persiste les scores, contributeurs et drivers incluant les événements d'aspect.
18. Les projecteurs publics extraient `aspects`, `sky_aspects` et `dominant_aspects`.
19. Le frontend traduit et affiche les aspects natals et daily.

## Points d'attention

- `astral_aspects` est stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- Les paramètres de scoring quotidien doivent rester dans `astral_aspect_profiles`, pas dans `astral_aspects`.
- Les orbes observés d'un thème ou d'un événement ne doivent pas être stockés dans `astral_aspects` ou `astral_aspect_profiles`.
- `astral_aspects.default_orb_deg` et `astral_aspect_profiles.orb_multiplier` ont des responsabilités différentes.
- Le référentiel relationnel actif ne contient que cinq aspects majeurs : conjonction, sextile, carré, trigone, opposition.
- Les aspects mineurs ne doivent pas être ajoutés dans les calculs publics sans mettre à jour `MAJOR_ASPECT_CODES`, les seeds, les tests, les traductions et les contrats.
- `quincunx` est présent dans le vocabulaire public mais absent du référentiel relationnel et du calcul majeur courant.
- Les aspects transit -> natal sont des événements, pas des lignes SQL relationnelles.
- Les aspects ciel -> ciel et progressions secondaires enrichis sont display-only dans l'état courant, avec `base_weight = 0.0`.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas d'intégrité référentielle avec `astral_aspects`.
- Les valeurs seedées de `default_valence` ne correspondent pas exactement aux branches explicites de `ContributionCalculator._pol`; auditer ce point avant de conclure sur la polarité effective des aspects.
- `phase_sensitive` est seedé mais peu consommé directement ; ne pas l'utiliser comme garantie fonctionnelle sans test dédié.
- Les paires d'aspects dans le catalogue d'évidence sont triées pour stabilité ; ne pas dépendre de l'ordre original des planètes.
- Le calcul natal public n'expose pas actuellement `applying/separating`.
- Les chemins runtime mélangent parfois codes titrés (`Sun`, `Moon`) et minuscules (`sun`, `moon`) ; les lookups font des normalisations partielles.
- Le garde-fou sur les aspects majeurs est double : table seedée à cinq lignes et constante `MAJOR_ASPECT_CODES`.

## Fichiers sources consultés

- `backend/app/core/constants.py`
- `backend/app/core/config.py`
- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/prediction/contribution_calculator.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/domain/prediction/intraday_activation_builder.py`
- `backend/app/domain/prediction/transit_signal_builder.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/llm/runtime/output_validator.py`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/components/AstroDailyEvents.tsx`
- `frontend/src/components/AstroFoundationSection.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- `backend/migrations/versions/20260218_0001_create_reference_tables.py`
- `backend/migrations/versions/20260226_0027_add_default_orb_deg_to_aspects.py`
- `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py`
- `backend/migrations/versions/20260512_0086_deversion_astrology_structures.py`
- `backend/migrations/versions/20260514_0099_rename_astral_reference_tables.py`
