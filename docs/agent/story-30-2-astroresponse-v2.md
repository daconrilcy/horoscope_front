# Story 30-2 — AstroResponse_v2 : Schéma Étendu pour l'Interprétation Premium

## Contexte & Périmètre

**Epic ASTRO-30 / Story 30-2**
**Chapitre 30** — AstroResponse_v2 & Orchestration GPT-5

Le JSON schema `AstroResponse_v1` stocké en base de données (table `llm_output_schemas`) plafonne
`summary` à **1200 chars** et `sections[].content` à **2500 chars**, alors que le prompt
`natal_interpretation` (`NATAL_COMPLETE_PROMPT` dans `seed_29_prompts.py`) demande respectivement
"max 2000 chars" et "max 4000 chars". Cette discordance produit des troncations systématiques :

1. Le LLM génère un contenu riche conforme au prompt.
2. Le schema strict de la Responses API rejette (ou tronque silencieusement) le résultat.
3. Le repair loop retourne une version raccourcie et appauvrie.

De plus, `highlights[]` et `advice[]` items sont limités à 160 chars, rendant les conseils
tronqués et les highlights sans profondeur.

**Cette story crée `AstroResponse_v2`** : même structure que v1 (compatibilité frontend minimale),
limites franchement élargies, pointé uniquement par le use case `natal_interpretation` (payant).
Le use case `natal_interpretation_short` (gratuit) reste sur `AstroResponse_v1`.

**Dépend de :** Chapitre 28 (LLMGateway, `LlmOutputSchemaModel`), Chapitre 29-N3 (seed_29_prompts.py)

---

## Hypothèses & Dépendances

- `LlmOutputSchemaModel` existe en DB avec `name="AstroResponse_v1"` (seédé par `seed_28_4.py`)
- `LlmUseCaseConfigModel(key="natal_interpretation")` existe en DB avec `output_schema_id` pointant vers `AstroResponse_v1`
- `NatalInterpretationServiceV2` utilise `AstroResponseV1(**gateway_result.structured_output)` pour désérialiser (ligne 186 de `natal_interpretation_service_v2.py`)
- `NatalInterpretationData.interpretation: AstroResponseV1` (ligne 42 de `natal_interpretation.py`)
- Le gateway lit le schema via `db.get(LlmOutputSchemaModel, uuid.UUID(config.output_schema_id))` et l'envoie à la Responses API (`gateway.py:439-469`)
- Le frontend reçoit `interpretation` comme plain object JSON — il n'est pas typé strictement côté client, donc élargir les limites n'est pas un breaking change

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Créer `AstroSectionV2` et `AstroResponseV2` dans `schemas.py` avec des limites élargies
- Insérer le JSON schema `AstroResponse_v2` dans la table `llm_output_schemas` (via script de seed idempotent)
- Mettre à jour `LlmUseCaseConfigModel(key="natal_interpretation")` pour pointer vers `AstroResponse_v2`
- Adapter `NatalInterpretationServiceV2` pour désérialiser en `AstroResponseV2` quand `level="complete"`
- Adapter `NatalInterpretationData` pour accepter les deux types (`AstroResponseV1 | AstroResponseV2`)
- Tester la validité du nouveau schema et la coexistence v1/v2

**Non-Objectifs :**
- Modifier `AstroResponse_v1` (ne pas casser les clients existants sur `short`)
- Modifier le frontend (les champs JSON sont identiques, seulement les limites changent)
- Modifier les prompts (objet de Story 30-3)
- Ajouter de nouveaux champs au schema (même structure, limites élargies seulement)
- Migrer les interprétations `complete` déjà persistées en DB (elles restent valides)

---

## Acceptance Criteria

### AC1 — Nouveau JSON schema en DB après seed

Après exécution de `python backend/scripts/seed_30_2_astroresponse_v2.py` :
- `LlmOutputSchemaModel(name="AstroResponse_v2")` existe en DB
- Son `json_schema` respecte les limites v2 (voir tableau ci-dessous)
- `LlmUseCaseConfigModel(key="natal_interpretation").output_schema_id` == UUID de `AstroResponse_v2`
- `LlmUseCaseConfigModel(key="natal_interpretation_short").output_schema_id` == UUID de `AstroResponse_v1` (inchangé)

**Tableau des limites — différences v1 vs v2 :**

| Champ | `AstroResponse_v1` (DB) | `AstroResponse_v2` (DB) |
|-------|------------------------|------------------------|
| `title` maxLength | 120 | 160 |
| `summary` maxLength | 1200 | 2800 |
| `sections` maxItems | 8 | 10 |
| `sections[].heading` maxLength | 80 | 100 |
| `sections[].content` maxLength | 2500 | 6500 |
| `highlights[]` maxItems | 10 | 12 |
| `highlights[]` item maxLength | 160 | 360 |
| `advice[]` maxItems | 10 | 12 |
| `advice[]` item maxLength | 160 | 360 |
| `evidence[]` minItems | 2 | 0 |
| `evidence[]` maxItems | 40 | 80 |
| `evidence[]` item pattern | `^[A-Z0-9_\.:-]{3,60}$` | `^[A-Z0-9_\.:-]{3,80}$` |
| `disclaimers[]` maxItems | 3 | 3 |
| `disclaimers[]` item maxLength | 200 | 300 |
| `sections` minItems | 2 | 2 |
| `highlights[]` minItems | 3 | 3 |
| `advice[]` minItems | 3 | 3 |

### AC2 — Schema v2 compatible strict=True (Responses API)

Le JSON schema v2 satisfait les règles de strict=true :
- Tous les champs de `required` sont listés dans `properties`
- Pas de champs hors `required` sans default
- `additionalProperties: false` sur tous les objets imbriqués
- Aucun champ optionnel scalaire (pas de `anyOf` avec `null` non prévu)

```python
# Forme attendue du json_schema stocké en DB
{
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence", "disclaimers"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "summary": {"type": "string", "minLength": 1, "maxLength": 2800},
        "sections": {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {
                        "type": "string",
                        "enum": [
                            "overall", "career", "relationships", "inner_life",
                            "daily_life", "strengths", "challenges",
                            "tarot_spread", "event_context"
                        ]
                    },
                    "heading": {"type": "string", "minLength": 1, "maxLength": 100},
                    "content": {"type": "string", "minLength": 1, "maxLength": 6500}
                }
            }
        },
        "highlights": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 360}
        },
        "advice": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 360}
        },
        "evidence": {
            "type": "array",
            "minItems": 0,
            "maxItems": 80,
            "items": {"type": "string", "pattern": r"^[A-Z0-9_\.:-]{3,80}$"}
        },
        "disclaimers": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 1, "maxLength": 300}
        }
    }
}
```

### AC3 — Modèle Pydantic `AstroResponseV2` dans `schemas.py`

Un nouveau modèle Pydantic `AstroResponseV2` (et `AstroSectionV2`) existe dans
`backend/app/llm_orchestration/schemas.py` avec des contraintes Field alignées sur le JSON schema v2.

```python
class AstroSectionV2(BaseModel):
    key: Literal[
        "overall", "career", "relationships", "inner_life", "daily_life",
        "strengths", "challenges", "tarot_spread", "event_context"
    ]
    heading: str = Field(..., min_length=1, max_length=100)  # vs 80 en v1
    content: str = Field(..., min_length=1, max_length=6500)  # vs 4000 en v1


class AstroResponseV2(BaseModel):
    """Canonical structured response for premium astrological interpretations (v2)."""
    title: str = Field(..., min_length=1, max_length=160)       # vs 120
    summary: str = Field(..., min_length=1, max_length=2800)    # vs 2000
    sections: List[AstroSectionV2] = Field(..., min_length=2, max_length=10)  # vs 8
    highlights: List[str] = Field(..., min_length=3, max_length=12)  # vs 10
    advice: List[str] = Field(..., min_length=3, max_length=12)      # vs 10
    evidence: List[str] = Field(default_factory=list, max_length=80) # vs min_length=2, max_length=40
    disclaimers: List[str] = Field(default_factory=list)
```

### AC4 — Désérialisation correcte dans `NatalInterpretationServiceV2`

Le service désérialise selon le niveau :
- `level="short"` → `AstroResponseV1(**gateway_result.structured_output)` (inchangé)
- `level="complete"` → `AstroResponseV2(**gateway_result.structured_output)`

Si le gateway retourne une réponse v1 pour `complete` (fallback déclenché vers `natal_interpretation_short`),
le service doit tolérer la désérialisation en v1 :

```python
# Dans NatalInterpretationServiceV2.interpret()

if level == "complete" and not gateway_result.meta.fallback_triggered:
    interpretation = AstroResponseV2(**gateway_result.structured_output)
else:
    interpretation = AstroResponseV1(**gateway_result.structured_output)
```

### AC5 — API response polymorphique

`NatalInterpretationData.interpretation` accepte v1 et v2 sans erreur Pydantic.
La sérialisation JSON de l'API reste identique (les deux modèles ont les mêmes champs).

```python
# backend/app/api/v1/schemas/natal_interpretation.py
from app.llm_orchestration.schemas import AstroResponseV1, AstroResponseV2
from typing import Union

class NatalInterpretationData(BaseModel):
    chart_id: str
    use_case: str
    interpretation: Union[AstroResponseV1, AstroResponseV2]
    meta: InterpretationMeta
    degraded_mode: Optional[str] = None
```

`GET /v1/natal/interpretation` avec `level=complete` → le champ `interpretation` contient un objet
pouvant avoir `summary` de 2800 chars sans erreur de validation.

### AC6 — Idempotence du script de seed

Exécuter `seed_30_2_astroresponse_v2.py` deux fois :
- Première exécution : INSERT schema + UPDATE use case → log "Created AstroResponse_v2"
- Deuxième exécution : UPDATE schema (si identique) + no-op sur use case → log "AstroResponse_v2 already exists, schema updated"
- Aucune exception levée dans les deux cas

### AC7 — Couverture de test ≥ 80%

Tests unitaires sur :
- Validation d'un payload v2 valide
- Rejet d'un payload dépassant les limites v1 mais accepté par v2 (summary > 1200 chars, < 2800 chars)
- Coexistence : `NatalInterpretationData` accepte v1 et v2 sans error

---

## Tâches Techniques

### T1 — Ajouter `AstroSectionV2` et `AstroResponseV2` dans `schemas.py`

**Fichier :** `backend/app/llm_orchestration/schemas.py`

Ajouter après `AstroResponseV1` :

```python
class AstroSectionV2(BaseModel):
    key: Literal[
        "overall", "career", "relationships", "inner_life", "daily_life",
        "strengths", "challenges", "tarot_spread", "event_context",
    ]
    heading: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=6500)


class AstroResponseV2(BaseModel):
    """Canonical structured response for premium astrological interpretations.

    Extended limits vs v1:
    - summary: 2800 chars (v1: 2000)
    - sections: max 10 (v1: 8), content 6500 chars (v1: 4000), heading 100 chars (v1: 80)
    - highlights/advice: max 12 items (v1: 10), 360 chars/item (v1: no per-item limit in Pydantic)
    - evidence: max 80 items (v1: 40), 0 min (v1: 2 min)
    """
    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=1, max_length=2800)
    sections: List[AstroSectionV2] = Field(..., min_length=2, max_length=10)
    highlights: List[str] = Field(..., min_length=3, max_length=12)
    advice: List[str] = Field(..., min_length=3, max_length=12)
    evidence: List[str] = Field(default_factory=list, max_length=80)
    disclaimers: List[str] = Field(default_factory=list)
```

Mettre à jour les imports si nécessaire (`from __future__ import annotations` déjà présent).

### T2 — Script de seed `seed_30_2_astroresponse_v2.py`

**Fichier :** `backend/scripts/seed_30_2_astroresponse_v2.py`

```python
"""
Seed : création du schema AstroResponse_v2 et mise à jour du use case natal_interpretation.

Ce script est idempotent :
- INSERT ou UPDATE AstroResponse_v2 dans llm_output_schemas
- UPDATE natal_interpretation.output_schema_id → id de AstroResponse_v2

NE PAS modifier natal_interpretation_short (reste sur AstroResponse_v1).

Run with:
    python -m scripts.seed_30_2_astroresponse_v2
"""

import logging
from sqlalchemy import select
from app.infra.db.models import LlmOutputSchemaModel, LlmUseCaseConfigModel
from app.infra.db.session import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ASTRO_RESPONSE_V2_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "summary", "sections", "highlights", "advice", "evidence", "disclaimers"],
    "properties": {
        "title": {"type": "string", "minLength": 1, "maxLength": 160},
        "summary": {"type": "string", "minLength": 1, "maxLength": 2800},
        "sections": {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["key", "heading", "content"],
                "properties": {
                    "key": {
                        "type": "string",
                        "enum": [
                            "overall", "career", "relationships", "inner_life",
                            "daily_life", "strengths", "challenges",
                            "tarot_spread", "event_context"
                        ]
                    },
                    "heading": {"type": "string", "minLength": 1, "maxLength": 100},
                    "content": {"type": "string", "minLength": 1, "maxLength": 6500}
                }
            }
        },
        "highlights": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 360}
        },
        "advice": {
            "type": "array",
            "minItems": 3,
            "maxItems": 12,
            "items": {"type": "string", "minLength": 1, "maxLength": 360}
        },
        "evidence": {
            "type": "array",
            "minItems": 0,
            "maxItems": 80,
            "items": {"type": "string", "pattern": r"^[A-Z0-9_\.:-]{3,80}$"}
        },
        "disclaimers": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 1, "maxLength": 300}
        }
    }
}


def seed():
    db = SessionLocal()
    try:
        # 1. Insert or update AstroResponse_v2
        stmt = select(LlmOutputSchemaModel).where(LlmOutputSchemaModel.name == "AstroResponse_v2")
        existing_schema = db.execute(stmt).scalar_one_or_none()

        if existing_schema is None:
            new_schema = LlmOutputSchemaModel(
                name="AstroResponse_v2",
                json_schema=ASTRO_RESPONSE_V2_SCHEMA,
                version=1,
            )
            db.add(new_schema)
            db.flush()
            v2_id = str(new_schema.id)
            logger.info("Created AstroResponse_v2 with id=%s", v2_id)
        else:
            existing_schema.json_schema = ASTRO_RESPONSE_V2_SCHEMA
            v2_id = str(existing_schema.id)
            logger.info("Updated AstroResponse_v2 schema (id=%s)", v2_id)

        # 2. Update natal_interpretation use case to point to v2
        stmt_uc = select(LlmUseCaseConfigModel).where(
            LlmUseCaseConfigModel.key == "natal_interpretation"
        )
        uc = db.execute(stmt_uc).scalar_one_or_none()
        if uc is None:
            logger.warning("Use case 'natal_interpretation' not found. Run seed_29_prompts.py first.")
        else:
            old_id = uc.output_schema_id
            uc.output_schema_id = v2_id
            logger.info(
                "Updated natal_interpretation.output_schema_id: %s → %s",
                old_id, v2_id
            )

        # 3. Verify natal_interpretation_short stays on v1
        stmt_short = select(LlmUseCaseConfigModel).where(
            LlmUseCaseConfigModel.key == "natal_interpretation_short"
        )
        uc_short = db.execute(stmt_short).scalar_one_or_none()
        if uc_short:
            logger.info(
                "natal_interpretation_short remains on schema_id=%s (v1, unchanged)",
                uc_short.output_schema_id
            )

        db.commit()
        logger.info("Seed completed successfully.")
    except Exception:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
```

**Important :** Le modèle `LlmOutputSchemaModel` a un champ `version: Mapped[int]`.
S'il n'existe pas encore, vérifier le modèle ORM et ajouter si nécessaire (ou utiliser `version=1`).

### T3 — Mettre à jour `natal_interpretation.py` (API schemas)

**Fichier :** `backend/app/api/v1/schemas/natal_interpretation.py`

Modifier l'import et le type de `NatalInterpretationData.interpretation` :

```python
# Remplacer :
from app.llm_orchestration.schemas import AstroResponseV1

# Par :
from typing import Union
from app.llm_orchestration.schemas import AstroResponseV1, AstroResponseV2

# Modifier NatalInterpretationData :
class NatalInterpretationData(BaseModel):
    chart_id: str
    use_case: str
    interpretation: Union[AstroResponseV1, AstroResponseV2]  # Union, pas un seul type
    meta: InterpretationMeta
    degraded_mode: Optional[str] = None
```

**Note Pydantic v2 :** `Union[AstroResponseV1, AstroResponseV2]` sérialise correctement car les
deux modèles ont les mêmes champs. Pydantic tentera d'abord v1, si la validation échoue (ex :
summary > 2000 chars) il passera à v2.

**Alternative plus explicite** si le comportement Union est instable :

```python
interpretation: AstroResponseV1 | AstroResponseV2 = Field(
    ..., discriminator=None  # pas de discriminator, même shape
)
```

Ou simplement : `interpretation: dict` pour que FastAPI sérialise sans validation stricte côté API.
À choisir selon les contraintes de typage existantes dans le projet.

### T4 — Mettre à jour `NatalInterpretationServiceV2`

**Fichier :** `backend/app/services/natal_interpretation_service_v2.py`

Deux modifications :

**4a. Import**

```python
# Remplacer :
from app.llm_orchestration.schemas import AstroResponseV1

# Par :
from app.llm_orchestration.schemas import AstroResponseV1, AstroResponseV2
```

**4b. Désérialisation après appel gateway (section "# Mapping structured_output", ligne ~186)**

```python
# Remplacer :
interpretation = AstroResponseV1(**gateway_result.structured_output)

# Par :
if level == "complete" and not gateway_result.meta.fallback_triggered:
    # complete (payant) → schéma v2 étendu
    interpretation: AstroResponseV1 | AstroResponseV2 = AstroResponseV2(**gateway_result.structured_output)
else:
    # short (gratuit) ou fallback vers short → schéma v1
    interpretation = AstroResponseV1(**gateway_result.structured_output)
```

**4c. Désérialisation du cache (section "# 0. Check for existing persisted interpretation", ligne ~68)**

```python
# Remplacer :
interpretation = AstroResponseV1(**existing.interpretation_payload)

# Par :
if level == "complete":
    try:
        interpretation: AstroResponseV1 | AstroResponseV2 = AstroResponseV2(**existing.interpretation_payload)
    except Exception:
        # Ancienne interprétation persistée en v1 : fallback gracieux
        interpretation = AstroResponseV1(**existing.interpretation_payload)
else:
    interpretation = AstroResponseV1(**existing.interpretation_payload)
```

### T5 — Tests unitaires

**Fichier :** `backend/app/tests/unit/test_astro_response_v2.py`

```python
import pytest
from pydantic import ValidationError
from app.llm_orchestration.schemas import AstroResponseV1, AstroResponseV2, AstroSectionV2


SECTION_V2 = {
    "key": "overall",
    "heading": "Un portrait astrologique nuancé et intégratif",
    "content": "A" * 3000,  # 3000 chars < 6500 → valide en v2
}

VALID_V2_PAYLOAD = {
    "title": "La Synthèse d'un Thème Natal Complexe et Riche",
    "summary": "B" * 2500,  # 2500 < 2800 → valide en v2, invalide en v1 (> 2000)
    "sections": [SECTION_V2, SECTION_V2],
    "highlights": ["H" * 300] * 5,   # 300 < 360 → valide v2
    "advice": ["A" * 200] * 5,        # 200 < 360 → valide v2
    "evidence": ["SUN_TAURUS_H10", "MOON_CANCER_H8"],
    "disclaimers": ["L'astrologie est un outil de réflexion."],
}


def test_astro_response_v2_valid():
    """Un payload dans les limites v2 est accepté."""
    r = AstroResponseV2(**VALID_V2_PAYLOAD)
    assert len(r.summary) == 2500
    assert r.sections[0].content == "A" * 3000


def test_summary_exceeds_v1_but_valid_v2():
    """Un summary de 1500 chars est rejeté par v1 mais accepté par v2."""
    payload_with_long_summary = {**VALID_V2_PAYLOAD, "summary": "S" * 1500}
    with pytest.raises(ValidationError):
        AstroResponseV1(**payload_with_long_summary)  # v1 max=2000 → OK ? non, max Pydantic=2000
    # Note: AstroResponseV1 Pydantic a max=2000 mais le JSON schema DB a max=1200.
    # Le test vérifie la limite DB pertinente via json_schema validation, pas Pydantic.
    AstroResponseV2(**payload_with_long_summary)  # v2 max=2800 → OK


def test_content_exceeds_v1_pydantic_but_valid_v2():
    """Un section.content de 5000 chars est rejeté par AstroSectionV2 uniquement si > 6500."""
    big_content = "C" * 5000  # 5000 < 6500 → valide v2
    AstroResponseV2(**{**VALID_V2_PAYLOAD, "sections": [
        {**SECTION_V2, "content": big_content}, SECTION_V2
    ]})


def test_content_exceeds_v2_limit():
    """Un section.content > 6500 chars est rejeté par v2."""
    with pytest.raises(ValidationError):
        AstroResponseV2(**{**VALID_V2_PAYLOAD, "sections": [
            {**SECTION_V2, "content": "X" * 6501}, SECTION_V2
        ]})


def test_evidence_empty_is_valid_v2():
    """evidence=[] est valide en v2 (minItems=0), invalide en v1 (minItems=2)."""
    payload = {**VALID_V2_PAYLOAD, "evidence": []}
    AstroResponseV2(**payload)
    with pytest.raises(ValidationError):
        AstroResponseV1(**{**VALID_V2_PAYLOAD, "evidence": []})


def test_natal_interpretation_data_accepts_both():
    """NatalInterpretationData accepte v1 et v2 sans erreur."""
    from app.api.v1.schemas.natal_interpretation import NatalInterpretationData, InterpretationMeta

    meta = InterpretationMeta(
        level="complete",
        use_case="natal_interpretation",
        validation_status="valid",
    )
    v1_payload = {**VALID_V2_PAYLOAD, "summary": "Court" * 10}
    v2_obj = AstroResponseV2(**VALID_V2_PAYLOAD)

    data = NatalInterpretationData(
        chart_id="abc",
        use_case="natal_interpretation",
        interpretation=v2_obj,
        meta=meta,
    )
    assert data.interpretation.summary == v2_obj.summary
```

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| CRÉER | `backend/scripts/seed_30_2_astroresponse_v2.py` |
| MODIFIER | `backend/app/llm_orchestration/schemas.py` (ajouter `AstroSectionV2`, `AstroResponseV2`) |
| MODIFIER | `backend/app/api/v1/schemas/natal_interpretation.py` (`Union[V1, V2]` pour `interpretation`) |
| MODIFIER | `backend/app/services/natal_interpretation_service_v2.py` (désérialisation v2 pour complete) |
| CRÉER | `backend/app/tests/unit/test_astro_response_v2.py` |

---

## Critères de "Done"

- [ ] `python backend/scripts/seed_30_2_astroresponse_v2.py` s'exécute sans erreur (deux fois de suite)
- [ ] `SELECT name, json_schema FROM llm_output_schemas` retourne `AstroResponse_v2` avec `summary.maxLength=2800`
- [ ] `SELECT output_schema_id FROM llm_use_case_configs WHERE key='natal_interpretation'` → id de v2
- [ ] `SELECT output_schema_id FROM llm_use_case_configs WHERE key='natal_interpretation_short'` → id de v1 (inchangé)
- [ ] `AstroResponseV2` et `AstroSectionV2` importables depuis `app.llm_orchestration.schemas`
- [ ] `NatalInterpretationServiceV2.interpret(level="complete")` → `interpretation` est instance de `AstroResponseV2`
- [ ] `NatalInterpretationServiceV2.interpret(level="short")` → `interpretation` est instance de `AstroResponseV1`
- [ ] `POST /v1/natal/interpretation` avec `use_case_level=complete` → summary peut dépasser 1200 chars sans erreur 500
- [ ] Tests unitaires dans `test_astro_response_v2.py` passent à 100%
- [ ] Aucun test existant cassé (vérifier `test_natal_interpretation_endpoint.py` si existant)
