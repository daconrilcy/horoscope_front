# Travail différé (stories 67–69)

**Statut : done** (clos le 2026-04-18 ; revues de cohérence facettes / `live_execution` intégrées ensuite).

Les points listés précédemment dans ce fichier ont été pris en charge dans le code applicatif :

1. **Placeholders hors registre** — `assembly_preview` : `unknown` (signal contrat) ; `runtime_preview` et `live_execution` : `blocking_missing` (même sémantique runtime, `admin_llm.py`).
2. **Payload `resolved` partiel (graphe logique admin)** — `buildLogicGraphProjection` tolère champs ou listes absents (`frontend/src/pages/admin/AdminPromptsPage.tsx`).
3. **Double chargement catalogue onglet samples** — requête catalogue **sans filtres** dédiée à l’onglet « Échantillons runtime » pour les facettes (référentiel global), distincte du catalogue filtré de l’onglet Catalogue (`AdminPromptsPage.tsx`, `AdminSamplePayloadsAdmin.tsx`).
4. **`anonymize_text` exécution manuelle** — garde-fou dédié `_anonymize_for_admin_manual_execute` avec repli `[anonymization_unavailable]` (`admin_llm.py`, test unitaire).
5. **Mutation manuelle `isSuccess` sans `data`** — message d’avertissement affiché (`AdminPromptsPage.tsx`).

Pour de nouveaux reports de revue, réutiliser ce fichier ou en créer un suivant la convention d’équipe.
