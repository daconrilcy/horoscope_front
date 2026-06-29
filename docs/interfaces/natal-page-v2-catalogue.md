<!-- Commentaire global: ce catalogue decrit le layout cible de la page /natal V2 et sert de reference de refactorisation frontend. -->

# Catalogue Interface - Page Natal V2

## Reference Visuelle

La reference est `docs/interfaces/natal_page_v2.png`, capture desktop 1536 x 1024. Le modele attendu est une page de lecture natale scannable: navigation locale a gauche, lecture principale a droite, bandeau de marqueurs astraux, puis chapitres narratifs.

## Layout

Le shell conserve le header applicatif global existant. Dans la route `/natal`, la page completed utilise une grille locale en deux colonnes:

- `Sommaire`: colonne gauche sticky, limitee au parcours de lecture.
- `Contenu principal`: colonne droite, largeur commune pour hero, bandeau, cartes et details.

Sur tablette et mobile, la grille devient mono-colonne. Le sommaire passe au-dessus de la lecture sous forme compacte, sans modifier la sidebar globale de l'application ni la bottom nav mobile.

## Elements

- **Sommaire**
  - Titre `Sommaire`.
  - Pourcentage de progression derive du chapitre actif.
  - Barre de progression native.
  - Liste des chapitres avec numero colore, titre court et extrait sur desktop.
  - Lien vers le guide de lecture.

- **Header Lecture**
  - Pictogramme astral.
  - Fil d'Ariane visuel: `Accueil`, `Mon theme natal`, `Lecture`.
  - H1 issu du titre public Astral.
  - Resume court si disponible.
  - Badge statut issu du plan ou de la qualite de lecture.

- **Bandeau Astral**
  - Quatre cellules: `Soleil`, `Lune`, `Ascendant`, `Statut`.
  - Chaque cellule contient icone, libelle, valeur principale et detail.
  - Les trois premiers marqueurs viennent des faits publics normalises; le statut vient du view model de lecture.

- **Carte Chapitre**
  - Numero rond colore.
  - Titre complet du chapitre.
  - Temps de lecture estime cote UI.
  - Encadre `A retenir`.
  - Paragraphes publics avec divulgation progressive.
  - Ligne `Reperes & evidences` avec confiance, bases astrologiques et notes de prudence quand elles existent.

- **Base Du Calcul Natal**
  - Panneau secondaire repliable.
  - Conserve les groupes existants: reperes principaux, maisons, planetes notables, aspects notables.
  - Ne remonte aucun identifiant technique ou payload Astral brut.

- **Etats Non Completed**
  - Les etats `idle`, `working`, `transport-error` et `terminal-error` restent rendus par `NatalJobCard`.
  - L'en-tete introductif standard reste visible avant lecture complete.

## Composants Frontend

- `NatalChartPage`: orchestre la page, le hook Astral et le guide final.
- `NatalJobCard`: conserve les etats du job et les actions de lancement/reprise.
- `NatalAstralReading`: porte le layout V2 completed.
- `NatalReadingSummaryNav`: sommaire local et progression.
- `NatalReadingHero`: header de lecture et titre public.
- `NatalReadingMetricsBar`: bandeau Soleil/Lune/Ascendant/Statut.
- `NatalReadingChapterCard`: carte chapitre V2 avec accordions ARIA.
- `NatalReadingFactsDetails`: panneau repliable de base de calcul.

## Contraintes

- Aucun style inline.
- Aucun appel direct a Astral depuis le navigateur.
- Aucune modification backend ou contrat API.
- Les deux premiers chapitres principaux restent ouverts par defaut.
- Les boutons gardent `aria-expanded` et `aria-controls`.
- A 360 px, 390 px et 430 px, le layout ne doit pas deborder horizontalement.
