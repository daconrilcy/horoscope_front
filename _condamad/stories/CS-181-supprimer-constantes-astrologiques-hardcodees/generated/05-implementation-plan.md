# Implementation Plan

## Architecture finding

Le runtime natal possède déjà un repository canonique `AstrologyRuntimeReferenceRepository`. Le moteur daily charge des profils d'aspects depuis la DB, mais ne portait pas encore l'angle/famille dans le DTO prediction, ce qui forçait des mappings locaux.

## Plan

1. Supprimer `_legacy_payload_for_mock_db` et l'import `ReferenceDataService` du service natal.
2. Étendre `AspectProfileData` avec `angle` et `family_code` issus de `AspectModel`/`AstralAspectFamilyModel`.
3. Ajouter `app.domain.prediction.aspect_reference.major_aspect_angles` pour dériver les aspects majeurs depuis le contexte runtime chargé.
4. Remplacer les boucles `ASPECTS_V1` / `ASPECTS` dans EventDetector, builders v3 et orchestration par ce resolver.
5. Ajouter un guard AST contre les mappings d'aspects réintroduits.
6. Classer les constantes techniques conservées et capturer les scans avant/après.

## No Legacy stance

Aucun shim ni fallback: l'absence de profils d'aspects ou d'orbe runtime lève une erreur explicite.

## Rollback

Revenir les fichiers modifiés de cette story uniquement; aucune migration ni dépendance n'est introduite.
