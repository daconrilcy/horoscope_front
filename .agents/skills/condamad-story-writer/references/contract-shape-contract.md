# Contract Shape Contract

<!-- Contrat transverse pour figer les formes d'API, erreurs, payloads et DTO. -->

Use this contract when a story touches an API, HTTP error, payload, export, DTO,
OpenAPI contract, generated client, or frontend type.

## Rule

The exact contract shape must be explicit before implementation starts.

## Required Story Content

The story must state:

- fields and types;
- required versus optional fields;
- status codes and error envelope when HTTP is involved;
- serialization names;
- generated contract impact;
- frontend type impact;
- compatibility or removal decision.

## Required Evidence

Use runtime OpenAPI, JSON/schema assertions, generated type checks, or targeted
contract tests. Static scans may support the proof but cannot replace it.
