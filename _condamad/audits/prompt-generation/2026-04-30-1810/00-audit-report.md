# CONDAMAD Domain Audit - prompt-generation - 2026-04-30-1810

## Scope

- Domain target: `prompt-generation`
- Archetype: service-boundary-audit with No Legacy / DRY overlay
- Features auditees: `natal`, `horoscope_daily`, `chat`, `consultation specifique`
- Corpus complementaire integre: audit post-story 70-15 du 2026-04-21, stories BMAD 70.1 a 70.23 sous `_bmad-output/implementation-artifacts`, statut sprint epic 70.
- Mode: read-only for application code; audit artifacts written under `_condamad/audits/**`
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`

## Expected responsibility

Le domaine de generation de prompt doit avoir un proprietaire canonique unique pour les consignes LLM durables: contracts, assemblies, renderer, gateway et provider wrapper. Les services de feature peuvent preparer le contexte metier, mais ne doivent pas maintenir des prompts concurrents, des fallbacks legacy actifs ou des appels provider directs.

Cette responsabilite inclut aussi la chaine admin/ops creee par l'epic 70: catalogue, lecture des couches, preview, release, historisation, rollback, audit, QA interne et observabilite doivent lire ou tester le meme pipeline canonique, sans reconstruire une interpretation parallele du prompt.

## Cross-audit reconciliation

L'audit du 2026-04-21 post-story 70-15 etablissait un point de depart fort:

- `app.application.llm.*`, `app.domain.llm.*`, `app.infrastructure.*` et `app.ops.llm.*` sont devenus les namespaces nominaux.
- `backend/app/llm_orchestration/` et `legacy_prompt_runtime.py` ont ete retires du runtime actif.
- `app.prompts` ne porte plus de package runtime nominal; le point d'entree prompting canonique est `app.domain.llm.prompting.*`.
- Les operations release/eval/replay/golden/qualification vivent sous `app.ops.llm.*`.
- La validation backend tracee etait verte au 2026-04-21: `ruff format .`, `ruff check .`, `pytest -q` avec `2964 passed, 12 skipped`.

Le present audit du 2026-04-30 ne remet pas en cause cette convergence de namespaces. Il complete la lecture sur la chaine de generation effective par feature. Les ecarts detectes concernent surtout:

- des surfaces executables ou semi-executables residuelles qui ne sont pas des imports `llm_orchestration`, notamment `LLMNarrator` et certains fallback prompts;
- la repartition des consignes durables entre assembly canonique, builder de contexte et objectifs consultation;
- la couverture de preuve entre runtime, admin/ops et QA apres les stories 70.16, 70.20 et 70.21.

## BMAD 70 coverage map

| Segment de chaine | Stories BMAD relues | Couverture apportee | Impact audit |
|---|---|---|---|
| Navigation et surfaces admin prompts | 70.1 a 70.8, 70.11, 70.12 | Routes dediees, catalogue master-detail, graphe React Flow, libelles, responsive, lecture en couches observables. | Confirme que l'admin doit montrer les artefacts runtime reels et ne pas inventer un pipeline parallele. |
| Edition, versioning et audit prompt | 70.9, 70.10 | Creation de draft, statuts `draft/inactive/published`, diff, rollback, audit events sans contenu complet du prompt. | Complete le perimetre: toute correction F-002/F-003 doit rester compatible avec versioning, release snapshots et audit admin. |
| Nettoyage backend et canonique | 70.13, 70.14, 70.15, audit 2026-04-21 | Assembly/profile first, suppression des namespaces historiques, domaines `runtime`, `prompting`, `configuration`, `governance`, `ops`. | Les findings F-001/F-002 sont des dettes residuelles autour de l'executable et du fallback, pas une remise en cause de la migration de namespace. |
| Documentation, QA et routes test | 70.16 | Doc pipeline post-70-15, seed QA, routes internes guidance/chat/natal/horoscope, tests de resolution/messages/normalisation. | Ajoute un axe de preuve attendu pour verifier les fixes: tests QA et routes internes doivent continuer a executer le pipeline canonique. |
| Donnees et structure residuelle | 70.17, 70.18, 70.18b, 70.21, 70.23 | Cleanup DB/couche services, regroupement `services/llm_generation`, observabilite, guardrails zero legacy/DRY. | Les story candidates doivent respecter les nouveaux sous-namespaces de services et interdire les retours a plat ou shims. |
| Adapter applicatif | 70.20 | Audit/assainissement de `AIEngineAdapter`; objectif facade utile, sans fallback test ni responsabilite parasite. | F-001/F-003 doivent eviter de redeplacer de la logique narrative ou de prompting durable dans l'adapter. |

## Process map by feature

### `natal`

- Public service: `backend/app/services/llm_generation/natal/interpretation_service.py`
- Input preparation: `build_chart_json`, `build_enriched_evidence_catalog`, `NatalExecutionInput`
- Adapter: `AIEngineAdapter.generate_natal_interpretation`
- Canonical request: `feature="natal"`, subfeature derived from use case or `interpretation`
- Gateway: assembly/profile resolution, placeholder render, schema validation, provider call
- Evidence: E-003, E-004, E-005

Key risk: `PROMPT_FALLBACK_CONFIGS` keeps natal prompt strings as a second executable owner. See F-002.

BMAD reconciliation: 70.15/70.16 confirment que le chemin cible est `service metier -> AIEngineAdapter -> LLMGateway -> prompting/configuration canonique`; les preuves QA de 70.16 doivent rester le smoke de reference pour toute correction natal.

### `horoscope_daily`

- Public runtime path: `AIEngineAdapter.generate_horoscope_narration`
- Feature service: `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- Context/prompt-like payload: `AstrologerPromptBuilder().build(...)`
- Canonical request: `feature="horoscope_daily"`, `subfeature="narration"`, plan `free` or `premium`
- Gateway execution: `LLMGateway.execute_request`
- Evidence: E-003, E-004, E-010

Key risks: deprecated `LLMNarrator` still directly calls OpenAI (F-001), and `AstrologerPromptBuilder` owns durable prompt instructions outside assembly (F-003).

BMAD reconciliation: 70.20 reduit la surface de l'adapter et interdit d'y reposer des responsabilites narratives parasites; 70.21 demande un sous-namespace explicite `llm_generation/horoscope_daily`. Le fix F-003 doit donc converger vers assembly/configuration + service de generation dedie, pas vers un nouveau helper transverse.

### `chat`

- Public service: `backend/app/services/llm_generation/chat/chat_guidance_service.py`
- Input preparation: anonymized user message/history, context window, persona/current context, plan
- Adapter: `AIEngineAdapter.generate_chat_reply`
- Canonical request: `use_case="chat_astrologer"`, `feature="chat"`, `subfeature="astrologer"`
- Gateway: chat interaction mode, history + user payload composition
- Evidence: E-003, E-005, E-011

Key risk: prompt fallback for `chat` remains present in `PROMPT_FALLBACK_CONFIGS`. See F-002.

BMAD reconciliation: 70.16 exige des tests de messages provider, persona et normalisation pour chat; ces tests doivent etre conserves comme garde anti-regression si les fallback prompts sont retires.

### `consultation specifique`

- Public service: `backend/app/services/llm_generation/consultation_generation_service.py`
- Precheck: refusal/block/reframe can stop generation before LLM call
- Context assembly: consultation objective, relation natal context, route key, third-party context
- Runtime service: `GuidanceService.request_contextual_guidance_async`
- Canonical request: `use_case="guidance_contextual"`, `feature="guidance"`, `subfeature="contextual"`
- Evidence: E-005, E-012

Key risk: no explicit LLM family or documented ownership for consultation-specific prompts. See F-004.

BMAD reconciliation: 70.16 a retabli et documente `guidance_contextual` pour les consultations thematiques. F-004 devient donc une decision de taxonomie/ownership a formaliser: conserver `consultation specifique` comme sous-cas documente de `guidance`, ou creer une sous-feature canonique distincte.

## Findings summary

| Severity | Count | Findings |
|---|---:|---|
| Critical | 0 | - |
| High | 2 | F-001, F-002 |
| Medium | 2 | F-003, F-004 |
| Low | 0 | - |
| Info | 2 | F-005, F-006 |

## Mandatory audit dimensions

### DRY

Fail. Assemblies and `PROMPT_FALLBACK_CONFIGS` both own executable prompt text for supported families. `horoscope_daily` also has durable prompt instructions in `AstrologerPromptBuilder`. Les stories 70.9-70.12 ajoutent une contrainte de DRY supplementaire: l'admin ne doit pas afficher, editer ou auditer une source de prompt differente de celle qui part reellement au provider.

### No Legacy

Fail. `LLMNarrator` remains executable and direct-provider. The legacy residual registry already classifies `fb.narrator_legacy`, `fb.use_case_first` and `fb.resolve_model` as removal candidates for supported families. This is a residual executable surface after the successful 70.15 namespace migration, not a reappearance of `app.llm_orchestration`.

### Mono-domain ownership

Partial. `LLMGateway` is the central runtime owner, but `horoscope_daily` and `consultation specifique` still distribute stable prompt decisions across feature services and prediction modules. Admin/ops ownership is otherwise well covered by 70.9-70.12 and `app.ops.llm.*`.

### Dependency direction

Pass. No `app.api`, `HTTPException` or `JSONResponse` usage was found in the audited generation layers.

## Coverage conclusion

La chaine est couverte sur les axes structurels suivants: namespaces canoniques, runtime gateway, prompting/configuration, admin catalog/release/consumption, versioning/audit, QA interne et guardrails de non-retour legacy.

La chaine n'est pas encore couverte de facon satisfaisante sur trois axes executables:

1. extinction technique d'un chemin provider direct ancien (`LLMNarrator`);
2. extinction ou bornage prouve des prompts fallback pour familles supportees;
3. convergence des consignes durables `horoscope_daily` et de la taxonomie `consultation specifique`.

## Files created

- `00-audit-report.md`
- `01-evidence-log.md`
- `02-finding-register.md`
- `03-story-candidates.md`
- `04-risk-matrix.md`
- `05-executive-summary.md`
