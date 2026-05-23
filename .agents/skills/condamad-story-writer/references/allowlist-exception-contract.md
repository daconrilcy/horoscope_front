# Allowlist Exception Contract

<!-- Contrat transverse pour rendre les exceptions explicites et auditables. -->

Use this contract when a broad rule has allowed exceptions.

## Rule

Exceptions must be exact, justified, and testable. No exception may be implicit.

## Required Table

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

## Forbidden

- wildcard exception;
- folder-wide exception;
- empty expiry;
- `temporary` without a date, condition, or tracked decision;
- exception validated only by reviewer memory.

Each exception must be validated by a test, scan, or guard.
