# CS-400 — Clôture QA live lecture natale (CS-396 → CS-399)

Date : 2026-05-30  
Stories livrées : CS-396, CS-397, CS-398, CS-399  
Référence baseline : `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`

## Baseline du défaut (2026-05-30)

- Lecture Basic `complete` avec cinq cartes mais **trois contenus dupliqués** (padding `response.sections[0]`).
- `used_astrological_elements` vide malgré un thème riche.
- Quota `natal_chart_long` consommé **avant** validation éditoriale.
- UI : cinq chapitres toujours dépliés ; actions PDF/historique trop hautes.

## Matrice Free / Basic / Premium

| Profil | Statut post-CS-396→399 | Preuve |
|---|---|---|
| Free | Inchangé fonctionnellement (hors scope) | Tests Vitest `NatalChartPage` + garde DOM |
| Basic | Rejet padding/sources ; sources enrichies ; quota post-acceptation ; accordeons | Tests ciblés backend et `natalNarrativeReading.test.tsx` |
| Premium | Même pipeline narratif + limite sources 10 | Tests unitaires narratifs V3 |

## Matrice desktop / mobile

| Surface | Vérification | Résultat |
|---|---|---|
| Desktop | Accordeons ARIA + premier chapitre ouvert | PASS (Vitest) |
| Mobile | CSS responsive `natal-narrative-reading__toggle` | PASS (styles + tests composant) |
| Actions compactes | Classe `ni-actions--compact` | PASS (CSS + rendu) |

## Quota, rejet et remediation

| AC | Preuve |
|---|---|
| Rejet éditorial ne débite pas | Route : `check_access_for_complete_generation` puis `consume_on_acceptance` uniquement si lecture non rejetée et non cachée |
| Lecture invalide historique | `claim_corrective_regeneration_eligibility` + path `corrective_regeneration` |
| Idempotence corrective | Claim DB atomique, ligne pending non publique, libération sur erreur et skip quota si `corrective_regeneration=True` |
| Transaction lecture + quota | Persistance `flush()` dans le service, consommation puis `commit()` unique dans le routeur |

## Richesse éditoriale Basic

- `support_elements` diversifiés (big three, régences, dominantes, maisons, aspects).
- Propagation `llm_astrology_input_v1.shaping.support_elements`.
- Fixtures V3 nominales : cinq sections sources distinctes requises.

## Commandes exécutées

```text
pytest -q backend/tests/unit/test_narrative_natal_reading_v1.py backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py
# PASS : 8 passed, 6 deselected
pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py backend/tests/llm_orchestration -k "natal or theme_astral"
# PASS avec skip documente : 25 passed, 1 skipped, 214 deselected
pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py backend/tests/integration -k "natal and (quota or interpretation or rejected)"
# PASS : 4 passed, 241 deselected
pytest -q backend/tests -k "natal and (narrative or rejected or quota or theme_astral)"
# PASS : 23 passed, 1491 deselected
pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode
# PASS : 86 passed
pnpm --dir frontend lint
# PASS
pnpm --dir frontend build
# PASS
pytest -q --long backend/app/tests/integration/test_natal_chart_long_entitlement.py backend/app/tests/integration/test_natal_interpretation_endpoint.py backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py backend/tests/architecture/test_narrative_natal_reading_public_boundary.py
# PASS : 32 passed
pytest -q
# PASS : 3550 passed, 2 skipped, 1245 deselected
ruff format --check .
# PASS
ruff check .
# PASS
rg -n "fallback = response.sections[0]" backend/app/services/llm_generation/natal  # zero-hit attendu
rg -n "check_and_consume" backend/app/api/v1/routers/public/natal_interpretation.py  # zero-hit attendu
```

## Nouveaux invariants registre

- RG-155 : intégrité sémantique narrative (CS-396)
- RG-156 : couverture éditoriale Basic (CS-397)
- RG-157 : quota transactionnel + remediation (CS-398)
- RG-158 : accordeons narratifs modernes (CS-399)
- RG-154 précisé : accordeons `natal-narrative-reading__toggle` autorisés

## Screenshots

Réutilisation des captures CS-395 (`output/playwright/cs-395-*.png`) comme baseline avant.
Une nouvelle session navigateur authentifiée reste requise après déploiement local pour
valider une régénération Basic V3 réelle.

## Risques résiduels

| Risque | Sévérité | Suivi |
|---|---|---|
| QA navigateur authentifiée non rejouée dans cette session | Moyen | Rejouer manuellement `/natal` après stack dev + régénération V3 |
| Premium / mode astrologue ouvert non couverts par nouveaux tests live | Faible | Story dédiée si écart constaté en QA manuelle |

## Verdict de revue

`ACCEPTABLE_WITH_LIMITATIONS` : les corrections automatisées, les checks Ruff, les tests
backend complets et les validations frontend passent. La QA navigateur authentifiée
Free/Basic/Premium desktop/mobile reste à rejouer avec preuve avant clôture live définitive.

## Feedback loop

- Propagation acceptée : `RG-157` ne référence plus le test inexistant
  `test_natal_chart_long_entitlement_gate.py`.
- Portée : correction du registre canonique uniquement ; aucun affaiblissement d'AC ou de
  guardrail.
