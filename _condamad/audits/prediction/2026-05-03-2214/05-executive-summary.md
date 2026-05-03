<!-- Synthese executive de l'audit CONDAMAD prediction. -->

# Executive Summary

Audit cible: `backend/app/prediction`

Conclusion: le dossier est actif et contient des proprietaires canoniques utiles, mais il ne doit pas rester a la racine de `app`. Il regroupe trop de couches: moteur metier, contrats, orchestration, DB, projection publique, templates et LLM. Le legacy `llm_narrator` est correctement eteint; le legacy restant concerne surtout les vues de compatibilite V2/V3 et le payload public.

Findings:

- High: 3
- Medium: 4
- Low: 1
- Story candidates: 8

Top risks:

1. `app.prediction` est un namespace multi-couches sans owner unique.
2. `context_loader.py`, `persistence_service.py` et `public_projection.py` violent la direction des dependances attendue.
3. Des compatibilites legacy restent actives sans registre de retrait.
4. `PublicAstroFoundationPolicy` a un bug probable: fallback `engine_output.detected_events` ignore et aspects exacts non pris comme aspects dominants.
5. `PredictionComputeRunner` partage une session DB avec un thread de calcul et documente un risque non-thread-safe apres timeout.

Refactorisation cible recommandee:

- `domain/prediction`: schemas purs, moteur de calcul, aggregators, temporal kernel/sampler, event detection, scoring, public taxonomies pures.
- `services/prediction`: orchestration de use-case, compute runner, run reuse, fallback, relative scoring, projection publique deterministe si elle reste applicative.
- `infra/db`: context loader DB, persistence service ou repository adapter, persisted read models si lies au stockage.
- `api` / `services/api_contracts`: contrats de payload public et assemblage final destine aux routes.
- `ops`: jobs, bootstrap, seed et generation de datasets/QA.
- racine `app`: aucune nouvelle racine `prediction`; garder seulement imports transitoires avec story de migration et guards.

Validation: artefacts generes; validation CONDAMAD a executer apres creation des fichiers.
