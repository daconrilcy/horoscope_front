# Natal Pro Dev Guide (Settings, Errors, Validation)

Ce guide decrit comment reproduire un calcul natal pro de maniere deterministe, diagnostiquer les erreurs 422/503, et valider les resultats avec la suite Golden Pro.

## 1. Reglages pro figes (recommandes)

Pour un run pro reproductible, envoyer explicitement les options dans `POST /v1/astrology-engine/natal/calculate`:

- `accurate=true`
- `zodiac="tropical"` ou `zodiac="sidereal"`
- `ayanamsa="lahiri"` si `zodiac="sidereal"` (doit être envoyé explicitement pour garantir la reproductibilité, même si un défaut serveur existe)
- `frame="geocentric"` ou `frame="topocentric"`
- `house_system="placidus"` (ou `equal`, `whole_sign`)
- `tt_enabled=true` pour tracer `delta_t_sec` et `jd_tt`

Notes importantes:

- En configuration par defaut, les valeurs backend sont:
  - `zodiac=tropical`
  - `frame=geocentric`
  - `house_system=placidus`
  - `aspect_school=modern`
  - `tt_enabled=false` (sauf activation implicite par `SWISSEPH_PRO_MODE=true`)
- En mode non-accurate (`accurate=false`) sans `house_system` explicite, le service peut basculer vers `house_system=equal` pour la compatibilite moteur simplifie.
- Pour eviter toute ambiguite d audit, figer les champs ci-dessus dans chaque appel.

## 2. Variables runtime a verifier avant execution

Variables minimales a verifier cote backend:

- `SWISSEPH_ENABLED=true`
- `SWISSEPH_PRO_MODE=true` (recommande en phase pro)
- `EPHEMERIS_PATH`
- `EPHEMERIS_PATH_VERSION`
- `EPHEMERIS_PATH_HASH` (recommande)
- `EPHEMERIS_REQUIRED_FILES` (CSV)

Verifier l etat runtime:

```powershell
curl -sS http://127.0.0.1:8000/v1/ephemeris/status
```

Resultat attendu en mode OK:

- `status="ok"`
- `path_version` renseigne
- `path_hash` renseigne (si configure)

## 3. Exemples d appels endpoints

### 3.1 Prepare (normalisation temps + trace timezone)

```bash
curl -sS -X POST "http://127.0.0.1:8000/v1/astrology-engine/natal/prepare" \
  -H "Content-Type: application/json" \
  --max-time 30 \
  -d '{
    "birth_date": "1990-06-15",
    "birth_time": "12:34",
    "birth_place": "Paris",
    "birth_timezone": "Europe/Paris",
    "tt_enabled": true
  }'
```

### 3.2 Calculate (profil pro audit-grade)

```bash
curl -sS -X POST "http://127.0.0.1:8000/v1/astrology-engine/natal/calculate" \
  -H "Content-Type: application/json" \
  --max-time 60 \
  -d '{
    "birth_date": "1990-06-15",
    "birth_time": "12:34",
    "birth_place": "Paris",
    "birth_timezone": "Europe/Paris",
    "reference_version": "1.0.0",
    "accurate": true,
    "zodiac": "sidereal",
    "ayanamsa": "lahiri",
    "frame": "topocentric",
    "house_system": "placidus",
    "tt_enabled": true
  }'
```

Points de verification de reponse:

- `data.result.engine="swisseph"`
- `data.result.aspect_school` present
- `meta.ephemeris_path_version` present
- `meta.time_scale` = `TT` si TT actif
- `meta.delta_t_sec` et `meta.jd_tt` presents si TT actif

## 4. Erreurs standardisees 422 et 503

### 4.1 Erreurs 422 (fonctionnelles / validation)

| Code | Cause probable | Remediation |
|---|---|---|
| `invalid_birth_input` | Payload invalide (schema, type, champs manquants) | Corriger JSON selon schema endpoint |
| `invalid_birth_time` | Format heure invalide | Utiliser `HH:MM` ou `HH:MM:SS` |
| `invalid_timezone` | IANA timezone inconnue | Fournir un identifiant IANA valide (`Europe/Paris`) |
| `missing_timezone` | Timezone absente sans derivation active | Fournir `birth_timezone` ou activer derivation |
| `missing_coordinates` | Derivation timezone active mais lat/lon absents | Fournir `birth_lat` et `birth_lon` |
| `timezone_derivation_failed` | Derivation timezone impossible | Verifier coordonnees ou passer timezone explicite |
| `ambiguous_local_time` | Heure locale ambigue (DST fold) | Re-saisir heure exacte UTC ou ajuster l heure locale |
| `nonexistent_local_time` | Heure locale inexistante (DST gap) | Choisir une heure valide hors transition DST |
| `date_out_of_range` | Date hors fenetre de calcul supportee | Utiliser une date comprise dans la plage supportee |
| `invalid_zodiac` | Valeur zodiac invalide | Utiliser `tropical` ou `sidereal` |
| `missing_ayanamsa` | `zodiac=sidereal` sans ayanamsa | Ajouter `ayanamsa` (ex: `lahiri`) |
| `invalid_ayanamsa` | Ayanamsa non supportee | Utiliser une valeur supportee |
| `invalid_frame` | Frame invalide | Utiliser `geocentric` ou `topocentric` |
| `missing_topocentric_coordinates` | `frame=topocentric` sans lat/lon | Fournir `birth_lat` et `birth_lon` |
| `invalid_house_system` | House system invalide | Utiliser `placidus`, `equal`, ou `whole_sign` |
| `accurate_mode_required` | Options necessitant SwissEph avec `accurate=false` | Passer `accurate=true` |
| `invalid_aspect_school` | Aspect school invalide | Utiliser `modern`, `classic`, ou `strict` |

### 4.2 Erreurs 503 (techniques / indisponibilite)

| Code | Cause probable | Remediation |
|---|---|---|
| `ephemeris_data_missing` | Fichier ephemeris requis absent | Verifier `EPHEMERIS_PATH` et `EPHEMERIS_REQUIRED_FILES` |
| `swisseph_init_failed` | Initialisation SwissEph echouee | Verifier path/permissions/fichiers, redemarrer backend |
| `swisseph_not_initialized` | Bootstrap non execute | Verifier sequence startup et flags |
| `ephemeris_calc_failed` | Echec calcul planete SwissEph | Verifier donnees entree et installation ephemeris |
| `houses_calc_failed` | Echec calcul maisons SwissEph | Verifier coordonnees, house system, integrite runtime |
| `natal_engine_unavailable` | Moteur SwissEph indisponible | Activer SwissEph ou ajuster options de calcul |

Regle pratique:

- `422`: corriger la requete ou les parametres fonctionnels.
- `503`: corriger l etat runtime/service (fichiers, bootstrap, disponibilite moteur).

## 5. Guide de validation Golden Pro

Prerequis:

- venv actif
- backend installe avec extras dev
- SwissEph disponible pour les tests qui le requierent

Commandes (depuis racine repo):

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/app/tests/unit/test_golden_pro_dataset.py
pytest -q backend/app/tests/unit/test_golden_zodiac_frame_invariants.py
```

Tolerances Golden Pro attendues (dataset v1):

- `planets_deg = 0.01`
- `angles_deg = 0.05`

Verification de prerequis dataset:

- Dataset id: `golden-pro-v1`
- Volume: entre 50 et 200 cas
- Scope settings: moteur SwissEph + combinaisons frame/zodiac/house_system supportees

Si ecart:

1. Verifier les variables ephemeris (`EPHEMERIS_PATH_VERSION`, `EPHEMERIS_PATH_HASH`).
2. Verifier que les options de calcul de la requete sont figees.
3. Regenerer un run propre puis comparer au dataset golden.

## 6. Smoke manuel "from scratch"

1. Demarrer backend avec SwissEph actif.
2. Verifier `GET /v1/ephemeris/status` en `status=ok`.
3. Executer un `POST /v1/astrology-engine/natal/prepare`.
4. Executer un `POST /v1/astrology-engine/natal/calculate` avec options pro figees.
5. Verifier les champs d audit (`engine`, `ephemeris_path_version`, `time_scale`, `jd_tt` si TT).
6. Executer les tests Golden Pro ci-dessus.
7. Conserver les artefacts de sortie (logs + versions ephemeris) pour tracabilite.
