# Story 48.2: Intégrer le fond astrologique animé au résumé dashboard

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product-facing frontend engineer,
I want brancher le composant `AstroMoodBackground` sur la carte résumé de `/dashboard`,
so that le résumé du jour gagne une présence premium sans changer le contrat backend ni casser les états existants de la landing.

## Acceptance Criteria

1. La carte résumé de `/dashboard` utilise `AstroMoodBackground` lorsque la prédiction du jour est disponible, tout en restant cliquable et activable au clavier vers `/dashboard/horoscope`.
**Mise à jour post-review :** Le Dashboard s'adapte en `min-height: 100dvh`, la section Horoscope a un titre visible, la carte occupe `min-height: 33dvh` et affiche un pill avec le logo du signe.
2. Le mapping des paramètres visuels (`sign`, `userId`, `dateKey`, `dayScore`) est centralisé dans un module ou hook dédié et ne duplique pas de logique dans le JSX de `DashboardPage` ou `DashboardHoroscopeSummaryCard`.
3. `sign` vient de `astro_profile.sun_sign_code` via les données de naissance existantes, `dateKey` vient de `prediction.meta.date_local`, `userId` vient du sujet du token ou du profil auth, et `dayScore` est dérivé des catégories daily existantes sans nouveau contrat backend.
4. Si le signe est absent, la carte utilise un fallback visuel neutre et stable au lieu d'échouer ou de masquer le résumé.
5. Les états `loading`, `error` et `empty` du dashboard restent cohérents et ne masquent jamais la section activités.
6. Le texte résumé reste lisible, la zone gauche reste respirante et aucune nouvelle chaîne inutile n'est hardcodée hors i18n dashboard.
7. Le branchage réutilise les mécanismes de cache/chargement existants du frontend et n'introduit pas de logique réseau directement dans les composants UI.
8. Les tests dashboard couvrent le nouveau rendu et les fallback visuels quand le signe ou la prédiction ne sont pas disponibles.
9. Le résumé dashboard reste affichable sans attendre `birth-data`; en l'absence temporaire ou durable de `sun_sign_code`, un rendu `neutral` est utilisé sans bloquer la landing.

## Tasks / Subtasks

- [x] Task 1: Centraliser le mapping métier -> paramètres visuels (AC: 2, 3, 4, 7)
  - [x] Introduire un module ou hook dédié, par exemple `frontend/src/components/dashboard/useDashboardAstroSummary.ts`
  - [x] Réutiliser `useDailyPrediction` pour la donnée daily
  - [x] Réutiliser `getBirthData` via un hook React Query dédié ou une couche `api` équivalente pour charger `sun_sign_code`
  - [x] Dériver un `dayScore` stable à partir des `categories.note_20` existantes selon une formule normative unique
  - [x] Utiliser le sujet du token comme seed primaire si le profil auth n'est pas encore disponible
  - [x] Déclencher la requête `birth-data` uniquement si le sujet utilisateur est disponible, sans rendre le résumé bloquant

- [x] Task 2: Recomposer la carte résumé dashboard autour du fond animé (AC: 1, 4, 6)
  - [x] Mettre à jour `DashboardHoroscopeSummaryCard` pour envelopper son contenu dans `AstroMoodBackground`
  - [x] Préserver le comportement de navigation `click + Enter + Space`
  - [x] Conserver la sémantique actuelle de résumé court et CTA vers `/dashboard/horoscope`
  - [x] Maintenir une mise en page lisible avec texte à gauche et affordance d'action visible

- [x] Task 3: Préserver les états et l'intégration landing existante (AC: 5, 7)
  - [x] Garder les rendus `loading`, `error` et `empty` cohérents avec l'epic 45
  - [x] Ne pas masquer `ShortcutsSection`
  - [x] Ne pas introduire d'endpoint backend supplémentaire

- [x] Task 4: Aligner styles et i18n sans dette visuelle (AC: 6)
  - [x] Ajouter uniquement les styles nécessaires autour du résumé dashboard
  - [x] Réutiliser les tokens visuels déjà présents dans `App.css` / la charte existante
  - [x] Centraliser tout nouveau libellé critique dans `frontend/src/i18n/dashboard.tsx`

- [x] Task 5: Mettre à jour les tests dashboard (AC: 1, 5, 8)
  - [x] Adapter `frontend/src/tests/DashboardPage.test.tsx`
  - [x] Vérifier la navigation inchangée vers `/dashboard/horoscope`
  - [x] Vérifier que les activités restent visibles dans tous les états
  - [x] Ajouter un cas de fallback quand `sun_sign_code` est absent ou que `birth-data` retourne `null`

## Dev Notes

- Le contrat backend actuel suffit: la story ne doit pas introduire d'endpoint image, ni d'enrichissement daily dédié au background.
- Le `dayScore` visuel doit être dérivé à partir des données daily existantes avec une formule normative: `round(mean(categories.note_20 valides))`, puis `clamp(1..20)`, avec fallback à `12` si aucune note exploitable n'est disponible.
- Le dashboard ne consomme pas encore `birth-data`; cette story peut introduire un hook query frontend dédié tant qu'il reste dans `frontend/src/api`.
- Le composant ne doit pas transformer la landing `/dashboard` en page détail. Le résumé reste court, cliquable et orienté navigation.
- Le rendu du résumé ne doit jamais attendre `birth-data`: le chemin nominal est `summary disponible -> fond neutral immédiat -> enrichissement éventuel avec signe quand sun_sign_code arrive`.

### Previous Story Intelligence

- La story 45.2 a déjà posé la structure `DashboardPage -> DashboardHoroscopeSummaryCard -> ShortcutsSection`; cette hiérarchie doit rester la base du branchage.
- La story 45.4 a verrouillé les états `loading/error/empty` et la navigation dashboard; l'intégration du fond animé ne doit pas casser ces assertions.
- `HeroHoroscopeCard` montre une direction premium utile, mais il ne faut pas recopier tout son contenu si cela crée un delta produit trop large par rapport au besoin initial.

### Project Structure Notes

- Fichiers probablement modifiés:
  - `frontend/src/pages/DashboardPage.tsx`
  - `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
  - `frontend/src/App.css`
  - `frontend/src/i18n/dashboard.tsx`
- Fichiers probablement ajoutés:
  - `frontend/src/api/useBirthData.ts` ou équivalent
  - `frontend/src/components/dashboard/useDashboardAstroSummary.ts` ou équivalent
- Fichiers de test:
  - `frontend/src/tests/DashboardPage.test.tsx`

### Technical Requirements

- Réutiliser TanStack Query pour toute donnée serveur supplémentaire nécessaire au dashboard.
- Ne pas appeler `getBirthData` directement dans le rendu d'un composant.
- Dériver `userId` depuis une source stable déjà disponible (`getSubjectFromAccessToken`, `auth/me`) pour éviter les variations inutiles.
- Prévoir un fallback visuel quand `astro_profile.sun_sign_code` est absent, sans bloquer le résumé.

### Architecture Compliance

- Respecter la séparation actuelle:
  - données serveur dans `frontend/src/api`
  - mapping ou hook UI dans `frontend/src/components/dashboard` ou `frontend/src/utils`
  - rendu dans le composant dashboard
- Ne pas glisser de logique d'animation ou de dérivation métier directement dans `DashboardPage.tsx`.
- Ne pas introduire de couplage avec `/dashboard/horoscope` ou la page détail pour calculer le fond de la landing.

### Library / Framework Requirements

- Réutiliser React Query déjà présent dans le projet pour `birth-data`.
- Réutiliser les utilitaires auth existants (`useAccessTokenSnapshot`, `getSubjectFromAccessToken`) plutôt que dupliquer la logique utilisateur.
- Pas de nouvelle bibliothèque de styling ou d'animation.

### File Structure Requirements

- Garder le code de récupération `birth-data` dans `frontend/src/api`.
- Garder le mapping visuel dashboard proche de la feature dashboard, pas dans le composant canvas générique.
- Limiter le delta dans `DashboardPage.tsx` au branchement des hooks et props, pas à la logique détaillée de calcul.

### Testing Requirements

- Étendre `DashboardPage.test.tsx` avec le nouveau chemin de données `birth-data`.
- Vérifier que la carte reste activable au clavier.
- Vérifier qu'un fallback neutre s'affiche si le signe est indisponible.
- Vérifier qu'aucune régression ne fait disparaître `ShortcutsSection`.

### Project Context Reference

- Aucun `project-context.md` n'a été détecté dans le dépôt lors de la génération.
- Appliquer les conventions de `AGENTS.md`, de `architecture.md` et des epics 45 / 48.

### References

- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#5-variables-metier-a-injecter]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#7-logique-de-couleur-selon-l-humeur-du-jour]
- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md#15-integration-cote-backend-front]
- [Source: _bmad-output/planning-artifacts/epic-48-fond-astrologique-anime-dashboard.md]
- [Source: _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]
- [Source: _bmad-output/implementation-artifacts/45-4-verrouiller-qa-accessibilite-et-coherence-i18n-du-parcours-dashboard.md]
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/api/useDailyPrediction.ts]
- [Source: frontend/src/api/birthProfile.ts]
- [Source: frontend/src/api/authMe.ts]
- [Source: frontend/src/i18n/dashboard.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée selon le workflow BMAD create-story en mode autonome.
- Contexte extrait du dashboard courant, de l'API `birth-data` et des stories 45.x.

### Completion Notes List

- Story context prêt pour implémentation.
- Mapping `prediction + birth profile + user seed` explicitement cadré pour éviter la duplication.
- DashboardHoroscopeSummaryCard adaptated to consume `AstroMoodBackground` locally via `astroBackgroundProps`.
- SVG rendering fixed by dropping Vite's SVG plugin and instead using the previously engineered `getZodiacIcon` React components map. SVGs scaled seamlessly using `stroke: currentColor`.
- Injected `useThemeSafe` context to ensure the `DashboardHoroscopeSummaryCard` text elements flip to white during `dark` mode and remain high contrast `var(--text-1)` during light mode to remain readable over the `AstroMoodBackground`.

### File List

- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
- `frontend/src/api/useBirthData.ts`
- `frontend/src/components/dashboard/useDashboardAstroSummary.ts`
- `frontend/src/i18n/dashboard.tsx`
- `frontend/src/App.css`
- `frontend/src/tests/DashboardPage.test.tsx`
