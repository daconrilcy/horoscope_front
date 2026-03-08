# Story 38.2 : Internationalisation et cohérence stylistique éditoriale

Status: done

## Story

As a développeur de l'application horoscope,
I want des templates éditoriaux disponibles en FR et EN avec une charte rédactionnelle stable,
so that la même structure de template est réutilisée dans les deux langues sans dupliquer de logique, et que les labels UI s'affichent correctement quelle que soit la langue de l'utilisateur.

## Acceptance Criteria

### AC1 — Structure identique entre FR et EN

[x] Les templates EN dans `backend/app/prediction/editorial_templates/en/` sont des miroirs structurels exacts des templates FR : mêmes noms de fichiers, mêmes placeholders, mêmes sections.

### AC2 — Seules les chaînes changent entre les langues

[x] Aucune logique conditionnelle ou calculatoire n'est dupliquée entre les dossiers `fr/` et `en/`. Un diff structurel entre les deux dossiers ne révèle que des différences de libellés.

### AC3 — Aucune logique calculatoire dans la couche i18n

[x] Le fichier `frontend/src/i18n/predictions.ts` ne contient que des dictionnaires de traduction (Record). Toute logique de sélection de label reste dans le composant appelant.

### AC4 — Charte rédactionnelle documentée

[x] Le fichier `docs/editorial/charte-redactionnelle.md` documente le ton, le registre, la longueur cible des textes, et les niveaux de certitude attendus pour chaque type de template.

### AC5 — Labels catégories et bandes disponibles en FR et EN dans le frontend

[x] `frontend/src/i18n/predictions.ts` exporte `CATEGORY_LABELS`, `NOTE_BAND_LABELS`, `TONE_LABELS` et `PIVOT_LABELS` utilisables directement par les composants React avec un paramètre `lang: 'fr' | 'en'`.

## Tasks / Subtasks

### T1 — Créer les templates EN miroirs du FR (AC1, AC2) — ARCHITECTURE UNIFIÉE

- [x] Créer le dossier `backend/app/prediction/editorial_templates/en/`
- [x] Créer les 6 templates EN en miroir des templates FR (mêmes noms, même extension `.txt`) :
  - [x] `intro_du_jour.txt` — même placeholders que FR
  - [x] `resume_categorie.txt` — mêmes placeholders
  - [x] `phrase_pivot.txt` — mêmes placeholders
  - [x] `meilleure_fenetre.txt` — mêmes placeholders
  - [x] `prudence_sante.txt` — "Pay particular attention to your health today."
  - [x] `prudence_argent.txt` — "Exercise caution in financial matters; consider postponing major commitments."
- [x] Vérifier que chaque template EN contient exactement les mêmes placeholders que son équivalent FR

### T2 — Créer la charte rédactionnelle (AC4)

- [x] Créer `docs/editorial/charte-redactionnelle.md` avec toutes les sections requises (Ton, Registre, Longueur, Certitude, Prudence, Exemples).

### T3 — Créer `frontend/src/i18n/predictions.ts` (AC3, AC5)

- [x] Créer `frontend/src/i18n/predictions.ts` avec les exports `CATEGORY_LABELS`, `NOTE_BAND_LABELS`, `TONE_LABELS` et `PIVOT_LABELS`.
- [x] Implémenter le helper `getLabel` avec fallback.
- [x] Vérifier que le fichier ne contient aucune logique conditionnelle.

### T4 — Tests unitaires backend i18n (AC1, AC2, AC5)

- [x] Créer `backend/app/tests/unit/test_editorial_i18n.py`
- [x] `test_fr_en_same_placeholders` — vérification automatique de l'égalité des placeholders
- [x] `test_no_calculatory_logic_in_templates` — vérification de l'absence de code dans les templates
- [x] `test_engine_selects_correct_lang` — validation du switch FR/EN dans le moteur

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Backend tests pass: `3 passed in 0.07s`
- Frontend lint pass: `npm run lint` (tsc checks)

### Completion Notes List
- Création des templates éditoriaux EN en miroir des templates FR.
- Rédaction de la charte rédactionnelle complète dans `docs/editorial/charte-redactionnelle.md`.
- Implémentation de la couche i18n frontend dans `frontend/src/i18n/predictions.ts`.
- Mise à jour de `EditorialTemplateEngine` pour supporter les libellés EN (catégories, tons, sévérités).
- Ajout de tests unitaires backend validant l'intégrité de l'i18n des templates.
- 2026-03-08: correctif UX complémentaire — humanisation frontend des résumés de pivots techniques (`delta_note`, `top3_change`, `high_priority_event`) et des labels de drivers pour éviter l'exposition de codes internes dans `TodayPage`.

### File List

- `backend/app/prediction/editorial_templates/en/intro_du_jour.txt`
- `backend/app/prediction/editorial_templates/en/resume_categorie.txt`
- `backend/app/prediction/editorial_templates/en/phrase_pivot.txt`
- `backend/app/prediction/editorial_templates/en/meilleure_fenetre.txt`
- `backend/app/prediction/editorial_templates/en/prudence_sante.txt`
- `backend/app/prediction/editorial_templates/en/prudence_argent.txt`
- `docs/editorial/charte-redactionnelle.md`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `backend/app/prediction/editorial_template_engine.py` (modifié)
- `backend/app/tests/unit/test_editorial_i18n.py`
- `frontend/src/tests/TodayPage.test.tsx`

## Change Log

- 2026-03-08: Story créée pour Epic 38.
- 2026-03-08: Implémentation complète de l'i18n éditorial (EN templates, frontend i18n, charte).
- 2026-03-08: Correctif d'affichage `TodayPage` — les libellés techniques de pivots et drivers sont désormais rendus en texte utilisateur lisible.
