# CS-390 - Auditer Les Fuites Techniques Et Cadrer L'Architecture De Lecture Natale

<!-- Commentaire global: ce brief cadre l'audit de la lecture publique /natal avant la refonte narrative. -->

## Resume

Auditer la page publique `/natal` apres CS-386 a CS-389 afin de classer chaque bloc visible
selon son lecteur reel: utilisateur debutant, passionne d'astrologie ou astrologue. Produire
une architecture cible qui separe interpretation, justification astrologique et detail
technique sans supprimer la richesse calculee par le moteur.

## Contexte

La page est structurellement plus riche, mais elle melange encore plusieurs niveaux:

- `NatalProfileHero` affiche directement des codes comme `visibility_expression`;
- `NatalAstrologicalDna` concatene des `explanation_facts` calculatoires;
- `NatalChallenges`, `NatalRelationshipPotential`, `NatalCareerPotential`,
  `NatalLifeDomains`, `NatalHiddenTalents` et `NatalKarmicSignature` retombent vers des
  placements lorsque le texte interprete manque;
- `AstrologyProjectionsPanel` affiche des projections B2C deterministes a cote de la
  narration LLM, alors que leur role produit n'est pas clair pour l'utilisateur;
- `NatalAstrologerMode` existe deja et doit rester la destination des details techniques.

Le probleme a fermer est une fuite de couches: source de calcul, observabilite LLM,
projection B2C et lecture produit sont presentes dans le meme parcours visuel.

## Objectif

Produire un audit fini et un plan de migration vers une page `/natal` en trois couches:

1. Lecture narrative principale pour un utilisateur final.
2. Bloc final replie « Ce que nous avons utilise » pour la justification astrologique
   vulgarisee.
3. Mode astrologue premium pour les calculs, scores et donnees techniques.

## Perimetre inclus

1. Inventorier tous les blocs visibles de `/natal`, y compris les etats loading, empty,
   degraded, entitlement et error.
2. Classer chaque information: `narrative-public`, `astrology-explanation`,
   `expert-technical`, `debug-observability`, `premium-marketing` ou `remove`.
3. Identifier les fuites de codes, signaux, scores, payloads et placements-source.
4. Proposer l'ordre final des cinq chapitres narratifs:
   `personnalite`, `monde_emotionnel`, `relations`, `vocation`, `chemin_evolution`.
5. Definir les owners cibles frontend et backend sans implementation.
6. Documenter les suppressions, deplacements et conservations attendus.

## Hors perimetre

- Modifier React, CSS, prompts, schemas Pydantic ou builders backend.
- Supprimer les calculs du moteur astrologique.
- Modifier les entitlements ou le prix des plans.
- Refaire le design visuel avant validation de l'architecture de contenu.

## Livrable attendu

Creer:

```text
_condamad/reports/cs-390-audit-architecture-lecture-natale.md
```

Le rapport doit contenir:

1. Inventaire des blocs visibles.
2. Matrice lecteur / information / owner actuel / owner cible / decision.
3. Liste finie des fuites techniques publiques.
4. Architecture cible de la page.
5. Carte de dependances des stories CS-391 a CS-395.
6. Captures navigateur desktop et mobile annotees.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-071` - ne pas recreer un owner `NatalInterpretation` monolithique.
  - `RG-073` - conserver l'orchestration sous `features/natal-chart/**`.
  - `RG-129` - ne jamais proposer de recalcul astrologique frontend.
  - `RG-150` - conserver l'exclusion publique des interpretations LLM rejetees.
  - `RG-151` - conserver l'identite stable des aspects si leur restitution reste visible.
- Required regression evidence:
  - `pnpm --dir frontend test -- NatalChartPage natalInterpretation NatalAstrologerMode`
  - `rg -n "dominant_topics|dominant_axes|narrative_priorities|explanation_facts|interpretation_adapter|projection_version" frontend/src/features/natal-chart frontend/src/components/natal-interpretation`
- Allowed differences:
  - Aucune modification applicative dans cette story d'audit.

## Criteres d'acceptation

1. Chaque bloc visible de `/natal` possede une decision explicite.
2. La cible distingue clairement debutant, passionne et astrologue.
3. Le rapport liste les composants a supprimer de la vue publique principale.
4. Le rapport liste les donnees techniques a conserver uniquement dans `NatalAstrologerMode`.
5. Les cinq chapitres narratifs cibles sont definis avec leur source de contenu.
6. Les captures desktop et mobile prouvent les problemes classes.

## Commandes De Validation Minimales

```powershell
cd frontend
pnpm test -- NatalChartPage natalInterpretation NatalAstrologerMode
pnpm lint
```

Depuis la racine:

```powershell
rg -n "dominant_topics|dominant_axes|narrative_priorities|explanation_facts|interpretation_adapter|projection_version" frontend/src/features/natal-chart frontend/src/components/natal-interpretation
```

## Dependances

- CS-386 a CS-389 implementes.

## Risques

Le risque principal est de transformer l'audit en liste de retouches CSS. Cette story doit
statuer sur l'architecture de contenu et la separation des lecteurs avant toute nouvelle
implementation.
