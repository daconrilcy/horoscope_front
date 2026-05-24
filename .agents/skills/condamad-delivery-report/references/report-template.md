# Delivery Report Template

Use this skeleton. Keep prose concise; put evidence in tables/lists.

```md
# Delivery Report - <initiative or story range>

## 0. Report metadata

| Field | Value |
|---|---|
| Generated at | <date/time or Not evidenced> |
| Repository | <repo name/path> |
| Branch | `<branch>` or Not evidenced |
| Commit range | `<from..to>` or Not evidenced |
| Stories covered | <story keys> |
| Source documents | <paths or Not evidenced> |
| Diff source | git diff / modified files / provided patch / Not evidenced |
| Validation source | story-time / CI / report-time / external / Not evidenced |

## 1. Executive summary

<Status summary: story count, validation level, final delivery status.>

## 2. Initial context and trigger

<Why the stories existed. Cite source evidence or mark Not evidenced.>

## 3. Story scope

| Story | Goal | AC source | Non-goals / exclusions |
|---|---|---|---|
| <key> | <goal> | `<path>` | <non-goals or Not evidenced> |

## 4. Implementation summary

<Group by domain/story. Cite paths and symbols; avoid unsupported claims.>

## 5. Traceability matrix

| Story | AC / Expected outcome | Initial need source | Implemented evidence | Validation evidence | Status |
|---|---|---|---|---|---|
| <key> | <AC/outcome> | `<path>` / Not evidenced | `<path>` / `<symbol>`: <proof> | `<command>` <result> | <workflow status> |

## 6. Evidence of completion

### Code evidence

- `<path>` / `<symbol>`: <what it proves>

### Test evidence

- `<path>` / `<test_name>`: <what it proves>

### Documentation evidence

- `<path>`: <what it proves>

### Operational evidence

- `<log path>` / `<command output>`: <what it proves>

## 7. Validation results

| Command / source | Scope | Result | Evidence | Notes |
|---|---|---|---|---|
| `<command>` | targeted / full suite / manual / external | PASS / FAIL / SKIPPED / NOT RUN / EXTERNALLY REQUIRED | `<path or log>` | <story-time, CI, report-time, or external> |

## 8. Deviations, limits and assumptions

### Deviations from story scope

- <Deviation and evidence>

### Known limits

- <Limit and evidence>

### Assumptions

- <Assumption and reason>

## 9. Residual risks

- <Risk, impact, evidence, suggested mitigation>

## 10. Evidence gaps

- <Missing claim/proof that could not be verified>

## 11. Recommended next actions

1. <Action tied to risk/gap/deferred scope>
2. <Action tied to validation or QA>

## 12. Final delivery status

`<workflow status>`

<One evidence-anchored paragraph explaining the status.>
```
