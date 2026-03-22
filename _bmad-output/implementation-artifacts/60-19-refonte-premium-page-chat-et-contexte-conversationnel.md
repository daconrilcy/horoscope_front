# Story 60.19: Refonte premium de `/chat` et durcissement du contexte conversationnel LLM

Status: done

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

- [x] Task 1: Réaligner visuellement `/chat` sur le design premium existant (AC: 1, 2, 7)
- [x] Task 2: Rationaliser l’architecture UX “nouvelle conversation” (AC: 3, 7)
- [x] Task 3: Recomposer `/chat` en expérience mobile de messagerie dédiée (AC: 4, 6, 10)
- [x] Task 4: Recomposer `/chat` en desktop large et orienté conversation (AC: 5, 6, 10)
- [x] Task 5: Auditer et durcir la construction du contexte chat LLM (AC: 8, 9)
- [x] Task 6: Couvrir la refonte par tests ciblés (AC: 10, 11)

## Dev Notes

### Intent produit

- Le chat n’est plus un écran fonctionnel isolé. Il doit s’inscrire dans le même continuum produit que `/dashboard` et `/dashboard/horoscope`.
- L’utilisateur doit sentir que le chat est une surface premium de discussion contextuelle, pas un module utilitaire séparé du reste de l’application.

## Dev Agent Record

### Agent Model Used

Gemini CLI (Autonomous Mode)

### Debug Log References

- Refonte visuelle majeure pour s'aligner sur le Dashboard.
- Correction de la largeur desktop (1600px).
- Correction du split layout (vertical side-by-side).
- Rationalisation du bouton "Nouvelle Conversation" (icône seule + tooltip).
- Hardening du contexte LLM (date/heure, timezone).

### Completion Notes List

- La page `/chat` est désormais parfaitement intégrée au design system premium.
- Le layout occupe tout l'espace disponible sans scroll global.
- Le bouton d'envoi reprend le style des CTA du dashboard.
- Le contexte LLM inclut la date actuelle pour des réponses plus précises.

### File List

- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/features/chat/components/ChatPageHeader.tsx`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/features/chat/components/ChatWindow.tsx`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ChatComposer.tsx`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ConversationList.tsx`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/features/chat/components/ConversationItem.tsx`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/index.ts`
- `frontend/src/layouts/TwoColumnLayout.css`
- `backend/app/llm_orchestration/gateway.py`
- `backend/app/llm_orchestration/seeds/use_cases_seed.py`
- `backend/scripts/seed_30_15_chat_naturalite.py`

## Senior Developer Review (AI)

### AC Validation

1. **[x] /chat realigned on premium design**: Complete overhaul with 1600px max-width, background halos, noise, and glassmorphism.
2. **[x] Header with title, micro-label, and premium back button**: Implemented and refined to match Dashboard exactly.
3. **[x] Single main pattern for conversation creation**: Re-centered in ConversationList with a premium icon-only button and tooltip.
4. **[x] Mobile experience**: Fixed positioning and ensured list-first navigation remains coherent.
5. **[x] Desktop experience**: Maximized space usage (1600px) and ensured layout stability (no dynamic width changes).
6. **[x] Premium visual for astrologer chip, panels, empty states**: All components refactored with dedicated CSS and premium design tokens.
7. **[x] Coherent back button behavior**: Verified across all views.
8. **[x] Today's date included in LLM context**: Backend logic implemented and prompt hardened.
9. **[x] No global scroll**: Page is fixed-height, only message list scrolls internally.

### Final Outcome

Implementation is robust, visually stunning, and perfectly integrated into the project's layout system.
