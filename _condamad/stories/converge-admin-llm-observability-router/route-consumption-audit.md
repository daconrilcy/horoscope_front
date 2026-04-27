# Route Consumption Audit

Audit de suppression des handlers Python historiques dans `prompts.py`. Les URLs HTTP restent
inchangées; seule la propriété runtime des handlers converge vers `observability.py`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `backend/app/api/v1/routers/admin/llm/prompts.py::list_call_logs` | Python handler | historical-facade | Aucun import direct hors références d'audit/story; consommateurs HTTP préservés par `/v1/admin/llm/call-logs`. | `backend/app/api/v1/routers/admin/llm/observability.py::list_call_logs` | delete | `rg list_call_logs`; route owner before/after; OpenAPI diff stable. | Faible: le contrat HTTP et `operationId` restent stables. |
| `backend/app/api/v1/routers/admin/llm/prompts.py::get_dashboard` | Python handler | historical-facade | Aucun import direct hors références d'audit/story; consommateurs HTTP préservés par `/v1/admin/llm/dashboard`. | `backend/app/api/v1/routers/admin/llm/observability.py::get_dashboard` | delete | `rg get_dashboard`; route owner before/after; OpenAPI diff stable. | Faible: le contrat HTTP et `operationId` restent stables. |
| `backend/app/api/v1/routers/admin/llm/prompts.py::replay_request` | Python handler | historical-facade | Aucun import direct hors références d'audit/story; consommateur frontend HTTP préservé par `/v1/admin/llm/replay`. | `backend/app/api/v1/routers/admin/llm/observability.py::replay_request` | delete | `rg replay_request`; route owner before/after; OpenAPI diff stable. | Faible: le contrat HTTP et `operationId` restent stables. |
| `backend/app/api/v1/routers/admin/llm/prompts.py::purge_logs` | Python handler | historical-facade | Aucun import direct hors références d'audit/story; consommateurs HTTP préservés par `/v1/admin/llm/call-logs/purge`. | `backend/app/api/v1/routers/admin/llm/observability.py::purge_logs` | delete | `rg purge_logs`; route owner before/after; OpenAPI diff stable. | Faible: le contrat HTTP et `operationId` restent stables. |
