# Domain Purity Audit Contract

Domain may:

- define business invariants;
- define pure rules;
- define domain entities/value objects;
- define policy concepts.

Domain must not depend on:

- FastAPI;
- HTTP response types;
- DB session;
- infrastructure clients;
- frontend DTOs;
- application service orchestration.

Required checks:

- forbidden framework import scan;
- infrastructure dependency scan;
- DTO leakage scan;
- domain rule duplication scan;
- pure-rule test inventory.
