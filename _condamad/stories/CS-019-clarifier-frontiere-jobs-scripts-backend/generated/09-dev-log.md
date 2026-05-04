# Dev Log — CS-019

## Preflight

- Initial `git status --short`: registres CONDAMAD modifies et capsule CS-019 non suivie preexistants.
- `AGENTS.md` lu a la racine.
- `_condamad/stories/regression-guardrails.md` lu; `RG-010`, `RG-011`, `RG-013`, `RG-015`, `RG-035`, `RG-038`, `RG-039` appliques.

## Decisions

- Owner canonique des traitements planifiables: `app.scheduled_tasks`.
- Owner canonique des helpers calibration: `app.services.calibration`.
- Wrappers CLI ajoutes sous `backend/scripts` pour `generate_review_grid`, `generate_qa_cases` et `validate_dataset`.
- Aucun shim ou re-export `app.jobs` conserve.

## Validation deja passee

- Tests cibles jobs/calibration, integration baseline et guardrails transverses passes.
- Scans No Legacy: zero hit actif pour `app.jobs`; `app/prediction` absent.
