# Rapport registre legacy r�siduel (schema_version=2026.04.14)

## Chemins fallback
- `fb.deprecated_feature_alias` | type=alias | fallback=deprecated_feature_alias | statut_registre=deprecated | statut_exec=transitoire | p�rim�tre=Normalisation pr�-gateway ; ne remplace pas l'assembly.
- `fb.deprecated_use_case` | type=legacy_use_case | fallback=deprecated_use_case | statut_registre=deprecated | statut_exec=transitoire | p�rim�tre=Cl�s list�es dans deprecated_use_cases[] du m�me registre ; la r�solution nominale support�e reste assembly obligatoire.
- `fb.execution_config_admin` | type=fallback | fallback=execution_config_admin | statut_registre=removal_candidate | statut_exec=� retirer | p�rim�tre=Tous parcours nominaux jusqu'� migration ExecutionProfile.
- `fb.legacy_wrapper` | type=legacy_resolution_path | fallback=legacy_wrapper | statut_registre=deprecated | statut_exec=transitoire | p�rim�tre=Entr�e legacy execute() uniquement ; parcours non nominal (is_nominal=false).
- `fb.narrator_legacy` | type=legacy_resolution_path | fallback=narrator_legacy | statut_registre=removal_candidate | statut_exec=� retirer | p�rim�tre=horoscope_daily via LLMNarrator uniquement.
- `fb.natal_no_db` | type=fallback | fallback=natal_no_db | statut_registre=deprecated | statut_exec=transitoire | p�rim�tre=Tests et contextes explicitement non nominaux.
- `fb.provider_openai` | type=fallback | fallback=provider_openai | statut_registre=deprecated | statut_exec=tol�r� durablement | p�rim�tre=Provider non list� dans supported_providers sur chemins non strictement nominaux.
- `fb.resolve_model` | type=fallback | fallback=resolve_model | statut_registre=removal_candidate | statut_exec=� retirer | p�rim�tre=Chemins sans profil explicite ; interdit sur familles support�es en nominal.
- `fb.test_local` | type=fallback | fallback=test_local | statut_registre=allowed | statut_exec=tol�r� durablement | p�rim�tre=Environnements non production uniquement.
- `fb.use_case_first` | type=legacy_resolution_path | fallback=use_case_first | statut_registre=removal_candidate | statut_exec=� retirer | p�rim�tre=Features hors SUPPORTED_FAMILIES ou tests explicites (test_fallback_active).

## Aliases gouvern�s
- `alias.feature.daily_prediction` | feature `daily_prediction` -> `horoscope_daily` | deprecated
- `alias.feature.natal_interpretation` | feature `natal_interpretation` -> `natal` | deprecated
- `alias.subfeature.natal_interpretation` | subfeature `natal_interpretation` -> `interpretation` | deprecated

## Use cases d�pr�ci�s (bindings)
- `horoscope_daily_free` -> `deprecated.use_case.horoscope_daily_free` | deprecated
- `horoscope_daily_full` -> `deprecated.use_case.horoscope_daily_full` | deprecated

## Blocage progressif effectif
- ids: fb.resolve_model, fb.use_case_first

## Violations
- (aucune � la g�n�ration ; ex�cuter les tests registre pour validation)
