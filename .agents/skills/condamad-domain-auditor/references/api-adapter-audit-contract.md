# API Adapter Audit Contract

API may:

- parse HTTP requests;
- validate HTTP request/response contracts;
- call application services;
- map application errors to HTTP;
- expose OpenAPI.

API must not:

- own business rules;
- perform persistence orchestration directly;
- duplicate service logic;
- keep historical compatibility facades;
- expose undocumented legacy routes;
- become a dependency of services/domain.

Required checks:

- router inclusion inventory;
- runtime OpenAPI if available;
- dependency scans;
- HTTP error handling scan;
- route facade scan;
- architecture guard inventory.
