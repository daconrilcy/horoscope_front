# Implementation Plan

1. Capture baseline OpenAPI/runtime evidence before creating the runtime.
2. Add one canonical runtime module under `backend/app/domain/astrology/runtime/`.
3. Reuse chart-object, aspect, proof, doctrine and graph-family primitives.
4. Add runtime unit tests and extend API neutrality architecture tests.
5. Persist evidence, update AC traceability and mark `CS-280` ready for review.

No frontend, route, migration, public serializer, generated client, LLM interpretation or fixed-star exposure is in scope.
