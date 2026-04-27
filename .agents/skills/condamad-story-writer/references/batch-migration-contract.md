# Batch Migration Contract

<!-- Contrat transverse pour migrer plusieurs sous-domaines par lots independants. -->

Use this contract when a story crosses multiple packages, route groups,
namespaces, DTO groups, generated artifacts, or consumer categories.

## Rule

The story must split the migration into independent batches. Each batch must
have its own mapping and proof.

## Required Story Content

For each batch, state:

- old surface;
- canonical surface;
- consumers changed;
- imports or contracts changed;
- tests adapted;
- no-shim proof;
- rollback or blocker condition.

## Forbidden

- one undifferentiated repo-wide migration task;
- hidden compatibility re-export;
- batch completion without negative proof for the old surface.
