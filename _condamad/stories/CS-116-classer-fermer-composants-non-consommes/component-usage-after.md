<!-- Inventaire apres CS-116 des composants non consommes. -->

# CS-116 Component Usage After

Result:
- `frontend/src/components/AppShell.tsx` deleted after classification `remove`.
- Prediction files without runtime reachability, direct tests or public barrel proof were deleted with stale CSS where applicable.
- Retained F-005 candidates have exact metadata in `component-usage-allowlist.ts`.
- The guard now scans every exported component file under `frontend/src/components/**`, not only the original F-005 list.
- Additional no-runtime candidates discovered by the whole-component guard are classified exactly, including no-runtime component chains.
- Runtime references are detected from a reachable runtime import/export graph rooted at `main.tsx`; `import type` does not count as runtime usage.

Validation:

```powershell
cd frontend
npm run test -- component-usage components
```

Result: PASS.
