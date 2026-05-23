<!-- Taxonomie CONDAMAD des refactorisations autorisees. -->

# Refactor Taxonomy

The skill accepts only mapped, bounded refactor types. Unmapped intents must be
rejected before edits.

## Allowed Refactor Types

Use exactly one `Refactor Type` value:

- `extract-function`
- `extract-class`
- `move-function`
- `move-class`
- `rename-symbol`
- `inline-function`
- `split-module`
- `merge-duplicate-logic`
- `simplify-conditional`
- `replace-primitive-with-value-object`
- `separate-query-from-modifier`
- `introduce-parameter-object`
- `remove-dead-code`
- `consolidate-imports`
- `isolate-side-effect`
- `strengthen-boundary`

## Invalid Intents

Reject these as too vague or behavior-risky:

- "refactor this"
- "clean up"
- "modernize everything"
- "make it nicer"
- "rewrite"
- "optimize" without behavior invariants
- any multi-domain refactor
- any request that adds a feature or new behavior

Every accepted type still requires one primary domain, current-state evidence,
target-state evidence, and Behavior Invariants.
