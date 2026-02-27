# Story 20.14: Guide natal - clarification approfondie et FAQ

Status: done

## Story

As a utilisateur qui consulte son thème natal,
I want une version plus claire et pédagogique de "Comment lire ton thème natal" avec une FAQ complète,
so that je comprenne précisément les notions de signes, maisons, angles, aspects et conventions de calcul.

## Acceptance Criteria

1. **Given** la page natal est affichée **When** l'utilisateur ouvre le guide pédagogique **Then** le contenu est structuré en 6 sections: signes, planètes, maisons, angles, signe solaire/ascendant, aspects.
2. **Given** chaque section du guide **When** elle est rendue **Then** le texte explicite le passage des coordonnées 0-360° vers une lecture humaine (signe + degré, maisons, angles, aspects).
3. **Given** la section maisons **When** l'utilisateur lit les conventions **Then** la règle `[debut, fin)` est explicitement documentée **And** le cas de wrap 360° -> 0° est expliqué.
4. **Given** l'utilisateur ouvre la FAQ **When** le contenu est affiché **Then** les 8 questions/réponses demandées sont présentes (360°, signes vs maisons, longitude brute, cuspide, wrap, orbe, symbole ℞, signe solaire vs ascendant).
5. **Given** le guide est affiché **When** les données natales sont incomplètes (heure absente) **Then** le texte reste cohérent avec le mode dégradé déjà en place (ascendant non calculé).
6. **Given** les tests frontend sont exécutés **When** les nouvelles sections/FAQ sont vérifiées **Then** les assertions passent sans régression des tests existants du guide natal.

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 2, 3, 5) Recomposer la structure du guide "Comment lire ton thème natal"
  - [x] Mettre à jour le composant de guide avec les nouvelles sections métier
  - [x] Conserver la convention `[debut, fin)` et le wrap 360° -> 0°
  - [x] Préserver la compatibilité avec le cas `missingBirthTime`
- [x] Task 2 (AC: 4) Ajouter une FAQ complète dans le guide natal
  - [x] Créer une structure de données FAQ explicite et maintenable
  - [x] Intégrer les 8 entrées demandées en contenu canonique FR
- [x] Task 3 (AC: 6) Renforcer les tests UI du guide natal
  - [x] Ajouter tests de présence des sections enrichies
  - [x] Ajouter tests de présence des 8 Q/R FAQ
  - [x] Vérifier absence de régression sur les comportements existants

## Dev Notes

- Frontend uniquement.
- Composants et fichiers cibles probables:
  - `frontend/src/components/NatalChartGuide.tsx`
  - `frontend/src/i18n/natalChart.ts`
  - `frontend/src/tests/NatalChartPage.test.tsx`
- Ne pas réintroduire de logique métier backend dans le composant; cette story porte sur la pédagogie et la restitution.
- Préparer la structure i18n pour la story suivante (20.15), sans implémenter toutes les traductions dans cette story.

### Contenu canonique FR à intégrer

```txt
Comprendre ton profil astrologique:

Ton thème natal est une représentation géométrique du ciel au moment et au lieu de ta naissance. Les calculs placent des points (planètes) sur un cercle de 360°. Ensuite, on traduit ces positions en repères lisibles : signes, maisons, angles et aspects.

1. Les signes astrologiques : un repérage fixe en 12 zones
   Le zodiaque est divisé en 12 signes de 30° chacun. Un signe n'est pas une planète : c'est une zone du cercle qui sert de "grille de lecture" pour exprimer une position.

Chaque position astronomique est d'abord une longitude écliptique entre 0° et 360°. Cette longitude est ensuite convertie en :

* un signe (dans quel segment de 30° on se situe),
* un degré à l'intérieur du signe (de 0°00' à 29°59').

Les minutes (') sont des sous-unités du degré (1° = 60').

2. Les planètes : des points positionnés sur le cercle
   Les planètes (et, en astrologie, le Soleil et la Lune) sont des points placés sur le cercle zodiacal à une longitude précise.

Pour chaque planète, l'affichage donne généralement :

* sa position en signe + degré (lecture humaine),
* sa longitude brute (valeur de calcul),
* la maison dans laquelle elle se situe (secteur du thème).

Rétrogradation (R)
Le symbole R signifie que la planète est en "mouvement rétrograde apparent" (vue depuis la Terre, elle semble reculer temporairement dans le zodiaque). C'est un état de mouvement apparent, pas un objet supplémentaire.

3. Les maisons : 12 secteurs dépendants de l'heure et du lieu
   Les maisons découpent aussi le cercle en 12 secteurs, mais contrairement aux signes (fixes), elles dépendent du lieu et de l'heure de naissance. Elles se basent sur l'horizon et le méridien locaux à cet instant.

Cuspides et intervalles
Chaque maison commence à une cuspide (son "point d'ouverture") et s'étend jusqu'à la cuspide de la maison suivante.

Convention d'appartenance
Quand une planète est indiquée dans une maison, cela signifie que sa longitude se trouve dans l'intervalle de cette maison. Une convention courante (souvent utilisée en calcul) est l'intervalle semi-ouvert [début, fin) :

* le début est inclus,
* la fin ne l'est pas (si une planète tombe exactement sur la cuspide de fin, elle est comptée dans la maison suivante).

Passage par 0° (wrap 360°)
Certaines maisons peuvent traverser la jonction 360° -> 0°. Dans ce cas, l'intervalle "boucle" : il couvre la fin du cercle puis reprend au début.

Système de maisons
Il existe plusieurs systèmes (maisons égales, Placidus, etc.). Le système utilisé doit être indiqué dans l'en-tête, car il change les cuspides et donc la répartition des planètes dans les maisons.

4. Les angles : les 4 points structurants de la carte
   Les "angles" sont quatre points de référence majeurs, issus des cuspides de maisons clés. Ils structurent le thème en deux axes.

* Ascendant (ASC) : cuspide de la Maison I. C'est le point où le zodiaque coupe l'horizon Est au moment de la naissance.
* Descendant (DSC) : cuspide de la Maison VII (opposé à l'Ascendant, à ~180°).
* Milieu du Ciel (MC) : cuspide de la Maison X, lié au méridien supérieur.
* Fond du Ciel (IC) : cuspide de la Maison IV (opposé au MC, à ~180°).

En pratique :

* "Ascendant" correspond au signe qui contient la cuspide de la Maison I.
* MC correspond au signe qui contient la cuspide de la Maison X.

5. Signe solaire et ascendant : ce que ça désigne exactement

* Signe solaire : le signe dans lequel se trouve le Soleil au moment de la naissance.
* Ascendant : le signe de la cuspide de la Maison I.

Ce sont deux "résumés" très utilisés, mais ils proviennent des mêmes données de base : des positions en degrés sur le cercle (pour le Soleil) et des cuspides calculées (pour l'Ascendant).

6. Les aspects : des angles entre planètes
   Les aspects sont des angles géométriques entre deux planètes, mesurés sur le cercle zodiacal. On compare l'écart angulaire entre leurs longitudes.

Chaque aspect correspond à un angle de référence (par exemple 0°, 60°, 90°, 120°...). Comme les positions ne tombent presque jamais "pile" sur ces angles, on utilise une tolérance.

Orbe et orbe effectif

* Orbe : l'écart maximal accepté autour de l'angle théorique pour considérer l'aspect comme valide.
* Orbe effectif : l'écart réellement mesuré dans ce thème précis.

L'aspect est listé si l'orbe effectif est inférieur ou égal à l'orbe autorisé.

FAQ

Pourquoi parle-t-on de 360° ?
Parce que le thème est représenté comme un cercle complet. Les positions des planètes et des cuspides sont exprimées en degrés sur ce cercle, ce qui permet de calculer facilement maisons et aspects.

Pourquoi y a-t-il deux découpages (signes et maisons) ?
Les signes sont un découpage fixe du zodiaque (12 x 30°), identique pour tout le monde. Les maisons sont un découpage "local" calculé à partir du lieu et de l'heure de naissance, donc spécifique à chaque personne.

Qu'est-ce qu'une "longitude brute" ?
C'est la valeur numérique (0-360°) utilisée pour les calculs. L'affichage "signe + degré" est une conversion plus lisible de cette même valeur.

Qu'est-ce qu'une cuspide ?
C'est le point de départ d'une maison. Les cuspides sont des repères calculés sur le cercle, qui définissent les limites des secteurs (maisons).

Pourquoi certaines maisons semblent "bizarres" ou traversent 0° ?
Parce que le cercle n'a pas de "début réel" : 360° et 0° sont le même point. Si une maison démarre près de la fin du cercle, elle peut continuer après 0°.

À quoi sert l'orbe dans les aspects ?
L'orbe sert de tolérance. Sans orbe, presque aucun aspect ne serait exact. Avec l'orbe, on retient les angles "proches" d'un angle de référence.

Que signifie le symbole R ?
R indique une rétrogradation apparente : depuis la Terre, la planète semble reculer temporairement dans le zodiaque. C'est une information de mouvement apparent issue des éphémérides.

Pourquoi le signe solaire et l'ascendant sont mis en avant ?
Parce que ce sont deux repères très utilisés : l'un est la position du Soleil (un point), l'autre est un angle issu des maisons (une cuspide). Ils résument des éléments différents de la structure du thème, sans être une interprétation à eux seuls.
```

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-2014--guide-natal-clarification-approfondie--faq]
- [Source: _bmad-output/implementation-artifacts/19-1-comment-lire-ton-theme-natal-dans-l-app.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Story créée via workflow BMAD `create-story` (ciblée 20.14).
- Implémentée via workflow BMAD `dev-story` (20.14).

### Completion Notes List

- `NatalChartGuide.tsx` : guide restructuré en 7 sections (6 métier + FAQ). Nouvelle section "Les angles" ajoutée entre maisons et "Signe solaire et ascendant". Section ascendant renommée et enrichie. Fix: Utilisation de `item.question` comme clé React stable pour la FAQ.
- `natalChart.ts` : type `NatalChartGuideTranslations` étendu avec `planetsRetrogradeTip`, `anglesTitle`, `anglesDesc`, `sunAscendantTitle`, `sunAscendantDesc`, `faqTitle`, `faq: NatalChartFaqItem[]`. Contenu canonique FR intégré; traductions EN/ES ajoutées pour respecter le contrat `Record<AstrologyLang, ...>`.
- `NatalChartPage.test.tsx` : 6 nouveaux tests ajoutés dans `describe("Story 20-14")`. Correction de la régression `getByText(/Lune/)` → `getAllByText(/Lune/)` causée par "Lune" présent dans le nouveau `planetsDesc` FR. Fix: Tests resserrés via `within()` pour cibler spécifiquement les sections résultats vs guide.
- `BirthProfilePage.tsx` & `api/natalChart.ts` : Inclus dans la liste des fichiers pour régulariser les changements de typage (orb_used null) et nettoyage mineur.
- Résultat: **53/53 tests passent**, zéro régression, qualité de code renforcée après revue.

### File List

- `frontend/src/components/NatalChartGuide.tsx`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `_bmad-output/implementation-artifacts/20-14-guide-natal-clarification-faq.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-02-27: Implémentation story 20-14 — guide natal enrichi avec 6 sections métier (ajout angles, renommage signe solaire/ascendant, astuce rétrograde dans planètes) + FAQ 8 Q/R en FR/EN/ES. 6 nouveaux tests UI. 53/53 tests verts.
