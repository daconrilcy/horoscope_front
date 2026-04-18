# Travail différé (stories 67–69)

**Statut : done** (clos le 2026-04-18 ; revues de cohérence facettes / `live_execution` intégrées ensuite).

Les points listés précédemment dans ce fichier ont été pris en charge dans le code applicatif :

1. **Placeholders hors registre** — `assembly_preview` : `unknown` (signal contrat) ; `runtime_preview` et `live_execution` : `blocking_missing` (même sémantique runtime, `admin_llm.py`).
2. **Payload `resolved` partiel (graphe logique admin)** — `buildLogicGraphProjection` tolère champs ou listes absents (`frontend/src/pages/admin/AdminPromptsPage.tsx`).
3. **Double chargement catalogue onglet samples** — requête catalogue **sans filtres** dédiée à l’onglet « Échantillons runtime » pour les facettes (référentiel global), distincte du catalogue filtré de l’onglet Catalogue (`AdminPromptsPage.tsx`, `AdminSamplePayloadsAdmin.tsx`).
4. **`anonymize_text` exécution manuelle** — garde-fou dédié `_anonymize_for_admin_manual_execute` avec repli `[anonymization_unavailable]` (`admin_llm.py`, test unitaire).
5. **Mutation manuelle `isSuccess` sans `data`** — message d’avertissement affiché (`AdminPromptsPage.tsx`).

---

## Non-régression tests (2026-04-18)

Suite à l’implémentation, les tests d’intégration backend et Vitest frontend ont été réalignés pour refléter le comportement actuel (gateway, release snapshots, admin sample payloads, UI Aide / admin).

**Backend** (`backend/tests/integration/`)

| Fichier | Ajustement principal |
|--------|------------------------|
| `test_email_unsubscribe.py` | Session alignée sur l’app via `get_db_session` ; emails uniques ; JWT expiré signé avec `settings.jwt_secret_key`. |
| `test_admin_llm_sample_payloads.py` | Round-trip : clé payload sans segment `user` (règle `classify_field` / sample payloads admin). |
| `test_llm_release.py` | `_ensure_published_assembly_for_release_snapshots` avant `build_snapshot` ; promotion sync avant le test async d’activation. |
| `test_story_66_22_provider_locking.py` | Exception `GatewayConfigError` ; mocks assembly sans `MagicMock` sur métadonnées snapshot. |
| `test_story_66_25_observability.py` | Plan avec `assembly_id` + `execution_profile_source` pour `CANONICAL_ASSEMBLY`. |
| `test_story_66_29_extinction.py` | `AsyncMock` sur `_resolve_config` ; repair : `execute_request` imbriqué court-circuité pour l’assertion fallback. |
| `test_story_66_30_suppression.py` | `SimpleNamespace` pour `execution_config` ; patch `_resolve_config` pour éviter le fallback `resolve_model`. |
| `test_story_66_21_governance.py` | Suppression du bruit `DeprecationWarning` sur `LLMNarrator` (chemin legacy volontaire). |

**Documentation** — `docs/llm-prompt-generation-by-feature.md` : section « Maintenance de cette documentation » et références explicites `_resolve_plan()`, `execute_request()`, `_build_messages()`, `_call_provider()` pour les contrôles 66.26.

**Frontend**

| Fichier | Ajustement principal |
|--------|------------------------|
| `AdminPage.test.tsx` | Après redirect `/admin/personas` → `/admin/prompts/personas`, vérifie le chemin et le panneau personas (`personas-admin-title`), pas le catalogue (story 70.1). |
| `HelpPage.test.tsx` | Plusieurs boutons « Ouvrir un ticket support » : `getAllByRole` + `length > 0`. |

**Vérification** : `pytest` (backend, venv activé) et `npm run test` (frontend) au vert.

Pour de nouveaux reports de revue, réutiliser ce fichier ou en créer un suivant la convention d’équipe.

---

## Deferred from: code review of 70-4-rendre-le-schema-visuel-des-processus-llm-avec-react-flow.md (2026-04-18)

- **Couverture tests accessibilité clavier** (zoom/pan React Flow, critère « compatible clavier » de la story) — aucun test automatisé ajouté ; à couvrir par smoke manuel admin ou story QA dédiée.
- **Churn `package-lock.json`** (d3, zustand, `devOptional` sur `@types/react`) — surveiller build CI et `npm audit` après merge de `@xyflow/react`.

## Deferred from: code review of 70-2-refaire-le-catalogue-canonique-en-mode-master-detail (2026-04-18)

- **Fichier `AdminPromptsPage.tsx` déjà volumineux** — dette structurelle (extraction composants catalogue) hors périmètre strict de la story 70.2 ; à traiter si refactor dédié.
