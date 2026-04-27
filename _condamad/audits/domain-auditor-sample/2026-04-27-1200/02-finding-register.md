# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | missing-guard | .agents/skills/condamad-domain-auditor | E-001 proves self-tests cover the validator and scanner, but repo-level CI integration is not part of this package sample. | Future changes to the skill could bypass local self-tests if contributors do not run them. | Add this self-test command to the project validation checklist or CI when skill checks are centralized. | yes |

## Finding Details

### F-001 - Skill validation is local only

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: .agents/skills/condamad-domain-auditor
- Evidence:
  - id: E-001
  - path: .agents/skills/condamad-domain-auditor/scripts/self_tests
  - command: python -S -B -m unittest discover -s .agents/skills/condamad-domain-auditor/scripts/self_tests -p "*selftest.py" -v
- Expected rule: new skill contracts have repeatable validation evidence.
- Actual state: local self-tests exist and pass; centralized CI integration is outside this task.
- Impact: Future changes to the skill could bypass local self-tests if contributors do not run them.
- Recommended action: Add this self-test command to the project validation checklist or CI when skill checks are centralized.
- Story candidate: yes
- Suggested archetype: test-guard-hardening
