# CS-393 - Refondre La Page /natal Autour De La Lecture Narrative

<!-- Commentaire global: ce brief cadre la refonte frontend de /natal vers une lecture narrative unique. -->

## Resume

Remplacer la succession de cartes factuelles publiques de `/natal` par un parcours de lecture
narratif centre sur les cinq chapitres de `narrative_natal_reading_v1`. La page doit afficher
les conclusions avant les donnees astrologiques et garder le mode astrologue en fin de page.

## Contexte

`NatalChartPage.tsx` compose actuellement:

- hero;
- synthese IA;
- ADN astrologique;
- domaines de vie;
- forces;
- defis;
- aspects majeurs;
- trajectoire karmique;
- talents caches;
- potentiel relationnel;
- potentiel professionnel;
- mode astrologue.

Cette structure cree une page longue mais sans fil directeur. Plusieurs composants retombent
sur des placements ou signaux internes et ne fournissent pas de conclusion utile.

## Objectif

Afficher dans la vue publique principale:

1. Votre personnalite.
2. Votre monde emotionnel.
3. Vos relations.
4. Votre vocation.
5. Votre chemin d'evolution.

La lecture narrative doit devenir le contenu central. Le hero et les etats produit restent
concis. Le mode astrologue reste disponible en fin de page selon l'entitlement existant.

## Perimetre inclus

1. Introduire un owner presentational `NatalNarrativeReading`.
2. Brancher les cinq chapitres depuis la reponse natale acceptee.
3. Supprimer de la composition publique principale:
   `NatalAstrologicalDna`, `NatalLifeDomains`, `NatalStrengths`, `NatalChallenges`,
   `NatalMajorAspects`, `NatalKarmicSignature`, `NatalHiddenTalents`,
   `NatalRelationshipPotential`, `NatalCareerPotential`.
4. Conserver `NatalProfileHero` uniquement comme entree courte et lisible; retirer les traits
   moteur bruts.
5. Conserver loading, empty, degraded, error, quota, historique, PDF et upsell.
6. Conserver `NatalAstrologerMode` en fin de page sans fuite par defaut.
7. Supprimer les composants devenus sans usage apres preuve d'absence d'import.
8. Reutiliser les tokens CSS existants; aucun style inline.

## Hors perimetre

- Modifier backend, prompts ou entitlements.
- Recalculer une interpretation en React.
- Refaire le panneau expert.
- Conserver les anciennes cartes sous un wrapper de compatibilite visible.

## Sources obligatoires

- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalThemeSynthesis.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalProfileHero.tsx`
- `frontend/src/features/natal-chart/NatalAstrologerMode.tsx`
- `frontend/src/pages/NatalChartPage.css`
- `_condamad/reports/cs-390-audit-architecture-lecture-natale.md`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - aucun style inline statique.
  - `RG-052` - reutiliser les tokens CSS canoniques.
  - `RG-071` - ne pas regonfler `NatalInterpretation.tsx`.
  - `RG-073` - conserver l'owner feature `features/natal-chart/**`.
  - `RG-129` - aucune regle astrologique locale React.
  - `RG-150` - ne jamais rendre une interpretation rejetee.
  - `RG-151` - si les aspects restent accessibles, conserver leur identite stable.
- Required regression evidence:
  - `pnpm --dir frontend test -- NatalChartPage natalInterpretation NatalAstrologerMode`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - `rg -n "NatalAstrologicalDna|NatalLifeDomains|NatalStrengths|NatalChallenges|NatalMajorAspects|NatalKarmicSignature|NatalHiddenTalents|NatalRelationshipPotential|NatalCareerPotential" frontend/src`
  - `rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages/NatalChartPage.tsx`
- Allowed differences:
  - Ordre et composition visibles de `/natal`.
  - Suppression des composants publics devenus orphelins.

## Criteres d'acceptation

1. La vue principale affiche les cinq chapitres narratifs dans l'ordre attendu.
2. Les anciennes cartes factuelles ne sont plus rendues dans la vue publique principale.
3. Le hero n'affiche plus de codes moteur comme traits dominants.
4. Les etats loading, empty, degraded, error, quota et entitlement restent explicites.
5. L'historique et les actions PDF continuent de fonctionner.
6. `NatalAstrologerMode` reste replie par defaut et place apres la lecture publique.
7. Aucun style inline ni calcul astrologique frontend n'est introduit.
8. Desktop et mobile montrent un fil de lecture continu sans accumulation de cartes.

## Commandes De Validation Minimales

```powershell
cd frontend
pnpm test -- NatalChartPage natalInterpretation NatalAstrologerMode
pnpm lint
pnpm build
```

QA navigateur:

```text
Manual check: ouvrir /natal en desktop et mobile avec l'utilisateur test; verifier les cinq
chapitres, les etats produit et le mode astrologue replie en fin de lecture.
```

## Dependances

- CS-390.
- CS-392.

## Risques

Le risque principal est de casser les parcours quota, historique ou PDF en remaniant le rendu.
La refonte doit extraire la lecture narrative sans dupliquer l'orchestration existante.
