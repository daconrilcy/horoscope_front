<!-- Commentaire global: ce document audite le style de la page /natal V2 face a la maquette de reference et fixe les ecarts a corriger. -->

# Audit Style - Page Natal V2

## Sources Et Perimetre

- Maquette de reference: `docs/interfaces/natal_page_v2.png`, capture desktop 1536 x 1024.
- Catalogue fonctionnel: `docs/interfaces/natal-page-v2-catalogue.md`.
- Implementation inspectee: `frontend/src/pages/NatalChartPage.tsx`, `frontend/src/features/natal-chart/NatalJobCard.tsx`, `frontend/src/features/natal-chart/NatalAstralReading.tsx`, `frontend/src/features/natal-chart/natalTheme.css`, `natalCards.css`, `natalBadges.css`, `NatalReading.css`, `NatalReadingFacts.css`, `NatalJobCard.css`.
- Guardrails applicables: `RG-047`, `RG-052`, `RG-178`, `RG-180`, `RG-182`, `RG-183`, `RG-184`.

## Inventaire De L'Implementation Actuelle

La route `/natal` est composee par `NatalChartPage`. Elle affiche le header introductif seulement tant que le job Astral n'est pas completed. Le rendu du job est delegue a `NatalJobCard`, qui gere les etats `idle`, `working`, `transport-error`, `terminal-error` et `completed`. En completed, `NatalJobCard` rend `NatalAstralReading` dans le meme wrapper `.natal-card` que les etats courts.

`NatalAstralReading` porte le layout V2: grille deux colonnes, sommaire local sticky, hero de lecture, bandeau de quatre metriques, chapitres progressifs, base de calcul repliable, explications moteur Astral, disclaimer. Les deux premiers chapitres principaux sont ouverts par defaut. Les boutons de chapitre conservent `aria-expanded` et `aria-controls`; le sommaire utilise `aria-current`.

Les styles sont separes par role:

- `natalTheme.css`: variables locales de page, surfaces, bordures, rayons, ombres, texte, badges et typographie.
- `natalCards.css`: enveloppes communes `.natal-card`, `.natal-reading-facts`, `.natal-reading__chapter`.
- `natalBadges.css`: variantes de badges publiques, donnees astrologiques, confiance, repere et statut.
- `NatalReading.css`: layout de lecture, sommaire, hero, metriques, chapitres, accordions et repères.
- `NatalReadingFacts.css`: panneau secondaire de base de calcul.
- `NatalJobCard.css`: etats de job, erreur, loading et actions.

L'implementation respecte deja la structure fonctionnelle cible, mais l'identite visuelle reste plus "glass premium pastel" que la maquette: surfaces translucides, gradients doux, ombres plus larges, badges epais, accents violets nombreux et carte completed globale.

## Description Ultra Detaillee De La Maquette

La maquette presente une page claire, blanche et editee, dans un shell applicatif tres fin. Le header global est horizontal, blanc, separe du contenu par une ligne gris-lavande pale. A gauche, l'icone menu, un separateur vertical, le logo et le nom `Astroraison`. A droite, quatre actions compactes: theme, globe, favori ou signet, avatar. Ces elements restent discrets pour laisser la lecture dominer.

Le fond de page est presque blanc, avec une nuance froide tres legere. Il n'y a pas de halo decoratif visible, pas de bokeh, pas de gradient fort. La profondeur vient surtout des bordures fines et des ombres tres douces sous les cartes.

La zone de contenu commence sous le header avec une grille en deux colonnes. Le sommaire occupe une colonne fixe etroite a gauche, proche de 212 px. Le contenu principal occupe tout le reste, avec un espace horizontal modere entre les deux colonnes. Les marges externes sont contenues: la page est dense, mais respire par des espaces verticaux reguliers.

Le sommaire est une carte blanche a rayon moyen. Son en-tete contient `Sommaire`, le pourcentage `0% complete` et une barre de progression tres basse. Une ligne horizontale separe cet en-tete de la timeline. La timeline affiche six etapes verticales. Chaque etape a une pastille numerotee circulaire, pleine, coloree selon le chapitre. Une ligne verticale gris pale connecte les pastilles. Les titres sont bleu-nuit et gras; les descriptions sont plus petites, gris-bleu, sur deux ou trois lignes. Le CTA `Guide de lecture` est en bas dans un bouton blanc borde, avec icone livre a gauche et chevron a droite.

Le hero de lecture est compact. A gauche, un pictogramme astral carre arrondi, blanc, borde, avec motif circulaire violet et petites etoiles orange. A droite, le breadcrumb est petit, violet/gris, avec chevrons fins. Le H1 `Lecture du theme natal` est tres grand, bleu-nuit, gras, avec ligne courte. Le texte d'introduction est plus petit, gris-bleu, sur deux lignes, sans carte autour.

Le bandeau astral est une grande carte horizontale blanche. Il contient quatre cellules egales: Soleil, Lune, Ascendant, Statut. Chaque cellule a une icone ronde pastel a gauche, un label petit, une valeur principale en gras, puis un detail secondaire. Les cellules sont separees par de fines lignes verticales lavande. Les couleurs sont differenciees: Soleil orange, Lune turquoise, Ascendant violet/bleu, Statut violet.

Les cartes chapitre sont les elements dominants. Elles sont blanches, a bordure fine gris-lavande, rayon moyen et ombre subtile. Une barre verticale coloree a gauche marque le chapitre. Le haut de carte aligne la pastille numerotee, le titre, le badge de temps de lecture et un chevron de repli a droite. Le titre est bleu-nuit, gras, en une ligne longue. Le badge temps est petit, borde, blanc, avec icone horloge.

Le bloc `A retenir` est un encadre interne tres important. Il a un fond tres legerement teinte par la couleur du chapitre, une bordure coloree, un rayon plus petit que la carte et une icone ampoule coloree a gauche. Le label `A retenir` est gras, puis le texte est compact et lisible. Ce bloc donne le resume editorial avant le detail.

Les paragraphes de lecture sont denses mais confortables. La couleur est bleu-nuit adoucie, l'interligne est lisible, la largeur du texte reste controlee. Les paragraphes ne sont pas enfermes dans une sous-carte. Le contenu se lit comme un rapport editorial.

La ligne `Reperes & evidences` est compacte. Le label est gras. Les evidences apparaissent en petits badges rectangulaires blancs, bordes, peu hauts, avec icones fines. Ces badges ne doivent pas avoir le meme poids que les informations principales.

La palette est polyphonique mais calme. Chapitre 1 violet, chapitre 2 turquoise, chapitre 3 orange, chapitre 4 bleu, chapitre 5 jaune/orange, chapitre 6 violet. Le violet reste reserve aux accents importants, au statut et a l'etat actif; les surfaces neutres restent blanches.

Responsive implicite: la maquette desktop privilegie une colonne gauche sticky et une lecture large. Sur tablette et mobile, la structure doit devenir mono-colonne, le sommaire passer au-dessus en version compacte, les metriques s'empiler sans debordement, les repères longs se wrapper et les cibles tactiles rester au moins a 44 px.

## Ecarts Constates

| Zone | Maquette | Implementation actuelle | Ecart a corriger |
| --- | --- | --- | --- |
| Enveloppe completed | Lecture sans grande carte globale | `NatalJobCard` garde `.natal-card` autour de `NatalAstralReading` | Neutraliser la surface completed |
| Fond et surfaces | Blanc net, bordures fines | Glass semi-transparent, blur, ombres premium | Recalibrer les variables `/natal` vers blanc/quasi opaque |
| Hero | Compact, pictogramme image-like, H1 dominant | Hero proche mais pictogramme lucide simple et surface glass | Garder la structure, alleger surface et ombre |
| Metriques | Quatre tons distincts | Icones principalement violettes | Ajouter tons deterministes par metrique |
| Sommaire | Timeline nette, header separe, CTA bas compact | Sommaire proche mais plus glass et moins separe | Renforcer separation et densite |
| Chapitres | Cartes blanches plates, accent gauche | Gradient pastel, bordures et ombres plus premium | Supprimer gradient visible et renforcer carte blanche |
| A retenir | Encadre avec ampoule et bordure coloree | Encadre sans icone, accent discret | Ajouter icone et ton theme |
| Badges | Petits badges bas, rectangulaires | `padding: 12px` desktop sur plusieurs badges | Reduire hauteurs et paddings |
| Repères | Ligne compacte sous texte | Aside/panneau meta visuel | Desktop en ligne compacte; mobile repli conserve |
| Base calcul | Annexe secondaire | Panneau encore assez present | Diminuer poids visuel |

## Plan D'Evolution Priorise

1. Corriger l'enveloppe completed pour que la lecture ne soit pas incluse dans une grande carte globale.
2. Recalibrer les tokens locaux `/natal`: surface blanche, bordures fines, ombres faibles, rayon proche de la maquette.
3. Ajouter les classes de ton aux metriques et aux chapitres, puis colorer uniquement icones, index, bordures et accents.
4. Ajouter l'icone ampoule decoratif au bloc `A retenir`.
5. Compacter les badges desktop et harmoniser leurs roles: statut, confiance, donnee cle, detail, evidence.
6. Rapprocher le sommaire de la timeline de la maquette: header separe, progress bas, connecteur plus fin, CTA compact.
7. Rendre les cartes chapitre blanches et editoriales; garder le mobile mono-colonne et le repli des repères.
8. Rendre `Base du calcul natal` plus annexe: surface claire, ombre plus faible, groupes plus discrets.

## Criteres D'Acceptation Visuelle

- A 1536 x 1024, la page donne une impression blanche, nette et compacte proche de la maquette.
- Le sommaire, les metriques et les cartes chapitre partagent une largeur et des rayons coherents.
- Les cartes chapitre n'ont plus de gradient visible.
- Les badges desktop sont bas et lisibles, sans `padding: 12px`.
- Les metriques ont des tons distincts et comprehensibles.
- Le bloc `A retenir` contient une icone decoratif et une bordure de chapitre.
- La lecture progressive, les deux premiers chapitres ouverts, les accordions ARIA et les repères mobiles restent fonctionnels.
- Aucun style inline, aucun appel Astral direct, aucune surface legacy natal.
