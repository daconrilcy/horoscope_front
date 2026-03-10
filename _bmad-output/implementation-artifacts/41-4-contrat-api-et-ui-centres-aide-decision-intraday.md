# Story 41.4 : Contrat API et UI centrés sur l'aide à la décision intraday

Status: done

## Story

En tant qu'utilisateur consultant `/dashboard`,
je veux voir quelques fenêtres claires avec des libellés actionnables et des drivers humanisés,
afin de comprendre rapidement à quels moments de la journée lancer une action, prendre une décision ou rester prudent.

## Acceptance Criteria

### AC1 — Le contrat API expose des fenêtres lisibles

- [x] Le payload `/v1/predictions/daily` expose un champ lisible et stable pour les fenêtres décisionnelles
- [x] Les drivers techniques ne remontent plus tels quels dans le contrat utilisateur final

### AC2 — `TodayPage` met en avant l'aide à la décision

- [x] L'UI affiche en priorité 3 à 6 fenêtres maximum
- [x] Chaque fenêtre présente une période, un ton actionnable, des domaines clés et un message utile
- [x] La hiérarchie visuelle distingue clairement `moment fort`, `prudence`, `fenêtre favorable`

### AC3 — La timeline détaillée devient secondaire

- [x] La chronologie complète peut rester disponible, mais elle n'est plus la vue principale du produit
- [x] Les répétitions techniques sont masquées ou condensées

### AC4 — Les libellés sont entièrement humanisés

- [x] Aucun label technique type `enter_orb` n'est visible dans le rendu final
- [x] Les drivers affichés sont limités aux éléments vraiment utiles à l'utilisateur

### AC5 — Les tests frontend sont réalignés

- [x] Les tests `TodayPage` et composants prediction couvrent les nouvelles fenêtres et le rendu orienté décision

## Tasks / Subtasks

### T1 — Étendre les types backend/front

- [x] Ajouter les types API/TS nécessaires pour les fenêtres décisionnelles
- [x] Préserver la compatibilité des consommateurs existants si nécessaire

### T2 — Revoir la présentation de `TodayPage`

- [x] Créer ou adapter les composants de fenêtres décisionnelles
- [x] Réduire le poids visuel de la timeline brute

### T3 — Humaniser complètement les drivers

- [x] Étendre `predictionI18n`
- [x] Filtrer les drivers de faible valeur produit

### T4 — Tests

- [x] Mettre à jour `TodayPage.test.tsx`
- [x] Ajouter des tests ciblés sur les nouveaux composants si nécessaire

## Dev Notes

- Cette story dépend du contrat backend produit par 41.3.
- Le but n'est pas seulement esthétique: l'information affichée doit devenir plus utile, plus rare et mieux hiérarchisée.

### Fichiers probables à toucher

- `backend/app/api/v1/routers/predictions.py`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/pages/TodayPage.tsx`
- `frontend/src/components/prediction/*`
- `frontend/src/utils/predictionI18n.ts`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- AC1 backend : le contrat `decision_windows` (type + score + confidence + dominant_categories) était déjà exposé par 41.3 dans `predictions.py`. Aucune modification backend nécessaire.
- `AdminPage.test.tsx` : 1 test pré-existant en échec (non lié à cette story, confirmé par `git stash` avant/après).

### Completion Notes List

- **T1** : Ajouté `DailyPredictionDecisionWindow` interface et champ `decision_windows?: DailyPredictionDecisionWindow[] | null` dans `DailyPredictionResponse` (frontend/src/types/dailyPrediction.ts). Compat ascendante préservée (champ optionnel).
- **T2** : Créé `DecisionWindowsSection.tsx` — affiche jusqu'à 6 fenêtres triées, badge coloré par type (favorable=vert, prudence=jaune, pivot=violet), message actionnable, domaines dominants avec icônes. `TodayPage.tsx` : `DecisionWindowsSection` en position prioritaire (avant CategoryGrid), `DayTimeline` déplacée dans un `<details>` pliable.
- **T3** : Étendu `predictionI18n.ts` — ajouté labels pour `decision_windows_title`, `window_type_*`, `window_msg_*` (fr+en) ; ajouté humanisation des event_types V2 : `aspect_exact_to_angle`, `aspect_exact_to_luminary`, `aspect_exact_to_personal`, `aspect_enter_orb`, `aspect_exit_orb`, `moon_sign_ingress`, `asc_sign_change` ; suppression du fallback `return eventType` qui exposait les codes techniques.
- **T4** : Ajouté 4 nouveaux tests TodayPage (decision_windows affichées, labels humanisés, nouveaux event_type V2, timeline secondaire dans `<details>`). 10/10 tests TodayPage passent. 1121/1122 tests totaux passent (1 régression pré-existante AdminPage non liée).
- **Post-validation 2026-03-09** : Le backend reconstruit désormais `decision_windows` depuis les données persistées quand une prédiction est réutilisée depuis le cache/DB (`was_reused=true`). Le contrat `/v1/predictions/daily` reste donc stable pour `/dashboard` même sans `engine_output` en mémoire.
- **Post-validation 2026-03-09** : Le démarrage local SQLite répare le schéma et ré-amorce la référence/ruleset `2.0.0` si nécessaire, ce qui supprime les erreurs locales `version_missing`/`ruleset_missing` qui bloquaient le chargement du dashboard.
- **Post-validation 2026-03-10** : Le message de calibration provisoire affiché sur `/dashboard` reprend désormais `summary.calibration_note` quand elle existe, au lieu d'un warning frontend générique plus alarmiste.
- **Post-validation 2026-03-10** : Les libellés utilisateur ont été clarifiés (`Moments charnières`, `Transition à surveiller`, badge `Changement`) pour éviter l'ambiguïté de "moment de bascule".
- **Post-validation 2026-03-10** : Les blocs positifs ou prudents restent étiquetés `favorable` / `prudence` même s'ils démarrent sur un pivot ; seules les transitions neutres restent `pivot`, et elles sont limitées à 90 minutes maximum pour éviter les créneaux de bascule artificiellement longs.
- **Post-validation 2026-03-10** : La timeline API marque désormais un `turning_point` sur l'intervalle demi-ouvert `[start, end)`, ce qui supprime le double marquage des deux blocs adjacents autour d'une même heure de pivot.
- **Post-validation 2026-03-10** : En dev local, `/v1/predictions/daily` déclenche aussi une auto-réparation si la référence `2.0.0` existe mais reste partiellement seedée ; cela supprime les erreurs `compute_failed` qui empêchaient encore le chargement du dashboard.

### File List

- `frontend/src/types/dailyPrediction.ts` (modifié — ajout DailyPredictionDecisionWindow + champ decision_windows)
- `frontend/src/components/prediction/DecisionWindowsSection.tsx` (nouveau)
- `frontend/src/pages/TodayPage.tsx` (modifié — ajout DecisionWindowsSection, timeline dans details)
- `frontend/src/utils/predictionI18n.ts` (modifié — labels window_type/msg + event_type V2)
- `frontend/src/tests/TodayPage.test.tsx` (modifié — 4 nouveaux tests)
- `backend/app/prediction/decision_window_builder.py` (modifié — transitions pivot limitées et reclassement positif/négatif)
- `backend/app/api/v1/routers/predictions.py` (modifié — marquage demi-ouvert des turning points dans la timeline)
- `backend/app/services/daily_prediction_service.py` (modifié — auto-heal local sur contexte prédictif partiellement seedé)
- `_bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md` (modifié — statuts AC/tâches)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié — statut story)

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
- 2026-03-09 : Implémentation complète — types TS, DecisionWindowsSection, TodayPage redesign (decision windows prioritaires, timeline en details), humanisation event_type V2, 4 nouveaux tests TodayPage (10/10 pass). (claude-sonnet-4-6)
- 2026-03-09 : Validation finale de l'épic en environnement local réel — correction de la reconstruction des `decision_windows` sur runs réutilisés et auto-réparation du seed `reference/ruleset 2.0.0` pour rétablir `/dashboard`. (Codex)
- 2026-03-10 : Post-validation UX/runtime — calibration note backend priorisée dans l'UI, renommage des pivots utilisateur, limitation des transitions `pivot` à 90 min, marquage timeline corrigé et auto-heal local du contexte prédictif pour supprimer les `compute_failed` sur `/dashboard`. (Codex)
