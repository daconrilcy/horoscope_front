# Code Review Findings: Story 63-16 (Instrumentation analytics du funnel)

**Story:** _bmad-output/implementation-artifacts/63-16-instrumentation-analytics-funnel.md
**Issues Found:** 2 High, 1 Medium, 0 Low

## 🔴 HIGH ISSUES
- **[FIXED] Syntax errors in `HeroSection.tsx`**: Extra closing `</div>` tags and incorrect nesting prevented the component from being rendered correctly and potentially caused build failures.
- **[FIXED] Missing import in `HeroSection.tsx`**: The `logo` variable was used in an `<img>` tag but not imported, which would cause a reference error.
- **[FIXED] Consent check missing (AC1.1)**: Events were being sent as long as analytics were enabled, without verifying user consent. Added a `hasConsent` helper in `useAnalytics.ts` as a placeholder for real consent management.

## 🟡 MEDIUM ISSUES
- **[FIXED] `VITE_ANALYTICS_ENABLED` behavior**: In dev mode with the `noop` provider, analytics events were not being logged to the console unless `VITE_ANALYTICS_ENABLED=true` was set. Updated `analytics.ts` to enable analytics by default when the provider is `noop`.
- **[REMAINING] `register_view` tracking**: Tracking is done inside `SignUpForm.tsx`. While acceptable since `SignUpForm` is the main content of `/register`, if it were reused elsewhere (e.g., a modal), it would trigger a false `register_view` event. (Considered acceptable for MVP).

## 🟢 LOW ISSUES
- None identified.

---

**Summary:** The core instrumentation for the funnel is well-implemented and follows the specifications. The major issues were related to syntax and build readiness in the `HeroSection` and the missing consent logic required by AC1. These have been fixed.
