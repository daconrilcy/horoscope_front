# Finding Register - prompt-generation - 2026-04-30-1810

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | legacy-surface | `horoscope_daily` | E-008, E-009, E-015, E-016, E-019 | Un ancien chemin direct OpenAI reste executable pour la narration quotidienne, hors `LLMGateway`, alors que le registre legacy le marque comme candidat au retrait et interdit pour `horoscope_daily`. | Supprimer ou rendre techniquement inexecutable `LLMNarrator`, puis conserver uniquement le chemin canonique post-70.15. | yes |
| F-002 | High | High | duplicate-responsibility | LLM prompt generation | E-006, E-007, E-009, E-016, E-019, E-020 | Les prompts executables existent a la fois dans les assemblies canoniques et dans `PROMPT_FALLBACK_CONFIGS`; cela maintient un second proprietaire actif pour `natal`, `chat`, `horoscope_daily` et `guidance_contextual`. | Retirer les prompts fallback des familles supportees ou les bloquer par guard deterministe hors tests/bootstrap explicitement allowlistes; garder le bootstrap non-prod de 70.16 strictement borne et prouve. | yes |
| F-003 | Medium | High | missing-canonical-owner | `horoscope_daily` | E-010, E-018, E-020, E-021, E-022 | La partie la plus structurante du prompt `horoscope_daily` est construite dans `app.prediction` comme `question`, avec des consignes de format et de style hors assembly, hors renderer et hors gouvernance de placeholders. | Deplacer les consignes editoriales stables dans une assembly `horoscope_daily/narration`; limiter le builder aux donnees utilisateur/contextuelles et l'ancrer dans le sous-namespace de generation attendu. | yes |
| F-004 | Medium | Medium | needs-user-decision | `consultation specifique` | E-012, E-005, E-020 | Les consultations specifiques utilisent `guidance_contextual` et des objectifs issus de templates consultation; aucun domaine LLM canonique `consultation` n'existe, donc l'ownership produit est ambigu. | Decision utilisateur: documenter `consultation specifique` comme sous-cas de `guidance`, ou creer une famille/sous-feature canonique avec contrat, placeholders et assemblies dedies. | yes |
| F-005 | Info | High | boundary-violation | Prompt generation boundary | E-013, E-016, E-019 | Aucun import API/FastAPI n'a ete trouve dans les couches de generation de prompt auditees; les guardrails `RG-004` a `RG-006` sont respectes sur cette dimension. | Conserver les scans d'architecture existants comme garde anti-regression. | no |
| F-006 | Info | High | missing-guard | Test coverage | E-014, E-002, E-018, E-020, E-021, E-022 | La couverture de tests est riche, mais les constats F-001 a F-004 montrent que certains invariants utiles ne sont pas exprimes comme guards dedies par feature prompt-generation. | Ajouter les guards cibles dans les stories issues de cet audit, en reutilisant les tests QA/admin existants plutot qu'un nouveau harness parallele. | no |

## F-001 Legacy `LLMNarrator` encore executable

- Severity: High
- Confidence: High
- Category: legacy-surface
- Domain: `horoscope_daily`
- Evidence: E-008, E-009, E-015, E-016, E-019
- Expected rule: `horoscope_daily` doit passer par `AIEngineAdapter.generate_horoscope_narration` puis `LLMGateway`; les chemins directs OpenAI historiques ne doivent plus rester appelables.
- Actual state: `backend/app/prediction/llm_narrator.py` conserve une classe depreciee qui cree `openai.AsyncOpenAI`, assemble ses propres messages et appelle `chat.completions.create`.
- Impact: Un ancien chemin direct OpenAI reste executable pour la narration quotidienne, hors `LLMGateway`, alors que le registre legacy le marque comme candidat au retrait et interdit pour `horoscope_daily`.
- BMAD 70 reconciliation: 70.15 a supprime le namespace historique `llm_orchestration`; F-001 est donc un reliquat executable hors namespace legacy, pas une dette de migration de dossier. 70.20 impose de ne pas recréer un adapter narratif parasite.
- Recommended action: Supprimer ou rendre techniquement inexecutable `LLMNarrator`, puis conserver uniquement le chemin canonique post-70.15 (`service de generation -> gateway canonique`).
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

## F-002 Prompts fallback actifs en doublon des assemblies

- Severity: High
- Confidence: High
- Category: duplicate-responsibility
- Domain: LLM prompt generation
- Evidence: E-006, E-007, E-009, E-016, E-019, E-020
- Expected rule: Les familles supportees `chat`, `guidance`, `natal`, `horoscope_daily` ont un proprietaire canonique unique: assembly + renderer + gateway.
- Actual state: `PROMPT_FALLBACK_CONFIGS` contient encore des prompts pour les quatre surfaces auditees et `build_fallback_use_case_config` peut les transformer en `UseCaseConfig`.
- Impact: Les prompts executables existent a la fois dans les assemblies canoniques et dans `PROMPT_FALLBACK_CONFIGS`; cela maintient un second proprietaire actif pour `natal`, `chat`, `horoscope_daily` et `guidance_contextual`.
- BMAD 70 reconciliation: le post-audit 70.15 accepte `domain.llm.prompting.catalog` comme point d'entree canonique des donnees runtime/fallback borne; 70.16 documente un bootstrap non-prod borne pour base vide. Le probleme F-002 n'est donc pas l'existence d'un module `catalog`, mais l'executabilite de prompts fallback comme second proprietaire sur des familles supportees.
- Recommended action: Retirer les prompts fallback des familles supportees ou les bloquer par guard deterministe hors tests/bootstrap explicitement allowlistes; si un bootstrap non-prod subsiste, il doit etre flagge, observable, teste et absent du nominal prod.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

## F-003 Prompt quotidien construit hors domaine LLM

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: `horoscope_daily`
- Evidence: E-010, E-018, E-020, E-021, E-022
- Expected rule: Les consignes stables de sortie, de style et de securite editoriale appartiennent au prompt assembly gouverne.
- Actual state: `AstrologerPromptBuilder` produit un long bloc d'instructions contenant objectif, format JSON, interdictions, contraintes de longueur et correction de retry, puis ce bloc devient `question`.
- Impact: La partie la plus structurante du prompt `horoscope_daily` est construite dans `app.prediction` comme `question`, avec des consignes de format et de style hors assembly, hors renderer et hors gouvernance de placeholders.
- BMAD 70 reconciliation: 70.12 impose que l'admin expose des couches observables et artefacts runtime reels; si les consignes quotidiennes restent dans le builder, l'admin ne peut pas representer fidelement la source de verite. 70.21 demande aussi une organisation explicite de `llm_generation/horoscope_daily`.
- Recommended action: Deplacer les consignes editoriales stables dans une assembly `horoscope_daily/narration`; limiter `AstrologerPromptBuilder` aux donnees utilisateur/contextuelles; migrer ou encapsuler le builder dans le sous-namespace de generation attendu sans remettre de logique durable dans `AIEngineAdapter`.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

## F-004 Ownership consultation specifique ambigu

- Severity: Medium
- Confidence: Medium
- Category: needs-user-decision
- Domain: `consultation specifique`
- Evidence: E-012, E-005, E-020
- Expected rule: Chaque feature auditee doit avoir une taxonomie et un contrat de prompt explicites, ou une decision documentee de reutilisation.
- Actual state: La consultation specifique passe par `GuidanceService.request_contextual_guidance_async` avec `use_case="guidance_contextual"`; les objectifs viennent soit de la requete soit de templates consultation.
- Impact: Les consultations specifiques utilisent `guidance_contextual` et des objectifs issus de templates consultation; aucun domaine LLM canonique `consultation` n'existe, donc l'ownership produit est ambigu.
- BMAD 70 reconciliation: 70.16 indique que `guidance_contextual` et les prompts guidance ont ete remis dans le bootstrap canonique pour exposer les consultations thematiques. La decision la plus courte peut donc etre documentaire si le produit confirme que `consultation specifique` est une variante de `guidance`.
- Recommended action: Decision utilisateur: garder `consultation specifique` comme sous-cas de `guidance` documente, ou creer une famille/sous-feature canonique avec contrat, placeholders et assemblies dedies.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

## F-005 Frontieres API/services respectees

- Severity: Info
- Confidence: High
- Category: boundary-violation
- Domain: Prompt generation boundary
- Evidence: E-013, E-016, E-019
- Expected rule: Les couches de generation de prompt ne doivent pas dependre de l'API ou des types FastAPI.
- Actual state: Aucun `from app.api`, `HTTPException` ou `JSONResponse` n'est present dans les chemins `domain/llm`, `services/llm_generation` et `prediction` audites.
- Impact: Aucun import API/FastAPI n'a ete trouve dans les couches de generation de prompt auditees; les guardrails `RG-004` a `RG-006` sont respectes sur cette dimension.
- Recommended action: Conserver les scans d'architecture existants comme garde anti-regression.
- Story candidate: no
- Suggested archetype: no-story

## F-006 Couverture existante mais guards a completer

- Severity: Info
- Confidence: High
- Category: missing-guard
- Domain: Test coverage
- Evidence: E-014, E-002, E-018, E-020, E-021, E-022
- Expected rule: Les invariants durables decouverts par audit doivent etre proteges par tests ou scans cibles dans les stories de correction.
- Actual state: Les tests couvrent le renderer, les assemblies, la migration narrator et la gouvernance legacy. Les guards exacts proposes pour ce domaine doivent etre ajoutes dans les stories.
- Impact: La couverture de tests est riche, mais les constats F-001 a F-004 montrent que certains invariants utiles ne sont pas exprimes comme guards dedies par feature prompt-generation.
- BMAD 70 reconciliation: les stories 70.9-70.12, 70.16, 70.20 et 70.21 fournissent deja des harness utiles. Les nouveaux guards doivent les reutiliser: tests admin de couches runtime, routes QA, garde-fous d'import, scans direct-provider et tests de sous-namespace services.
- Recommended action: Ajouter les guards cibles dans les stories issues de cet audit.
- Story candidate: no
- Suggested archetype: no-story
