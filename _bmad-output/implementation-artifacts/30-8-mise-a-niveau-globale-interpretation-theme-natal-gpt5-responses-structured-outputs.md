# Story 30.8: Mise à niveau globale de l'interprétation thème natal (GPT-5 / Responses API / Structured Outputs)

**Status**: done

## Story

As a product and tech team,
I want to industrialiser le flux `natal_interpretation` avec un contrat strict Structured Outputs v3 (sans disclaimers LLM, densité premium), des disclaimers statiques côté application, et un filtrage `evidence ⊆ allowed_evidence` garanti,
so that la qualité premium augmente, les coûts tokens baissent et les erreurs de validation disparaissent en production.

## Acceptance Criteria

1. Aucune réponse LLM `natal_interpretation` ne contient de champ `disclaimers` généré — le disclaimer est injecté statiquement par l'API backend selon le `locale`.
2. Tous les appels `natal_interpretation` (niveau `complete`) utilisent un payload Responses API conforme au JSON Schema strict `AstroResponse_v3` (nouveau schéma).
3. Les réponses LLM acceptées passent la validation JSON Schema v3 en `strict: true` sans correction manuelle.
4. Le mode erreur retourne une structure valide strictement compatible avec le schéma v3 (via `AstroErrorResponseV3`).
5. En mode `complete`, les seuils minimaux de densité sont respectés :
   - `summary` length >= 900 caractères
   - `sections` >= 5 éléments
   - chaque `sections[].content` >= 280 caractères
   - `highlights` >= 5 éléments
   - `advice` >= 5 éléments
6. Le champ `evidence` final retourné ne contient aucun identifiant hors `allowed_evidence` (filtrage sécurisé appliqué même après validation bidirectionnelle).
7. Le paramètre `reasoning.effort` est toujours défini pour les modèles GPT-5 ; aucun `reasoning.summary` n'est demandé en production.
8. Les métriques d'observabilité suivantes sont disponibles : `natal_validation_pass_total`, `natal_validation_fail_total`, `natal_repair_total`, `natal_repair_fail_total`, `natal_summary_len` (histogram), `natal_section_len` (histogram), `natal_invalid_evidence_total`.

## Tasks / Subtasks

- [x] T1: Définir le schéma v3 sans disclaimers et avec minima densité (AC: 2, 3, 4, 5)
  - [x] T1.1: Créer `AstroSectionV3` dans `schemas.py` (content `min_length=280`, max 6500)
  - [x] T1.2: Créer `AstroResponseV3` sans champ `disclaimers`, avec `summary min_length=900`, `sections/highlights/advice min_length=5`
  - [x] T1.3: Créer `AstroErrorResponseV3` pour le mode erreur strictement valide (union discriminée ou structure dédiée)
  - [x] T1.4: Ajouter `ASTRO_RESPONSE_V3_JSON_SCHEMA` dict complet dans `use_cases_seed.py` (avec `additionalProperties: false`, `minLength`, `minItems` corrects)
- [x] T2: Mettre à jour les prompts pour le contrat v3 et la densité premium (AC: 1, 5)
  - [x] T2.1: Supprimer toute instruction de génération de disclaimer dans le prompt `natal_interpretation` (DB via prompt registry)
  - [x] T2.2: Ajouter instructions densité explicites dans le prompt (≥5 sections, summary ≥900 chars, contenu ≥280 chars par section, ≥5 highlights, ≥5 advice)
  - [x] T2.3: Créer une nouvelle version de prompt `natal_interpretation` (seed script ou migration) avec version bumped
- [x] T3: Aligner l'intégration Responses API — reasoning.effort sans summary (AC: 7)
  - [x] T3.1: Vérifier/compléter dans `gateway.py` que `reasoning.effort` est défini pour les modèles GPT-5 / o-series
  - [x] T3.2: S'assurer que `reasoning.summary` est absent (ou `"disabled"`) des paramètres de production
- [x] T4: Renforcer le validateur output — filtrage evidence sécurisé (AC: 6)
  - [x] T4.1: Ajouter dans `output_validator.py` un filtrage final `evidence ⊆ allowed_evidence` (après validation bidirectionnelle) avec log warning
  - [x] T4.2: Écrire tests unitaires pour le filtrage (evidence avec ID hors catalog → filtré, pas rejeté)
- [x] T5: Déporter les disclaimers en couche application (AC: 1)
  - [x] T5.1: Créer `backend/app/services/disclaimer_registry.py` — dict statique `locale → List[str]` avec fallback `_default`
  - [x] T5.2: Ajouter `disclaimers: list[str]` dans `NatalInterpretationResponse` (schéma API, **pas** dans le payload LLM stocké en DB)
  - [x] T5.3: Mettre à jour l'endpoint `natal_interpretation.py` pour appeler `get_disclaimers(locale)` et l'injecter dans la réponse
- [x] T6: Adapter la logique de repair pour le schéma v3 (AC: 3)
  - [x] T6.1: Adapter `build_repair_prompt()` dans `repair_prompter.py` pour cibler les violations v3 (densité insuffisante, champs manquants)
  - [x] T6.2: Confirmer que le repair est single-pass (max 1 retry, pas de boucle)
- [x] T7: Mettre à jour les seeds et le feature flag de routage (AC: 2)
  - [x] T7.1: Enregistrer `AstroResponse_v3` en DB via `use_cases_seed.py` (upsert `LlmOutputSchemaModel`)
  - [x] T7.2: Mettre à jour le use case `natal_interpretation` pour pointer vers `AstroResponse_v3`
  - [x] T7.3: Ajouter `natal_schema_version` dans `backend/app/core/config.py` (settings, env override possible via `NATAL_SCHEMA_VERSION`)
  - [x] T7.4: Mettre à jour `NatalInterpretationServiceV2` pour brancher `AstroResponseV3` quand `settings.natal_schema_version == "v3"`
- [x] T8: Déployer les métriques d'observabilité (AC: 8)
  - [x] T8.1: Ajouter compteurs `natal_validation_pass_total` / `natal_validation_fail_total` dans `output_validator.py`
  - [x] T8.2: Ajouter compteurs `natal_repair_total` / `natal_repair_fail_total` dans `gateway.py`
  - [x] T8.3: Ajouter histograms `natal_summary_len` et `natal_section_len` dans le service v2
  - [x] T8.4: Ajouter compteur `natal_invalid_evidence_total` lors du filtrage sécurisé (T4.1)
  - [x] T8.5: Écrire tests unitaires vérifiant que les métriques sont bien incrémentées
- [x] T9: Hardening post-go-live (stabilité runtime + data integrity)
  - [x] T9.1: Corriger le crash `MultipleResultsFound` dans `NatalInterpretationServiceV2` en cas de doublons historiques
  - [x] T9.2: Ajouter migration de nettoyage + index uniques partiels sur `user_natal_interpretations`
  - [x] T9.3: Ajouter script d'audit pré-migration pour lister les doublons potentiels (staging/prod)
- [x] T10: Industrialisation UX et conformité légale d'affichage
  - [x] T10.1: Déplacer les disclaimers en footer dédié (hors panneau audit)
  - [x] T10.2: Enrichir les disclaimers statiques multi-locale (non médical/juridique/financier, non prédictif, libre arbitre)
  - [x] T10.3: Transformer "Données principales analysées" en panneau audit pliable, dédupliqué et groupé par catégories
  - [x] T10.4: Renommer Maison VI en "Routines / hygiène de vie" côté UI pour réduire le risque de perception médicale
- [x] T11: Non-régression prompt v3 et contrats de seed
  - [x] T11.1: Renforcer les règles rédactionnelles du prompt (anti-redondance, exemples observables bénéfice/risque, leviers actionnables avec durée/fréquence)
  - [x] T11.2: Ajouter assertions de contrat prompt + lint dans les tests unitaires dédiés

## Dev Notes

### Architecture du pipeline natal_interpretation (état post-epic 30)

```
API endpoint (natal_interpretation.py)
  → NatalInterpretationServiceV2.interpret()
      → build_chart_json() + build_enriched_evidence_catalog()
      → LLMGateway.execute()
          → 4-layer message: HardPolicy + DeveloperPrompt + Persona + UserData
          → ResponsesClient → Responses API (strict JSON Schema en DB)
          → validate_output() avec evidence catalog (bidirectionnel)
          → repair single-pass si echec → fallback natal_interpretation_short si repair échoue
      → AstroResponseV1/V2 sélection selon level + was_fallback
      → Persistence UserNatalInterpretationModel (interpretation_payload JSON)
      → Return NatalInterpretationResponse (sans disclaimers dans payload)
```

### Fichiers clés à modifier / créer

| Fichier | Action |
|---|---|
| `backend/app/llm_orchestration/schemas.py` | Ajouter `AstroSectionV3`, `AstroResponseV3`, `AstroErrorResponseV3` |
| `backend/app/llm_orchestration/seeds/use_cases_seed.py` | Ajouter `ASTRO_RESPONSE_V3_JSON_SCHEMA`, mettre à jour `natal_interpretation` |
| `backend/app/llm_orchestration/services/output_validator.py` | Filtrage sécurisé evidence, repair v3, métriques |
| `backend/app/llm_orchestration/gateway.py` | Vérifier reasoning.effort, métriques repair |
| `backend/app/services/natal_interpretation_service_v2.py` | Brancher AstroResponseV3, feature flag, métriques longueur |
| `backend/app/services/disclaimer_registry.py` | **Nouveau** — disclaimers statiques localisés |
| `backend/app/api/v1/routers/natal_interpretation.py` | Injecter disclaimers dans réponse |
| `backend/app/api/v1/schemas/natal_interpretation.py` | Ajouter champ `disclaimers: list[str]` dans `NatalInterpretationResponse` |
| `backend/app/core/config.py` | Ajouter `NATAL_SCHEMA_VERSION: str = "v3"` |
| `backend/migrations/versions/20260304_0028_dedupe_and_unique_user_natal_interpretations.py` | **Nouveau** — déduplication + index uniques partiels |
| `backend/scripts/diagnose_natal_interpretation_duplicates.py` | **Nouveau** — audit des doublons avant migration |
| `backend/app/infra/db/models/user_natal_interpretation.py` | Aligner `__table_args__` avec index uniques partiels |
| `frontend/src/components/NatalInterpretation.tsx` | Footer legal dédié + panneau audit pliable/dédupliqué |
| `frontend/src/i18n/natalChart.ts` | Libellés i18n audit/disclaimer (intro, catégories, labels toggle) |
| `frontend/src/i18n/astrology.ts` | Renommer Maison VI (FR/EN/ES) en formulation non médicale |

### Addendum post-go-live (2026-03-04)

- Incident observé: erreurs 500 `internal_error` côté frontend après reconnexion/retry.
- Cause racine: lecture cache via `scalar_one_or_none()` sur `user_natal_interpretations` alors que des doublons historiques existaient.
- Correctif applicatif immédiat:
  - `NatalInterpretationServiceV2` capture `MultipleResultsFound` et récupère la ligne la plus récente (`ORDER BY created_at DESC, id DESC`).
- Correctif structurel:
  - migration de nettoyage (keep latest row par clé logique) + contraintes uniques partielles pour empêcher la recréation.
- Outil d'exploitation:
  - script de diagnostic pré-migration pour inventorier les doublons en staging/prod.
- Renforcement qualité:
  - tests unitaires ajoutés pour le cas `MultipleResultsFound`.
  - tests de contrat prompt v3 renforcés (lint + assertions règles rédactionnelles).

### Schéma v3 — Design exact à implémenter

**`AstroSectionV3`** (dans `schemas.py`, après `AstroSectionV2`) :
```python
class AstroSectionV3(BaseModel):
    """Section premium v3 — contenu obligatoirement substantiel."""
    key: _SECTION_KEYS
    heading: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=280, max_length=6500)  # min_length=280 NEW
```

**`AstroResponseV3`** (sans disclaimers, densité premium) :
```python
class AstroResponseV3(BaseModel):
    """Réponse structurée v3 — sans disclaimers LLM, densité premium obligatoire."""
    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=900, max_length=2800)    # min_length=900 NEW
    sections: List[AstroSectionV3] = Field(..., min_length=5, max_length=10)  # min_length=5 NEW
    highlights: List[_HighlightItem] = Field(..., min_length=5, max_length=12)  # min_length=5 NEW
    advice: List[_AdviceItem] = Field(..., min_length=5, max_length=12)         # min_length=5 NEW
    evidence: List[_EvidenceItem] = Field(..., max_length=80)
    # NB: PAS de champ disclaimers
```

**`AstroSectionErrorV3`** (sections mode erreur — pas de contrainte densité) :
```python
class AstroSectionErrorV3(BaseModel):
    """Section mode erreur v3 — pas de contrainte de densité premium."""
    key: _SECTION_KEYS
    heading: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=6500)  # min_length=1 (pas 280)
```

**`AstroErrorResponseV3`** (mode erreur strictement valide) :
```python
class AstroErrorResponseV3(BaseModel):
    """Structure dédiée pour le mode erreur v3 — compatible schéma strict."""
    error_code: Literal["insufficient_data", "calculation_failed"]
    message: str = Field(..., min_length=1, max_length=500)
    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=1, max_length=500)  # Longueur réduite, mode erreur
    sections: List[AstroSectionErrorV3] = Field(default_factory=list, max_length=2)  # ← AstroSectionErrorV3, pas V3
    highlights: List[_HighlightItem] = Field(default_factory=list, max_length=3)
    advice: List[_AdviceItem] = Field(default_factory=list, max_length=3)
    evidence: List[_EvidenceItem] = Field(default_factory=list, max_length=5)
```

**Attention** : `AstroErrorResponseV3` ne respecte pas les `minItems=5` de `AstroResponseV3` — ce sont deux modèles distincts. Si le LLM doit choisir entre les deux, utiliser un JSON Schema avec `oneOf` discriminé par `error_code`.

**Important** : `AstroErrorResponseV3.sections` utilise `AstroSectionErrorV3` (min_length=1 sur le contenu) et non `AstroSectionV3` (min_length=280). Le mode erreur n'a pas de contrainte de densité premium — imposer 280 chars sur un message d'erreur serait incohérent.

### JSON Schema v3 pour le seed

Le `ASTRO_RESPONSE_V3_JSON_SCHEMA` est le JSON Schema strict à stocker en DB. Il **doit** avoir `additionalProperties: false` et tous les `minLength`/`minItems` pour que `strict: true` soit respecté par le LLM.

Exemple de structure (à compléter) :
```python
ASTRO_RESPONSE_V3_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "summary": {"type": "string", "minLength": 900, "maxLength": 2800},
        "sections": {
            "type": "array",
            "minItems": 5,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {"type": "string", "enum": [...]},  # _SECTION_KEYS
                    "heading": {"type": "string", "minLength": 1, "maxLength": 100},
                    "content": {"type": "string", "minLength": 280, "maxLength": 6500},
                },
            },
        },
        "highlights": {"type": "array", "minItems": 5, "maxItems": 12, "items": {"type": "string", "maxLength": 360}},
        "advice": {"type": "array", "minItems": 5, "maxItems": 12, "items": {"type": "string", "maxLength": 360}},
        "evidence": {"type": "array", "maxItems": 80, "items": {"type": "string", "pattern": EVIDENCE_ID_REGEX}},
    },
}
```

**Important** : importer `EVIDENCE_ID_REGEX` depuis `app.llm_orchestration.models` et les valeurs de `_SECTION_KEYS` depuis `schemas.py`. Ne pas dupliquer.

### Feature Flag `NATAL_SCHEMA_VERSION`

Dans `backend/app/core/config.py` (Settings Pydantic) :
```python
NATAL_SCHEMA_VERSION: str = "v3"  # "v2" pour rollback
```

Dans `NatalInterpretationServiceV2.interpret()` :
```python
use_v3 = settings.NATAL_SCHEMA_VERSION == "v3" and level == "complete"
response_model = AstroResponseV3 if use_v3 else AstroResponseV2
# use_case_key reste "natal_interpretation", seul le schema DB change
```

### Disclaimers applicatifs — Décision d'architecture définitive

> **⚠️ NE PAS REVENIR EN ARRIÈRE — Décision intentionnelle, story 30-8 (2026-03-03)**
>
> Les disclaimers légaux ont été **délibérément retirés du prompt LLM** et déplacés dans une couche applicative statique (`disclaimer_registry.py`). Ce choix est permanent et motivé :
>
> - **Économie de tokens** : chaque appel `natal_interpretation` (complete) évite de générer ~50–100 tokens de disclaimer non-différentiés.
> - **Stabilité légale** : le texte disclaimer ne peut plus "dériver" d'une version de prompt à l'autre ou être paraphrasé par le modèle.
> - **i18n propre** : la localisation est gérée par `get_disclaimers(locale)` côté app, pas par le LLM (qui n'est pas une source de vérité i18n fiable).
> - **Schéma v3 strict** : `AstroResponseV3` n'a pas de champ `disclaimers` — tout ajout serait rejeté par `extra="forbid"`.
>
> **Si vous vous sentez tenté d'ajouter un disclaimer dans le prompt ou dans le schéma LLM** : c'est le signe que la bonne action est de modifier `_DISCLAIMERS` dans `disclaimer_registry.py` ou d'ajouter un locale dans ce fichier. Pas de toucher au prompt.

### Disclaimers applicatifs — Pattern à créer

**Nouveau fichier** `backend/app/services/disclaimer_registry.py` :
```python
_DISCLAIMERS: dict[str, list[str]] = {
    "fr-FR": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
    "fr-BE": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
    "en-US": [
        "Astrology is a tool for personal reflection, not a certified predictive science."
    ],
    "en-GB": [
        "Astrology is a tool for personal reflection, not a certified predictive science."
    ],
    "_default": [
        "L'astrologie est un outil de réflexion personnelle, pas une science prédictive certifiée."
    ],
}

def get_disclaimers(locale: str) -> list[str]:
    # 1. Locale exact
    result = _DISCLAIMERS.get(locale)
    if result:
        return result
    # 2. Fallback langue de base (ex: fr-CA → premier locale "fr-*" connu)
    if "-" in locale:
        lang = locale.split("-")[0]
        for key, value in _DISCLAIMERS.items():
            if key.startswith(f"{lang}-"):
                return value
    # 3. Fallback final
    return _DISCLAIMERS.get("_default") or []
```

**Dans `NatalInterpretationResponse`** (schéma API, `api/v1/schemas/natal_interpretation.py`) :
```python
class NatalInterpretationResponse(BaseModel):
    # ... champs existants ...
    disclaimers: list[str] = Field(default_factory=list)  # Injectés par l'API, pas le LLM
```

**Dans l'endpoint** (`api/v1/routers/natal_interpretation.py`) :
```python
from app.services.disclaimer_registry import get_disclaimers
# ...
response = NatalInterpretationResponse(
    ...,
    disclaimers=get_disclaimers(locale),
)
```

**Le payload LLM (`interpretation_payload` en DB) ne doit JAMAIS contenir de disclaimers.**

### Filtrage sécurisé evidence (T4)

Dans `output_validator.py`, **après** la validation bidirectionnelle existante, ajouter :
```python
# Secure filter — garantit evidence ⊆ allowed_evidence
if evidence_catalog and strict:
    allowed_ids = set(evidence_catalog.keys())
    original_count = len(parsed.evidence)
    parsed.evidence = [e for e in parsed.evidence if e in allowed_ids]
    filtered_count = original_count - len(parsed.evidence)
    if filtered_count > 0:
        logger.warning(f"Filtered {filtered_count} evidence IDs not in allowed_evidence")
        metrics.natal_invalid_evidence_total.inc(filtered_count)
```

Ce filtrage est **non-bloquant** (ne rejette pas la réponse, filtre silencieusement). C'est la garantie finale de conformité.

### Reasoning.effort — Pattern gateway

Vérifier dans `gateway.py` que la config reasoning suit ce pattern pour GPT-5 :
```python
if self._is_reasoning_model(model_name):
    extra_params["reasoning"] = {"effort": reasoning_effort}
    # NE PAS ajouter "summary" ici
```

`reasoning_effort` = `"medium"` (défaut post-review, était `"low"`) pour les interprétations premium — compromis coût/qualité validé pour `natal_interpretation`. La valeur est forcée dans `_adjust_reasoning_config()` si `config.reasoning_effort` est falsy, garantissant qu'aucun appel GPT-5/o-series ne parte sans effort de raisonnement défini.

### Observabilité — Métriques Prometheus

Pattern existant : utiliser `prometheus_client` déjà intégré dans le projet. Créer les métriques dans les modules où elles sont incrémentées :

```python
from prometheus_client import Counter, Histogram

# Dans output_validator.py
natal_validation_pass = Counter("natal_validation_pass_total", "Validated natal responses", ["schema_version"])
natal_validation_fail = Counter("natal_validation_fail_total", "Failed natal responses", ["schema_version", "reason"])
natal_invalid_evidence = Counter("natal_invalid_evidence_total", "Evidence IDs filtered out")

# Dans gateway.py
natal_repair = Counter("natal_repair_total", "Repair attempts", ["use_case"])
natal_repair_fail = Counter("natal_repair_fail_total", "Failed repairs", ["use_case"])

# Dans natal_interpretation_service_v2.py
natal_summary_len = Histogram("natal_summary_len", "Summary length in chars", buckets=[200,500,900,1200,1500,2000,2800])
natal_section_len = Histogram("natal_section_len", "Section content length", buckets=[100,280,500,1000,2000,4000,6500])
```

Labels effectifs (post-review) : `use_case`, `schema_version` (`"v1"`, `"v2"`, `"v3"`, `"v3_error"`). Le label `schema_version` est propagé depuis `GatewayMeta.schema_version` — toutes les métriques (`natal_repair_total`, `natal_repair_fail_total`, `natal_validation_pass/fail_total`, `natal_invalid_evidence_total`) portent ce label pour permettre un filtrage Prometheus par version.

`output_validator.py` a reçu un paramètre `schema_version: str = "v1"` en signature afin de propager la version dans les labels sans couplage au gateway.

### Seed — Incohérence à corriger

**Attention** : dans `use_cases_seed.py` actuel, `natal_interpretation` pointe vers `AstroResponse_v1` (pas v2). C'est probablement un résidu — le service v2 sélectionne v1/v2 dynamiquement en code. La story 30-8 doit nettoyer cela : le seed doit pointer vers `AstroResponse_v3` et la sélection dynamique doit se faire via `NATAL_SCHEMA_VERSION`.

**Correction post-review (Fix #1)** : Le champ `question` était dans `required` de l'`input_schema` de `natal_interpretation`, mais le service `complete` n'envoie jamais `question` (`user_question_policy: "none"`). Ce désalignement provoquerait une validation failure en production. Corrigé : `question` retiré de `required`, seul `chart_json` est obligatoire :
```python
"required": ["chart_json"],
"properties": {
    "chart_json": {"type": "object"},
    "locale": {"type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$"},
    # question : optionnel, utilisé uniquement pour le niveau "short"
}
```

### Tests à écrire

**Unitaires prioritaires :**
- `test_schemas_v3.py` : validation contraintes — `summary` < 900 chars → `ValidationError`, `sections` < 5 → `ValidationError`, `disclaimers` field absent → no error
- `test_disclaimer_registry.py` : `get_disclaimers("fr-FR")` ≠ empty, `get_disclaimers("unknown-locale")` = `_default`
- `test_output_validator_v3.py` : evidence avec IDs hors catalog → filtrés, pas rejetés; compteur `natal_invalid_evidence_total` incrémenté

**Intégration :**
- `test_natal_interpretation_endpoint.py` (mise à jour) : réponse API contient `disclaimers` (liste non vide), `interpretation.disclaimers` absent du payload LLM
- `test_natal_interpretation_service_v3.py` : `NATAL_SCHEMA_VERSION=v3` → `AstroResponseV3` utilisé; `=v2` → `AstroResponseV2` utilisé

### Contexte depuis les stories précédentes

**Ce qui est stable et ne doit PAS être recréé :**
- `build_enriched_evidence_catalog()` dans `chart_json_builder.py` — ne pas dupliquer
- Validation bidirectionnelle `evidence ↔ text` dans `output_validator.py` — étendre, ne pas réécrire
- Pattern 4-layer message (HardPolicy + DevPrompt + Persona + UserData) — ne pas modifier la structure
- `user_question_policy: "none"` pour `natal_interpretation` complete — ne pas changer
- `fallback_use_case_key: "natal_interpretation_short"` — maintenir

**Ce qui change exclusivement dans cette story :**
- Ajout du modèle `AstroResponseV3` (et suppression du champ `disclaimers` du contrat LLM)
- Migration des disclaimers vers la couche API (nouveau `DisclaimerRegistry`)
- Mise à jour seed `natal_interpretation` → `AstroResponse_v3`
- Ajout métriques Prometheus dédiées
- Verification/complétion de `reasoning.effort`

### Stratégie rollback

`NATAL_SCHEMA_VERSION=v2` dans `.env` → rollback immédiat vers AstroResponseV2 sans redéploiement DB. Le seed `AstroResponse_v3` peut coexister avec `AstroResponse_v2` sans conflit.

### Références

- [Source: backend/app/llm_orchestration/schemas.py] — AstroResponseV1/V2 existants
- [Source: backend/app/llm_orchestration/seeds/use_cases_seed.py] — Contrats use cases et JSON Schemas DB
- [Source: backend/app/llm_orchestration/services/output_validator.py] — Validation bidirectionnelle evidence
- [Source: backend/app/services/natal_interpretation_service_v2.py] — Orchestration v2, sélection v1/v2
- [Source: backend/app/llm_orchestration/gateway.py] — PAID_USE_CASES, reasoning config
- [Source: backend/app/api/v1/routers/natal_interpretation.py] — Endpoint API
- [Source: _bmad-output/implementation-artifacts/30-7-nouveaux-produits-tarot-event-chat.md] — Story précédente (parité DB, ChatV2, strict-by-default)
- [Source: _bmad-output/implementation-artifacts/30-8-... (planning)] — Objectifs business initiaux

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Pydantic v2 error types: `string_too_short` (not `min_length`) and `too_short` (not `minItems`) — tests updated accordingly.
- `validate_output` signature extended with `use_case` kwarg (default `""`) and `schema_version` kwarg (default `"v1"`); gateway updated to pass both.
- `reasoning_effort` default corrigé à `"medium"` (pas `"low"`) dans `_adjust_reasoning_config()` — `"low"` était insuffisant pour la densité premium attendue.
- Schema version detection dans gateway : robustifiée via `schema_model.version` (entier DB) + fallback `"v3" in schema_name` string, au lieu d'un simple test de chaîne fragile.

### Completion Notes List

- T6.1: `build_repair_prompt()` est dans `repair_prompter.py` (pas `output_validator.py` comme mentionné en story). Correction appliquée.
- T6.2: Single-pass confirmé — guard `is_repair_call=True` dans `_handle_validation` empêche toute récursion.
- T8.3: `observe_duration` utilisé pour les histogrammes de longueur (char count) — c'est la fonction générique du système metrics du projet (pas `prometheus_client`).
- T8 (post-review): toutes les métriques natal portent le label `schema_version` pour permettre le filtrage Prometheus par version de schéma.
- Rollback: `NATAL_SCHEMA_VERSION=v2` dans `.env` bascule vers `AstroResponseV2` sans redéploiement.
- Disclaimers (post-review): `get_disclaimers()` supporte un fallback langue de base (`fr-CA → fr-FR`) avant le `_default`, couvrant les locales régionaux non listés explicitement.
- Post-prod fix (frontend, 2026-03-04): le rendu `complete` pouvait crasher si `interpretation.disclaimers` était absent (v3). Le front utilise désormais un fallback défensif vers `data.disclaimers` (top-level API), puis `[]`.
- Post-prod fix (frontend, 2026-03-04): homogénéisation de l'affichage `evidence` (ex: `ASPECT_*`, `HOUSE_*_IN_*`, `SUN_TAURUS_H10`) pour éviter des libellés hétérogènes en UI.
- UX fix (frontend, 2026-03-04): ajout d'un bouton de régénération aussi pour le mode `complete` (pas seulement `short`) avec déclenchement répétable via `refreshKey` pour forcer `force_refresh=true` à chaque clic.
- Prompt extension (backend, 2026-03-04): enrichissement du prompt v3 avec un catalogue de modules thématiques `NATAL_*` (psy profile, shadow integration, leadership/workstyle, creativity/joy, relationship style, community/networks, values/security, evolution path) et règle d'erreur dédiée `insufficient_data_for_module` pour `NATAL_EVOLUTION_PATH` en absence de nœuds lunaires.
- Correctif runtime modules (backend, 2026-03-04): ajout du champ `module` à l'endpoint natal, injection `MODULE=<NATAL_...>` dans le contexte LLM, bypass cache et non-persistance des réponses modulaires pour éviter les retours génériques `cached=true`.
- Correctif schéma modules (backend, 2026-03-04): extension de l'enum `_SECTION_KEYS` (Pydantic + JSON schema DB) pour autoriser les nouvelles clés de sections thématiques (`leadership_signature`, `patterns`, `values_core`, etc.), sans quoi le modèle restait contraint aux clés standard.
- Correctif pipeline données (backend, 2026-03-04): réintroduction explicite de `{{chart_json}}` dans le prompt publié `natal_interpretation` et ajout au lint requis pour garantir l'injection effective des données techniques (évite les réponses "données manquantes" alors que le thème existe).

### File List

**Modifiés:**
- `backend/app/llm_orchestration/schemas.py` — AstroSectionV3, **AstroSectionErrorV3** (new), AstroResponseV3, AstroErrorResponseV3 (sections → AstroSectionErrorV3), _SECTION_KEY_VALUES, model_config strict
- `backend/app/llm_orchestration/schemas.py` — extension `_SECTION_KEY_VALUES` / `_SECTION_KEYS` avec les clés modules `NATAL_*`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py` — ASTRO_RESPONSE_V3_JSON_SCHEMA (oneOf), upsert AstroResponse_v3, natal_interpretation → v3, **question retiré de required (Fix #1)**
- `backend/app/llm_orchestration/gateway.py` — reasoning.effort default `"medium"` (post-review: was `"low"`), schema_version detection robustifiée (via `schema_model.version` entier), natal_repair/fail counters + label `schema_version`, use_case param to validate_output
- `backend/app/llm_orchestration/services/output_validator.py` — secure filter (after bidirectional check), natal metrics avec label `schema_version`, params `use_case` + `schema_version`
- `backend/app/llm_orchestration/services/repair_prompter.py` — v3 density guidance block
- `backend/app/core/config.py` — natal_schema_version setting
- `backend/app/services/natal_interpretation_service_v2.py` — cascade v3→v3_error→v2→v1 robustifiée sur les deux chemins (cache + nouveau), observe_duration metrics
- `backend/app/api/v1/schemas/natal_interpretation.py` — disclaimers field, AstroResponseV3/AstroErrorResponseV3 in union, ajout `module` (enum `NATAL_*`) dans la request
- `backend/app/api/v1/routers/natal_interpretation.py` — get_disclaimers injection, propagation `module` vers le service
- `backend/app/tests/unit/test_output_validator.py` — updated test name/assertions for secure filter behavior
- `backend/app/tests/unit/test_repair_prompter.py` — added v3 density tests
- `frontend/src/api/natalChart.ts` — `disclaimers` optionnel sur `interpretation`, support `disclaimers` top-level API pour V3 (fallback défensif)
- `frontend/src/components/NatalInterpretation.tsx` — rendu robuste sans `interpretation.disclaimers`; normalisation homogène des libellés `evidence`; bouton de régénération disponible en `short` et `complete`
- `frontend/src/tests/natalInterpretation.test.tsx` — non-régression crash `complete` sans `interpretation.disclaimers`; test de formatage homogène `evidence`; test bouton régénération `complete`
- `_bmad-output/planning-artifacts/epics.md` — updated epic status
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — synced status

**Créés:**
- `backend/app/services/disclaimer_registry.py`
- `backend/scripts/seed_30_8_v3_prompts.py`
- `backend/scripts/seed_30_8_v3_prompts.py` — prompt injecte explicitement `{{chart_json}}` + lint requis mis à jour
- `backend/app/tests/unit/test_seed_30_8_v3_prompt_contract.py`
- `backend/app/tests/unit/test_schemas_v3.py` (27 tests — +2 post-review: error section densité, type AstroSectionErrorV3)
- `backend/app/tests/unit/test_output_validator_v3.py` (10 tests)
- `backend/app/tests/unit/test_disclaimer_registry.py` (10 tests)
- `backend/app/tests/unit/test_natal_metrics.py` (7 tests)

## Change Log

| Date | Change | Author |
|---|---|---|
| 2026-03-03 | Story créée depuis artefact 30-8 (proposed) via create-story workflow | claude-sonnet-4-6 |
| 2026-03-03 | Implémentation complète T1-T8, 66 tests unitaires au vert, status → review | claude-sonnet-4-6 |
| 2026-03-03 | Code Review fixes: Error mode schema (oneOf), service integration, secure filter order, Pydantic strictness, prompt cleanup. Status → done | Gemini-CLI |
| 2026-03-03 | Post-review hardening: Fix #1 — question retiré du required de l'input_schema natal_interpretation; Fix #3 — AstroSectionErrorV3 introduit, AstroErrorResponseV3.sections migré vers type sans contrainte densité; Polish B — guard liste vide dans get_disclaimers(). 60 tests au vert (60/60) | claude-sonnet-4-6 |
| 2026-03-03 | **Architecture note (ne pas revenir en arrière)** : les disclaimers légaux ne sont plus générés par le LLM — ils sont injectés statiquement côté app via `disclaimer_registry.py` selon le locale. Économie de ~50–100 tokens/appel, texte légal stable et versionnée en code, i18n fiable. `AstroResponseV3` rejette tout champ `disclaimers` via `extra="forbid"`. Pour modifier les textes ou ajouter un locale, éditer uniquement `_DISCLAIMERS` dans `disclaimer_registry.py`. | claude-sonnet-4-6 |
| 2026-03-03 | Hardening final (5 fixes post-implémentation) : [High] use_cases_seed — correction des tableaux du branch erreur dans ASTRO_RESPONSE_V3_JSON_SCHEMA ; [Medium] gateway — schema_version detection robuste via `schema_model.version` (entier), reasoning_effort default → `"medium"`, label `schema_version` ajouté sur tous les compteurs natal ; [Medium] output_validator — paramètre `schema_version` propagé dans les métriques ; [Medium] natal_interpretation_service_v2 — cascade v3→v3_error→v2→v1 robustifiée sur les deux chemins (cache + live) ; [Low] disclaimer_registry — fallback langue de base `fr-CA → fr-FR` avant `_default`. 60/60 tests au vert. | Gemini-CLI |
| 2026-03-04 | Stabilisation frontend post-validation réelle : correction crash `TypeError` en mode `complete` quand `interpretation.disclaimers` est absent, fallback vers `data.disclaimers` (API-level) et normalisation homogène des libellés `evidence` (`ASPECT_*`, `HOUSE_*_IN_*`, `*_Hn`). Tests UI ciblés verts. | Codex |
| 2026-03-04 | UX runtime: ajout du bouton de régénération en mode `complete` et mécanisme de refresh répétable (`refreshKey`) dans le hook `useNatalInterpretation` pour garantir une nouvelle requête `force_refresh=true` à chaque clic. Test frontend dédié ajouté. | Codex |
| 2026-03-04 | Prompt v3 étendu avec modules thématiques `NATAL_*` et objectifs éditoriaux dédiés (profil psycho, intégration de l'ombre, leadership, créativité, style relationnel, collectif, valeurs/sécurité, évolution). Ajout de la règle d'erreur module `insufficient_data_for_module` pour `NATAL_EVOLUTION_PATH` si les nœuds lunaires sont absents. Tests contrat prompt mis à jour. | Codex |
| 2026-03-04 | Activation runtime des modules thématiques: endpoint natal enrichi avec `module`, signal module injecté en contexte gateway (`MODULE=<...>`), bypass cache + skip persistence pour les interprétations modulaires afin d'éviter la réutilisation d'un payload complet standard en cache. | Codex |
| 2026-03-04 | Déblocage sections thématiques: mise à jour de l'enum des `section.key` dans les schémas applicatifs et le schema DB seedé (`AstroResponse_v3`) pour autoriser les clés modules (ex: `leadership_signature`, `patterns`, `values_core`, `comfort_zone`). Ajout de `meta.module` pour tracer le module appliqué côté réponse API. | Codex |
| 2026-03-04 | Fix pipeline données natal: le prompt v3 `natal_interpretation` inclut désormais `{{chart_json}}` explicitement (et lint obligatoire), supprimant le défaut où le gateway n'envoyait pas les données techniques au modèle et provoquait des réponses "insufficient data" quasi vides. | Codex |
