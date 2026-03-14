# Epic 48 Quality Gate: Astro Mood Background Dashboard

## 1. Accessibilité (A11y)
- **Décoration** : Le canvas a la propriété `aria-hidden="true"` pour ne pas perturber les lecteurs d'écran.
- **Mouvement Réduit** : Le composant vérifie et respecte la media query `(prefers-reduced-motion: reduce)`. L'animation stoppe sans faire de régression visuelle ou planter.
- **Contraste** : Les configurations nominales de couleurs ciblent et respectent le WCAG AA, le fond gardant des couleurs modérées pour laisser lisible le résumé par dessus.
- **Raccourcis Claviers** : La carte résumé de l'horoscope a été confirmée active aux évènements claviers `Space` et `Enter`.

## 2. Performances & Stabilité
- **Cleanup / Fuites de mémoire** : Les tests en mode `React.StrictMode` avec le remounting immédiat assurent qu'il n'y ait pas de dédoublement du `requestAnimationFrame` ni de l'écouteur `ResizeObserver`.
- **Render Cycle React** : Le composant fonctionne en dehors du cycle natif de react (par mutations directes du canvas) pour s'affranchir de la pénalité de `setState` par frame.
- **Résolution Apparente (Device Pixel Ratio)** : Un plafond de sécurité `Math.min(window.devicePixelRatio || 1, 2)` a été ajouté dans le `AstroMoodBackground` pour éviter d'imploser la frame rate de dessiner sur des écrans 4K de téléphones très denses. 

## 3. Gestion des Contextes & Fallbacks Data
- **Scénarios Incomplets** : Des fallbacks robustes gèrent l'absence d'`astro_profile` ou des données passées (`sign="neutral"`, `dayScore=12`).
- **Dashboard Global** : Le système se met en pause, remonte des états *error*, ou *loading* adéquats lorsque les requêtes de `daily prediction` ne sont pas résolues, tout en préservant l'affichage des Autres Activités qui ne dépendent pas des planètes du jour.

## Stabilité Globale
Le module ne crée pas de nouvelle surcharge sur le backend, en utilisant de concert le endpoint de *prevision journalière* et les données de *profil d'anniversaire* déjà appelées en fond. La charge visuelle ajoutée satisfait aux critères de l'Epic sans alourdir indument.
