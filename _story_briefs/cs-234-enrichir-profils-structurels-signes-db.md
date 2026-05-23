# CS-234 — Enrichir Profils Structurels Signes DB

## Résumé

CS-234 étend le modèle canonique des profils de signes pour couvrir les attributs structurels encore absents :

```text
seasonal quadrant
fertility
voice
humane / bestial
sect / gender-compatible traits si déjà présents dans les sources
```

Après CS-185, `astral_sign_profiles` alimente déjà `element`, `modality` et `polarity`. La table reste toutefois trop pauvre pour porter les classifications traditionnelles utiles aux balances, signatures et interprétations structurées.

Cette story est une story DB + seed + intégrité. Elle ne branche pas encore ces nouveaux attributs dans le runtime natal.

---

## Contexte

Le flux actuel charge :

```text
astral_sign_profiles
→ astral_elements / astral_modalities / astral_polarities
→ SignReferenceData
→ SignRuntimeData
→ chart balance / JSON public
```

Mais le modèle `AstralSignProfileModel` ne contient aujourd’hui que :

```text
astral_element_id
astral_modality_id
astral_polarity_id
keywords_json
shadow_keywords_json
```

Les dimensions suivantes ne sont pas persistées sous forme structurée :

```text
seasonal quadrant
fertility
voice
humane / bestial
```

Elles ne doivent pas être recréées dans le domaine via mappings locaux.

---

## Problème à résoudre

Sans colonnes ou référentiels dédiés, les futures couches runtime devront soit :

- coder des mappings locaux par signe ;
- mélanger mots-clés narratifs et classifications structurelles ;
- inférer des attributs depuis `keywords_json` ;
- dupliquer des règles dans les calculateurs et les prompts.

CS-234 doit rendre ces attributs persistés, validables et versionnables.

---

## Objectifs

### Objectif fonctionnel

Ajouter au modèle DB les classifications structurelles de signe manquantes et les seeder pour les douze signes.

### Objectif architectural

Conserver la règle :

```text
Tout attribut structurel d'un signe consommé par le runtime doit provenir de la DB canonique,
pas de constantes locales dans `domain/astrology` ou `services/natal`.
```

---

## Périmètre inclus

CS-234 couvre :

1. L’analyse du modèle existant `astral_sign_profiles`.
2. La création des référentiels nécessaires si les valeurs méritent une taxonomie dédiée.
3. L’ajout des colonnes ou FK sur `astral_sign_profiles`.
4. La migration Alembic correspondante.
5. La mise à jour des seeds sous `docs/db_seeder/astrology`.
6. Le seed complet des douze signes.
7. Les tests d’intégration de migration et de seed.
8. La documentation minimale des nouvelles classifications.

---

## Hors périmètre

CS-234 ne doit pas :

- modifier `SignReferenceData` ;
- modifier `SignRuntimeData` ;
- modifier le JSON public ;
- modifier les balances ou signatures ;
- ajouter de texte interprétatif ;
- appeler un LLM ;
- ajouter des mappings locaux dans le domaine.

---

## Contrat DB attendu

Choisir l’option la plus cohérente avec les conventions existantes :

### Option recommandée — taxonomies dédiées

```text
astral_sign_seasonal_quadrants
astral_sign_fertility_classes
astral_sign_voice_classes
astral_sign_form_classes
```

Puis ajouter les FK :

```text
astral_sign_profiles.seasonal_quadrant_id
astral_sign_profiles.fertility_class_id
astral_sign_profiles.voice_class_id
astral_sign_profiles.form_class_id
```

Exemples de codes attendus :

```text
seasonal_quadrant: spring, summer, autumn, winter
fertility: fruitful, semi_fruitful, barren
voice: vocal, semi_vocal, mute
form: humane, bestial, double_bodied, hybrid
```

Les noms exacts doivent être validés contre les sources déjà présentes dans `docs/recherches astro` et rester cohérents avec les codes anglais utilisés par les autres référentiels.

### Option acceptable — colonnes code

Si aucune taxonomie dédiée n’est justifiée, ajouter des colonnes code non nulles :

```text
seasonal_quadrant_code
fertility_code
voice_code
form_code
```

Cette option doit être justifiée dans la story si retenue.

---

## Tests attendus

Ajouter ou mettre à jour :

```text
backend/app/tests/integration/test_reference_data_migrations.py
backend/app/tests/unit/test_prediction_reference_repository.py si le seed passe par le repository existant
```

Les tests doivent prouver :

1. Les nouvelles colonnes/tables existent à la tête Alembic.
2. Les douze signes ont une valeur non nulle pour chaque attribut.
3. Les codes attendus existent dans les taxonomies.
4. Les seeds ne réintroduisent pas d’anciennes tables `signs` / `sign_rulerships`.
5. `keywords_json` et `shadow_keywords_json` restent des champs éditoriaux, pas des sources structurelles.

---

## Validation attendue

Commandes :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/integration/test_reference_data_migrations.py app/tests/unit/test_prediction_reference_repository.py
```

Ajouter un scan ciblé :

```powershell
rg -n "seasonal_quadrant|fertility|voice|humane|bestial|fruitful|barren|mute" backend/app/domain/astrology backend/app/services/natal -g "*.py"
```

À ce stade, le scan ne doit pas trouver de nouveau mapping métier dans le domaine.
