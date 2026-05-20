<!-- Reference CONDAMAD pour consigner un retour et sa transformation en action durable. -->

# Feedback Record

Use this compact structure when recording feedback in story evidence, review
notes, guardrail updates, or skill-change notes.

```markdown
## Feedback Loop

- Source:
- Date:
- Target:
- Feedback:
- Classification:
- Decision:
- Changes:
- Validation:
- Propagation:
- Residual risk:
```

## Field rules

- `Source`: conversation, review file, validation log, audit finding, or story
  artifact.
- `Date`: local date in `YYYY-MM-DD` format when durable evidence is written.
- `Target`: one story, skill, guardrail, code surface, or evidence file.
- `Feedback`: short factual summary, not a long transcript.
- `Classification`: one primary category from `SKILL.md`.
- `Decision`: accepted, rejected, deferred, or blocked with reason.
- `Changes`: concrete files or evidence updated.
- `Validation`: commands run and result; skipped commands require a reason.
- `Propagation`: related skills, guardrails, or story registry updates.
- `Residual risk`: remaining uncertainty, or `Aucun risque restant identifie`.
