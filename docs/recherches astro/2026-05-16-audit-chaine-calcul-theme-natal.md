# Audit de la chaine de calcul du theme astrologique natal

Date: 2026-05-16  
Perimetre: backend FastAPI, domaine astrologique, persistance, API publique, consommation React.  
Objectif: verifier la chaine effective de calcul du theme natal, ses garde-fous et ses limites.

## Synthese executive

La chaine de calcul natal est globalement structuree, tracable et testee sur les invariants critiques: preparation temps/fuseau, choix du moteur, chargement du referentiel runtime, calcul des positions/maisons/aspects, enrichissements runtime, persistance et restitution front.

Le flux de production privilegie le moteur SwissEph en mode `accurate=true` depuis le front. Le moteur simplifie reste present, mais il est encadre comme fallback/dev/interne et limite a un systeme tropical, geocentrique, maisons egales. Les versions de referentiel, ruleset, moteur, systeme de maisons, zodiaque, frame, JD UT/TT et chemins d'ephemerides sont exposes dans les metadonnees.

Les principaux risques residuels ne sont pas des ruptures immediates, mais des zones a surveiller:

- La precision des positions depend de la configuration runtime `swisseph_enabled` et du bootstrap des ephemerides.
- Le calcul utilise `prepared.julian_day`/JD UT pour SwissEph; les champs TT sont traces mais pas injectes dans `swe.calc_ut`, ce qui est coherent avec `calc_ut` mais doit rester documente.
- La validation astronomique externe est partielle: il existe des golden/cross-tool tests, mais l'audit n'a pas execute de comparaison live contre un outil tiers.
- Le front affiche surtout le contrat historique plat (`planet_positions`, `houses`, `aspects`) et exploite peu les enrichissements runtime (`signs_runtime`, `chart_balance`, runtime maisons/aspects).

## Flux nominal utilisateur

1. L'utilisateur renseigne ses donnees de naissance via `PUT /v1/users/me/birth-data`.
2. Le front lance la generation depuis `generateNatalChart(accessToken, true)`, donc `POST /v1/users/me/natal-chart` avec `accurate=true`.
3. La route `generate_me_natal_chart` valide la requete, appelle `UserNatalChartService.generate_for_user`, puis commit.
4. `UserNatalChartService` charge le profil, exige une heure de naissance, resout les coordonnees, impose un lieu resolu en mode accurate, puis construit un `BirthInput`.
5. `NatalCalculationService.calculate` resout les options astrologiques, charge le referentiel runtime DB, choisit le moteur, verifie le bootstrap SwissEph et appelle `build_natal_result`.
6. `build_natal_result` prepare le temps, calcule positions, maisons, affectations en maisons, aspects, maitres de maisons, runtime signes/maisons/aspects et signature de theme.
7. `ChartResultService.persist_trace` persiste le resultat avec hash d'entree et payload complet.
8. `GET /v1/users/me/natal-chart/latest` restitue le theme et ajoute `astro_profile` derive de la geometrie.
9. La page React `NatalChartPage` affiche planetes, maisons, aspects, profil astro et declenche l'interpretation LLM via `/v1/natal/interpretation`.

Points d'ancrage:

- `backend/app/api/v1/routers/public/users.py:441` - generation utilisateur.
- `backend/app/services/user_profile/natal_chart_service.py:157` - orchestration utilisateur.
- `backend/app/services/natal/calculation_service.py:329` - orchestration calcul.
- `backend/app/domain/astrology/natal_calculation.py:302` - construction du resultat natal.
- `backend/app/services/chart/result_service.py:78` - persistance audit.
- `frontend/src/api/natal-chart/index.ts:121` - appel front de generation.
- `frontend/src/pages/NatalChartPage.tsx:87` - action utilisateur.

## Preparation temps, fuseau et entree

Le modele `BirthInput` interdit les champs inconnus, normalise les chaines et accepte les champs de lieu et coordonnees. `prepare_birth_data` gere:

- Fuseau IANA fourni par l'utilisateur ou derive depuis lat/lon si l'option runtime l'autorise.
- Detection explicite des heures locales ambigues ou inexistantes lors des transitions DST.
- Conversion local vers UTC.
- Calcul du timestamp UTC et du jour julien UT.
- Validation de plage de dates supportee.
- Champs TT optionnels: `delta_t_sec`, `jd_tt`, `time_scale`.

Constat: la gestion des fuseaux et des ambiguities DST est robuste. Les erreurs fonctionnelles sont levees avec codes explicites (`missing_timezone`, `invalid_timezone`, `ambiguous_local_time`, `nonexistent_local_time`).

Point d'attention: si l'heure de naissance manque, `prepare_birth_data` sait utiliser minuit local, mais le flux utilisateur de generation natale refuse actuellement `birth_time=None`. C'est coherent pour un theme natal precis, mais le produit doit rester clair sur cette contrainte.

Ancrage: `backend/app/domain/astrology/natal_preparation.py:385`.

## Choix moteur et options astrologiques

`NatalCalculationService` resout:

- `zodiac`: tropical ou sidereal.
- `ayanamsa`: requis si sidereal explicitement demande.
- `frame`: geocentric ou topocentric.
- `house_system`: placidus, equal, whole_sign, porphyry selon enums/config.
- `altitude_m`: forcee a `0.0` en topocentric si absente.
- `aspect_school`: par defaut via settings.

Le moteur SwissEph est obligatoire pour sidereal, topocentric ou systeme de maisons non equal. Le moteur simplifie est bloque en production et refuse les options non supportees.

Constat: la resolution des options evite les fallbacks silencieux et remonte des codes fonctionnels utiles (`missing_ayanamsa`, `accurate_mode_required`, `invalid_zodiac`, `invalid_frame`, `invalid_house_system`, `natal_engine_unavailable`).

Risque residuel: le comportement depend fortement des settings (`swisseph_enabled`, `natal_engine_default`, `natal_engine_simplified_enabled`, `active_reference_version`). Une verification de config au demarrage reste critique.

Ancrage: `backend/app/services/natal/calculation_service.py:37`.

## Ephemerides, maisons et geometrie

Pour SwissEph:

- Les positions planetaires sont calculees via `swe.calc_ut`.
- Les corps proviennent du catalogue runtime `astral_planets.code -> swe_id`.
- Les longitudes sont normalisees en `[0, 360)`.
- La vitesse longitudinale et la retrogradation sont exposees.
- Le mode sidereal est encapsule et reinitialise apres calcul.
- Le mode topocentric pose puis reinitialise `swe.set_topo`.

Pour les maisons:

- Les cuspides 1..12 sont calculees via `swe.houses_ex`.
- Les systemes supportes sont centralises (`placidus`, `equal`, `whole_sign`, `porphyry`).
- ASC/MC sont calcules dans `HouseData`, mais le resultat natal persiste surtout les cuspides.

Pour l'affectation:

- Chaque planete est assignee a une maison par intervalle de cuspides.
- Le signe attendu est recalcule depuis la longitude.
- Toute incoherence signe/longitude ou maison/intervalle leve `inconsistent_natal_result`.

Constat: les invariants geometriques internes sont bons. La chaine ne se contente pas de faire confiance aux providers: elle reverifie signe et maison apres calcul.

Points d'attention:

- L'ASC n'est pas expose comme objet angle separe dans `NatalResult`; le front le deduit de la cuspide maison 1 via `astro_profile`.
- Le front ne consomme pas encore toutes les donnees runtime enrichies des maisons.

Ancrages:

- `backend/app/domain/astrology/ephemeris_provider.py:86`
- `backend/app/domain/astrology/houses_provider.py:109`
- `backend/app/domain/astrology/calculators/houses.py:21`

## Referentiel runtime et enrichissements

Le calcul depend du `AstrologyRuntimeReference` charge depuis la DB. Les validations connues couvrent:

- 12 signes.
- 12 maisons.
- planetes requises.
- points d'angle ASC/DSC/MC/IC.
- systemes de maisons requis actifs.
- definitions d'aspects.
- regles d'orbes.
- dignites et maitrises de signes.
- axes de maisons.
- interdiction des references orphelines et codes inconnus.

`build_natal_result` enrichit ensuite:

- `houses` via `build_house_runtime_data`.
- `signs_runtime` via `build_sign_runtime_data`.
- `aspects` via `build_aspect_runtime_data`.
- `chart_balance` via `ChartSignatureCalculator`.
- `house_rulers` via `HouseRulerResolver`.

Constat: la source de verite a converge vers le runtime DB; les artefacts CS-171/172/175 indiquent une consolidation recente de cette couche.

Risque residuel: la compatibilite legacy pour les mocks existe encore dans `_legacy_payload_for_mock_db`. Elle est bornee aux doubles de tests, mais elle doit rester surveillee pour ne pas redevenir un chemin runtime.

Ancrages:

- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py:74`
- `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/runtime-reference-integrity.json`
- `_condamad/stories/CS-175-creer-runtime-canonique-signes/baseline-natal-runtime-after.md`

## Aspects et orbes

Les aspects sont calcules entre paires de positions avec:

- definitions runtime typees (`AspectDefinitionRuntimeData`);
- regles d'orbes typees (`AspectOrbRuleRuntimeData`);
- filtrage `is_enabled`, `is_major`, `system_code`;
- resolution d'orbe par systeme, contexte et specificite corps/source/cible;
- tri deterministe du resultat.

Le calcul rejette les champs legacy d'orbes si presents dans la reference. Des metriques suivent les aspects calcules et rejetes par orbe.

Constat: la logique d'orbes est explicite et extensible sans duplication locale. Le tri rend le payload stable pour tests et audit.

Point d'attention: le front affiche seulement le code aspect, angle et orbe; les valences, families et `aspect_runtime` restent surtout utiles cote backend/LLM.

Ancrage: `backend/app/domain/astrology/calculators/aspects.py`.

## API, erreurs et securite

Les surfaces principales sont:

- `POST /v1/users/me/natal-chart`: flux utilisateur authentifie.
- `GET /v1/users/me/natal-chart/latest`: lecture du dernier theme.
- `GET /v1/users/{user_id}/natal-chart/consistency`: support/ops/admin seulement.
- `POST /v1/astrology-engine/natal/prepare`: preparation technique.
- `POST /v1/astrology-engine/natal/calculate`: calcul technique avec persistance.
- `POST /v1/astrology-engine/natal/compare`: comparaison interne support/ops/admin, indisponible en production.
- `POST /v1/natal/interpretation`: interpretation LLM du dernier theme.

Les erreurs sont mappees en enveloppes standard avec `request_id`. Le flux utilisateur distingue correctement 401, 403, 404, 422 et 503.

Constat: les routes sensibles de comparaison et audit sont role-gated. Le payload `prepared_input` persiste des donnees temporelles mais ne reinjecte pas `birth_place`, `birth_city`, `birth_country` dans le resultat natal.

Risque residuel: `POST /v1/astrology-engine/natal/calculate` persiste des traces sans `user_id`; c'est utile pour audit/outillage, mais doit rester controle par les politiques d'acces globales de l'API.

## Frontend React

Le front:

- Genere toujours avec `accurate=true` dans les CTA natals.
- Lit le dernier theme via React Query avec clef par sujet token.
- Gere loading, erreurs 404 de theme absent, profil incomplet et erreurs generiques.
- Affiche les planetes, maisons, aspects, date de generation, version de reference et systeme de maisons.
- Declenche l'interpretation natale depuis le theme charge.

Constat: le front ne recalcul rien d'astrologique critique; il formate et traduit. La seule logique geometrique front notable sert a deduire le signe d'une cuspide pour l'affichage maison.

Point d'attention: les types front `HouseResult` et `AspectResult` sont plus pauvres que le payload backend enrichi. Cela limite l'exploitation UI des donnees runtime, mais ne casse pas la chaine de calcul.

Ancrages:

- `frontend/src/api/natal-chart/index.ts:113`
- `frontend/src/pages/NatalChartPage.tsx:55`

## Couverture de tests observee

Couvertures significatives reperees:

- Generation API utilisateur et lecture latest: `backend/app/tests/integration/test_user_natal_chart_api.py:157`.
- Coherence astro profile vs geometrie: `backend/app/tests/integration/test_user_natal_chart_api.py:1000`.
- Determinisme et invariants signe/maison: `backend/app/tests/unit/test_natal_calculation_service.py:149`.
- Topocentric et geocentric: `backend/app/tests/unit/test_natal_calculation_service.py:524` et `:551`.
- TT / DeltaT: `backend/app/tests/unit/test_natal_tt.py:139`.
- Integrite runtime DB: `backend/app/tests/unit/test_astrology_runtime_reference_repository.py:74`.
- Runtime maisons golden: `backend/tests/unit/domain/astrology/test_house_runtime_builder.py:81`.
- Tests providers et golden SwissEph presents: `test_ephemeris_provider.py`, `test_houses_provider.py`, `test_natal_golden_swisseph.py`, `test_natal_pipeline_swisseph.py`.

Constat: les tests couvrent bien les invariants internes et les erreurs metier. La couverture la plus importante a maintenir est celle des providers SwissEph et des golden tests, car ce sont eux qui protegent la precision astronomique effective.

## Constats classes par severite

### Critique

Aucun blocage critique identifie dans la chaine lue.

### Eleve

1. Dependence forte a la disponibilite SwissEph et aux fichiers d'ephemerides.
   - Impact: generation accurate impossible ou degradee si bootstrap absent.
   - Mitigation existante: bootstrap verifie, erreurs 503, metadonnees `ephemeris_path_version/hash`.
   - Recommandation: ajouter un smoke de demarrage qui calcule un theme de reference et verifie quelques longitudes attendues.

2. Validation externe de precision a renforcer.
   - Impact: les invariants internes peuvent passer meme si le provider/config diverge d'un outil de reference.
   - Mitigation existante: golden/cross-tool artefacts et tests nommes.
   - Recommandation: versionner 3 a 5 cas de naissance compares a SwissEph CLI ou astro.com-equivalent, avec tolerances explicites.

### Moyen

3. Exposition partielle des angles.
   - Impact: l'ASC est disponible implicitement par cuspide maison 1; MC est calcule par provider mais non expose comme angle public central.
   - Recommandation: envisager un bloc `angles` dans `NatalResult` pour ASC/DSC/MC/IC si les interpretations ou UI en ont besoin.

4. Front sous-consommateur du runtime enrichi.
   - Impact: l'UI reste correcte mais ne montre pas la richesse canonique recente.
   - Recommandation: aligner progressivement les types TS avec `signs_runtime`, `chart_balance`, champs runtime maisons/aspects.

5. Chemin legacy test mock encore present.
   - Impact: risque de confusion si un mock DB fuit dans un test d'integration non voulu.
   - Recommandation: conserver un test de garde qui prouve que le chemin legacy ne s'active pas avec une vraie session SQLAlchemy.

### Faible

6. Documentation technique dispersee.
   - Impact: les garanties existent mais sont reparties entre stories, tests et docs.
   - Recommandation: maintenir ce document comme index vivant de la chaine natale.

## Recommandations prioritaires

1. Ajouter un smoke SwissEph reproductible au demarrage ou en predeploy: date/heure/lieu fixes, verification Soleil/Lune/ASC/MC avec tolerance.
2. Exposer explicitement les angles dans le contrat backend si l'interpretation complete doit s'appuyer sur ASC/MC/IC/DSC autrement que par les maisons.
3. Etendre les types front pour ne pas perdre les champs runtime maintenant disponibles.
4. Centraliser dans `docs/recherches astro` une matrice des cas golden: Paris moderne, naissance DST ambigue, hemisphere sud, sidereal Lahiri, topocentric.
5. Continuer a bloquer toute reintroduction de dictionnaires astrologiques locaux hors resolver DB-backed.

## Conclusion

La chaine de calcul du theme natal est maintenable et plutot bien verrouillee: les responsabilites sont separees, les erreurs sont explicites, le referentiel runtime est valide, les invariants geometriques sont controles et la persistance garde une trace audit exploitable.

Le prochain gain qualite n'est pas une refonte: c'est une consolidation de preuve. Il faut renforcer la validation externe SwissEph/golden, exposer les angles si necessaire, et aligner le front avec les enrichissements runtime deja produits par le backend.
