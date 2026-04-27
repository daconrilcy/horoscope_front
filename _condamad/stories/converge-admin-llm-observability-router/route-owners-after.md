# Route Owners After

| Method | Path | Endpoint | Owner module |
|---|---|---|---|
| `GET` | `/v1/admin/llm/call-logs` | `list_call_logs` | `app.api.v1.routers.admin.llm.observability` |
| `GET` | `/v1/admin/llm/dashboard` | `get_dashboard` | `app.api.v1.routers.admin.llm.observability` |
| `POST` | `/v1/admin/llm/replay` | `replay_request` | `app.api.v1.routers.admin.llm.observability` |
| `POST` | `/v1/admin/llm/call-logs/purge` | `purge_logs` | `app.api.v1.routers.admin.llm.observability` |
