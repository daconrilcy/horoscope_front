# Evidence Log

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | self-test | `python -S -B -m unittest discover -s .agents/skills/condamad-domain-auditor/scripts/self_tests -p "*selftest.py" -v` | PASS | 17 tests cover validator, linter strict mode, and dependency scanner. |
| E-002 | validation | `python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_validate.py _condamad/audits/domain-auditor-sample/2026-04-27-1200` | PASS | Sample audit folder validates successfully. |
| E-003 | lint | `python -B .agents/skills/condamad-domain-auditor/scripts/condamad_domain_audit_lint.py _condamad/audits/domain-auditor-sample/2026-04-27-1200 --strict` | PASS | Strict lint has no warnings. |
