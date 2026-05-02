# Finding Register - prompt-generation - 2026-05-02-1452

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | duplicate-responsibility | LLM prompt fallback exceptions | E-004, E-010, E-011 | Les fallbacks explicitement interdits sont bloques, mais des prompts fallback executables subsistent pour plusieurs use cases canoniques ou proches du nominal. | Converger les exceptions restantes vers assemblies/prompts gouvernes ou documenter une decision produit/ops stricte pour chaque exception executable. | yes |
| F-002 | Low | High | runtime-contract-drift | Story validation evidence | E-010, E-011, E-012 | Des chemins de validation listes dans les stories ne correspondent pas aux fichiers collectes; cela ralentit la verification et peut masquer une preuve ciblee. | Mettre a jour les chemins de validation dans les stories concernees ou ajouter une garde documentaire qui verifie les chemins de tests references. | yes |
| F-003 | Info | High | legacy-surface | `horoscope_daily` narrator | E-002, E-010, E-011 | Le chemin direct `LLMNarrator` / OpenAI est eteint dans le runtime et les tests collectes audites. | Conserver les guards `RG-016` / `RG-017`. | no |
| F-004 | Info | High | missing-canonical-owner | `horoscope_daily` prompt assembly | E-005, E-006, E-010, E-011 | Les consignes durables quotidiennes sont dans l'assembly; le builder ne conserve que le contexte metier. | Conserver le scan anti-retour du builder et les tests de seed assembly. | no |
| F-005 | Info | High | needs-user-decision | Consultation specifique | E-007, E-008, E-010 | La decision d'ownership est formalisee: consultation specifique reste un sous-cas de `guidance_contextual`. | Conserver le guard anti famille `consultation` sans decision produit. | no |
| F-006 | Info | High | dependency-direction-violation | Prompt generation boundary | E-009 | Aucune dependance API/FastAPI interdite n'a ete detectee dans les couches auditees. | Conserver les scans d'architecture existants. | no |

## F-001 Fallback exceptions encore executables

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: LLM prompt fallback exceptions
- Evidence:
  - id: E-004
  - id: E-010
  - id: E-011
- Expected rule: Les consignes durables des use cases canoniques doivent etre gouvernees par assemblies/prompts versionnes, sans second proprietaire runtime.
- Actual state: `PROMPT_FALLBACK_CONFIGS` conserve une allowlist exacte incluant notamment `natal_interpretation_short`, `guidance_daily`, `guidance_weekly`, `event_guidance`, `natal_long_free` et `astrologer_selection_help`. `build_fallback_use_case_config` peut encore transformer ces entrees en `UseCaseConfig`.
- Impact: Les fallbacks explicitement interdits sont bloques, mais des prompts fallback executables subsistent pour plusieurs use cases canoniques ou proches du nominal.
- Recommended action: Converger les exceptions restantes vers assemblies/prompts gouvernes ou documenter une decision produit/ops stricte pour chaque exception executable.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening

## F-002 Chemins de validation de stories obsoletes

- Severity: Low
- Confidence: High
- Category: runtime-contract-drift
- Domain: Story validation evidence
- Evidence:
  - id: E-010
  - id: E-011
  - id: E-012
- Expected rule: Les stories livrees doivent pointer vers des commandes de validation executables sans correction manuelle.
- Actual state: Les chemins `tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` et `tests/unit/test_guidance_service.py` n'existent pas; les fichiers reels sont sous `app/tests/unit`.
- Impact: Des chemins de validation listes dans les stories ne correspondent pas aux fichiers collectes; cela ralentit la verification et peut masquer une preuve ciblee.
- Recommended action: Mettre a jour les chemins de validation dans les stories concernees ou ajouter une garde documentaire qui verifie les chemins de tests references.
- Story candidate: yes
- Suggested archetype: test-guard-hardening

## F-003 Narrator legacy eteint

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: `horoscope_daily` narrator
- Evidence:
  - id: E-002
  - id: E-010
  - id: E-011
- Expected rule: `horoscope_daily` ne doit pas exposer de narrateur direct OpenAI hors gateway.
- Actual state: Aucun hit executable pour `LLMNarrator(`, import nominal legacy, `chat.completions.create` ou `openai.AsyncOpenAI` dans `backend/app` et `backend/tests`.
- Impact: Le chemin direct `LLMNarrator` / OpenAI est eteint dans le runtime et les tests collectes audites.
- Recommended action: Conserver les guards `RG-016` / `RG-017`.
- Story candidate: no
- Suggested archetype: no-story

## F-004 Consignes quotidiennes dans l'assembly

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: `horoscope_daily` prompt assembly
- Evidence:
  - id: E-005
  - id: E-006
  - id: E-010
  - id: E-011
- Expected rule: Les consignes stables de sortie, style et interdiction appartiennent a l'assembly.
- Actual state: `AstrologerPromptBuilder` assemble le contexte; `HOROSCOPE_DAILY_NARRATION_PROMPT` porte les consignes durables.
- Impact: Les consignes durables quotidiennes sont dans l'assembly; le builder ne conserve que le contexte metier.
- Recommended action: Conserver le scan anti-retour du builder et les tests de seed assembly.
- Story candidate: no
- Suggested archetype: no-story

## F-005 Consultation formalisee sous guidance

- Severity: Info
- Confidence: High
- Category: needs-user-decision
- Domain: Consultation specifique
- Evidence:
  - id: E-007
  - id: E-008
  - id: E-010
- Expected rule: La taxonomie consultation doit etre explicite.
- Actual state: Documentation et tests gardent `consultation specifique` comme sous-cas de `guidance_contextual`; aucune famille `consultation` n'est active.
- Impact: La decision d'ownership est formalisee: consultation specifique reste un sous-cas de `guidance_contextual`.
- Recommended action: Conserver le guard anti famille `consultation` sans decision produit.
- Story candidate: no
- Suggested archetype: no-story

## F-006 Frontiere API respectee

- Severity: Info
- Confidence: High
- Category: dependency-direction-violation
- Domain: Prompt generation boundary
- Evidence:
  - id: E-009
- Expected rule: Les couches de generation de prompt ne dependent pas de l'API ou des types FastAPI.
- Actual state: Aucun hit interdit dans le scope audite.
- Impact: Aucune dependance API/FastAPI interdite n'a ete detectee dans les couches auditees.
- Recommended action: Conserver les scans d'architecture existants.
- Story candidate: no
- Suggested archetype: no-story
