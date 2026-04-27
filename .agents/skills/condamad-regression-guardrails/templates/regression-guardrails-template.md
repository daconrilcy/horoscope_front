<!-- Registre vivant des invariants protegeant les stories CONDAMAD deja livrees ou pretes a implementer. -->

# CONDAMAD Regression Guardrails

Ce document est la reference commune que chaque nouvelle story doit consulter,
citer et enrichir avant d'etre marquee `ready-for-dev`.

Son objectif est d'eviter qu'une story locale casse un comportement, un contrat
ou une decision d'architecture acquis par une story precedente.

## Usage obligatoire pour une nouvelle story

Toute nouvelle story sous `_condamad/stories/<story-key>/00-story.md` doit:

1. Lire ce registre avant de definir son scope.
2. Ajouter dans sa section `Current State Evidence` une preuve de consultation:
   - `Evidence N: _condamad/stories/regression-guardrails.md - invariants consultes avant cadrage.`
3. Ajouter dans `Explicit non-goals` les invariants applicables qu'elle ne doit pas changer.
4. Ajouter dans `Acceptance Criteria` au moins un AC de non-regression quand un invariant applicable existe.
5. Ajouter dans `Validation Plan` les commandes de garde correspondantes.
6. Enrichir ce registre si la story cree un nouvel invariant durable.

Une story qui modifie une surface couverte par ce registre doit capturer un
baseline avant/apres et documenter les differences autorisees dans son dossier.

## Controle avant ready-for-dev

Avant de passer une story a `ready-for-dev`, verifier:

- Le domaine de la story est unique et ne contourne pas un proprietaire canonique existant.
- Les stories precedentes impactables sont listees dans la story.
- Les invariants applicables ci-dessous sont cites comme non-goals ou AC.
- Les snapshots avant/apres sont prevus pour les routes, l'OpenAPI, les imports ou les contrats touches.
- Les guards anti-reintroduction sont deterministes: test AST, inventaire runtime, diff OpenAPI ou scan cible.
- Aucune compatibilite transitoire, alias, fallback ou re-export legacy n'est autorise sans decision explicite.

## Invariants actifs

| ID | Source story | Surface protegee | Invariant | Guard attendu |
|---|---|---|---|---|

## Format d'enrichissement

Quand une story cree un invariant durable, ajouter une ligne a `Invariants actifs`
avec:

- `ID`: prochain identifiant `RG-XXX`.
- `Source story`: dossier de story.
- `Surface protegee`: route, module, contrat, ownership, comportement ou artefact.
- `Invariant`: regle stable a proteger.
- `Guard attendu`: preuve executable ou audit determine qui echoue en cas de regression.

L'invariant doit etre concret. Eviter les formulations vagues comme "ne pas
casser l'existant"; nommer le contrat, le proprietaire, le chemin, le module ou
le symbole protege.

## Snippet a copier dans les nouvelles stories

```md
## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-XXX` - <raison concrete pour laquelle l'invariant s'applique>
- Non-applicable invariants:
  - `RG-YYY` - <raison concrete pour laquelle la story ne touche pas cette surface>
- Required regression evidence:
  - <test, scan, snapshot, diff ou audit>
- Allowed differences:
  - <differences explicitement autorisees, ou "none">
```

## Commandes de controle recommandees

Adapter les commandes au scope de la story. Les commandes Python doivent etre
executees apres activation du venv.

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/<story-key>/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/<story-key>/00-story.md
```

Commandes indicatives selon les surfaces touchees:

```powershell
rg "<forbidden-symbol-or-import>" <paths>
```
