<!-- Registre des constats pour l'audit CONDAMAD du domaine prediction. -->

# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | boundary-violation | `backend/app/prediction` | E-001, E-002, E-005, E-006, E-007, E-017 | Le package racine `app.prediction` possede plusieurs couches a la fois: domaine, orchestration applicative, infra DB, projection API publique et LLM. | Decider et appliquer une convergence namespace: domain pour calcul/contrats purs, services pour use cases, infra pour persistence/context loading, api/contracts pour projection publique, ops pour jobs/bootstrap. | yes |
| F-002 | High | High | dependency-direction-violation | `backend/app/prediction` | E-002, E-005, E-006, E-007 | Des composants qui devraient etre purs ou applicatifs dependent directement de SQLAlchemy, repositories infra, settings globaux et runtime LLM. | Extraire les ports/use-cases et deplacer les implementations DB/LLM vers `infra` et `services`, avec guards AST sur `app.prediction`/futur `domain.prediction`. | yes |
| F-003 | High | High | legacy-surface | `backend/app/prediction` | E-008, E-009, E-010, E-011, E-012 | Le legacy `llm_narrator` est supprime, mais le package conserve d'autres surfaces de compatibilite actives (`EngineOutput`, `TimeBlock`, aliases V3, `engine_output` kwargs, payload `categories`). | Classer chaque surface legacy: garder temporairement avec owner/date de retrait, migrer les consommateurs, ou supprimer. Ne pas recreer `llm_narrator`. | yes |
| F-004 | Medium | High | duplicate-responsibility | `backend/app/prediction.public_projection` | E-007, E-013, E-014 | La projection publique et l'enrichissement astro/LLM sont partages entre `public_projection.py`, `public_astro_daily_events.py`, API/services consommateurs et tests, avec des chemins fallback divergents. | Isoler une couche canonique de projection publique sous `services/api_contracts` ou `services/prediction/public_projection`, puis migrer les policies une par une. | yes |
| F-005 | Medium | High | runtime-contract-drift | `PublicAstroFoundationPolicy` | E-013, E-014 | `astro_foundation` peut etre absent ou incomplet quand l'appelant fournit un `engine_output` dont les evenements sont dans `detected_events`; les aspects exacts `aspect_exact_*` peuvent etre ignores pour les aspects dominants. | Corriger la resolution d'evenements et ajouter tests unitaires pour `engine_output.detected_events` et `aspect_exact_*`. | yes |
| F-006 | Medium | Medium | data-integrity-risk | `PredictionComputeRunner` / prediction compute | E-015 | Le calcul threade capture la session DB de l'appelant; apres timeout, le thread peut continuer avec une session non thread-safe. Cela peut corrompre l'etat de session ou produire des erreurs intermittentes. | Sortir le chargement DB du thread ou ouvrir une session dediee par worker; ajouter un test/guard de non-partage de session. | yes |
| F-007 | Medium | High | missing-guard | architecture prediction | E-010, E-016 | Les guardrails protegent des points LLM precis, mais aucun test d'architecture n'empeche la croissance du package racine `app.prediction` ou l'ajout de nouveaux imports infra/LLM/API. | Ajouter une garde d'architecture de namespace et dependances avant toute migration large. | yes |
| F-008 | Low | Medium | observability-gap | `public_projection` | E-007 | Quand la projection appelle le LLM sans trace/request fournis, elle genere des UUID locaux; la correlation avec la requete API peut etre perdue. | Passer request_id/trace_id depuis l'adaptateur API/service et limiter la projection a l'assemblage deterministe. | yes |

## Finding Details

### F-001

- Severity: High
- Confidence: High
- Category: boundary-violation
- Domain: `backend/app/prediction`
- Evidence: E-001, E-002, E-005, E-006, E-007, E-017
- Expected rule: `backend/app/prediction` ne doit pas etre un dossier racine applicatif concurrent; les responsabilites doivent rejoindre les racines existantes.
- Actual state: le dossier contient calcul pur, DTO/dataclasses, contexte DB, persistance, projection publique, templates et integration LLM.
- Impact: Le package racine `app.prediction` possede plusieurs couches a la fois: domaine, orchestration applicative, infra DB, projection API publique et LLM.
- Recommended action: Decider et appliquer une convergence namespace: domain pour calcul/contrats purs, services pour use cases, infra pour persistence/context loading, api/contracts pour projection publique, ops pour jobs/bootstrap.
- Story candidate: yes
- Suggested archetype: namespace-convergence

### F-002

- Severity: High
- Confidence: High
- Category: dependency-direction-violation
- Domain: `backend/app/prediction`
- Evidence: E-002, E-005, E-006, E-007
- Expected rule: le domaine de prediction pur ne depend pas de SQLAlchemy, repositories, settings globaux ou runtime LLM.
- Actual state: `context_loader.py` et `persistence_service.py` importent infra DB; `public_projection.py` importe `settings`, `Session` et `AIEngineAdapter`.
- Impact: Des composants qui devraient etre purs ou applicatifs dependent directement de SQLAlchemy, repositories infra, settings globaux et runtime LLM.
- Recommended action: Extraire les ports/use-cases et deplacer les implementations DB/LLM vers `infra` et `services`, avec guards AST sur `app.prediction`/futur `domain.prediction`.
- Story candidate: yes
- Suggested archetype: service-boundary-refactor

### F-003

- Severity: High
- Confidence: High
- Category: legacy-surface
- Domain: `backend/app/prediction`
- Evidence: E-008, E-009, E-010, E-011, E-012
- Expected rule: aucune facade, alias, fallback ou re-export legacy ne reste sans classification et plan de retrait.
- Actual state: `llm_narrator` est correctement supprime, mais plusieurs compatibilites restent actives dans les schemas et services.
- Impact: Le legacy `llm_narrator` est supprime, mais le package conserve d'autres surfaces de compatibilite actives (`EngineOutput`, `TimeBlock`, aliases V3, `engine_output` kwargs, payload `categories`).
- Recommended action: Classer chaque surface legacy: garder temporairement avec owner/date de retrait, migrer les consommateurs, ou supprimer. Ne pas recreer `llm_narrator`.
- Story candidate: yes
- Suggested archetype: legacy-facade-removal

### F-004

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: `backend/app/prediction.public_projection`
- Evidence: E-007, E-013, E-014
- Expected rule: projection API publique et enrichissements LLM ont un proprietaire unique et testable.
- Actual state: `PublicPredictionAssembler` assemble le payload, appelle le LLM, garde la retrocompatibilite `categories`, et cohabite avec des services API/LLM.
- Impact: La projection publique et l'enrichissement astro/LLM sont partages entre `public_projection.py`, `public_astro_daily_events.py`, API/services consommateurs et tests, avec des chemins fallback divergents.
- Recommended action: Isoler une couche canonique de projection publique sous `services/api_contracts` ou `services/prediction/public_projection`, puis migrer les policies une par une.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

### F-005

- Severity: Medium
- Confidence: High
- Category: runtime-contract-drift
- Domain: `PublicAstroFoundationPolicy`
- Evidence: E-013, E-014
- Expected rule: les policies publiques lisent les memes sources d'evenements que le moteur et les autres modules publics.
- Actual state: `PublicAstroFoundationPolicy` ignore `core.detected_events` et limite les aspects dominants a `event_type == "aspect"`.
- Impact: `astro_foundation` peut etre absent ou incomplet quand l'appelant fournit un `engine_output` dont les evenements sont dans `detected_events`; les aspects exacts `aspect_exact_*` peuvent etre ignores pour les aspects dominants.
- Recommended action: Corriger la resolution d'evenements et ajouter tests unitaires pour `engine_output.detected_events` et `aspect_exact_*`.
- Story candidate: yes
- Suggested archetype: bugfix-contract-preservation

### F-006

- Severity: Medium
- Confidence: Medium
- Category: data-integrity-risk
- Domain: `PredictionComputeRunner` / prediction compute
- Evidence: E-015
- Expected rule: une session SQLAlchemy ne doit pas etre partagee entre threads.
- Actual state: `PredictionComputeRunner` capture `db` dans `ctx_loader`, lance `orchestrator.run` dans un worker et documente que la session peut rester non thread-safe apres timeout.
- Impact: Le calcul threade capture la session DB de l'appelant; apres timeout, le thread peut continuer avec une session non thread-safe. Cela peut corrompre l'etat de session ou produire des erreurs intermittentes.
- Recommended action: Sortir le chargement DB du thread ou ouvrir une session dediee par worker; ajouter un test/guard de non-partage de session.
- Story candidate: yes
- Suggested archetype: robustness-hardening

### F-007

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: architecture prediction
- Evidence: E-010, E-016
- Expected rule: une dette de namespace connue doit avoir un guard anti-croissance.
- Actual state: les guards LLM existent, mais pas de guard global contre nouveaux fichiers/imports dans `backend/app/prediction`.
- Impact: Les guardrails protegent des points LLM precis, mais aucun test d'architecture n'empeche la croissance du package racine `app.prediction` ou l'ajout de nouveaux imports infra/LLM/API.
- Recommended action: Ajouter une garde d'architecture de namespace et dependances avant toute migration large.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

### F-008

- Severity: Low
- Confidence: Medium
- Category: observability-gap
- Domain: `public_projection`
- Evidence: E-007
- Expected rule: les appels LLM heritent du trace/request id de la requete ou du service appelant.
- Actual state: `PublicPredictionAssembler` genere des UUID fallback avant d'appeler `AIEngineAdapter`.
- Impact: Quand la projection appelle le LLM sans trace/request fournis, elle genere des UUID locaux; la correlation avec la requete API peut etre perdue.
- Recommended action: Passer request_id/trace_id depuis l'adaptateur API/service et limiter la projection a l'assemblage deterministe.
- Story candidate: yes
- Suggested archetype: observability-guard-hardening
