# Story Candidates

## SC-001 - Centralize domain auditor validation

- Source finding: F-001
- Suggested story title: Centralize domain auditor validation
- Suggested archetype: test-guard-hardening
- Primary domain: .agents/skills/condamad-domain-auditor
- Required contracts:
  - Report Output Contract
  - Story Candidate Contract
- Draft objective:
  - Add the domain auditor self-test command to the project-level validation checklist or CI workflow when skill checks are centralized.
- Must include:
  - The exact self-test command with `python -S -B`.
  - A no-bytecode artifact check for the skill folder.
- Validation hints:
  - Run the self-tests and artifact scans from the repository root after activating the venv.
- Blockers:
  - User decision required on whether skill validation belongs in CI or a documented local checklist.
