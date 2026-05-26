# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | backend-domain | E-004, E-005, E-009, E-010, E-016 | Une evolution de prompt pourrait continuer a s'appuyer sur `chart_json` ou sur une projection B2C, avec perte de faits ou shaping editorial non controle. | Declarer une decision d'architecture pour faire de `AINarrativeInputContract` le candidat cible, avec migration ulterieure separee et garde de non-injection accidentelle. | yes |
| F-002 | Medium | High | duplicate-responsibility | backend-domain | E-006, E-007, E-008, E-014, E-017, E-018, E-019 | Les labels `llm_input_selection`, `editorial_depth_profile` ou `frontend_visibility_rules` peuvent etre pris pour des faits alors qu'ils sont du shaping produit. | Conserver `structured_facts_v1` comme source factuelle et traiter `client_interpretation_projection_v1` comme support produit/shaping, pas comme source canonique prompt. | yes |
| F-003 | Medium | High | observability-gap | backend-domain | E-011, E-012, E-013, E-015, E-021, E-022 | Confondre cette surface avec une entree prompt ferait fuiter ou dupliquer des metadonnees operationnelles dans la generation. | Documenter une frontiere stricte: audit-only pour hashes, provider/model, prompt refs et `evidence_refs`; jamais payload prompt brut. | no |
| F-004 | Low | High | missing-guard | backend-domain | E-001, E-003, E-016, E-023 | Risque modere lors d'une story ulterieure si la decision cible n'est pas reprise. | Ne pas modifier le registre global pour cet audit; proposer un guardrail seulement lors d'une story de migration prompt. | no |

## F-001 - Canonical LLM input target remains undecided in runtime

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend-domain
- Evidence: E-004, E-005, E-009, E-010, E-016
- Expected rule: Le contrat cible d'injection LLM doit etre distingue des projections produit, des traces d'audit et des payloads historiques.
- Actual state: `AINarrativeInputContract` est le meilleur candidat interne car il porte faits, signaux, readiness flags, provenance et masquage, mais le chemin LLM natal scope ne le consomme pas encore.
- Impact: Une evolution de prompt pourrait continuer a s'appuyer sur `chart_json` ou sur une projection B2C, avec perte de faits ou shaping editorial non controle.
- Recommended action: Declarer une decision d'architecture pour faire de `AINarrativeInputContract` le candidat cible, avec migration ulterieure separee et garde de non-injection accidentelle.
- Story candidate: yes
- Suggested archetype: llm-input-contract-architecture-decision

## F-002 - Client projections are not factual prompt contracts

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: backend-domain
- Evidence: E-006, E-007, E-008, E-014, E-017, E-018, E-019
- Expected rule: Les faits hashables, les signaux interpretatifs et le shaping produit doivent avoir des owners separes.
- Actual state: `structured_facts_v1` expose une frontiere hashable, tandis que `beginner_summary_v1` et `client_interpretation_projection_v1` reduisent, labelisent et filtrent pour le client.
- Impact: Les labels `llm_input_selection`, `editorial_depth_profile` ou `frontend_visibility_rules` peuvent etre pris pour des faits alors qu'ils sont du shaping produit.
- Recommended action: Conserver `structured_facts_v1` comme source factuelle et traiter `client_interpretation_projection_v1` comme support produit/shaping, pas comme source canonique prompt.
- Story candidate: yes
- Suggested archetype: prompt-input-surface-separation

## F-003 - Narrative audit storage is evidence, not injection context

- Severity: Medium
- Confidence: High
- Category: observability-gap
- Domain: backend-domain
- Evidence: E-011, E-012, E-013, E-015, E-021, E-022
- Expected rule: Les surfaces d'audit doivent prouver provenance, hashes et ancrage sans devenir payload prompt.
- Actual state: `narrative_answer_audit_v1` stocke `projection_hash`, `llm_input_hash`, `prompt_version`, `provider`, `model`, `grounding_status` et `evidence_refs`; le workflow de rejet valide ces references.
- Impact: Confondre cette surface avec une entree prompt ferait fuiter ou dupliquer des metadonnees operationnelles dans la generation.
- Recommended action: Documenter une frontiere stricte: audit-only pour hashes, provider/model, prompt refs et `evidence_refs`; jamais payload prompt brut.
- Story candidate: no
- Suggested archetype: none

## F-004 - Exact projection-readiness guardrail is local only

- Severity: Low
- Confidence: High
- Category: missing-guard
- Domain: backend-domain
- Evidence: E-001, E-003, E-016, E-023
- Expected rule: Une migration prompt future devrait avoir un guard executable contre la confusion projection produit / entree LLM / audit.
- Actual state: Le registre global n'a pas d'invariant exact; CS-326 reste audit-only et garde le code applicatif inchanged.
- Impact: Risque modere lors d'une story ulterieure si la decision cible n'est pas reprise.
- Recommended action: Ne pas modifier le registre global pour cet audit; proposer un guardrail seulement lors d'une story de migration prompt.
- Story candidate: no
- Suggested archetype: none
