# Story 60.17 : Refonte visuelle premium et glassmorphism maîtrisé de `/dashboard/horoscope`

Status: done

## Story

En tant qu'utilisateur de la page `/dashboard/horoscope`,
je veux une expérience visuelle plus premium, plus cohérente et mieux hiérarchisée,
afin de percevoir immédiatement les priorités de lecture du jour dans un langage glassmorphism maîtrisé au lieu d'un empilement de cartes pastel au poids visuel équivalent.

## Acceptance Criteria

### AC1 — Unification de la direction visuelle au niveau page

1. La page `/dashboard/horoscope` adopte une seule colonne vertébrale colorielle dominée par les violets/lilas, avec des neutres chauds pour le fond et des couleurs secondaires limitées à des usages sémantiques ponctuels.
2. Le fond global de la page n'utilise plus d'aplats uniformes : il combine un dégradé doux `#f7f2f8 -> #ede4f6` et 2 à 3 halos radiaux larges reprenant une direction proche de :
   - halo violet `rgba(156, 121, 255, 0.18)`
   - halo rose `rgba(255, 211, 236, 0.16)`
   - halo blanc `rgba(255, 255, 255, 0.45)`
3. Le fond global conserve un noise très fin, discret et premium (2 à 3% d’opacité effective), sans donner un rendu sale.
4. Les variables CSS de la page sont rationalisées autour d’un système unique de surfaces glass, profondeurs, rayons, ombres, texte et accents, au lieu d’accumuler des variations ad hoc par section.
5. Le vert ne pilote plus la structure visuelle des cartes. Il ne peut subsister que comme accent sémantique rare sur des signaux exceptionnellement favorables.

### AC2 — Hiérarchie de profondeur limitée à 3 niveaux

6. Toute la page respecte au maximum 3 niveaux de profondeur visuelle :
   - niveau 0 : fond global diffus, sans contours marqués
   - niveau 1 : cartes standards en verre léger
   - niveau 2 : cartes focus avec plus d’opacité, plus de lumière interne, une ombre plus présente et un blur légèrement supérieur
7. Les surfaces glass du niveau standard suivent une direction proche de :
   - surface 1 `rgba(255,255,255,0.34)`
   - surface 2 `rgba(255,255,255,0.46)`
   - bordure `1px solid rgba(255,255,255,0.42)`
   - bordure renforcée `1px solid rgba(196,177,235,0.42)`
   - `backdrop-filter: blur(18px) saturate(145%)`
   - ombre `0 12px 40px rgba(88, 58, 130, 0.10)`
   - lumière interne `inset 0 1px 0 rgba(255,255,255,0.42)`
8. Les composants principaux de la page n’introduisent pas de nouveaux systèmes d’ombre, de border radius ou de blur hors de ces 3 niveaux.

### AC3 — Cadre global, grille et typographie premium

9. La page adopte un cadre visuel plus éditorial :
   - mobile : largeur utile `100%` avec `padding-inline: 20px`
   - tablette / desktop : `max-width: 760px` centré
   - espacement vertical entre sections : `24px`
   - padding interne des cartes : `20px` ou `24px` selon le niveau
10. Les rayons sont strictement rationalisés :
   - hero : `28px`
   - cartes principales : `24px`
   - mini-panels : `18px`
   - pills / capsules : `999px`
11. La page respecte une échelle typographique cohérente :
   - titre de page : 40px / 1.05 / 700
   - titre de section : 20px / 1.2 / 600
   - meta / sous-titre : 13px / 1.3 / 500
   - texte courant : 15px / 1.65 / 400
   - micro-label : 11 à 12px, uppercase léger, `letter-spacing: 0.06em`
12. Les composants ne multiplient pas inutilement les poids de police : utiliser prioritairement `400`, `500`, `600`, `700`.

### AC4 — Recomposition éditoriale du haut de page

13. La zone header de `/dashboard/horoscope` est recomposée en entrée de page éditoriale :
   - le bouton retour conserve sa fonction mais devient un bouton verre circulaire de 36 à 40px
   - le libellé “Aujourd’hui” est plus discret et secondaire
   - la date devient l’élément visuel principal
   - le badge d’état est placé sous la date, aligné à gauche, intégré au système glass
14. Le badge principal adopte un style frosted cohérent :
   - fond `rgba(255,255,255,0.38)`
   - bordure `1px solid rgba(156,121,255,0.25)`
   - texte violet moyen
   - ombre minimale
15. L’ombre du badge n’est plus coupée par un conteneur parent.

### AC5 — Hero card comme pièce maîtresse

16. `DayClimateHero` devient la carte focus majeure de la page :
   - hauteur minimum 220 à 240px
   - padding interne 24px
   - composition en 2 zones : contenu à gauche ~60%, décor astro à droite ~40%
   - fond interne plus contrasté et plus cinématographique que les autres cartes
17. La lisibilité du texte est renforcée par un voile sombre très léger ou une couche de contraste local derrière la zone de contenu, sans casser l’effet glass.
18. Le décor astro côté droit reste fin et élégant :
   - halo lumineux flou local
   - constellation plus subtile
   - points lumineux nets mais peu nombreux
19. Le titre principal de la hero n’utilise plus de vert structurel ; il s’appuie sur un violet profond ou un quasi-noir chaud.
20. Le texte de la hero respecte une meilleure respiration :
   - largeur de lecture max 38 à 45 caractères
   - espacement de 16px entre titre et texte
   - espacement de 18px avant les pills
21. Les pills de la hero sont harmonisées avec le reste de la page :
   - hauteur 28 à 30px
   - fond semi-transparent
   - bordure blanche très douce
   - texte 12px medium
   - icônes discrètes et cohérentes

### AC6 — Section “Astrologie du jour” traitée comme lecture analytique

22. `AstroDailyEvents` est traitée comme une carte analytique et non comme une simple boîte uniforme :
   - header interne distinct
   - introduction visuellement séparée des groupes d’aspects
   - grille 2 colonnes sur grand mobile / tablette, 1 colonne sur petit mobile
23. Chaque groupe d’aspects a son mini sous-bloc, mais sans recréer de grosses cartes opaques.
24. Les items ressemblent à des capsules analytiques premium, sobres et régulières :
   - fond `rgba(255,255,255,0.42)`
   - bordure `1px solid rgba(255,255,255,0.34)`
   - rayon `12px`
   - padding `10px 12px`
   - texte `13px`
   - ombre nulle ou quasi imperceptible

### AC7 — Rationalisation de la section “Vos domaines clés”

25. `DomainRankingCard` est recomposée sur un pattern uniforme ligne par ligne :
   - à gauche : icône dans mini rond glass 24px + libellé
   - à droite : score numérique dans capsule puis statut dans capsule outline
   - sous la ligne : barre de progression fine alignée sur toute la largeur
26. Les barres suivent une gamme majoritairement violet/lilas :
   - track de 6px
   - fond du track `rgba(123,104,180,0.14)`
   - fill en dégradé violet clair vers violet dense
   - lueur légère uniquement pour les meilleurs scores
27. Les statuts Favorable / Stable / Très favorable utilisent un même composant visuel ; seule la teinte varie légèrement.
28. Les séparations entre lignes se font davantage par l’espace que par des traits visibles.

### AC8 — Refonte stylistique du “Déroulé de votre journée”

29. `DayTimelineSectionV4` abandonne les grosses bordures colorées ou fonds colorés structurels par période.
30. Toutes les cartes de période partagent la même base :
   - fond glass uniforme
   - bordure blanche/lilas identique
   - padding 20px
   - rayon 22px
   - espacement vertical 14 à 16px
31. La couleur n’existe plus que comme accent secondaire :
   - petit liseré en haut
   - badge horaire ou badge statut
   - pastille d’icône
   - marqueur de timeline
32. Les accents de période restent subtils et confinés aux détails :
   - Nuit : violet bleuté doux
   - Matin : champagne / ambre pastel
   - Après-midi : lilas froid
   - Soirée : prune légère
33. La structure interne de chaque carte est rationalisée :
   - ligne 1 : icône + nom de période / heure + statut
   - ligne 2 : titre fort
   - ligne 3 : texte
   - ligne 4 : mini liste d’indices ou marqueurs secondaires
34. Une timeline verticale discrète ou un fil narratif équivalent est ajoutée à la section pour relier visuellement les 4 périodes.

### AC9 — Carte “Conseil du jour” plus précieuse et conclusive

35. `DailyAdviceCard` se distingue légèrement des cartes standards :
   - fond glass plus dense
   - halo local derrière l’icône
   - contraste du titre renforcé
   - rendu plus éditorial, moins “bloc générique”
36. La phrase finale de la carte devient l’élément textuel le plus visible, avec `font-weight: 600`.
37. Le fond bas de page éventuel reste très doux et ne crée pas de “nappe violette” autonome qui concurrence les cartes.

### AC10 — Icônes, micro-interactions et discipline système

38. Les icônes visibles sur `/dashboard/horoscope` sont unifiées en line icons cohérentes, idéalement Lucide, avec trait fin homogène ; les emojis décoratifs sont retirés des surfaces premium.
39. Les icônes de section ou de statut sont rendues dans de petits contenants ronds ou squircle semi-transparents cohérents avec le système glass.
40. Les micro-interactions suivent un même langage :
   - hover carte : translation Y `-2px`
   - augmentation légère de luminosité / opacité
   - bordure plus lumineuse
   - durée 180 à 220ms
   - easing doux
41. Le système ne dépasse pas 3 familles d’ombres :
   - page flottante : `0 18px 60px rgba(76,52,122,0.08)`
   - carte standard : `0 10px 30px rgba(76,52,122,0.08)`
   - focus / hover : `0 16px 40px rgba(76,52,122,0.14)`

### AC11 — Non-régression fonctionnelle et garde-fous de mise en œuvre

42. La story est strictement front/style : aucun changement de contrat API, de DTO backend ou de logique métier horoscope n’est introduit.
43. Les styles inline encore présents sur les composants concernés sont migrés vers les fichiers CSS existants lorsque cela améliore la cohérence et la maintenabilité.
44. Les composants réutilisent au maximum les traces de design system déjà présentes dans le front, notamment les acquis des epics 17, 49 et 58, au lieu de recréer un nouveau langage graphique parallèle.
45. Vérifications minimales requises :
   - `npx tsc --noEmit`
   - tests Vitest ciblés sur la page horoscope et les CSS statiques concernés
   - vérification manuelle de la page sur mobile et desktop

## Tasks / Subtasks

- [x] T1 — Refondre le socle visuel global de la page (AC: 1, 2, 3, 10, 11, 12)
  - [x] T1.1 — Recentrer `DailyHoroscopePage.css` autour d’un système unique de tokens page-level (`fond`, `surface`, `border`, `shadow`, `text`, `accent`)
  - [x] T1.2 — Réduire les couleurs structurelles concurrentes et faire du violet la teinte maîtresse
  - [x] T1.3 — Ajuster `backgrounds.css` ou les halos page-level pour soutenir le rendu glass sans attirer plus l’attention que les cartes

- [x] T2 — Recomposer le header éditorial (AC: 4)
  - [x] T2.1 — Ajuster `TodayHeader`, `DailyPageHeader` et `DayStateBadge` pour installer la hiérarchie “Aujourd’hui” / date / badge
  - [x] T2.2 — Unifier les styles du bouton retour, du badge et des micro-meta
  - [x] T2.3 — Vérifier qu’aucun parent ne coupe les ombres utiles

- [x] T3 — Renforcer la hero card comme carte focus (AC: 5)
  - [x] T3.1 — Faire évoluer `DayClimateHero.tsx/css` sans perdre `AstroMoodBackground`
  - [x] T3.2 — Recomposer la zone texte et la zone décor en 60/40 avec meilleur contraste
  - [x] T3.3 — Harmoniser pills, chips et meilleure fenêtre avec le nouveau système

- [x] T4 — Recomposer les cartes analytiques standards (AC: 6, 7, 9)
  - [x] T4.1 — Retravailler `AstroDailyEvents.tsx/css` en carte analytique découpée
  - [x] T4.2 — Rationaliser `DomainRankingCard.tsx/css` autour d’un pattern ligne + barre premium
  - [x] T4.3 — Donner à `DailyAdviceCard.tsx/css` un statut de carte conclusive plus précieuse

- [x] T5 — Refaire le langage visuel de la timeline (AC: 8)
  - [x] T5.1 — Uniformiser les fonds et bordures de `DayTimelineSectionV4`
  - [x] T5.2 — Remplacer les différenciations structurelles par des accents fins
  - [x] T5.3 — Ajouter un fil visuel discret entre les périodes

- [x] T6 — Aligner les cartes secondaires et les composants transverses (AC: 2, 10, 11)
  - [x] T6.1 — Harmoniser `TurningPointCard`, `BestWindowCard`, `AstroFoundationSection` avec les mêmes rayons, profondeurs et capsules
  - [x] T6.2 — Unifier l’iconographie et retirer les restes d’emojis décoratifs si présents
  - [x] T6.3 — Rationaliser les hovers et transitions pour toute la page

- [x] T7 — Tests et validation visuelle (AC: 11)
  - [x] T7.1 — Mettre à jour les tests statiques CSS si les tokens ou structures attendues changent
  - [x] T7.2 — Vérifier `npx tsc --noEmit`
  - [x] T7.3 — Exécuter les tests Vitest ciblés sur la page horoscope
  - [x] T7.4 — Valider manuellement le rendu mobile et desktop de `/dashboard/horoscope`

## Dev Notes

### Contrainte de périmètre

Cette story est une **évolution stylistique frontend uniquement**. Elle ne doit pas modifier :
- le payload `GET /v1/predictions/daily`
- les mappers métier existants
- les DTO backend ou TypeScript hors besoin purement de présentation
- la logique de calcul, d’assemblage ou d’interprétation du daily horoscope

### Composants et fichiers à cibler en priorité

**Page / shell**
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/styles/backgrounds.css`

**Header**
- `frontend/src/components/TodayHeader.tsx`
- `frontend/src/components/prediction/DailyPageHeader.tsx`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayStateBadge.tsx`
- `frontend/src/components/prediction/DayStateBadge.css`

**Hero**
- `frontend/src/components/DayClimateHero.tsx`
- `frontend/src/components/DayClimateHero.css`
- `frontend/src/components/astro/AstroMoodBackground.tsx`
- `frontend/src/components/astro/AstroMoodBackground.css`

**Sections standards**
- `frontend/src/components/AstroDailyEvents.tsx`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/BestWindowCard.tsx`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/components/prediction/DailyAdviceCard.tsx`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/AstroFoundationSection.tsx`
- `frontend/src/components/AstroFoundationSection.css`

**Timeline**
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`

### Réutilisation impérative des acquis existants

- Réutiliser les patterns et traces de style déjà présents dans les stories de l’epic 58, notamment :
  - header éditorial
  - hero premium
  - timeline sophistiquée
  - conseil du jour
- Réutiliser aussi les tokens et primitives des epics 17 et 49 au lieu de réinventer un second design system.
- La page a déjà commencé à converger vers un socle glass unifié ; la story doit **consolider** cette direction, pas repartir d’un style parallèle.

### Garde-fous de mise en œuvre

- Pas de Tailwind.
- CSS pur et variables custom du projet uniquement.
- Limiter les styles inline aux cas réellement dynamiques impossibles à exprimer proprement en CSS.
- Si une variation de couleur ou de profondeur est introduite, elle doit passer par des variables ou classes claires, pas par des valeurs éparses dans plusieurs composants.
- Ne pas réintroduire de grosses bordures colorées sur les cartes timeline.
- Ne pas mélanger emoji et line icons sur les surfaces premium.

### Stratégie de test recommandée

- Cibler au minimum :
  - `frontend/src/tests/DailyHoroscopePage.test.tsx`
  - les tests CSS statiques existants autour de `backgrounds.css` si les halos ou le noise changent
  - les tests des composants les plus impactés si présents
- Ajouter ou adapter les assertions de non-régression uniquement là où elles sécurisent la nouvelle hiérarchie visuelle sans sur-spécifier des détails fragiles.

### Project Structure Notes

- Les composants restent à leur emplacement actuel ; pas de refactor structurel hors nécessité forte.
- Les mappers (`dayClimateHeroMapper`, `astroDailyEventsMapper`, `domainRankingCardMapper`, etc.) restent la source des view models ; la story n’est pas un prétexte pour déplacer de la logique métier côté JSX.
- Le langage visuel doit être piloté principalement depuis les CSS de page et de composants, pas depuis `tsx` avec des objets style volumineux.

### References

- `_bmad-output/planning-artifacts/epic-60-refonte-v4-horoscope-du-jour.md`
- `_bmad-output/implementation-artifacts/58-7-refonte-layout-page-horoscope-quotidien.md`
- `_bmad-output/implementation-artifacts/58-8-daily-page-header-bar.md`
- `_bmad-output/implementation-artifacts/58-9-hero-summary-card.md`
- `_bmad-output/implementation-artifacts/58-11-day-timeline-section.md`
- `_bmad-output/implementation-artifacts/58-12-detail-and-scores-section.md`
- `_bmad-output/implementation-artifacts/58-13-daily-advice-card.md`
- `_bmad-output/implementation-artifacts/17-10-correctifs-p0-contrastes-tokens-et-fonds-premium.md`
- `_bmad-output/implementation-artifacts/17-11-correctifs-p0-header-hero-glass-cta-constellation.md`
- `_bmad-output/implementation-artifacts/49-1-design-tokens-couleurs-semantiques-et-surfaces.md`
- `_bmad-output/implementation-artifacts/49-2-design-tokens-typo-espacement-rayons-ombres-animations.md`
- `_bmad-output/implementation-artifacts/49-4-systeme-glassmorphism-mutualise.md`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/styles/backgrounds.css`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story créée à partir du cadrage utilisateur et des acquis design des epics 17, 49, 58 et 60.
- Le scope est volontairement borné à une refonte stylistique frontend sans changement de payload métier.
- Les AC sont structurés pour permettre une implémentation incrémentale carte par carte tout en gardant un socle visuel unique.
- L’implémentation finale a dépassé la première passe “cohérente et propre” pour intégrer une vraie finition premium : colonne desktop élargie, fond plus atmosphérique, surfaces glass plus denses et micro-composants harmonisés.
- Le header a été recomposé pour intégrer l’action de refresh dans la même bande éditoriale que le titre et le badge d’état, avec moins de vide structurel.
- La hero card a été rééquilibrée pour supprimer l’effet de “carte dans la carte” trop visible : le voile de lecture est désormais diffus, la zone décorative droite est plus présente, et la composition texte/décor est mieux proportionnée.
- La timeline a été consolidée en parcours vertical premium : rail plus proche des cartes, points plus présents, cartes de période plus denses, et tags d’aspects/domaines rendus comme de vrais micro-tags analytiques.
- Les blocs `AstroDailyEvents`, `DomainRankingCard` et `DailyAdviceCard` ont été harmonisés dans un langage moins “UI fonctionnelle” et plus éditorial, avec des capsules, badges et halos cohérents.
- Vérifications exécutées après les dernières retouches :
  - `npx tsc --noEmit`
  - `npm run test -- src/tests/DailyHoroscopePage.test.tsx src/tests/AstroMoodBackground.test.tsx src/tests/visual-smoke.test.tsx`

### File List

- `_bmad-output/implementation-artifacts/60-17-refonte-visuelle-premium-page-horoscope.md`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyPageHeader.tsx`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/DayClimateHero.tsx`
- `frontend/src/components/DayClimateHero.css`
- `frontend/src/components/AstroDailyEvents.tsx`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/AstroFoundationSection.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/i18n/horoscope_copy.ts`
- `frontend/src/components/prediction/DomainIcon.tsx`
- `frontend/src/app/routes.tsx`
- `frontend/src/components/BestWindowCard.tsx`
- `frontend/src/components/AstroFoundationSection.tsx`
- `frontend/src/components/TurningPointCard.tsx`
