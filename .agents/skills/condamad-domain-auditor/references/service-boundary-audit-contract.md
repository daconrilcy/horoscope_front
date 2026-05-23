# Service Boundary Audit Contract

Services may:

- orchestrate application use cases;
- call domain rules;
- call infra through repositories/ports;
- expose application-level operations.

Services must not:

- import API adapters;
- return HTTP responses;
- own persistence models directly when infra owns them;
- duplicate domain policy;
- keep compatibility routes or aliases.

Required checks:

- service-to-api dependency scan;
- HTTP type scan;
- persistence ownership scan;
- duplicated domain rule scan;
- use-case test inventory.
