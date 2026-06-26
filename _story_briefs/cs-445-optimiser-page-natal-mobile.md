# CS-445 - Optimiser La Page /natal Sur Mobile

<!-- Commentaire global: ce brief cadre la phase 4 mobile de la page /natal apres les ameliorations UI des phases 1 a 3. -->

## Resume

Rendre `/natal` agreable, fiable et scannable sur mobile sans changer le contrat Astral ni
la structure produit existante. La page doit garder le theme Astrorizon, proteger le rendu
progressif livre en phase 3 et corriger les irritants mobiles: contenu masque par la bottom
nav, densite excessive en haut de page, badges longs, cartes d'interpretation trop chargees
et zones tactiles trop petites.

## Contexte

Les phases 1, 2 et 3 ont ameliore la page `/natal` autour d'une lecture Astral plus lisible:
portrait astral, base du calcul natal, parcours de lecture, chapitres progressifs et
explications repliees. Sur mobile, le rendu reste expose a plusieurs risques ergonomiques:

- la navigation basse peut masquer les derniers contenus;
- le haut de page consomme trop de hauteur avant l'interpretation;
- certains badges longs, notamment les maisons ou routines, peuvent deborder ou devenir
illisibles;
- les cartes de lecture gardent des comportements issus du desktop;
- les longs paragraphes donnent une page difficile a scanner.

Cette phase doit etre une passe mobile ciblee, principalement CSS/layout, avec ajustements
React uniquement si la divulgation progressive ou l'accessibilite tactile l'exigent.

Attention: l'evidence navigateur CS-423 contient des assertions mobiles devenues trop
compressives (`fontSize <= 11`, `lineHeight <= 16`, badges de repères en `nowrap` avec
scroll horizontal). Cette phase doit remplacer ces attentes par des seuils de lisibilite
mobile, sinon la validation peut continuer a proteger le defaut que l'on veut corriger.

## Objectif

Mettre en place:

```text
/natal mobile = portrait compact -> donnees de calcul lisibles -> lecture mono-colonne -> repères replieables -> fin de page non masquee
```

La page doit rester premium, verticale, sans zigzag visuel, et utilisable a 360 px, 390 px
et 430 px de large.

## Perimetre inclus

1. Ajouter un espace de securite bas de page tenant compte de la bottom nav et de
   `env(safe-area-inset-bottom)`.
2. Verifier que le dernier bloc, les accordéons, les ancres et les etats de contenu long ne
   passent jamais sous la navigation basse.
3. Compacter le bloc `Portrait astral` sur mobile: marges, grille des faits, hauteur des
   badges et longueur visible du resume.
4. Reduire moderement les paddings des cartes de donnees sans tomber sous une lisibilite
   premium.
5. Stabiliser les badges et tags longs avec retour a la ligne propre, `min-width: 0`,
   `overflow-wrap` et suppression des scrolls horizontaux non necessaires.
6. Passer les cartes d'interpretation en mono-colonne stricte sur petit ecran.
7. Afficher les `Repères utilisés` sous le texte, en bloc compact et lisible, ou les replier
   si la densite reste trop forte, sans imposer de scroll horizontal aux libelles longs.
8. Conserver la premiere valeur immediate: au moins le premier chapitre principal reste
   ouvert par defaut, conformement a la logique progressive existante.
9. Reduire la longueur percue avec `Lire la suite` / accordéons existants, sans cacher les
   informations indispensables.
10. Ameliorer le confort typographique mobile: interligne des paragraphes longs, tailles de
    titres, espacement entre paragraphes.
11. Garantir des zones tactiles d'au moins 44 px de haut pour boutons, accordéons, menus et
    items de navigation, sauf texte statique non interactif.
12. Ajouter ou ajuster les tests frontend utiles pour verrouiller le comportement mobile
    critique.
13. Ajouter une spec Playwright dediee `frontend/e2e/cs-445-natal-mobile.spec.ts`, ou mettre
    a jour une spec existante uniquement si elle ne conserve pas les seuils compressifs CS-423.
14. Capturer une preuve visuelle Playwright aux largeurs 360 px, 390 px et 430 px.

## Hors perimetre

- Modifier backend, contrats Astral, calculs astrologiques, entitlements ou quotas.
- Reintroduire l'ancien rendu legacy natal ou des composants factuels supprimes.
- Ajouter des styles inline.
- Changer le theme visuel general Astrorizon ou creer une nouvelle palette.
- Refaire l'architecture de `NatalAstralReading` hors besoin mobile concret.
- Remplacer la bottom nav ou modifier la navigation globale hors correction d'espacement.

## Sources obligatoires

- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/features/natal-chart/NatalAstralReading.tsx`
- `frontend/src/features/natal-chart/natalAstralReadingViewModel.ts`
- `frontend/src/layouts/components/BottomNav.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/e2e/cs-423-natal-basic-readable.spec.ts` pour remplacer les attentes mobiles
  compressives si cette spec reste dans le plan de validation
- `frontend/e2e/cs-445-natal-mobile.spec.ts` a creer pour les preuves mobiles ciblees
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - aucun style inline statique.
  - `RG-052` - reutiliser les tokens CSS canoniques et variables existantes.
  - `RG-178` - le frontend ne contacte jamais Astral directement.
  - `RG-180` - pas de relance automatique multiple du job Astral.
  - `RG-182` - proteger la lecture Astral longue progressive: parcours numerote, chapeau
    `À retenir`, chapitres ouverts/replies, boutons ARIA, aucun style inline.
  - `RG-183` - proteger la lisibilite mobile `/natal` a 360 px, 390 px et 430 px.
- Historical invariants kept as zero-regression scans:
  - `RG-153`, `RG-154`, `RG-158` - invariants de l'ancien rendu narratif remplaces par
    l'externalisation Astral, a conserver comme scans anti-reintroduction legacy seulement.
- Non-applicable invariants:
  - `RG-151`, `RG-152`, `RG-155` a `RG-157`, `RG-159` a `RG-174` - la story ne touche pas
    les contrats ou validateurs backend de lecture natale.
  - `RG-175` a `RG-177`, `RG-181` - la story ne touche pas la facade backend Astral.
- Required regression evidence:
  - `npm run test -- src/tests/NatalChartPage.test.tsx`
  - `npm run test -- src/tests/astralExternalization.test.ts`
  - `npm run test -- src/tests/inline-style-policy.test.ts`
  - `npm run test -- src/tests/theme-tokens.test.ts src/tests/component-architecture-guards.test.ts`
  - `npm run lint`
  - `npm run build`
  - `npm run test:e2e -- cs-445-natal-mobile.spec.ts`
  - Zero-hit scan `style=\\{\\{` sur `src/pages/NatalChartPage.tsx`, `src/features/natal-chart`
    et `src/tests/NatalChartPage.test.tsx`.
  - Zero-hit scan legacy natal `NatalNarrativeReading|NatalReadingSources|NatalInterpretationLegacyBody|natal-narrative-reading__toggle|ni-actions--compact` sur `src`.
  - Zero-hit scan direct Astral `localhost:8081|localhost:8082|localhost:3000` sur `src`.
  - Captures Playwright `/natal` a 360 px, 390 px et 430 px, avec verification DOM que
    `document.documentElement.scrollWidth <= window.innerWidth`.
- Allowed differences:
  - Les differences visuelles sont limitees au responsive mobile: espacement, wrapping,
    ordre mono-colonne, taille des zones tactiles et divulgation compacte des repères.

## Criteres d'acceptation

1. A 360 px, 390 px et 430 px, aucun texte, badge, carte, bouton ou dernier bloc n'est masque
   par la bottom nav.
2. Le bloc `Portrait astral` reste lisible mais occupe moins de hauteur qu'avant sur mobile.
3. L'utilisateur atteint plus rapidement l'interpretation sans perdre les badges essentiels
   du resume.
4. Les badges longs comme `Maison VI - Routines / hygiene de vie` restent lisibles a 390 px,
   sans debordement horizontal ni micro-texte compresse.
5. `Base du calcul natal` et les cartes de donnees restent en mono-colonne ou grille mobile
   stable, sans shift au hover ou a l'ouverture d'un accordéon.
6. Les cartes d'interpretation principales sont en mono-colonne stricte sur mobile.
7. Les `Repères utilisés` ne forment plus une colonne laterale mobile; ils sont sous le texte
   ou replies dans un bloc compact accessible.
8. La premiere lecture principale donne une valeur immediate; les lectures secondaires
   restent accessibles via `Lire la suite` ou accordéons.
9. Les paragraphes longs se lisent sans zoom: taille stable, interligne confortable,
   largeur de ligne adaptee.
10. Les boutons `Lire la suite`, `Reduire`, lancement/regeneration et elements de navigation
    ont une cible tactile d'au moins 44 px de haut et un espacement suffisant.
11. Aucun style inline n'est ajoute; les changements CSS reutilisent les tokens existants.
12. Les comportements existants de lancement unique, reprise manuelle, erreurs, loading,
    theme partiel et guide natal restent fonctionnels.

## Plan De Mise En Oeuvre

1. Auditer le rendu mobile actuel a 360 px, 390 px et 430 px.
   - Capturer haut de page, `Base du calcul natal`, cartes longues, accordéons ouverts/replies
     et fin de page.
   - Identifier les classes CSS responsables des hauteurs, paddings, colonnes et badges.
   - Mesurer la bottom nav avec ses tokens existants `--app-mobile-nav-inset`,
     `--app-mobile-nav-padding`, `--app-mobile-nav-radius` et les styles `.bottom-nav`.

2. Corriger la securite de bas de page.
   - Ajuster le padding bottom de `.page-layout.natal-page-container .page-layout__main`.
   - Tenir compte de la hauteur effective de `BottomNav`, de l'inset global existant
     `.app-shell-main { padding-bottom: 110px; }` et de `env(safe-area-inset-bottom)`.
   - Eviter une double compensation excessive entre `.app-shell-main` et
     `.page-layout__main`: le test doit verifier le dernier bloc visible, pas seulement une
     valeur de padding.
   - Verifier le dernier bloc `NatalChartGuide` et les panneaux replies/deplies.

3. Compacter les sections initiales.
   - Revoir les styles mobiles de `.natal-page-header`, `.natal-page-portrait`,
     `.natal-page-portrait__facts` et `.natal-reading-facts`.
   - Conserver les informations cles mais reduire les hauteurs inutiles.

4. Stabiliser badges, tags et repères.
   - Appliquer des regles mobiles robustes sur `.natal-badge`, `.natal-badge--astro-data`,
     `.natal-badge--fact-detail`, `.natal-badge--basis` et `.natal-reading__basis`.
   - Preferer le retour a la ligne lisible aux scrolls horizontaux pour les libelles longs.
   - Remplacer les attentes CS-423 de type `whiteSpace: nowrap`, `overflowX: auto`,
     `fontSize <= 10` et `height <= 16` par des assertions de lisibilite et d'absence de
     debordement horizontal.

5. Adapter les cartes d'interpretation.
   - Forcer `.natal-reading__chapter` en mono-colonne mobile.
   - Replacer `.natal-reading__chapter-meta` sous le contenu et retirer tout comportement
     sticky mobile.
   - Si necessaire, rendre les repères secondaires repliables sans modifier les chapitres
     principaux.

6. Ameliorer typographie et tactile.
   - Ajuster line-height, gaps et tailles de titres dans les media queries existantes.
   - Assurer une hauteur tactile suffisante sur `.natal-reading__chapter-toggle`,
     `.ni-action-btn`, details/summary et elements interactifs de guide.
   - Ne pas valider la lisibilite avec des plafonds de type `font-size <= 11px`; utiliser
     plutot des minimums lisibles, un line-height confortable et une absence de chevauchement.

7. Verrouiller par tests et preuves.
   - Ajouter/mettre a jour les assertions React Testing Library sur accordéons, ARIA et absence
     de style inline si necessaire.
   - Ajouter `frontend/e2e/cs-445-natal-mobile.spec.ts` avec payload mocke Astral contenant
     au moins un repere long: `Maison VI - Routines / hygiene de vie`.
   - Dans la spec Playwright, verifier a 360/390/430 px:
     - pas de scroll horizontal document;
     - dernier bloc visible au-dessus de `.bottom-nav`;
     - boutons interactifs principaux `>= 44px`;
     - badges longs non tronques et non compresses;
     - meta/repères sous le texte ou replies, jamais en colonne laterale.
   - Produire les captures 360/390/430 en evidence.

## Commandes De Validation Minimales

```powershell
cd frontend
npm run test -- src/tests/NatalChartPage.test.tsx
npm run test -- src/tests/astralExternalization.test.ts
npm run test -- src/tests/inline-style-policy.test.ts
npm run test -- src/tests/theme-tokens.test.ts src/tests/component-architecture-guards.test.ts
npm run lint
npm run build
npm run test:e2e -- cs-445-natal-mobile.spec.ts
$inlineHits = rg -n "style=\\{\\{" src/pages/NatalChartPage.tsx src/features/natal-chart src/tests/NatalChartPage.test.tsx; if ($LASTEXITCODE -eq 0) { throw "Styles inline interdits trouves: $inlineHits" } elseif ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
$legacyHits = rg -n "NatalNarrativeReading|NatalReadingSources|NatalInterpretationLegacyBody|natal-narrative-reading__toggle|ni-actions--compact" src; if ($LASTEXITCODE -eq 0) { throw "Surfaces legacy natal retrouvees: $legacyHits" } elseif ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
$astralDirectHits = rg -n "localhost:8081|localhost:8082|localhost:3000" src; if ($LASTEXITCODE -eq 0) { throw "Appels Astral directs trouves: $astralDirectHits" } elseif ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
```

QA navigateur:

```text
Ouvrir /natal avec l'utilisateur test.
Verifier les largeurs 360 px, 390 px et 430 px.
Controler le haut de page, Base du calcul natal, badges longs, chapitres ouverts/replies,
Repères utilisés, guide final et dernier pixel visible au-dessus de la bottom nav.
```

## Donnees De Test

- Utilisateur: `daconrilcy@hotmail.com`
- Mot de passe: `admin123`
- Route: `/natal`
- Cas a verifier:
  - job Astral deja complete via `runId`;
  - lancement depuis page vierge;
  - theme partiel si donnees de naissance incompletes;
  - erreur/reprise manuelle si job terminal en echec.

## Dependances

- Phases UI `/natal` 1, 2 et 3 livrees.
- `RG-182` deja present dans le registre pour proteger la lecture Astral longue.
- Acces a un run Astral de test ou mock frontend permettant de rendre les longs contenus.

## Risques

Le risque principal est de trop compacter la page et de degrader la qualite percue. Les
changements doivent donc rester mobiles, mesures et centres sur la lisibilite. Le second
risque est de casser la divulgation progressive de phase 3: les tests doivent verifier les
boutons `aria-expanded` / `aria-controls`, les chapitres ouverts par defaut et l'absence de
style inline.
