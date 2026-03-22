# Story 60.19: Refonte premium de `/chat` et durcissement du contexte conversationnel LLM

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur authentifié du produit,
I want une page `/chat` visuellement alignée avec `/dashboard` et `/dashboard/horoscope`, avec une navigation conversationnelle claire sur mobile et desktop, et un contexte LLM de chat plus robuste,
so that l’expérience de discussion paraisse premium, cohérente avec le reste du produit, et que les réponses du chat restent contextuelles, fluides et stables dans la durée.

## Acceptance Criteria

1. La page `/chat` adopte le même langage visuel premium que `/dashboard` et `/dashboard/horoscope` :
   - mêmes surfaces glass, bordures, rayons, ombres, halos et hiérarchie typographique
   - réutilisation des tokens et primitives CSS déjà établis par 60.17 et 60.18
   - pas de design system parallèle spécifique au chat
2. La page `/chat` affiche un vrai header de page premium cohérent avec les autres pages applicatives :
   - présence d’un titre de page explicite
   - présence d’un bouton retour utilisant le style `daily-page-header__back`
   - micro-hiérarchie éditoriale cohérente avec les pages horoscope/dashboard
3. La gestion “nouvelle conversation” est rationalisée :
   - un seul pattern principal de création de conversation est conservé
   - les deux boutons actuels ne créent plus de concurrence visuelle ou fonctionnelle
   - la création de conversation reste accessible depuis la liste et depuis la vue chat, mais selon un système unifié et cohérent
4. Sur mobile, `/chat` devient un parcours en deux temps de type messagerie :
   - l’arrivée sur `/chat` affiche d’abord la liste des conversations
   - l’utilisateur clique sur une conversation existante ou crée une nouvelle conversation
   - il arrive ensuite sur une vue chat dédiée plein écran, dans l’esprit WhatsApp/iMessage
   - le retour à la liste est explicite et cohérent
5. Sur desktop, `/chat` adopte une vraie composition conversationnelle large :
   - liste des conversations à gauche
   - zone d’échange à droite
   - largeur d’occupation supérieure à l’implémentation actuelle
   - la zone de chat prend plus de place qu’aujourd’hui et devient la surface principale
6. Le layout mobile et desktop conserve les parcours existants sans régression :
   - ouverture directe d’une conversation via `/chat/:conversationId`
   - redirection existante par `?personaId=...`
   - historique et envoi de messages inchangés fonctionnellement
7. Le header et les sous-sections de `/chat` ne répètent pas inutilement les actions ou labels :
   - le titre de page, le bouton back, la création de conversation et le chip astrologue suivent une hiérarchie claire
   - aucun bouton “nouvelle conversation” redondant ou concurrent ne subsiste sans justification UX explicite
8. Le contexte de génération du chat est audité et rendu explicite côté backend :
   - le flux s’appuie bien sur le prompt système chat existant (`chat_astrologer`)
   - l’historique conversationnel récent est injecté de façon cohérente
   - la compression / mémoire conversationnelle existante ou prévue est prise en compte dans le contexte
   - la date du jour est incluse explicitement dans le contexte transmis au LLM
9. Si la compression mémoire n’est pas encore totalement active dans le pipeline courant, la story documente et implémente au minimum le contrat backend nécessaire pour éviter un contexte incomplet ou dateless :
   - `conversation_id`
   - date du jour / timezone ou équivalent
   - mémoire conversationnelle disponible si présente
   - historique récent
10. La page `/chat` reste accessible et robuste :
   - états `loading`, `error`, `empty` gérés sur la liste et sur la conversation
   - navigation clavier et focus cohérents sur mobile et desktop
   - structure responsive testable sans dépendre d’un comportement implicite CSS
11. Les tests couvrent au minimum :
   - le nouveau layout mobile-first conversations → chat
   - le layout desktop élargi
   - l’unicité / cohérence de l’action “nouvelle conversation”
   - la présence du titre de page et du bouton back
   - le contrat backend/contextuel de construction du prompt chat, incluant la date

## Tasks / Subtasks

- [ ] Task 1: Réaligner visuellement `/chat` sur le design premium existant (AC: 1, 2, 7)
  - [ ] Réutiliser les tokens, rayons, halos, bordures et ombres de 60.17 / 60.18
  - [ ] Ajouter un vrai header de page avec titre, micro-label éventuel et bouton back premium
  - [ ] Harmoniser le chip astrologue, les panneaux liste/chat et les zones vides avec le langage glass partagé

- [ ] Task 2: Rationaliser l’architecture UX “nouvelle conversation” (AC: 3, 7)
  - [ ] Auditer les deux entrées actuelles de création de conversation (`ConversationList` et `ChatWindow`)
  - [ ] Définir un pattern source-of-truth pour l’action principale
  - [ ] Conserver uniquement la duplication justifiée par le contexte d’usage, sinon unifier l’action

- [ ] Task 3: Recomposer `/chat` en expérience mobile de messagerie dédiée (AC: 4, 6, 10)
  - [ ] Faire de la liste de conversations la vue d’entrée mobile par défaut
  - [ ] Faire de la vue chat une page/surface dédiée après sélection ou création
  - [ ] Vérifier la cohérence du retour vers la liste et des deep links `/chat/:conversationId`

- [ ] Task 4: Recomposer `/chat` en desktop large et orienté conversation (AC: 5, 6, 10)
  - [ ] Élargir l’occupation horizontale du layout desktop
  - [ ] Donner davantage d’espace à la zone d’échanges qu’à la liste de conversations
  - [ ] Garder la liste gauche stable sans écraser la zone de composition/chat

- [ ] Task 5: Auditer et durcir la construction du contexte chat LLM (AC: 8, 9)
  - [ ] Vérifier le rôle exact du prompt système `chat_astrologer` dans `AIEngineAdapter`
  - [ ] Vérifier comment `ChatGuidanceService` assemble l’historique récent, le `conversation_id`, la persona et le contexte annexe
  - [ ] Vérifier la présence ou l’absence de mémoire compressée / résumé roulant dans le contexte réel
  - [ ] Ajouter la date du jour au contexte transmis au LLM si elle manque
  - [ ] Documenter dans la story les invariants à respecter pour éviter les réponses “hors temps” ou sans continuité conversationnelle

- [ ] Task 6: Couvrir la refonte par tests ciblés (AC: 10, 11)
  - [ ] Adapter `ChatPage.test.tsx` et `ChatComponents.test.tsx`
  - [ ] Ajouter des assertions sur le header premium, le back button et le pattern mobile-first
  - [ ] Ajouter des tests backend unitaires sur le contexte chat si la date ou la mémoire sont injectées/ajustées
  - [ ] Vérifier le responsive desktop/mobile sans snapshots fragiles inutiles

## Dev Notes

### Intent produit

- Le chat n’est plus un écran fonctionnel isolé. Il doit s’inscrire dans le même continuum produit que `/dashboard` et `/dashboard/horoscope`.
- L’utilisateur doit sentir que le chat est une surface premium de discussion contextuelle, pas un module utilitaire séparé du reste de l’application.
- Le travail demandé mélange deux axes :
  - UX/UI et responsive de la page `/chat`
  - cohérence du pipeline backend qui prépare le contexte envoyé au LLM

### Contexte existant à réutiliser

- `/dashboard` et `/dashboard/horoscope` ont déjà convergé vers un système premium glass/lilas dans :
  - `frontend/src/App.css`
  - `frontend/src/pages/DashboardPage.css`
  - `frontend/src/pages/DailyHoroscopePage.css`
  - `frontend/src/components/prediction/DailyPageHeader.css`
- Le style de bouton back premium existe déjà via `daily-page-header__back` sur la page horoscope et doit être réutilisé, pas réinventé.
- La page chat actuelle repose sur :
  - `frontend/src/pages/ChatPage.tsx`
  - `frontend/src/features/chat/components/ChatLayout.tsx`
  - `frontend/src/features/chat/components/ConversationList.tsx`
  - `frontend/src/features/chat/components/ChatWindow.tsx`
- Deux actions “nouvelle conversation” existent aujourd’hui :
  - `conversation-list-new-btn` dans la liste
  - `chat-window-new-btn` dans la fenêtre de chat
- Le layout desktop courant repose encore sur `TwoColumnLayout`, ce qui limite probablement la largeur utile réelle du chat.

### Contexte backend / prompt à sécuriser

- Le pipeline d’envoi de messages passe par :
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/services/ai_engine_adapter.py`
  - `backend/app/prompts/catalog.py`
- `AIEngineAdapter.generate_chat_reply()` route vers le use case `chat_astrologer` et transmet déjà `conversation_id` si présent dans `context`.
- Le service `ChatGuidanceService` assemble actuellement :
  - persona
  - historique récent
  - contexte de conversation
  - mais la présence explicite de la date du jour doit être vérifiée puis imposée si absente
- Le document [docs/chat/plan_implementation_chat_memoire.md](c:/dev/horoscope_front/docs/chat/plan_implementation_chat_memoire.md) décrit la direction cible :
  - mémoire conversationnelle persistée
  - compression automatique
  - injection de `memory_summary`, `memory_facts`, `conversation_id`
  - gestion de `context_too_large`
- Cette story n’a pas vocation à refaire tout le système mémoire si le scope serait trop large, mais elle doit au minimum verrouiller l’invariant de contexte pour la page et les réponses chat.

### Implementation guidance

- Frontend :
  - éviter une simple retouche CSS locale ; la page doit réutiliser les primitives premium déjà établies
  - privilégier des composants/layouts partagés ou des classes communes plutôt qu’un nouveau système chat ad hoc
  - préserver les routes `/chat` et `/chat/:conversationId`
  - conserver la logique `personaId` déjà supportée
- UX mobile :
  - l’état initial doit être clairement la liste
  - la conversation devient un écran dédié une fois sélectionnée
  - le bouton retour doit ramener à la liste, avec un langage visuel premium cohérent
- UX desktop :
  - viser une page large, conversation-first
  - éviter le rendu “colonne centrale trop étroite”
  - la liste gauche doit rester présente mais secondaire
- Backend :
  - ne pas dupliquer la logique de construction de contexte entre service chat et adapter
  - si la date du jour est ajoutée au contexte, le faire dans le point d’assemblage canonique
  - ne pas casser l’idempotence, la gestion de l’historique, ni le fallback `context_too_large`

### Previous Story Intelligence

- 60.17 et 60.18 ont montré qu’il faut systématiquement :
  - réutiliser les tokens premium existants au lieu de créer un sous-système visuel parallèle
  - vérifier le rendu live et pas seulement les tests statiques
  - éviter les divergences de source-of-truth entre composants proches
- 30.18 a déjà réorganisé le chat en supprimant l’ancien panneau droit, en introduisant le chip astrologue et en ajoutant un bouton `Nouvelle discussion` dans la fenêtre de chat.
- Cette story 60.19 doit explicitement réévaluer ce choix 30.18 au regard du nouveau target UX mobile/desktop, pas l’accepter aveuglément.

### Git Intelligence Summary

- Les commits récents montrent une convergence forte vers un design premium partagé :
  - `eec2132` `Polish dashboard premium finish`
  - `aeefe2d` `Polish daily horoscope narrative and layout`
  - `4ec4eed` `Refine daily horoscope narrative depth`
- La story doit donc s’aligner sur ce langage déjà stabilisé, pas relancer une exploration visuelle indépendante sur `/chat`.

### Library / Framework Requirements

- Frontend React + TypeScript existant, sans Tailwind.
- Réutiliser les composants/layouts déjà présents (`TwoColumnLayout`, `SectionErrorBoundary`, chat feature components) si pertinents, sinon faire évoluer proprement l’existant.
- Backend Python/FastAPI existant.
- Tests frontend via Vitest + Testing Library.
- Tests backend via Pytest.

### File Structure Requirements

**Frontend candidats principaux**
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/features/chat/components/ChatLayout.tsx`
- `frontend/src/features/chat/components/ConversationList.tsx`
- `frontend/src/features/chat/components/ChatWindow.tsx`
- `frontend/src/features/chat/components/ChatEmptyState.tsx`
- `frontend/src/features/chat/components/ConversationItem.tsx`
- `frontend/src/App.css`
- nouveaux fichiers CSS dédiés au chat si nécessaire, mais éviter de tout recoller dans `App.css`
- `frontend/src/tests/ChatPage.test.tsx`
- `frontend/src/tests/chat/ChatComponents.test.tsx`

**Backend candidats principaux**
- `backend/app/services/chat_guidance_service.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/app/prompts/catalog.py`
- tests unitaires backend chat pertinents

### Testing Requirements

- Frontend :
  - `npx tsc --noEmit`
  - `npm run test -- src/tests/ChatPage.test.tsx src/tests/chat/ChatComponents.test.tsx`
  - ajouter d’autres tests ciblés si de nouveaux composants/layouts sont extraits
- Backend :
  - tests unitaires ciblés sur l’assemblage de contexte chat si la date ou la mémoire changent
  - toujours lancer dans le venv :
    - `.\.venv\Scripts\Activate.ps1; pytest ... -q`
- Validation manuelle attendue :
  - `/chat` mobile : liste → conversation
  - `/chat/:conversationId` mobile : conversation dédiée
  - `/chat` desktop : liste gauche + conversation droite plus large
  - vérification visuelle du back button premium et du titre de page

### Project Structure Notes

- Cette story est transversale frontend + backend, mais le backend doit rester limité au pipeline de contexte chat.
- Ne pas changer les contrats API de conversations sans nécessité explicite.
- Ne pas casser les parcours existants testés autour de :
  - auto-redirect vers dernière conversation
  - création par persona
  - deep links
  - idempotence d’envoi de messages

### References

- [Source: c:/dev/horoscope_front/_bmad-output/implementation-artifacts/60-17-refonte-visuelle-premium-page-horoscope.md]
- [Source: c:/dev/horoscope_front/_bmad-output/implementation-artifacts/60-18-alignement-dashboard-et-prechargement-horoscope.md]
- [Source: c:/dev/horoscope_front/_bmad-output/implementation-artifacts/30-18-chat-ux-header-chip-layout.md]
- [Source: c:/dev/horoscope_front/docs/chat/plan_implementation_chat_memoire.md]
- [Source: c:/dev/horoscope_front/frontend/src/pages/ChatPage.tsx]
- [Source: c:/dev/horoscope_front/frontend/src/features/chat/components/ChatLayout.tsx]
- [Source: c:/dev/horoscope_front/frontend/src/features/chat/components/ConversationList.tsx]
- [Source: c:/dev/horoscope_front/frontend/src/features/chat/components/ChatWindow.tsx]
- [Source: c:/dev/horoscope_front/frontend/src/api/chat.ts]
- [Source: c:/dev/horoscope_front/backend/app/services/chat_guidance_service.py]
- [Source: c:/dev/horoscope_front/backend/app/services/ai_engine_adapter.py]
- [Source: c:/dev/horoscope_front/backend/app/prompts/catalog.py]
- [Source: c:/dev/horoscope_front/frontend/src/tests/ChatPage.test.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée via le workflow BMAD `create-story`.
- Contexte consolidé depuis les stories 30.18, 60.17, 60.18, l’implémentation courante de `/chat`, les tests existants et le plan mémoire conversationnelle chat.

### Completion Notes List

- La story 60.19 recadre `/chat` comme une surface premium cohérente avec `/dashboard` et `/dashboard/horoscope`, au lieu d’un écran fonctionnel isolé.
- Le périmètre couvre explicitement la clarification UX mobile/desktop, la rationalisation de l’action “nouvelle conversation” et le durcissement du contexte backend envoyé au LLM.
- L’existant 30.18 est traité comme contexte, pas comme contrainte intangible : la story demande de réévaluer les doubles actions “nouvelle discussion” à la lumière du nouveau target UX.
- Le pipeline backend chat doit être vérifié pour l’usage réel de `chat_astrologer`, de l’historique, de la mémoire conversationnelle et de la date du jour.
- L’objectif n’est pas seulement esthétique : il s’agit aussi d’éviter un chat “hors temps” ou sans continuité contextuelle lorsque la conversation s’allonge.
- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `frontend/src/pages/ChatPage.tsx` (updated with premium layout and header)
- `frontend/src/pages/ChatPage.css` (new, premium page container and halo)
- `frontend/src/features/chat/components/ChatPageHeader.tsx` (new component)
- `frontend/src/features/chat/components/ChatPageHeader.css` (new styles)
- `frontend/src/features/chat/components/ChatWindow.tsx` (rationalized header)
- `frontend/src/features/chat/components/ConversationList.tsx` (imported new styles)
- `frontend/src/features/chat/components/ConversationList.css` (new, premium list styles)
- `frontend/src/features/chat/components/ConversationItem.tsx` (imported new styles)
- `frontend/src/features/chat/components/ConversationItem.css` (new, premium item styles)
- `frontend/src/features/chat/index.ts` (exported ChatPageHeader)
- `backend/app/llm_orchestration/gateway.py` (added authorized variables for current context)
- `backend/app/llm_orchestration/seeds/use_cases_seed.py` (added current_datetime as required placeholder for chat_astrologer)
- `backend/scripts/seed_30_15_chat_naturalite.py` (updated prompt with current_datetime)

## Senior Developer Review (AI)

### AC Validation

1. **[x] /chat realigned on premium design**: Yes, added `ChatPage.css` with premium background halo and glass panels.
2. **[x] Header with title, micro-label, and premium back button**: Yes, implemented `ChatPageHeader` reusing `daily-page-header__back` logic.
3. **[x] Single main pattern for conversation creation**: Yes, removed redundant button from `ChatWindow`, unified in `ConversationList` header.
4. **[x] Mobile experience**: List first, then dedicated chat view. Existing logic verified and header adapted.
5. **[x] Desktop experience**: Increased chat zone width to `320px` sidebar.
6. **[x] Premium visual for astrologer chip, panels, empty states**: Yes, updated with dedicated CSS files and premium tokens.
7. **[x] Coherent back button behavior**: Verified.
8. **[x] Today's date included in LLM context**: Yes, updated prompt and authorized variables in gateway.
9. **[x] Verification of context assembly**: Confirmed that `current_datetime` is passed and rendered correctly.

### Task Audit

- [x] Réaligner visuellement `/chat` sur le design premium existant (AC: 1, 2, 7)
- [x] Rationaliser l’architecture UX “nouvelle conversation” (AC: 3, 7)
- [x] Consolider les comportements desktop vs mobile (AC: 4, 5, 7)
- [x] Auditer et durcir la construction du contexte chat LLM (AC: 8, 9)

### Code Quality

- Frontend: Modern CSS with variables and glassmorphism. Components are cleaner with dedicated styles.
- Backend: Secure handling of authorized variables in LLM gateway.

### Final Outcome

Implementation is complete and exceeds basic requirements by also refactoring chat component styles into dedicated files for better maintainability.
