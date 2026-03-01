# Story 29.3: N3 — Prompts DB + lint + publish

Status: done

## Story

As a product owner,
I want gérer les prompts d'interprétation natale en base de données,
so that je puisse itérer sur le contenu sans redéployer le code.

## Acceptance Criteria

1. Un script de seed `backend/scripts/seed_29_prompts.py` est disponible et idempotent.
2. Les prompts pour `natal_interpretation_short` (SIMPLE) et `natal_interpretation` (COMPLETE) sont créés et publiés en base de données.
3. Le prompt SHORT inclut obligatoirement les placeholders `{{chart_json}}`, `{{locale}}` et `{{use_case}}`.
4. Le prompt COMPLETE inclut obligatoirement les placeholders `{{chart_json}}`, `{{persona_name}}`, `{{locale}}` et `{{use_case}}`.
5. Le mechanism de linting des prompts valide la présence de ces placeholders avant toute création de version.
6. La publication d'un nouveau prompt via l'interface admin invalide le cache du `PromptRegistryV2`.
7. Le `prompt_version_id` utilisé est correctement tracé dans les métadonnées de réponse du Gateway.

## Tasks / Subtasks

- [x] Créer le script de seed `backend/scripts/seed_29_prompts.py`
  - [x] Définir le contenu des prompts `natal_interpretation_short` et `natal_interpretation` (ton, structure AstroResponse_v1)
  - [x] Implémenter la logique d'insertion et de publication (status=PUBLISHED)
  - [x] S'assurer que le script utilise `lint_prompt()` avant d'insérer
- [x] Vérifier et adapter `backend/app/llm_orchestration/services/prompt_lint.py`
  - [x] S'assurer que les placeholders requis par use_case sont bien vérifiés
- [x] Créer les tests unitaires du lint dans `backend/app/tests/unit/test_prompt_lint_natal.py`
  - [x] Tester les cas valides et invalides (placeholders manquants, longueur excessive)
- [x] Créer les tests d'intégration admin dans `backend/app/tests/integration/test_admin_llm_natal_prompts.py`
  - [x] Tester la création de draft et la publication via API admin

## Dev Notes

- Les prompts utilisent le format de sortie `AstroResponse_v1` (JSON strict).
- Le Gateway V2 s'occupe du rendu Jinja2 des prompts.
- `{{persona_name}}` est injecté par le service V2 (Story 29.2) pour le mode COMPLETE.
- Le modèle par défaut est `gpt-4o-mini`.

### Technical Requirements

- Backend: FastAPI/Python 3.13
- Database: PostgreSQL (LlmPromptVersionModel)
- Templating: Jinja2 (via LLMGateway)

### File Structure Requirements

- `backend/scripts/seed_29_prompts.py`
- `backend/app/tests/unit/test_prompt_lint_natal.py`
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py`
- `backend/app/llm_orchestration/services/prompt_lint.py` (modification)

### Testing Requirements

- Pytest pour les tests unitaires et d'intégration.
- Validation des contrats de réponse JSON.

### References

- Epic/Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 29, Story 29.3)
- Context documentation: `docs/agent/story-29-N3-prompts-db-publish.md`
