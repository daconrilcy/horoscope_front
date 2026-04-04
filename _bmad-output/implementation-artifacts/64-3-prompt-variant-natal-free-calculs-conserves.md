# Story 64.3 — Prompt variant thème natal free : calculs conservés, texte restreint

Status: done

## Story

En tant que système backend,
je veux que le thème natal d'un utilisateur free soit toujours calculé intégralement mais que la génération textuelle LLM soit restreinte au variant "free_short",
afin de démontrer la profondeur de l'analyse tout en incitant à l'upgrade pour lire les détails.

## Context

Cette story s'appuie sur le `NatalChartLongEntitlementGate`. Elle modifie le comportement du plan `free` qui était auparavant bloqué (`is_enabled=False`). Maintenant, le plan `free` permet l'accès à `natal_chart_long` mais avec un `variant_code="free_short"`.

**Comportement du variant `free_short` :**
- Appelle le use-case LLM `natal_long_free`.
- Retourne uniquement un résumé global du thème natal et des titres de sections courts.
- Conserve les calculs astro complets en arrière-plan.

## Acceptance Criteria

- [x] **AC1 — Activation du gate pour le plan free** : `variant_code="free_short"` est retourné par le gate pour les utilisateurs free.
- [x] **AC2 — Catalogue des prompts mis à jour** : ajout de `natal_long_free`.
- [x] **AC3 — Schéma de sortie variant "free_short"** : `summary` + `accordion_titles`.
- [x] **AC4 — Orchestration dans `NatalInterpretationServiceV2`** : support de la redirection vers le prompt restreint.
- [x] **AC5 — Persistence du variant** : stockage du `variant_code` dans la table `user_natal_interpretations`.
- [x] **AC6 — Testabilité intégrative** : un utilisateur free peut générer un thème "complet" (en version restreinte).

## Tasks / Subtasks

- [x] T1 — Configurer le gate pour le variant "free_short" (AC1)
  - [x] T1.1 Mettre à jour `backend/scripts/seed_product_entitlements.py` pour activer `natal_chart_long` sur le plan free avec `variant_code="free_short"`

- [x] T2 — Ajouter `natal_long_free` dans `PROMPT_CATALOG` (AC2, AC3)
  - [x] T2.1 Définir `NATAL_FREE_SHORT_SCHEMA`
  - [x] T2.2 Ajouter l'entrée `natal_long_free` dans `PROMPT_CATALOG`

- [x] T3 — Mettre à jour `.env.example`
  - [x] T3.1 Ajouter `OPENAI_ENGINE_NATAL_LONG_FREE`

- [x] T4 — Modifier `NatalInterpretationServiceV2` pour respecter le variant (AC4, AC5)
  - [x] T4.1 Ajouter `variant_code` au modèle `UserNatalInterpretationModel` et aux index uniques
  - [x] T4.2 Mettre à jour `NatalInterpretationServiceV2.interpret()` pour accepter `variant_code`
  - [x] T4.3 Implémenter `NatalInterpretationServiceV2._generate_free_short()`
  - [x] T4.4 Gérer la persistence du `variant_code` dans la DB

- [x] T5 — Tests d'intégration (AC6)
  - [x] T5.1 Créer `backend/app/tests/integration/test_natal_free_short_variant.py`
  - [x] T5.2 Vérifier que l'appel `/v1/natal/interpretation` avec `level=complete` pour un user free utilise bien le prompt restreint

## Dev Agent Record

### File List
- `backend/scripts/seed_product_entitlements.py`: Activation de `natal_chart_long` pour le plan free.
- `backend/app/prompts/catalog.py`: Ajout du prompt `natal_long_free` et de son schéma.
- `backend/.env.example`: Ajout de la config moteur pour le nouveau prompt.
- `backend/app/infra/db/models/user_natal_interpretation.py`: Ajout de la colonne `variant_code` et mise à jour des index.
- `backend/app/services/natal_interpretation_service_v2.py`: Implémentation de la logique de génération restreinte.
- `backend/app/api/v1/routers/natal_interpretation.py`: Transmission du `variant_code` du gate vers le service.
- `backend/app/tests/integration/test_natal_free_short_variant.py`: Test d'intégration du flux complet.

### Change Log
- Passage du plan free d'un accès bloqué à un accès restreint (variant `free_short`) pour le thème natal long.
- Ajout du support de la persistence des variants d'interprétation dans la base de données.
- Implémentation d'un flux de génération spécifique pour le variant free, garantissant un format compatible `AstroResponseV1` tout en étant issu d'un prompt dédié plus léger.
- Validation par test d'intégration avec mock du gateway LLM.
- Stabilisation post-intégration :
  - normalisation du payload persisté `free_short` pour qu'il reste relu comme une interprétation logique `complete` côté API ;
  - mapping fiable des titres de sections depuis `accordion_titles` pour conserver le contrat frontend attendu.
