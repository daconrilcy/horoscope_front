<!-- Revue CONDAMAD finale pour CS-030. -->

# Code Review CS-030

Verdict: CLEAN

Findings fixed:

- CSS fallback allowlist is now enforced against actual `(file, token, literal)`
  occurrences through `CSS_FALLBACK_EXCEPTIONS`.
