# Implementation Plan - CS-290

1. Reuse CS-289 validation output and CS-288 audit persistence.
2. Add one canonical backend workflow helper for rejected narrative answers.
3. Integrate the helper in natal interpretation after gateway output and before persistence/response.
4. Add unit, integration and architecture guards for rejection, audit storage, response masking, logging, no retry and API neutrality.
5. Persist validation evidence and mark the story `ready-to-review`.
