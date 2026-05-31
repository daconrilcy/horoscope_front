# CS-420 - Adapter La Page Natal Au Rendu Free Et Basic V2

<!-- Commentaire global: ce brief cadre l'adaptation frontend de la page natal aux contrats publics free et Basic V2. -->

## Resume

Adapter `/natal` pour afficher correctement les interpretations natales publiques issues des
nouveaux contrats backend:

- Free short: afficher l'interpretation courte `AstroFreeResponseV1` de facon lisible.
- Basic complete V2: afficher `basic_natal_interpretation_v2` de facon structuree.
- Complete legacy sans contrat moderne: conserver le message de regeneration.

Le cas utilisateur actuel affiche a tort "Lecture complete a regenerer" alors que l'API retourne
une interpretation short valide avec titre, resume, sections, highlights, advice et disclaimers.

## Contexte

Le DOM observe sur `/natal` montre:

- un header Basic et une synthese IA;
- un endpoint `/v1/natal/interpretation` qui renvoie `meta.level=short` et
  `use_case=natal_interpretation_short`;
- `narrative_natal_reading_v1=null` et `basic_natal_interpretation_v2=null`;
- un rendu final limite a la carte `ni-content-card--missing-narrative`.

Ce comportement n'est correct que pour une ancienne lecture complete obsolette. Il ne l'est pas
pour une lecture free short valide.

## Objectif

Rendre la page lisible pour les deux modes attendus:

```text
Free / short
=> titre + resume + sections + highlights + conseils + disclaimers

Basic / complete V2
=> titre + introduction + themes + conclusion + preuves publiques + disclaimers

Complete legacy sans contrat moderne
=> message de regeneration uniquement
```

## Perimetre Inclus

1. Ajouter les types frontend pour `BasicNatalInterpretationV2` et ses sous-objets publics.
2. Adapter `NatalInterpretationViewData` pour transporter `basic_natal_interpretation_v2`.
3. Modifier `NatalInterpretationContent` pour choisir explicitement la branche de rendu:
   free short, Basic V2, narrative v1, ou complete legacy obsolette.
4. Creer un rendu presentational Basic V2 reutilisable, sans style inline.
5. Enrichir le rendu free short pour afficher les sections, highlights et advice de l'exemple
   dans des blocs publics simples, sans reintroduire les accordions legacy interdits par `RG-154`.
6. Conserver le rendu `NatalNarrativeReading` quand `narrative_natal_reading_v1` est present.
7. Garder le message de regeneration uniquement pour `meta.level=complete` sans
   `narrative_natal_reading_v1` ni `basic_natal_interpretation_v2`.
8. Ajouter des tests Vitest pour les payloads free short et Basic V2.
9. Ajouter ou etendre les tests de garde DOM contre les fuites techniques.
10. Afficher les preuves publiques Basic V2 via `label` et `meaning`; ne pas rendre des cles
    techniques ou themes bruts si leur libelle n'est pas public.

## Hors Perimetre

- Changer le pipeline backend ou les quotas.
- Refaire toute la page `/natal`.
- Reintroduire les anciennes cartes factuelles legacy interdites.
- Ajouter du style inline.
- Modifier les offres commerciales ou textes d'abonnement au-dela du strict besoin d'affichage.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_story_briefs/cs-419-stabiliser-contrat-public-interpretation-natale-free-basic.md`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalNarrativeReading.tsx`
- `frontend/src/features/natal-chart/NatalReadingSources.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`
- `frontend/src/styles` et feuilles CSS existantes associees aux classes `ni-*`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-153` - `/natal` reste centree sur une lecture publique, sans cartes factuelles legacy.
  - `RG-154` - le DOM public ne doit pas exposer les marqueurs techniques denylistes.
  - `RG-158` - les accordeons narratifs modernes restent accessibles quand `narrative_natal_reading_v1` est present.
  - `RG-168` - `basic_natal_interpretation_v2` reste le contrat public canonique Basic V2.
- Required regression evidence:
  - `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - `rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
  - `rg -n "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx`
  - `rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" frontend/src/components/natal-interpretation frontend/src/features/natal-chart`
  - Browser QA sur `/natal` avec l'utilisateur test `daconrilcy@hotmail.com`.
- Registry enrichment expected:
  - Non attendu si la story ne cree pas un nouvel invariant durable.
- Allowed differences:
  - Le rendu free short affiche plus de contenu public qu'auparavant.
  - Le rendu Basic V2 peut utiliser de nouveaux composants/classes CSS `ni-basic-*` si les styles sont centralises dans les feuilles existantes.

## Criteres D'acceptation

1. Le payload free short de l'exemple utilisateur affiche le titre
   "Decouverte de votre essence astrologique", son resume, les trois sections, les highlights,
   les conseils et les mentions legales.
2. Le payload free short n'affiche jamais "Lecture complete a regenerer".
3. Un payload Basic V2 affiche le titre, l'introduction, les themes avec leur narrative, la
   conclusion, les limitations si presentes, les preuves publiques `label`/`meaning` et les
   disclaimers.
4. Un payload Basic V2 sans `narrative_natal_reading_v1` n'est pas classe comme obsolete.
5. Une lecture complete legacy sans `narrative_natal_reading_v1` ni
   `basic_natal_interpretation_v2` conserve le message de regeneration.
6. Le rendu `narrative_natal_reading_v1` existant reste inchange et garde ses accordeons
   accessibles.
7. Aucun marqueur technique interdit n'apparait dans le DOM public, y compris dans les
   attributs `title`, `aria-label` et contenus caches.
8. Aucun style inline n'est ajoute; les nouvelles classes reutilisent les variables CSS
   existantes avant d'en creer de nouvelles.
9. Les tests couvrent free short, Basic V2, narrative v1 et complete legacy.

## Commandes De Validation Minimales

Frontend:

```powershell
pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading
pnpm --dir frontend lint
pnpm --dir frontend build
```

Scans:

```powershell
rg -n "style=\\{" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "ni-evidence-tags|ni-projections|LockedSection|NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects" frontend/src/components/natal-interpretation frontend/src/features/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "visibility_expression|audit_input|condition_axis:|interpretive_signal_ids|projection_version|ranking_score|weighted_score|prompt_hint" frontend/src/components/natal-interpretation frontend/src/features/natal-chart
```

Les fixtures de tests peuvent contenir les tokens interdits uniquement pour prouver leur absence
du DOM; les scans production ci-dessus doivent rester sans hit non classe.

QA locale:

```powershell
# Backend: venv active obligatoire avant toute commande Python.
.\.venv\Scripts\Activate.ps1
# Demarrer la stack locale selon le script projet, puis verifier /natal dans le navigateur.
```

## Dependances

- CS-419 pour le contrat backend executable.
- CS-418 pour le pipeline Basic V2.
- CS-393, CS-395 et CS-399 pour les invariants de rendu public `/natal`.

## Risques

Le risque principal est de confondre "pas de lecture narrative v1" avec "lecture obsolette". La
condition doit etre contractuelle: free short et Basic V2 sont des formats publics valides, tandis
que seule une complete sans contrat moderne doit afficher le message de regeneration.
