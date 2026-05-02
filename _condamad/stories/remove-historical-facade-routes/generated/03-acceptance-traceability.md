# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | L'inventaire de suppression est complet et deterministe. | Ajouter `route-consumption-audit.md` avec classification des routes, champs et UI routes. | Audit valide et route scan classifie. | PASS |
| AC2 | Les facades supprimables sont supprimees, jamais repointees. | Retirer le routeur `/v1/ai` et supprimer ses modules dedies. | `pytest -q app/tests/unit/test_api_router_architecture.py` passe. | PASS |
| AC3 | Aucun item externe n'a `Decision=delete`. | Preuve historique conservee dans `generated/10-final-evidence.md`; le validateur ponctuel racine a ete retire apres livraison. | Validation historique PASS dans `generated/10-final-evidence.md`. | PASS |
| AC4 | `/v1/ai/*` est absent de l'application et d'OpenAPI. | Retirer imports/montages et ajouter test OpenAPI. | `pytest -q app/tests/integration/test_api_openapi_contract.py` passe. | PASS |
| AC5 | Les modules Python supprimes ne sont plus importables. | Supprimer `routers/public/ai.py`, `router_logic/public/ai.py`, `schemas/ai.py`. | Import check et garde architecture passent. | PASS |
| AC6 | Les consommateurs LLM first-party ciblent les proprietaires canoniques. | Conserver `chat.ts` et `guidance.ts`; retirer references `/v1/ai`. | Scan negatif sans resultat. | PASS |
| AC7 | `use_case_compat` n'est plus produit ni lu. | Retirer champ export, headers deprecation, lectures front et tests positifs. | Scan negatif sans resultat. | PASS |
| AC8 | Les etats admin legacy ne sont plus types, produits ou affiches. | Retirer unions/types et payloads `legacy_maintenance`, `legacy_alias`, `legacy_registry_only`. | Scan negatif sans resultat. | PASS |
| AC9 | `/admin/prompts/legacy` est absent de `frontend/src`. | Retirer route enfant et mapping de resolution. | Scan negatif sans resultat et tests routing passent. | PASS |
| AC10 | Aucun wrapper ou fallback ne remplace la suppression. | Gardes d'architecture sur prefixe, import et routes front. | Garde architecture passe. | PASS |
| AC11 | TypeScript, lint, tests backend et tests frontend cibles passent. | Mettre a jour tests backend/front cibles. | Lint/tests cibles passent; frontend complet passe; backend complet timeout. | PASS_WITH_LIMITATIONS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
