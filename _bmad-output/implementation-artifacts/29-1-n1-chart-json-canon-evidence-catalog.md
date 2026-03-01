# Story 29.1: N1 — chart_json canonique + evidence_catalog

Status: done

## Story

As a service d'interprétation,
I want disposer d'un export JSON stable et d'un catalogue de preuves astrologiques,
so that le gateway LLM reçoive des données structurées et ancrées pour l'interprétation.

## Acceptance Criteria

1. La fonction `build_chart_json(natal_result, birth_profile, degraded_mode)` retourne un dictionnaire stable avec les clés `meta`, `planets`, `houses`, `aspects`, `angles`.
   - Le champ `meta` doit inclure `chart_json_version: "1"` pour assurer la compatibilité future des prompts.
2. Le mode dégradé (no_time, no_location) est correctement géré (angles mis à null, champs meta adaptés).
3. `longitude_in_sign` et `sign` sont calculés correctement pour chaque corps céleste.
4. La fonction `build_evidence_catalog(chart_json)` produit une liste d'identifiants UPPER_SNAKE_CASE conformes au pattern regex `^[A-Z0-9_\.:-]{3,60}$`.
5. Couverture de tests unitaires >= 90% sur le module `chart_json_builder.py`.

## Tasks / Subtasks

- [x] Créer le module `backend/app/services/chart_json_builder.py`
  - [x] Implémenter `_longitude_to_sign` et `_longitude_in_sign`
  - [x] Implémenter `build_chart_json` avec gestion des métadonnées et des angles
  - [x] Implémenter `build_evidence_catalog` avec les règles de nommage spécifiées
- [x] Créer les tests unitaires `backend/app/tests/unit/test_chart_json_builder.py`
  - [x] Tester le thème complet
  - [x] Tester les modes dégradés (no_time, no_location)
  - [x] Valider le format des évidences générées
- [x] Vérifier l'absence d'imports circulaires et la sérialisabilité JSON

## Dev Notes

- Utiliser `NatalResult` et `UserBirthProfileData` comme sources de données.
- Respecter le format de sortie attendu par le gateway LLM (Epic 28).
- Les identifiants de preuves (evidence) servent d'ancrage pour le LLM.
- Pas de DB ni de LLM requis pour cette story (utilitaires purs).

### Technical Requirements

- Backend: FastAPI/Python 3.13
- Regex validation pour les evidence IDs.
- Serialisation JSON stricte.

### File Structure Requirements

- `backend/app/services/chart_json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`

### Testing Requirements

- Pytest pour les tests unitaires.
- Couverture >= 90%.

### References

- Epic/Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 29, Story 29.1)
- Context documentation: `docs/agent/story-29-N1-chart-json-canon.md`
