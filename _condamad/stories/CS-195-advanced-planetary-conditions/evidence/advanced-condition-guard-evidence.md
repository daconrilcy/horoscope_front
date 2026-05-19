# Advanced Condition Guard Evidence

- `advanced_conditions/**` forbidden infra/services/API/prediction scan:
  zero hits.
- `advanced_conditions/**` forbidden LLM/narration scan: zero hits.
- Forbidden local advanced map names scan: zero hits.
- Deferred technique scan: zero hits.
- Serializer guard confirms `_serialize_advanced_conditions` does not call
  `AdvancedConditionEngine`.
