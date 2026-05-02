# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Chaque fichier `scripts` a une ligne exacte dans le registre. | `scripts/ownership-index.md` couvre les 21 chemins actuels retournes par `rg --files scripts`; `backend/app/tests/unit/test_scripts_ownership.py` compare l'inventaire filesystem au registre. | `pytest -q app/tests/unit/test_scripts_ownership.py` PASS. | PASS |
| AC2 | Le registre expose les colonnes requises. | Le tableau Markdown expose `script`, `family`, `owner`, `usage`, `validation_command`, `support_status`, `decision`; le test refuse les lignes invalides. | `pytest -q app/tests/unit/test_scripts_ownership.py` PASS. | PASS |
| AC3 | Les scripts actifs conservent leur chemin. | `scripts-inventory-baseline.txt` capture les 20 scripts avant registre; `scripts-inventory-after.txt` capture les memes scripts plus `scripts/ownership-index.md`; aucun script executable n'a ete deplace. | `rg --files scripts` PASS; `pytest -q app/tests/unit/test_scripts_ownership.py` PASS. | PASS |
| AC4 | `stripe-listen-webhook.sh` garde une decision bloquee. | La ligne `scripts/stripe-listen-webhook.sh` porte `support_status=needs-user-decision` et `decision=blocked-support-decision`. | `rg -n "stripe-listen" scripts/ownership-index.md` PASS; `pytest -q app/tests/unit/test_scripts_ownership.py` PASS. | PASS |
| AC5 | La story valide. | Capsule generee et evidence finale completee. | `condamad_story_validate.py` PASS; `condamad_story_lint.py --strict` PASS. | PASS |
