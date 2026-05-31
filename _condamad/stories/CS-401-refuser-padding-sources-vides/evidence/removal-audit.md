# Removal Audit — CS-401-refuser-padding-sources-vides

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `response.sections[0]` padding | symbol | historical-facade | builder only | explicit projection error `NarrativeChapterSourceMissingError` | delete | `rg -n "response\\.sections\\[0\\]" backend/app/services/llm_generation/natal` exit 1 no matches; architecture guard PASS | silent bad readings if reintroduced |

No allowlist entry is authorized for semantic padding, duplicated chapters or empty Basic/Premium sources.
