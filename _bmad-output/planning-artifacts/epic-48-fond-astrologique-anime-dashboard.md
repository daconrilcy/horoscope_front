# Epic 48: Animer le résumé astrologique du dashboard avec un fond astrologique déterministe et maintenable

Status: split-into-stories

## Contexte

L'epic 45 a stabilisé `/dashboard` comme landing distincte de `/dashboard/horoscope`, avec:

- une carte résumé courte et cliquable
- un hub d'activités visible sous le résumé
- des états `loading`, `error` et `empty` testés
- une navigation et une i18n déjà réalignées

Cette base est fonctionnellement correcte mais reste visuellement plus sobre que la direction premium déjà posée dans les epics 17.x. Le document `docs/interfaces/integration_fond_astrologique_dashboard.md` décrit maintenant une évolution ciblée du résumé astrologique:

- fond clair nacré / lavande / mauve
- grande zone de lecture respirante à gauche
- constellation lumineuse majoritairement à droite
- animation quasi imperceptible
- variation déterministe selon le signe, l'utilisateur et la date
- tonalité globale légèrement influencée par l'humeur de la journée

Le besoin ne porte pas sur une image figée ou une intégration lourde de type WebGL. Il faut produire un composant React maintenable, modifiable plus tard sans recoder toute la carte dashboard.

## Objectif Produit

Faire évoluer la carte résumé du dashboard pour qu'elle affiche un fond astrologique animé, doux et premium qui:

1. reste cohérent avec la direction visuelle du produit
2. varie de manière déterministe selon le signe, l'utilisateur et la date
3. réutilise les données front/back déjà disponibles sans nouveau contrat backend
4. respecte la lisibilité, l'accessibilité et la performance sur mobile et desktop
5. soit encapsulé dans un composant facilement modifiable pour des ajustements futurs

## Non-objectifs

- ne pas créer un service backend qui génère une image
- ne pas introduire Three.js, WebGL ou une dépendance d'animation lourde
- ne pas refondre toute la page `/dashboard/horoscope`
- ne pas déplacer la source de vérité du daily hors de `useDailyPrediction`
- ne pas changer la structure globale AppShell ou le fond plein écran déjà traité par l'epic 17
- ne pas transformer le résumé dashboard en copie de `HeroHoroscopeCard` si un delta plus petit suffit

## Diagnostic Technique

### Frontend actuel

Le parcours dashboard repose aujourd'hui sur:

- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
- `frontend/src/App.css`
- `frontend/src/i18n/dashboard.tsx`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/api/birthProfile.ts`

Forces actuelles:

- la landing `/dashboard` est déjà isolée du détail horoscope
- la carte résumé est cliquable et testée
- le produit possède déjà une grammaire visuelle premium (`AppShell`, `HeroHoroscopeCard`, fondations 17.x)
- le signe solaire est déjà exposé via `birth-data`
- la date locale et les notes journalières existent déjà dans le contrat daily

Limites actuelles:

- `DashboardHoroscopeSummaryCard` reste un panneau texte simple, sans identité astrologique spécifique
- le dashboard ne charge pas encore le `sun_sign_code`
- aucun module dédié ne centralise le mapping `prediction + profil + user -> paramètres visuels`
- aucune couche canvas animée n'existe pour ce résumé
- les garde-fous `prefers-reduced-motion`, cleanup `requestAnimationFrame` et `ResizeObserver` ne sont pas encore cadrés pour ce cas d'usage

### Backend et contrats réutilisables

Le besoin peut rester en V1 sur les contrats existants:

- `GET /v1/users/me/birth-data` pour `astro_profile.sun_sign_code`
- `GET /v1/predictions/daily` pour `meta.date_local`, `summary.overall_summary` et les `categories.note_20`
- `auth/me` ou le sujet du token pour une seed utilisateur stable

Point d'attention:

- le contrat daily n'expose pas un `dayScore` unique prêt à l'emploi; il faut donc dériver une intensité visuelle à partir des données déjà présentes au lieu d'inventer un endpoint backend supplémentaire

## Principe de mise en oeuvre

- encapsuler le fond dans un composant React dédié, par exemple `AstroMoodBackground`
- garder un dégradé stable en CSS et la couche vivante en Canvas 2D
- extraire les motifs zodiacaux et helpers de seed dans des modules typés dédiés
- dériver côté front un score visuel à partir des catégories daily existantes
- brancher ce composant dans la carte résumé dashboard en conservant navigation, i18n et états existants
- verrouiller accessibilité, reduced motion, cleanup et non-régression dashboard avant implémentation

## Découpage en stories

### Chapitre 1 - Moteur visuel réutilisable

- 48.1 Créer le composant `AstroMoodBackground` paramétrable et maintenable

### Chapitre 2 - Intégration dashboard

- 48.2 Intégrer le fond astrologique animé au résumé dashboard

### Chapitre 3 - Verrouillage final

- 48.3 Verrouiller QA, accessibilité et performance du fond astrologique

## Risques et mitigations

### Risque 1: introduire une animation coûteuse sur mobile

Mitigation:

- Canvas 2D uniquement
- nombre d'étoiles borné
- `devicePixelRatio` plafonné à `2`
- scène reconstruite uniquement au resize ou au changement de données pertinentes

### Risque 2: rendre le texte moins lisible dans la carte résumé

Mitigation:

- conserver une zone de lecture dégagée à gauche
- densifier le motif vers la droite
- verrouiller des tests et une review CSS ciblée sur la lisibilité

### Risque 3: disperser la logique métier visuelle dans les composants dashboard

Mitigation:

- centraliser le mapping `sign / userId / dateKey / dayScore`
- extraire motifs, palettes et helpers de seed hors du composant de page

### Risque 4: réinventer une deuxième grammaire premium concurrente de l'epic 17

Mitigation:

- réutiliser les tokens, effets glass et conventions visuelles déjà en place
- intégrer le nouveau fond comme évolution localisée du résumé dashboard, pas comme refonte globale

### Risque 5: dépendre d'un contrat backend absent pour le score de journée

Mitigation:

- dériver une intensité visuelle stable depuis `categories.note_20`
- documenter explicitement cette dérivation dans la story d'intégration

### Risque 6: ignorer les comportements React Strict Mode et reduced motion

Mitigation:

- nettoyer `requestAnimationFrame` et `ResizeObserver`
- figer ou simplifier l'animation si `prefers-reduced-motion` est actif
- couvrir ces comportements par des tests ciblés

## Ordre recommandé d'implémentation

### Lot 1 - Composant moteur

- 48.1

### Lot 2 - Branchage dashboard

- 48.2

### Lot 3 - Gate final

- 48.3

Chemin critique recommandé:

- 48.1 -> 48.2 -> 48.3

## Références

- [Source: docs/interfaces/integration_fond_astrologique_dashboard.md]
- [Source: _bmad-output/planning-artifacts/epics.md]
- [Source: _bmad-output/implementation-artifacts/17-2-fond-premium-gradient-noise-starfield.md]
- [Source: _bmad-output/implementation-artifacts/17-4-hero-horoscope-card-glassmorphism.md]
- [Source: _bmad-output/implementation-artifacts/45-2-creer-la-landing-dashboard-avec-resume-et-hub-d-activites.md]
- [Source: _bmad-output/implementation-artifacts/45-4-verrouiller-qa-accessibilite-et-coherence-i18n-du-parcours-dashboard.md]
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/App.css]
- [Source: frontend/src/api/useDailyPrediction.ts]
- [Source: frontend/src/api/birthProfile.ts]
