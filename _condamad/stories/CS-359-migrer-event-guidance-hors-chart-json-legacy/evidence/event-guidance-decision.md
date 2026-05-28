# Decision event_guidance CS-359

<!-- Commentaire global: cette preuve persistante consigne la decision produit et technique de suppression de event_guidance. -->

Decision finale: `delete`.

Raison: les audits CS-353/CS-354 et le scan courant ne montrent aucun trigger produit public supporte pour `event_guidance`. Les seules surfaces actives etaient un contrat canonique dormant, un seed guidance, deux lignes taxonomy, une branche adapter, une entree de catalog/config et des tests qui maintenaient le use case comme supporte. La story interdit de conserver une dette explicite; la suppression est donc l'option finale.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `event_guidance` contract | use case | dead | aucun trigger public audite; contrat interne dormant | none | delete | `rg -n "event_guidance" backend/app backend/tests`, `get_canonical_use_case_contract("event_guidance") is None` | recreation future sans decision produit |
| `chart_json` prompt carrier | field | historical-facade for event_guidance | ancien seed et ancien contrat uniquement | none | delete from event_guidance | AST guard, governance scan, seed scan | provider leakage si le seed revient |
| `event_guidance` seed | seed | dead | bootstrap provisioning only | none | delete | `all(prompt["use_case_key"] != "event_guidance" for prompt in GUIDANCE_PROMPTS_TO_SEED)` | stale prompt si seed restaure |

Residual classifications:

| Residual | Classification | Justification |
|---|---|---|
| `offer_event_guidance` | chat intent | Intent de suggestion chat distinct du use case runtime supprime. |
| Tests contenant `event_guidance` | anti-return guard | Verifient explicitement que le use case supprime n'est plus supporte. |
| `_condamad/**` mentions | historical/evidence | Story, audit, guardrail et preuves de migration/suppression. |
