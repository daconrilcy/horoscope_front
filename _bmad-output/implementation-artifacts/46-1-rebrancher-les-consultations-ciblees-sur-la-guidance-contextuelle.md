# Story 46.1: Rebrancher les consultations ciblées sur la guidance contextuelle

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend/backend integrator,
I want faire de la guidance contextuelle existante la source de vérité des consultations ciblées,
so that les parcours `dating`, `pro`, `event` et `free` restent utiles après la suppression des tirages sans retomber sur une interprétation natale hors sujet.

## Acceptance Criteria

1. Le parcours de génération des consultations n'utilise plus `useExecuteModule()` ni les endpoints `/v1/chat/modules/*` pour produire le résultat d'une consultation.
2. Le frontend appelle `POST /v1/guidance/contextual` avec un payload cohérent contenant au minimum `situation` et `objective`, et `time_horizon` si l'utilisateur l'a fourni.
3. Le mapping des types de consultation reste fonctionnel:
   - `dating` produit un objectif orienté relation/amour
   - `pro` produit un objectif orienté décision ou évolution professionnelle
   - `event` produit un objectif lié à l'événement saisi
   - `free` laisse l'objectif libre sans contrainte arbitraire
4. Le résultat d'une consultation ciblée n'utilise plus comme fallback l'interprétation du thème natal via `/v1/users/me/natal-chart/latest?include_interpretation=true`.
5. Le contrat frontend introduit un client API dédié et centralisé pour la guidance contextuelle, avec gestion uniforme des états `loading`, `error` et des enveloppes d'erreur backend.
6. Les routes `/consultations`, `/consultations/new` et `/consultations/result` restent inchangées et les deep links existants continuent de fonctionner.
7. Les tests frontend couvrent au minimum la génération réussie d'une consultation ciblée, l'erreur backend et l'absence de dépendance résiduelle à `useExecuteModule()` dans le flux consultations.

## Tasks / Subtasks

- [x] Task 1: Stabiliser la cible technique de génération (AC: 1, 2, 3, 4)
  - [x] Analyser le flux actuel dans `frontend/src/pages/ConsultationResultPage.tsx` et documenter précisément les deux branches à remplacer: `tarot/runes` et fallback natal
  - [x] Confirmer le contrat disponible dans `backend/app/api/v1/routers/guidance.py` et `backend/app/services/guidance_service.py`
  - [x] Définir la table de mapping produit entre `ConsultationType` et `objective` par défaut
  - [x] Définir la stratégie de composition de `situation`, `objective` et `time_horizon` à partir du draft consultation

- [x] Task 2: Introduire un client frontend dédié pour `guidance_contextual` (AC: 2, 5)
  - [x] Ajouter un appel centralisé dans `frontend/src/api/` au lieu d'un `fetch` inline dans `ConsultationResultPage`
  - [x] Réutiliser les conventions d'auth et de gestion d'erreur déjà présentes dans les clients frontend
  - [x] Typiser la réponse attendue à partir du contrat backend `ContextualGuidanceApiResponse`
  - [x] Prévoir un mapping explicite des erreurs `404`, `422`, `503` vers des messages UI lisibles

- [x] Task 3: Rebrancher la génération de résultat des consultations (AC: 1, 2, 3, 4, 6)
  - [x] Remplacer l'appel `useExecuteModule()` dans le flux consultations par le nouveau client contextual guidance
  - [x] Supprimer le fallback natal dans ce flux
  - [x] Préserver le garde-fou qui redirige vers `/consultations/new` si le draft est incomplet
  - [x] Vérifier que la page résultat continue de charger un historique sauvegardé via `?id=...`

- [x] Task 4: Préparer le contrat transitoire côté résultat sans casser les stories suivantes (AC: 3, 5, 6)
  - [x] Introduire un mapping temporaire ou final entre la réponse guidance et le modèle `ConsultationResult`
  - [x] Conserver la compatibilité des composants actuels jusqu'à la story 46.2
  - [x] Isoler la logique de mapping pour éviter une deuxième réécriture quand le modèle consultation sera nettoyé

- [x] Task 5: Tester le rebranchement et verrouiller la non-régression (AC: 1, 5, 6, 7)
  - [x] Ajouter un test de génération `dating`
  - [x] Ajouter un test d'erreur backend contextual guidance
  - [x] Ajouter un test explicitement centré sur l'absence d'appel à `useExecuteModule()` dans le parcours consultations
  - [x] Vérifier que le résultat reste accessible via historique ou deep link `?id=...`

## Dev Notes

- Le point de casse principal est déjà identifié: `frontend/src/pages/ConsultationResultPage.tsx` appelle aujourd'hui soit `useExecuteModule()`, soit une récupération d'interprétation natale qui n'est pas contextuelle.
- Cette story ne retire pas encore les types `drawingOption` ni le rendu des cartes/runes. Elle établit d'abord la bonne source de vérité métier afin que la suppression UI ultérieure ne casse pas la génération.
- La guidance contextuelle existe déjà et doit être réutilisée. Ne pas créer de nouvel endpoint ni dupliquer la logique métier.
- Le meilleur point d'appui historique est la story 3.5 pour la guidance contextuelle et la story 15.3 pour la migration des services vers l'AI engine.

### Previous Story Intelligence

- Story 16.5 a déjà centralisé `CHAT_PREFILL_KEY`, `AUTO_ASTROLOGER_ID`, `WIZARD_STEP_LABELS` et le store consultation. Il faut les réutiliser et non les contourner.
- Story 16.5 a aussi supprimé une duplication précédente de logique localStorage. Toute nouvelle API consultation doit rester minimale et ne pas recréer un faux repository local parallèle.
- Story 45.1 impose explicitement que les deep links `/consultations` restent stables.

### Project Structure Notes

- Frontend à toucher en priorité:
  - `frontend/src/pages/ConsultationResultPage.tsx`
  - `frontend/src/api/`
  - `frontend/src/tests/`
- Backend de référence à consommer sans modification structurelle majeure:
  - `backend/app/api/v1/routers/guidance.py`
  - `backend/app/services/guidance_service.py`

### Technical Requirements

- Aucun `fetch` inline nouveau ne doit être introduit dans `ConsultationResultPage.tsx`; le client doit être centralisé.
- Le mapping `ConsultationType -> objective` doit être explicite et testable, pas enfoui dans le composant.
- La story doit rester additive vis-à-vis du futur nettoyage du modèle consultation. Il faut éviter de lier le nouveau flux à `drawingOption`.
- Les enveloppes d'erreur backend de type `{ error: { code, message, details } }` doivent être respectées.

### Architecture Compliance

- Réutiliser le service existant `guidance_contextual` au lieu d'un nouveau use case.
- Maintenir la séparation `api client` / `page logic` / `store`.
- Garder le contrat de route existant du frontend.

### Testing Requirements

- Frontend: tests de succès, erreur et historique.
- Si des tests backend sont ajoutés, ils doivent rester focalisés sur le contrat `/v1/guidance/contextual` et non réintroduire tarot/runes.
- Vérifier que les mocks ne continuent pas à stubber `useExecuteModule()` dans les tests du parcours consultations.

### References

- [Source: frontend/src/pages/ConsultationResultPage.tsx]
- [Source: frontend/src/pages/ConsultationWizardPage.tsx]
- [Source: frontend/src/types/consultation.ts]
- [Source: frontend/src/state/consultationStore.tsx]
- [Source: frontend/src/api/chat.ts]
- [Source: backend/app/api/v1/routers/guidance.py]
- [Source: backend/app/services/guidance_service.py]
- [Source: _bmad-output/implementation-artifacts/16-5-consultations-pages.md]
- [Source: _bmad-output/implementation-artifacts/45-1-refondre-le-routing-dashboard-et-isoler-la-page-horoscope-detaillee.md]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- ConsultationReconnection.test.tsx created to verify AC1, AC2, AC5, AC7.
- Centralized mapping added to types/consultation.ts.
- getObjectiveForType used in ConsultationResultPage.tsx.

### Completion Notes List

- Replaced useExecuteModule and natal fallback with useContextualGuidance in ConsultationResultPage.tsx.
- Created dedicated guidance API client in frontend/src/api/guidance.ts.
- Mapped ConsultationType to localized objectives in types/consultation.ts.
- Preserved transitional compatibility by keeping dummy drawing data for now.
- Verified non-regression of history loading and deep links.

### File List

- frontend/src/api/guidance.ts
- frontend/src/i18n/consultations.ts
- frontend/src/pages/ConsultationResultPage.tsx
- frontend/src/types/consultation.ts
- frontend/src/tests/ConsultationReconnection.test.tsx
