<!-- Etape de presentation finale et de suite actionnable. -->

# Step 4 - Report and Next Action

## Objective

Present the review in a Codex-native final response: findings first, concise,
actionable, and grounded in file references.

## Final Response Shape

Use the user's language.

If findings exist:

```md
Findings:

- High - <title> (`relative/path.py:123`)
  Evidence: ...
  Impact: ...
  Suggested fix: ...

Verdict: BLOCKING / CHANGES_REQUESTED / ACCEPTABLE_WITH_LIMITATIONS

Reviewed:
- target/baseline
- story/capsule
- key commands

Notes:
- skipped checks or residual risks
```

If no findings exist:

```md
No actionable findings found.

Verdict: CLEAN / ACCEPTABLE_WITH_LIMITATIONS

Reviewed:
- target/baseline
- story/capsule
- key commands

Residual risks:
- ...
```

## Action Policy

Do not fix findings automatically unless the user asked for fixes in the same
request.

If the user asks to fix findings:

- preserve the original review findings;
- implement only unambiguous `patch` findings;
- ask before resolving `decision_needed` findings;
- run relevant validation after edits;
- update the review artifact with resolution notes.

## Required Final Details

Include:

- verdict;
- number of findings by severity;
- persisted review path, if written;
- commands run or not run;
- remaining risks or "None identified";
- suggested reviewer focus when verdict is not `CLEAN`.

Use paths relative to the repository root. Avoid absolute local paths unless no
repository root could be identified.
