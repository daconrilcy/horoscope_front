# CONDAMAD Code Review

## Review target

- Story: `CS-189-brancher-etoiles-fixes-scoring-runtime`
- Scope reviewed: rédaction de la story, ligne de statut, nouvel invariant `RG-117`
  et cohérence avec le code backend existant cité par la story.
- Review iterations: 2

## Inputs reviewed

- `_condamad/stories/CS-189-brancher-etoiles-fixes-scoring-runtime/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`

## Diff summary

- La story CS-189 est ajoutée comme story prête à implémenter.
- Le registre ajoute `RG-117` pour protéger le contrat runtime fixed stars daily.
- Le statut ajoute CS-189 en `ready-to-dev`.
- La review a corrigé la story sans modifier le code applicatif.

## Findings

No remaining actionable findings.

### Fixed during iteration 1

- Le contrat demandait `category_code` comme champ DB-backed alors que les modèles
  `astral_fixed_star_*` ne portent pas de catégorie produit par étoile fixe.
  Correction: la story distingue désormais `source_category`/keywords des poids
  de routage explicites de ruleset.
- `Reintroduction Guard` était marqué `no` alors que la story crée `RG-117` et
  exige AC6. Correction: le guard est désormais `required`, avec comportements
  attendus et preuves exécutables.
- AC6 et la validation ne couvraient pas systématiquement `fixed_star_display_name`.
  Correction: les scans citent le symbole dans le guard exécutable et RG-117.
- La correction initiale a créé des lignes trop longues et un faux placeholder
  via `tuple[str, ...]`. Correction: la rédaction respecte le lint strict.

## Acceptance audit

- AC1 à AC7 sont traçables vers des preuves de validation.
- Les non-goals interdisent les catalogues locaux, l'orbe hardcodée et les
  changements hors `domain/prediction`.
- Le champ `source_category` est explicitement limité à une métadonnée de source;
  aucune catégorie produit DB inexistante n'est imposée.

## Validation audit

- `CONDAMAD story validation`: PASS
- `CONDAMAD story lint --strict`: PASS
- `git diff --check`: PASS

## DRY / No Legacy audit

- Aucun fichier applicatif n'a été modifié.
- La story interdit toujours `_STAR_DATA`, `fixed_star_longitudes`,
  `fixed_star_display_name` et `FIXED_STAR_*` comme catalogues locaux.
- Aucun fallback, alias, shim ou exception large n'a été ajouté dans la rédaction.

## Commands run by reviewer

```powershell
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-189-brancher-etoiles-fixes-scoring-runtime\00-story.md
git diff --check
```

## Residual risks

Aucun risque restant identifie pour la rédaction. L'implémentation backend reste
à réaliser dans une story de développement séparée.

## Verdict

CLEAN
