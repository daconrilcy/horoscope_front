# CS-446 - Harmoniser Le Style De La Page /natal

<!-- Commentaire global: ce brief cadre la phase 5 de coherence visuelle de la page /natal apres les phases UI 1 a 4. -->

## Resume

Rendre `/natal` plus homogene, premium et maintenable sans changer son identite Astrorizon,
son contrat Astral ni les comportements livres par les phases precedentes. Cette phase est
une passe de coherence de style: inventaire des tokens, surfaces, rayons, bordures, badges,
couleurs d'accent, typographie, libelles visibles et etats d'interaction.

Le resultat attendu est une page qui parait issue d'un seul design system: pastel, astrale,
legere, violette avec mesure, et sans patchs visuels isoles.

## Contexte

Les phases 1 a 4 ont progressivement ameliore `/natal`: comprehension immediate, lecture
narrative, divulgation progressive, mode astrologue et optimisation mobile. La page contient
des surfaces visuelles nombreuses (`Portrait astral`, `Base du calcul natal`, lecture Astral,
explications, repères, actions, etats de chargement/erreur) qui peuvent diverger avec le temps:

- opacites et fonds empiles;
- variations locales de rayons, bordures, ombres et espacements;
- badges de meme intensite pour des informations de priorite differente;
- couleurs violettes trop presentes;
- niveaux typographiques parfois proches;
- libelles anglais restants dans certains payloads ou catalogues publics;
- risques de regression sur hover, focus, accordéons et mobile.

Cette phase doit reduire ces divergences en reutilisant les tokens existants et les classes
deja en place, sans creer une nouvelle direction artistique.

## Objectif

Mettre en place:

```text
/natal phase 5 = tokens existants -> 3 niveaux de surface -> badges hierarchises -> typographie stable -> contenu visible francais -> accessibilite preservee
```

La page doit conserver l'identite Astrorizon tout en devenant plus simple a maintenir:
moins de valeurs locales, moins de variantes visuelles concurrentes, plus de roles explicites
pour les composants de surface et de badge.

## Perimetre Inclus

1. Inventorier les variables CSS existantes pour couleurs, bordures, rayons, ombres,
   espacements et typographies.
2. Reperer les valeurs locales ou dupliquees dans les styles `/natal`.
3. Limiter la hierarchie visuelle a trois niveaux maximum:
   - fond de page;
   - section principale;
   - carte ou bloc de contenu.
4. Harmoniser les surfaces de `Portrait astral`, `Base du calcul natal`, lecture Astral,
   explications et repères calcules.
5. Uniformiser rayons, bordures, ombres et opacites via les tokens existants.
6. Rationaliser l'usage du violet: signes astrologiques, etat actif, focus, informations cles.
7. Introduire ou consolider une hierarchie de badges:
   - badge information cle;
   - badge detail;
   - badge statut;
   - badge metadonnee.
8. Stabiliser taille, graisse, bordure, fond, espacement et wrapping des badges.
9. Aligner les niveaux typographiques: H1, H2, H3, labels, paragraphes, micro-textes.
10. Traduire les libelles visibles restants en anglais quand ils passent par le frontend:
    `Career`, `Very high`, `How to read your natal chart`, et labels equivalents.
11. Verifier les etats hover, focus, actif, disabled, ouvert/ferme des navs, accordéons et
    actions.
12. Conserver les acquis mobile CS-445: pas de debordement, cibles tactiles, bottom nav,
    repères longs lisibles.
13. Ajouter ou ajuster les tests utiles pour verrouiller la non-regression style et contenu.

## Hors Perimetre

- Modifier backend, contrats Astral, calculs astrologiques, entitlements, quotas ou jobs.
- Changer le theme general Astrorizon ou creer une nouvelle palette.
- Ajouter des styles inline.
- Introduire une nouvelle librairie UI ou de design tokens.
- Refaire l'architecture de la page hors extraction CSS/React strictement necessaire.
- Reintroduire les surfaces legacy natal supprimees.
- Affaiblir la divulgation progressive `NatalAstralReading`.
- Remplacer l'optimisation mobile CS-445 par des compromis desktop.

## Sources Obligatoires

- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/features/natal-chart/NatalAstralReading.tsx`
- `frontend/src/features/natal-chart/natalAstralReadingViewModel.ts`
- `frontend/src/features/natal-chart/natalPublicCopy.ts`
- `frontend/src/i18n/astrology.ts`
- `frontend/src/styles/app/tokens.css`
- `frontend/src/App.css`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/tests/natalAstralReadingViewModel.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/e2e/cs-445-natal-mobile.spec.ts`
- `_condamad/stories/regression-guardrails.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - aucun style inline statique.
  - `RG-052` - reutiliser les tokens CSS canoniques et variables existantes.
  - `RG-178` - le frontend ne contacte jamais Astral directement.
  - `RG-180` - pas de relance automatique multiple du job Astral.
  - `RG-182` - proteger la lecture Astral progressive: parcours numerote, chapeau
    `À retenir`, chapitres ouverts/replies, boutons ARIA, aucun style inline.
  - `RG-183` - proteger la lisibilite mobile `/natal` a 360 px, 390 px et 430 px.
- Historical invariants kept as zero-regression scans:
  - `RG-153`, `RG-154`, `RG-158` - invariants de l'ancien rendu narratif remplaces par
    l'externalisation Astral, a conserver comme scans anti-reintroduction legacy seulement.
- Non-applicable invariants:
  - `RG-151`, `RG-152`, `RG-155` a `RG-174` - la phase ne touche pas les contrats backend,
    validateurs ou generation de lecture natale.
  - `RG-175` a `RG-177`, `RG-181` - la phase ne touche pas la facade backend Astral.
- Required regression evidence:
  - `npm run test -- src/tests/NatalChartPage.test.tsx`
  - `npm run test -- src/tests/natalAstralReadingViewModel.test.ts`
  - `npm run test -- src/tests/inline-style-policy.test.ts`
  - `npm run test -- src/tests/theme-tokens.test.ts src/tests/component-architecture-guards.test.ts`
  - `npm run test -- src/tests/astralExternalization.test.ts`
  - `npm run lint`
  - `npm run build`
  - `npm run test:e2e -- cs-445-natal-mobile.spec.ts`
  - Scan zero-hit `style=\\{\\{` sur `frontend/src/pages/NatalChartPage.tsx`,
    `frontend/src/features/natal-chart` et `frontend/src/tests/NatalChartPage.test.tsx`.
  - Scan zero-hit legacy natal `NatalNarrativeReading|NatalReadingSources|NatalInterpretationLegacyBody|natal-narrative-reading__toggle|ni-actions--compact`
    sur `frontend/src`.
  - Scan zero-hit direct Astral `localhost:8081|localhost:8082|localhost:3000` sur `frontend/src`.
  - Scan CSS ciblant les nouvelles valeurs hardcodees dans `NatalChartPage.css`.
- Allowed differences:
  - Differences visuelles limitees a la coherence de style: surface, couleur, border,
    radius, shadow, spacing, typographie, badges, etats interactifs et libelles visibles.

## Criteres D'acceptation

1. Aucun nouveau token visuel n'est cree si une variable existante couvre le besoin.
2. La page utilise au maximum trois niveaux de surface lisibles: fond, section, carte/bloc.
3. Les cartes imbriquees ou opacites empilees inutiles sont supprimees ou simplifiees.
4. `Portrait astral`, `Base du calcul natal`, lectures guidees et repères calcules partagent
   des rayons, bordures, ombres et espacements coherents.
5. Le violet est reserve aux signes, etats actifs, focus, CTA ou informations cles.
6. Les metadonnees et textes secondaires utilisent des tons neutres doux.
7. Les badges ont une hierarchie stable: information cle, detail, statut, metadonnee.
8. Les badges restent lisibles sur desktop et mobile, sans intensite uniforme ni debordement.
9. H1, H2, H3, labels, paragraphes et micro-textes ont des tailles et graisses distinctes.
10. Les libelles visibles en anglais identifies sont traduits ou normalises en francais.
11. Les etats hover, focus, actif, disabled et ouvert/ferme restent visibles et accessibles.
12. Les accordéons conservent `aria-expanded`, `aria-controls` et le comportement progressif
    de `RG-182`.
13. Les garanties mobiles `RG-183` restent vertes a 360 px, 390 px et 430 px.
14. Aucun style inline n'est ajoute.
15. Aucun appel direct Astral ni surface legacy natal n'est reintroduit.

## Plan De Mise En Oeuvre

1. Auditer les tokens et valeurs locales.
   - Lire `tokens.css`, `App.css` et `NatalChartPage.css`.
   - Lister les tokens disponibles pour couleurs, surfaces, bordures, rayons, ombres,
     espacements et typographies.
   - Reperer dans `NatalChartPage.css` les valeurs locales repetitives: `rgba`, `px`,
     `rem`, gradients, `border-radius`, `box-shadow`, couleurs et opacites.
   - Classer les valeurs a remplacer par token existant, a conserver car specifiques, ou a
     remonter en variable locale de page si aucune variable globale ne convient.

2. Cartographier les surfaces `/natal`.
   - Identifier les roles de `.natal-page-container`, `.natal-page-header`,
     `.natal-page-portrait`, `.natal-reading-facts`, `.natal-reading`,
     `.natal-reading__chapter`, `.natal-reading-explanations` et blocs d'etats.
   - Definir explicitement les trois niveaux retenus: fond, section principale, carte/bloc.
   - Supprimer les empilements qui n'apportent pas de hierarchie ou de lisibilite.

3. Harmoniser rayons, bordures et ombres.
   - Aligner les rayons des surfaces de section sur les tokens existants.
   - Aligner les cartes/blocs sur un second niveau stable.
   - Garder les badges en `radius` pilule uniquement quand leur role le justifie.
   - Verifier dark mode si la page declare des variantes `.dark`.

4. Rationaliser les couleurs d'accent.
   - Revoir les classes `.natal-badge--report-status`, `.natal-badge--confidence`,
     `.natal-badge--astro-data`, `.natal-badge--fact-detail`, `.natal-badge--basis`.
   - Differencier visuellement les informations cles des metadonnees secondaires.
   - Eviter que les repères, statuts et details aient tous le meme poids violet.
   - Conserver un focus visible raccorde aux tokens d'interaction.

5. Nettoyer et hierarchiser les badges.
   - Formaliser les roles CSS des badges sans ajouter de styles inline.
   - Stabiliser `display`, `gap`, `padding`, `font-size`, `font-weight`, `line-height`,
     `border`, `background` et wrapping.
   - Verifier les badges longs issus d'Astral et les donnees de calcul: maisons, aspects,
     confiance, statut, plan.
   - Ajouter une assertion test ou e2e si un badge long est critique.

6. Aligner la typographie.
   - Auditer `.natal-page-header__title`, titres de section, titres de carte,
     `.natal-reading__chapter-title`, labels et micro-textes.
   - Donner un usage stable a chaque niveau.
   - Eviter les titres trop proches des metadonnees et les micro-textes compresses.
   - Verifier les media queries mobile existantes apres ajustement.

7. Traduire et normaliser le contenu visible.
   - Corriger les libelles frontend ou mappings qui exposent `Career`, `Very high`,
     `How to read your natal chart` ou equivalents.
   - Ajouter des mappings defensifs dans `natalAstralReadingViewModel.ts` uniquement si les
     libelles viennent du payload Astral et doivent etre normalises cote affichage.
   - Mettre a jour `natalPublicCopy.ts` si des textes publics restent en anglais dans un
     parcours francais.
   - Ajuster les tests qui documentent actuellement ces valeurs anglaises.

8. Preserver interactions et accessibilite.
   - Tester clavier et focus sur actions, accordéons et navigation de lecture.
   - Verifier hover/active/disabled sans shift layout.
   - Conserver les cibles tactiles et l'absence de scroll horizontal mobile de CS-445.
   - Ne pas masquer les informations essentielles derriere un etat purement visuel.

9. Verrouiller par tests, scans et captures.
   - Mettre a jour les tests RTL pour les libelles francais et la structure de classes
     critique.
   - Renforcer `theme-tokens.test.ts` ou ajouter un test ciblant `NatalChartPage.css` si la
     politique anti-hardcode n'est pas deja couverte.
   - Rejouer la spec e2e mobile CS-445 apres harmonisation.
   - Capturer desktop et mobile avant/apres pour comparer densite, surfaces et lisibilite.

## Commandes De Validation Minimales

```powershell
cd frontend
npm run test -- src/tests/NatalChartPage.test.tsx
npm run test -- src/tests/natalAstralReadingViewModel.test.ts
npm run test -- src/tests/inline-style-policy.test.ts
npm run test -- src/tests/theme-tokens.test.ts src/tests/component-architecture-guards.test.ts
npm run test -- src/tests/astralExternalization.test.ts
npm run lint
npm run build
npm run test:e2e -- cs-445-natal-mobile.spec.ts
$inlineHits = rg -n "style=\\{\\{" src/pages/NatalChartPage.tsx src/features/natal-chart src/tests/NatalChartPage.test.tsx; if ($LASTEXITCODE -eq 0) { throw "Styles inline interdits trouves: $inlineHits" } elseif ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
$legacyHits = rg -n "NatalNarrativeReading|NatalReadingSources|NatalInterpretationLegacyBody|natal-narrative-reading__toggle|ni-actions--compact" src; if ($LASTEXITCODE -eq 0) { throw "Surfaces legacy natal retrouvees: $legacyHits" } elseif ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
$astralDirectHits = rg -n "localhost:8081|localhost:8082|localhost:3000" src; if ($LASTEXITCODE -eq 0) { throw "Appels Astral directs trouves: $astralDirectHits" } elseif ($LASTEXITCODE -gt 1) { exit $LASTEXITCODE }
```

Audit CSS cible:

```powershell
cd frontend
rg -n "#[0-9a-fA-F]{3,8}|rgba?\\(|hsla?\\(|box-shadow:|border-radius:|\\b[0-9]+px\\b" src/pages/NatalChartPage.css
```

Les hits CSS ne sont pas automatiquement interdits: chaque hit doit etre classe comme token
existant a utiliser, valeur locale justifiee, ou dette a retirer.

QA navigateur:

```text
Ouvrir /natal avec l'utilisateur test.
Comparer desktop et mobile.
Verifier Portrait astral, Base du calcul natal, lecture Astral, repères utilisés,
Explications du moteur Astral, etats loading/error/empty, accordéons ouverts/replies.
Verifier largeurs 360 px, 390 px et 430 px.
```

## Donnees De Test

- Utilisateur: `daconrilcy@hotmail.com`
- Mot de passe: `admin123`
- Route: `/natal`
- Cas a verifier:
  - job Astral deja complete via `runId`;
  - lancement depuis page vierge;
  - theme partiel si donnees de naissance incompletes;
  - erreur/reprise manuelle si job terminal en echec;
  - payload contenant maisons, aspects et repères longs;
  - payload contenant des libelles anglais a normaliser.

## Dependances

- Phases UI `/natal` 1, 2, 3 et 4 livrees.
- `RG-182` et `RG-183` presents dans le registre CONDAMAD.
- Acces a un run Astral de test ou mock frontend permettant de rendre les blocs longs.

## Risques

Le risque principal est de confondre harmonisation et refonte: cette phase ne doit pas
changer le parcours, le contrat ou la priorisation de contenu. Le second risque est de
sur-tokeniser des details specifiques a `/natal`: une variable locale est acceptable si elle
documente un role de page clair et ne cree pas un design system parallele. Le troisieme
risque est d'affaiblir l'accessibilite par simplification visuelle; les etats focus et les
accordéons doivent rester explicitement verifies.
