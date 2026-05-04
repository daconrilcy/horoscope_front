<!-- Revue CONDAMAD finale pour CS-028. -->

# Code Review CS-028

Verdict: ACCEPTABLE_WITH_LIMITATIONS

Findings fixed:

- Migrated settings page title now consumes `--type-page-title-*` tokens.

Limitation: this story formalizes roles and guards the selected migrated
surface; it does not normalize all historical typography literals.
