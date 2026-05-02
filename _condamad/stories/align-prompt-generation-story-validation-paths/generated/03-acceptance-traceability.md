# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les chemins actifs obsoletes sont remplaces. | Corriger les commandes actives dans `converge-horoscope-daily-narration-assembly/00-story.md`, `formalize-consultation-guidance-prompt-ownership/00-story.md`, et `regression-guardrails.md`. | Scan des anciens chemins sous `_condamad/stories` avec classification active/historique/interdit dans `validation-path-audit.md`. | PASS |
| AC2 | Les commandes corrigees executent au moins un test depuis `backend/`. | Aucun changement de code; utiliser les fichiers collectes existants sous `backend/app/tests/unit`. | `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py` passe avec 32 tests. | PASS |
| AC3 | Les anciens chemins historiques restent limites aux preuves passees. | Creer `validation-path-audit.md` avec une allowlist exacte des references historiques ou interdites. | `rg -n "historical|historique|historical-facade|forbidden-example|reintroduction-guard" ...\validation-path-audit.md` confirme les classifications. | PASS |
| AC4 | Une garde bloque le retour des anciens chemins. | Mettre a jour `RG-020`, conserver `RG-022`, et documenter le scan cible des anciens chemins dans les plans actifs. | `rg` cible sur les anciens chemins retourne seulement des references classees; les chemins collectes passent par pytest. | PASS |
