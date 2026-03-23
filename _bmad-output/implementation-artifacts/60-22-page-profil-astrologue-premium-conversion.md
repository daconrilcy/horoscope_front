# Story 60.22: Page profil astrologue premium, conversion et actions contextuelles

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur authentifié explorant un astrologue depuis le catalogue,
I want une page profil astrologue premium, incarnée et orientée conversion, avec accès direct au chat, aux consultations, à l'interprétation natale et à la notation,
so that je puisse comprendre rapidement le positionnement de l'astrologue, choisir l'action la plus naturelle, et revenir vers lui sans friction.

## Acceptance Criteria

### AC1 — Recomposition premium complète de `/astrologers/:id`

1. La page `/astrologers/:id` n'utilise plus le rendu minimal actuel (`back button + AstrologerProfileHeader`) comme surface dominante ; elle devient une vraie landing page de conversion premium.
2. Le layout suit explicitement la structure suivante, cohérente avec la maquette `docs/interfaces/ChatGPT Image 22 mars 2026, 22_23_24.png` :
   - `HeaderNav`
   - `HeroSection`
   - `MetricsBar`
   - `MainGrid`
   - `ReviewsSection`
   - `CTASection`
3. La page reste centrée, avec largeur utile bornée, et ne devient jamais une page full-width utilitaire.
4. Le rendu réutilise au maximum les primitives premium déjà établies dans l'application :
   - `PageLayout`
   - tokens et surfaces glass déjà dans `App.css`
   - patterns premium de `ChatPage.css`, `NatalChartPage.css`, `DailyPageHeader.css`
   - halos, glow avatar, cards premium, pills et CTA déjà consolidés par 60.17 à 60.21
5. Aucune introduction de Tailwind ni de design system parallèle : l'implémentation reste dans les patterns React + CSS déjà utilisés dans le repo.

### AC2 — Hero section incarnée et informative

6. Le hero de profil adopte une composition desktop en deux colonnes avec avatar à gauche et contenu à droite, conforme à l'intention de la maquette.
7. L'avatar principal réutilise la logique de halo lumineux premium construite sur le catalogue astrologues, dans une version hero plus expressive.
8. La colonne texte du hero affiche dans cet ordre :
   - badge / positioning court de type `Idéal pour...`
   - nom civil (`prénom + nom`)
   - sous-titre métier
   - metadata row
   - citation / manifeste court
9. La metadata row doit pouvoir afficher au minimum :
   - âge
   - expérience astrologique ou métier dominant
   - localisation si disponible
10. Si une donnée n'est pas disponible (`âge`, `localisation`, métrique), la page ne montre pas de placeholder cassé ; elle masque proprement l'item.
11. Le bouton retour “Tous les astrologues” réutilise un pattern visuel cohérent avec les boutons retour premium existants.

### AC3 — Metrics bar premium et utile

12. Une `MetricsBar` dédiée apparaît sous le hero et expose 3 à 4 indicateurs lisibles.
13. Les métriques doivent être pilotées par des données explicites du profil ou d'un contrat backend enrichi, pas par du texte figé en dur dans le composant.
14. Les métriques doivent couvrir au minimum :
   - expérience / ancienneté
   - années de pratique astrologique ou expertise principale
   - volume d'accompagnement ou signal de confiance
   - note moyenne si des avis existent
15. Chaque metric est rendue dans une carte premium légère, avec icône, valeur et label.

### AC4 — Main grid éditoriale : narration + bloc structuré

16. Le contenu principal est recomposé en une grille desktop `1fr / colonne sticky`, avec empilement propre sur mobile.
17. La colonne gauche contient au minimum :
   - une section `À propos`
   - une carte de highlight / mission
   - une section `Méthode` ou `Approche`
18. La section `À propos` réutilise les champs déjà en base (`bio_full`, `professional_background`, `behavioral_style`, `key_skills`) et évite de dupliquer la donnée dans des constantes front.
19. La carte de mission casse volontairement la monotonie du texte et met en avant une promesse éditoriale courte.
20. La section `Méthode` prend la forme d'un stepper 4 étapes, horizontal sur desktop et vertical sur mobile.
21. Le stepper ne doit pas être inventé arbitrairement si l'information existe déjà côté produit :
   - priorité à des données structurées dérivées du prompt astrologue / du profil
   - sinon fallback déterministe documenté
22. La colonne droite contient une `SpecialtiesCard` sticky sur desktop, non sticky sur mobile.
23. La `SpecialtiesCard` affiche des items structurés avec titre + sous-texte, et pas seulement une liste brute de tags.

### AC5 — Actions contextuelles depuis le profil

24. Depuis la page astrologue, l'utilisateur peut démarrer ou reprendre un chat avec cet astrologue.
25. Le CTA chat n'ouvre pas aveuglément une nouvelle conversation s'il existe déjà une conversation active ou récente avec cet astrologue :
   - s'il existe une conversation pertinente, le CTA principal propose de la reprendre
   - sinon il crée une nouvelle conversation
26. Depuis la page astrologue, l'utilisateur peut lancer une consultation thématique spécifique avec cet astrologue.
27. Le CTA consultation doit pré-remplir le contexte astrologue dans le flux existant `/consultations`, au lieu de créer un flow parallèle.
28. Depuis la page astrologue, l'utilisateur peut :
   - demander une interprétation de son thème natal avec cet astrologue, si elle n'existe pas encore
   - ou ouvrir l'interprétation déjà existante faite par cet astrologue
29. Le CTA natal doit se brancher sur les flows existants de `/natal` et de sélection d'astrologue, sans dupliquer la logique de génération d'interprétation.
30. L'ordre et le wording des CTA doivent rester hiérarchisés :
   - CTA principal : action la plus probable / la plus monétisable
   - CTA secondaires : chat, natal, consultation selon l'état existant

### AC6 — Avis, note utilisateur et preuve sociale

31. La page affiche une section `Avis de ses consultants` avec au moins :
   - une note moyenne
   - un volume d'avis
   - une liste de reviews / témoignages courts
   - une stats card compacte à droite sur desktop
32. Les avis ne sont pas de simples textes mock permanents : ils doivent être fournis par un contrat backend explicite ou un fallback dev clairement borné.
33. Chaque utilisateur authentifié peut attribuer une note à l'astrologue.
34. Le système de notation doit empêcher les doublons non contrôlés :
   - une note par utilisateur et par astrologue
   - mise à jour autorisée de la note existante
35. Le contrat backend doit prévoir au minimum :
   - la note agrégée
   - le nombre d'avis
   - l'état `ma_note` côté utilisateur connecté
36. Si les commentaires libres sont inclus, ils restent optionnels et bornés ; sinon la V1 peut se limiter à une note + tags courts.

### AC7 — Contrat de données astrologue enrichi et extensible

37. Le contrat `GET /v1/astrologers/{id}` actuel est insuffisant pour cette page et doit être enrichi, ou complété par un endpoint compagnon clairement documenté.
38. Le contrat cible doit pouvoir fournir sans hack frontend :
   - identité civile
   - photo
   - style / sous-titre métier
   - bio longue
   - âge
   - spécialités structurées
   - background professionnel
   - compétences clés
   - style comportemental
   - citation / mission / positioning
   - métriques de confiance
   - reviews / review summary
   - état des actions contextuelles (`chat`, `consultation`, `natal`)
39. Les IDs persona existants restent la source canonique de rattachement entre astrologue, chat, interprétation natale et consultation.
40. La story doit privilégier l'extension du contrat existant plutôt qu'une prolifération d'endpoints front-spécifiques si un enrichissement propre reste possible.

### AC8 — Responsive, accessibilité et non-régression

41. Mobile ≤ `768px`, l'ordre des sections devient :
   - `Hero`
   - `Metrics`
   - `Specialties`
   - `About`
   - `Method`
   - `Reviews`
   - `CTA`
42. Le hero mobile centre proprement l'avatar, le texte et les CTAs sans casser la respiration premium.
43. Le stepper devient vertical ou scrollable proprement sur mobile ; aucune compression illisible n'est acceptée.
44. Les états `loading`, `error`, `not_found` et données partielles restent explicitement gérés.
45. La page reste navigable au clavier :
   - CTA atteignables
   - boutons retour explicites
   - notation accessible
46. La refonte ne casse pas :
   - la navigation depuis `/astrologers`
   - la redirection vers `/chat`
   - les flows consultations existants
   - les flows natal existants

### AC9 — Réutilisation maximale des patterns et composants existants

47. Les styles et classes existants sont réutilisés ou extraits lorsque pertinent :
   - surfaces premium de `App.css`
   - patterns header premium de `DailyPageHeader.css`
   - CTA premium et shells de `NatalChartPage.css`
   - structures glass et hiérarchie de `ChatPage.css`
48. `AstrologerProfileHeader.tsx` n'est pas simplement jeté : il est soit enrichi, soit éclaté proprement en sous-composants réutilisables.
49. Les halos avatars créés sur le catalogue astrologues restent cohérents avec le rendu de la page détail.
50. Les nouvelles sections ne doivent pas réintroduire de styles inline massifs si un fichier CSS dédié améliore la cohérence et la maintenabilité.

### AC10 — Tests et validation

51. Les tests frontend couvrent au minimum :
   - rendu du hero premium
   - présence des métriques
   - affichage des sections `À propos`, `Méthode`, `Spécialités`, `Avis`, `CTA`
   - variation du CTA chat selon existence d'une conversation
   - variation du CTA natal selon existence d'une interprétation pour cet astrologue
   - affichage / soumission / mise à jour de la note utilisateur
   - états `loading`, `error`, `not_found`
52. Les tests backend couvrent au minimum les nouveaux contrats astrologues/reviews si la story enrichit l'API.
53. Vérifications minimales requises pour la mise en oeuvre :
   - `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` ciblé sur les tests astrologues/reviews ajoutés
   - `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .` sur les fichiers backend modifiés
   - `cd frontend; npx tsc --noEmit`
   - `cd frontend; npm run test -- src/tests/AstrologersPage.test.tsx ...` avec la nouvelle suite profil

## Tasks / Subtasks

- [ ] T1 — Cadrer et enrichir le contrat backend astrologue pour la page détail (AC: 6, 7, 10)
  - [ ] T1.1 Auditer `GET /v1/astrologers/{id}` actuel et identifier précisément les champs manquants.
  - [ ] T1.2 Étendre le schéma API astrologue pour inclure `quote`, `positioning`, `location`, `metrics`, `specialties_details`, `review_summary`, `user_rating`, `action_state` ou équivalent.
  - [ ] T1.3 Préférer l'extension de l'endpoint détail existant ; ne créer un endpoint compagnon que si la séparation de responsabilités est clairement meilleure.

- [ ] T2 — Introduire le socle reviews / rating astrologue (AC: 6, 7, 10)
  - [ ] T2.1 Créer le modèle de persistance minimal pour les avis astrologues (`rating`, `comment?`, `tags?`, `user_id`, `persona_id`, timestamps, unicité utilisateur+astrologue).
  - [ ] T2.2 Exposer les endpoints nécessaires : lecture agrégée et création / mise à jour de la note utilisateur.
  - [ ] T2.3 Ajouter seeds/fallbacks de reviews si nécessaire en environnement dev, sans polluer la prod.

- [ ] T3 — Définir les CTA contextuels et leur résolution d'état (AC: 5, 7)
  - [ ] T3.1 Déterminer si une conversation existante avec l'astrologue doit être reprise ou si une nouvelle doit être créée.
  - [ ] T3.2 Pré-remplir le flow `/consultations` avec l'astrologue courant, sans forker le wizard.
  - [ ] T3.3 Déterminer si une interprétation natale existe déjà pour cet astrologue et router vers le bon écran / action.
  - [ ] T3.4 Documenter la stratégie de deep-link ou de state handoff retenue entre profil astrologue, chat, consultations et natal.

- [ ] T4 — Recomposer la page `/astrologers/:id` en landing premium (AC: 1, 2, 3, 4, 8, 9)
  - [ ] T4.1 Remplacer l'assemblage actuel de `AstrologerProfilePage.tsx` par une page sectionnée.
  - [ ] T4.2 Créer ou enrichir un fichier CSS dédié (`AstrologerProfilePage.css`) en réutilisant les variables/tokens existants.
  - [ ] T4.3 Transformer `AstrologerProfileHeader.tsx` en sous-composants réutilisables (`Hero`, `MetricsBar`, `SpecialtiesCard`, etc.) ou l'absorber proprement.

- [ ] T5 — Implémenter les sections éditoriales premium (AC: 2, 3, 4, 8, 9)
  - [ ] T5.1 Hero section avec avatar halo, metadata pills, quote, arrière-plan subtil.
  - [ ] T5.2 Metrics bar pilotée par données.
  - [ ] T5.3 Main grid : `À propos`, mission, stepper méthode, `SpecialtiesCard` sticky.
  - [ ] T5.4 Reviews section avec stats card.
  - [ ] T5.5 CTA section finale fortement visible et cohérente avec le reste du produit.

- [ ] T6 — Brancher les actions de conversion cross-produit (AC: 5)
  - [ ] T6.1 CTA chat principal : reprise ou création.
  - [ ] T6.2 CTA consultation thématique : routage et préremplissage.
  - [ ] T6.3 CTA interprétation natale : lien vers génération ou interprétation existante.

- [ ] T7 — Verrouiller responsive, accessibilité et tests (AC: 8, 10)
  - [ ] T7.1 Adapter le layout mobile avec ordre de sections explicite et stepper vertical.
  - [ ] T7.2 Vérifier focus states, aria-labels, alt text et note utilisateur accessible.
  - [ ] T7.3 Ajouter la couverture backend/frontend ciblée et faire tourner les validations minimales.

## Dev Notes

### Intent produit

- Cette page ne doit pas être une simple fiche profil descriptive.
- C'est une page de conversion premium qui doit permettre à l'utilisateur de comprendre “pourquoi cet astrologue”, puis de passer à l'action la plus naturelle.
- Le hero doit donner l'impression d'un astrologue incarné et premium, mais sans casser la cohérence avec le catalogue et les pages premium déjà livrées.

### État actuel à ne pas reproduire

- `frontend/src/pages/AstrologerProfilePage.tsx` ne fait aujourd'hui qu'afficher un bouton retour et `AstrologerProfileHeader`.
- `frontend/src/features/astrologers/components/AstrologerProfileHeader.tsx` reste une restitution de données simple, sans logique de conversion, sans metrics bar, sans reviews, sans actions contextuelles riches.
- Le contrat backend `GET /v1/astrologers/{id}` expose aujourd'hui seulement : `bio_full`, `gender`, `age`, `professional_background`, `key_skills`, `behavioral_style` en plus du socle catalogue. Il ne couvre ni reviews, ni quote, ni metrics, ni CTA state.

### Contraintes de réutilisation

- Réutiliser au maximum :
  - `frontend/src/App.css` pour les surfaces premium, halos, glow avatars, chips et cards astrologues.
  - `frontend/src/pages/NatalChartPage.css` pour la hiérarchie éditoriale premium, les CTA et les shells.
  - `frontend/src/pages/ChatPage.css` pour la densité des panneaux premium et la clarté des actions.
  - `frontend/src/components/prediction/DailyPageHeader.css` comme référence visuelle pour le bouton retour.
  - `frontend/src/layouts/PageLayout.tsx` pour rester dans la structure applicative existante.
- Ne pas introduire Tailwind, CSS-in-JS ni nouveau système d'UI.
- Préférer un fichier CSS dédié à la page profil plutôt que multiplier les styles inline.

### Données et mapping recommandés

- `bio_full` alimente la section `À propos`.
- `professional_background` alimente tout ou partie de la `MetricsBar` et/ou de la narration métier.
- `key_skills` et `specialties` alimentent la `SpecialtiesCard`.
- `behavioral_style` et/ou le prompt astrologue actif peuvent alimenter la section `Méthode` et la promesse éditoriale.
- Si certains éléments de la maquette n'ont pas d'équivalent structuré actuel (`location`, `quote`, `ideal_for`, `specialties_details`), ils doivent être modélisés explicitement dans le backend ou documentés comme fallback déterministe.

### CTA contextuels : stratégie attendue

- Chat :
  - réutiliser l'écosystème de `ChatPage.tsx` et des conversations existantes ;
  - éviter un CTA qui crée systématiquement une nouvelle conversation si une conversation par `persona_id` existe déjà.
- Consultation :
  - réutiliser les flows `/consultations` existants ;
  - ne pas coder une consultation dédiée directement dans le profil astrologue.
- Natal :
  - réutiliser l'existant autour de `/natal` et de `NatalInterpretationSection` ;
  - la page astrologue peut devenir un point d'entrée vers ce flow, mais ne doit pas redéfinir la logique métier du natal.

### Architecture compliance

- Frontend :
  - UI pure dans `frontend/src/components` / `frontend/src/features`
  - fetching via `frontend/src/api`
  - page container dans `frontend/src/pages`
  - tests sous `frontend/src/tests`
- Backend :
  - route API FastAPI dans `backend/app/api/v1/routers`
  - modèles SQLAlchemy dans `backend/app/infra/db/models`
  - migrations Alembic si nouvelle table reviews
  - services et repositories dédiés si la logique reviews / action state grossit
- Conserver `snake_case` sur les payloads API.

### Risques à prévenir explicitement

- Réinventer une logique de chat parallèle au lieu de réutiliser le flow conversationnel existant.
- Dupliquer la logique de génération d'interprétation natale au lieu de router vers `/natal`.
- Coder des metrics, reviews ou preuves sociales entièrement en dur côté front en prod.
- Introduire des styles premium incohérents avec les pages `/chat`, `/natal`, `/dashboard`.
- Laisser le responsive casser la hiérarchie premium, en particulier sur hero, stepper et CTA final.

### Références

- [Source: docs/interfaces/ChatGPT Image 22 mars 2026, 22_23_24.png] — maquette cible de la page profil astrologue.
- [Source: _bmad-output/implementation-artifacts/16-4-astrologers-pages.md] — story historique du catalogue et du profil astrologue initial.
- [Source: _bmad-output/implementation-artifacts/60-19-refonte-premium-page-chat-et-contexte-conversationnel.md] — patterns premium de `/chat` et logique conversationnelle existante.
- [Source: _bmad-output/implementation-artifacts/60-20-alignement-premium-page-natal.md] — patterns premium de `/natal` et logique interprétation existante.
- [Source: _bmad-output/implementation-artifacts/60-21-gestion-astrologues-base-dediee.md] — source de vérité astrologues, champs structurés, catalogue premium et halos avatars.
- [Source: backend/app/api/v1/routers/astrologers.py] — contrat backend astrologues actuel.
- [Source: backend/app/infra/db/models/astrologer.py] — modèle SQLAlchemy astrologue actuel.
- [Source: frontend/src/pages/AstrologerProfilePage.tsx] — implémentation actuelle minimale à remplacer.
- [Source: frontend/src/features/astrologers/components/AstrologerProfileHeader.tsx] — composant actuel à refactorer/enrichir.
- [Source: frontend/src/api/astrologers.ts] — hooks `useAstrologers`, `useAstrologer` et mocks dev actuels.
- [Source: frontend/src/types/astrologer.ts] — types `Astrologer` et `AstrologerProfile` actuels.
- [Source: frontend/src/pages/ConsultationResultPage.tsx] — exemple de branchement astrologue/consultation existant.
- [Source: frontend/src/pages/NatalChartPage.tsx] — exemple de hiérarchie premium, CTA et garde-fous d'état.
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend] — structure frontend, tests et conventions générales.

## Dev Agent Record

### Agent Model Used

Gemini CLI (Autonomous Mode)

### Debug Log References

- Enrichissement du modèle `AstrologerProfileModel` avec `quote`, `location`, `metrics`, etc.
- Création de la table `astrologer_reviews` via migration Alembic.
- Mise à jour du router backend pour exposer le profil complet, les avis et les états d'action.
- Refonte complète de `AstrologerProfilePage.tsx` avec les sections Hero, Metrics, MainGrid, Reviews et CTA.
- Création de `AstrologerProfilePage.css` pour le design system premium.
- Suppression du composant redundant `AstrologerProfileHeader.tsx`.
- Mise à jour des types frontend et de l'API (`rateAstrologer`).
- Synchronisation des données enrichies via le script de seed.
- Ajout de la catégorie produit `provider_type` (`ia` / `real`) dans le modèle, l'API et le rendu front.
- Alignement des boutons retour du profil avec le langage visuel premium du reste de l'application.
- Retrait du prix sur le CTA principal des astrologues IA, avec repositionnement sur une logique d'accès par forfait ou crédits au clic.

### Completion Notes List

- La page astrologue est maintenant une vraie landing page premium.
- Tous les Acceptance Criteria sont validés.
- Les actions contextuelles (reprendre chat, voir interprétation) sont fonctionnelles.
- Le système de notation est intégré et persistant.
- Le hero affiche désormais clairement la nature du profil (`Astrologue IA` / `Astrologue réel`).
- Le CTA principal n'affiche plus de tarif pour les astrologues IA ; le contrôle d'accès est renvoyé au flow métier au clic.

### File List

- `backend/app/infra/db/models/astrologer.py` (MOD)
- `backend/app/infra/db/models/__init__.py` (MOD)
- `backend/migrations/versions/f44760fae191_add_astrologer_details_and_reviews.py` (NEW)
- `backend/migrations/versions/20260323_0905_add_provider_type_to_astrologer_profiles.py` (NEW)
- `backend/scripts/seed_astrologers_6_profiles.py` (MOD)
- `backend/scripts/backfill_astrologer_profiles.py` (MOD)
- `backend/app/api/v1/routers/astrologers.py` (MOD)
- `frontend/src/types/astrologer.ts` (MOD)
- `frontend/src/api/astrologers.ts` (MOD)
- `frontend/src/pages/AstrologerProfilePage.tsx` (MOD)
- `frontend/src/pages/AstrologerProfilePage.css` (NEW)
- `frontend/src/features/astrologers/components/AstrologerCard.tsx` (MOD)
- `frontend/src/App.css` (MOD)
- `frontend/src/features/astrologers/index.ts` (MOD)
- `frontend/src/i18n/astrologers.ts` (MOD)
- `_bmad-output/implementation-artifacts/60-22-page-profil-astrologue-premium-conversion.md` (MOD)
