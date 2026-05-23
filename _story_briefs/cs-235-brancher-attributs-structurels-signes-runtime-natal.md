# CS-235 — Brancher Attributs Structurels Signes Runtime Natal

## Résumé

CS-235 branche dans le runtime natal les attributs structurels de signes ajoutés par CS-234.

La cible est :

```text
astral_sign_profiles
→ AstrologyRuntimeReferenceRepository._load_sign_profiles()
→ SignReferenceData
→ SignRuntimeData
→ chart_objects / interpretation input
```

Cette story ne doit pas créer la donnée DB. Elle consomme les champs persistés par CS-234 et les rend disponibles aux couches de calcul et d’adaptation.

---

## Contexte

CS-185 a déjà branché :

```text
element
modality
polarity
```

dans :

```text
SignReferenceData
SignRuntimeData
ChartSignatureCalculator
json_builder
```

CS-234 ajoute les attributs structurels manquants. CS-235 doit prolonger le même chemin sans recréer un second mécanisme.

---

## Problème à résoudre

Les futures interprétations structurées ont besoin de traits de signe stables, mais ne doivent pas lire directement la DB ni reconstruire des mappings.

Sans contrat runtime explicite, les consommateurs risquent de faire :

```python
if sign_code in {"cancer", "scorpio", "pisces"}:
    fertility = "fruitful"
```

Ce type de mapping est interdit dans le domaine.

---

## Objectifs

### Objectif fonctionnel

Exposer les attributs de signe enrichis dans les contrats runtime natals.

Attributs attendus :

```text
seasonal_quadrant
fertility
voice
form
```

Adapter les noms si CS-234 retient une nomenclature différente.

### Objectif architectural

Unifier la source des profils :

```text
SignReferenceData doit être la seule source runtime des attributs structurels de signe.
SignRuntimeData doit copier ces attributs sans recalcul.
```

---

## Périmètre inclus

CS-235 couvre :

1. La mise à jour de `_load_sign_profiles()`.
2. La mise à jour de `AstrologyRuntimeReferenceMapper`.
3. La mise à jour de `SignReferenceData`.
4. La mise à jour de `SignRuntimeData`.
5. La mise à jour de `build_sign_runtime_data`.
6. La mise à jour des factories de tests runtime.
7. La projection publique contrôlée si le JSON expose déjà `signs_runtime`.
8. Les tests unitaires et d’intégration associés.
9. Les guardrails anti-mapping local.

---

## Hors périmètre

CS-235 ne doit pas :

- ajouter la migration DB de CS-234 ;
- modifier les scores de balance ;
- écrire des phrases d’interprétation ;
- modifier les prompts LLM ;
- changer la doctrine des dignités ;
- ajouter une nouvelle surface parallèle à `SignReferenceData`.

---

## Contrats attendus

### `SignReferenceData`

Étendre le contrat :

```python
@dataclass(frozen=True, slots=True)
class SignReferenceData:
    code: str
    name: str
    element: str
    modality: str
    polarity: str
    seasonal_quadrant: str
    fertility: str
    voice: str
    form: str
```

La validation doit refuser :

```text
valeur vide
unknown
None pour un attribut obligatoire
```

### `SignRuntimeData`

Étendre le contrat :

```python
@dataclass(frozen=True, slots=True)
class SignRuntimeData:
    sign: str
    ...
    element: str
    modality: str
    polarity: str
    seasonal_quadrant: str
    fertility: str
    voice: str
    form: str
```

Ces valeurs doivent venir de `SignReferenceData`, jamais du `sign_code`.

---

## Projection publique

Si `chart["signs_runtime"]` expose déjà les profils structurels, ajouter les nouveaux champs dans le même bloc :

```json
{
  "sign": "aries",
  "element": "fire",
  "modality": "cardinal",
  "polarity": "yang",
  "seasonal_quadrant": "spring",
  "fertility": "...",
  "voice": "...",
  "form": "..."
}
```

Ne pas ajouter de libellés localisés dans cette story.

---

## Tests attendus

Mettre à jour ou créer :

```text
backend/app/tests/unit/test_astrology_runtime_reference_repository.py
backend/tests/unit/domain/astrology/test_sign_runtime_builder.py
backend/app/tests/unit/test_chart_json_builder.py
backend/app/tests/unit/test_astrology_runtime_reference_guard.py
backend/tests/factories/astrology_runtime_reference_factory.py
```

Les tests doivent prouver :

1. Le repository charge les nouveaux attributs depuis la DB.
2. Le mapper échoue si un attribut obligatoire manque.
3. `SignRuntimeData` reçoit les attributs depuis `SignReferenceData`.
4. La projection publique ne recalcule rien.
5. Les fixtures ne réintroduisent pas de seed mapping importé.

Ajouter un guardrail qui interdit dans `backend/app/domain/astrology` et `backend/app/services/natal` :

```text
SEASONAL_QUADRANT_BY_SIGN
FERTILITY_BY_SIGN
VOICE_BY_SIGN
FORM_BY_SIGN
HUMANE_BY_SIGN
BESTIAL_BY_SIGN
```

---

## Validation attendue

Commandes :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py tests/unit/domain/astrology/test_sign_runtime_builder.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_runtime_reference_guard.py
```

Scan ciblé :

```powershell
rg -n "SEASONAL_QUADRANT_BY_SIGN|FERTILITY_BY_SIGN|VOICE_BY_SIGN|FORM_BY_SIGN|HUMANE_BY_SIGN|BESTIAL_BY_SIGN" backend/app/domain/astrology backend/app/services/natal -g "*.py"
```

Le scan doit être vide hors tests de guardrail.
