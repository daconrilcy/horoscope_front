# Contrat `narrative_natal_reading_v1`

Version: `narrative_natal_reading_v1`. Owner canonique: `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py`.

## Relation avec les contrats existants

| Contrat | Rôle |
|---|---|
| `AstroResponseV3` | Sortie LLM longue (sections techniques internes au pipeline) |
| `llm_astrology_input_v1` | Source astrologique backend-only (jamais exposée) |
| `narrative_natal_reading_v1` | **Contrat produit public** pour `/natal` : cinq chapitres + justification |
| `narrative_answer_audit_v1` | Rejets et audit interne (RG-150) |

Le runtime natal moderne persiste `narrative_natal_reading_v1` à côté du payload V3 accepté sous la clé `narrative_natal_reading_v1`. Les rejets (`status="rejected"`) ne sont jamais désérialisés en lecture publique.

## Projection runtime (CS-392)

La lecture publique est **projétée côté backend** depuis une `AstroResponseV3` acceptée via
`build_narrative_natal_reading_v1` (mapping sections V3 → cinq chapitres ordonnés). Le prompt
LLM natal nominal reste centré sur `AstroResponseV3`, mais demande explicitement les sections
sources `self_image`, `emotions`, `relationships`, `career` et `growth_direction`. La projection
post-acceptation reste le owner canonique du contrat produit public, validée par
`validate_narrative_reading_public_text` et `validate_narrative_semantic_integrity` avant
persistance. Aucun padding silencieux : une section source manquante déclenche un rejet
`narrative_semantic_integrity` / `chapter_source_missing`, jamais une recopie de
`response.sections[0]`.

## Chapitres (ordre fixe)

1. `personality` — personnalité
2. `emotional_world` — monde émotionnel
3. `relationships` — relations
4. `vocation` — vocation
5. `evolution_path` — chemin d'évolution

Chaque chapitre: `title`, `narrative` (texte principal), `key_points` optionnels.

## `used_astrological_elements`

Liste courte (max 12) d'objets `{ astrological_label, consequence }` en langage lisible. Pas de score, code moteur, hash, trace LLM.

## Denylist publique (interdit dans tout texte exposé)

- `chart_json`, `natal_data`, `evidence_refs`, `audit_input`
- `interpretive_signal_ids`, `technical_scores`, `prompt_payloads`
- `explanation_facts`, `interpretation_adapter`, `projection_version`
- `visibility_expression`, `condition_axis:`, `centrality score`

## Profondeur éditoriale

| Profil | Limite `used_astrological_elements` |
|---|---|
| `free` | 3 |
| `basic` | 6 |
| `premium` | 10 |

Exemples JSON: `backend/docs/examples/narrative-natal-reading-v1-*.json`.

## Non-régression

- RG-149, RG-150 applicables
- Preuve: `pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py backend/tests/architecture/test_narrative_natal_reading_public_boundary.py`
