<!-- Etape de cadrage pour identifier la cible de revue et les preuves. -->

# Step 1 - Target and Context

## Objective

Identify exactly what is being reviewed and load only the context required for a
reliable adversarial review.

## Actions

1. Locate the repository root.
2. Read applicable `AGENTS.md` files before running project commands.
3. Always collect baseline git evidence:

   ```powershell
   git status --short
   git diff --stat
   git diff --name-status
   git diff --cached --stat
   git diff --cached --name-status
   git diff HEAD --stat
   git diff HEAD --name-status
   git ls-files --others --exclude-standard
   git diff --check
   ```

   Record pre-existing dirty state and untracked files.
4. Determine the diff target in this order:
   - explicit user path, branch, commit, PR, staged/uncommitted instruction, or
     CONDAMAD capsule path;
   - active CONDAMAD capsule mentioned in recent context;
   - story file in review status;
   - current uncommitted changes;
   - current branch against default branch.
5. Build the review target:
   - staged-only review: review `git diff --cached`; still record unstaged and
     untracked files as residual risk unless explicitly out of scope.
   - uncommitted review: review `git diff HEAD`; inspect every untracked file
     listed by `git ls-files --others --exclude-standard`.
   - branch review: resolve the default branch using
     `git symbolic-ref refs/remotes/origin/HEAD` when available; fallback to
     `origin/main`, `origin/master`, `main`, then `master`; compute
     `git merge-base <base> HEAD`; review `git diff <merge-base>...HEAD`.
   - commit range: verify the range resolves, then review `git diff <range>`.
   - capsule/story review: prefer implementation evidence in
     `generated/10-final-evidence.md`; cross-check it against the real git diff;
     never rely only on capsule evidence.
6. If the diff is empty, stop and report that there is nothing to review.
7. Load story/capsule context when available:
   - `00-story.md` or story markdown;
   - acceptance traceability;
   - validation plan;
   - No Legacy guardrails;
   - final evidence;
   - implementation plan/dev log if present.
8. Read target files around changed hunks, not just the diff.
9. If a CONDAMAD capsule exists, prepare
   `generated/11-code-review.md` for the eventual review result.

## Required Context Summary

Before reviewing, know:

- review target and baseline;
- story key, if any;
- files changed;
- untracked files inspected or scoped out;
- ACs and non-goals;
- tests and commands claimed by implementation evidence;
- No Legacy expectations;
- dirty files that pre-date the review.

## Halt Conditions

Stop only when:

- no review target can be identified;
- the diff is empty;
- required story/capsule files are inaccessible;
- repository instructions cannot be read;
- a command would be destructive.

Otherwise continue to Step 2.
