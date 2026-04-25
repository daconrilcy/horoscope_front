<!-- Conseils operationnels pour exploiter les modeles Codex modernes en revue. -->

# Codex Modern Review Guidance

## Why This Skill Differs From BMAD

BMAD's original code-review flow assumes mandatory step checkpoints and
parallel review agents. Modern Codex-class models and GPT-5.4/5.5 can handle
larger review contexts, but this skill still requires targeted repository
reads, concrete command evidence, and explicit diff-based findings.

## Operating Pattern

1. Build the review target from git and story/capsule evidence.
2. Read just enough surrounding code to understand behavior.
3. Run adversarial passes as separate mental layers:
   - blind diff integrity;
   - acceptance auditor;
   - edge-case hunter;
   - No Legacy / DRY hunter;
   - validation skeptic;
   - security/data reviewer.
4. Merge and triage findings.
5. Present findings first.

## Subagent Policy

Use subagents only when the current user explicitly asks for sub-agents,
delegation, or parallel agent work. If that authorization is absent, perform the
layers in the main Codex session.

If subagents are authorized:

- make them read-only;
- give each a bounded layer;
- do not let them edit files;
- keep final severity, deduplication, and verdict decisions in the main session.

## Codex Self-Review Loop

Before finalizing, run this internal challenge:

- Could a failing AC be hidden behind broad passing tests?
- Did the implementation add a second active path?
- Did final evidence claim a command passed without actual execution?
- Is any file changed that the story does not justify?
- Were untracked files included or explicitly scoped out?
- Would a reviewer know exactly where to focus?
- Are line references precise enough to act on?

If the answer reveals uncertainty, inspect the repository again before reporting.

## Self-Validation Commands For This Skill

Use `python -B` so Python does not generate `__pycache__` files that the package
validator intentionally rejects.

From `.agents/skills/condamad-code-review`:

```bash
python -B scripts/condamad_review_validate.py .
```
