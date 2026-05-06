<!-- Journal de preuves de l'audit frontend design-system. -->

# Evidence Log

| ID | Evidence type | Command / Source | Result | Evidence | Limitation |
|---|---|---|---|---|---|
| E-001 | repo_status | `git status --short` | PASS | Worktree was clean before audit artifact creation. | Audit files are created after this point. |
| E-002 | guardrail_inventory | Read `_condamad/stories/regression-guardrails.md` | PASS | `RG-044` to `RG-050` define active frontend design-system invariants. | Backend guardrails not in scope. |
| E-003 | check_command | `npm run lint` from `frontend` | PASS | TypeScript lint completed with exit code 0. | ESLint is not configured in this package; script is TypeScript check. |
| E-004 | test_coverage_inventory | `npm run test -- design-system inline-style css-fallback legacy-style theme-tokens` | PASS | 5 test files passed, 111 tests passed. | Focused guard suite only. |
| E-005 | test_coverage_inventory | `npm run test -- AdminPromptsPage AdminPromptsRouting AppBgStyles visual-smoke` | PASS | 5 test files passed, 90 tests passed, 8 skipped. | Skipped tests remain as existing local test policy. |
| E-006 | build_check | `npm run build` | PASS | Build passed; Vite warned that `assets/index-v_SjIKd1.js` is 1,374.80 kB minified. | Performance finding is informational in this audit. |
| E-007 | targeted_forbidden_symbol_scan | `rg -n "admin-prompts-legacy\|admin-prompts-modal--legacy-rollback" frontend/src ...` | PASS | Zero active hits under `frontend/src`; hits only remain in CS-067 historical story artifacts and guard tests. | Historical `_condamad` evidence intentionally excluded. |
| E-008 | targeted_forbidden_symbol_scan | `rg -n -- "--text-\|--glass\|--primary" frontend/src/styles/theme.css frontend/src/App.css frontend/src/index.css frontend/src/styles/legacy-style-surface-registry.md` | PASS | Zero hits in global theme/App/index/legacy registry for CS-067 alias targets. | Local semantic extensions under Daily Horoscope are checked separately. |
| E-009 | targeted_forbidden_symbol_scan | `rg --files-with-matches ... "var(--compat-or-migration-token)" frontend/src` | FAIL | Compatibility/migration token consumers remain in 48 source/test files. | Pattern excludes canonical `--color-*`, `--type-*`, `--space-*`, etc. |
| E-010 | targeted_forbidden_symbol_scan | `rg --files-with-matches ... "--compat-or-migration-token:" frontend/src` | FAIL | Compatibility/migration token declarations remain in 28 CSS files. | Registry-classified namespaces may be intentional but still require convergence stories. |
| E-011 | targeted_forbidden_symbol_scan | `rg --pcre2 --files-with-matches ... hardcoded visual values ... frontend/src -g "*.css"` | FAIL | Hardcoded visual values remain in the CSS files listed below. | Static scan includes canonical token files and must be interpreted by cluster. |
| E-012 | targeted_forbidden_symbol_scan | `rg -n legacy-pattern frontend/src/pages/admin frontend/src/i18n/... frontend/src/tests/AdminPromptsPage.test.tsx` | FAIL | Admin prompts still uses product/runtime names containing `legacy`. | Could be a product-approved label; requires decision. |
| E-013 | canonical_replacement_evidence | `rg -n admin-prompts-archive-or-rollback ...` | PASS | Canonical replacement selectors are present in `AdminPromptsPage.tsx`, `AdminPromptsPage.css`, and guard tests. | Selector migration only, not product terminology. |
| E-014 | story_context | Read CS-067 `legacy-style-after.md` and `legacy-removal-audit.md` | PASS | CS-067 classifies removed selectors and aliases and records zero-hit goals after migration. | Story evidence is accepted as historical context, not primary runtime proof. |
| E-015 | repo_wide_negative_scan | `rg -n "var\([^\)]*," frontend/src -g "*.css"` | PASS | Only `App.css:3124` and `pages/settings/Settings.css:1052` remain; both use `--usage-progress`. | Dynamic fallback bridge remains active. |
| E-016 | architecture_guard_inventory | Read `css-fallback-allowlist.md` and `design-system-allowlist.ts` | PASS | Both list exactly the same two `--usage-progress` fallback exceptions. | No generator enforces markdown from TS source. |
| E-017 | targeted_forbidden_symbol_scan | `rg -n "style=\{" frontend/src -g "*.tsx"` | PASS | Five inline style hits match the exact allowlist. | Does not classify future style prop semantics beyond existing tests. |

## E-011 Hardcoded-Value File Inventory

These files matched the hardcoded-value scan and are the exhaustive files to consider for F-003. Work should be split into coherent clusters; token source files may be edited only when introducing or consolidating canonical tokens.

- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`
- `frontend/src/styles/utilities.css`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/layouts/AuthLayout.css`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/WizardLayout.css`
- `frontend/src/components/AdminGuard.css`
- `frontend/src/components/AstroDailyEvents.css`
- `frontend/src/components/AstroFoundationSection.css`
- `frontend/src/components/BestWindowCard.css`
- `frontend/src/components/DayClimateHero.css`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/components/HeroHoroscopeCard.css`
- `frontend/src/components/MiniInsightCard.css`
- `frontend/src/components/NatalInterpretation.css`
- `frontend/src/components/ShortcutCard.css`
- `frontend/src/components/SignUpForm.css`
- `frontend/src/components/TurningPointCard.css`
- `frontend/src/components/astro/AstroMoodBackground.css`
- `frontend/src/components/layout/Header.css`
- `frontend/src/components/layout/Sidebar.css`
- `frontend/src/components/prediction/CategoryGrid.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/components/prediction/DailyPageHeader.css`
- `frontend/src/components/prediction/DayAgenda.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/prediction/DayStateBadge.css`
- `frontend/src/components/prediction/DayTimeline.css`
- `frontend/src/components/prediction/DayTimelineSection.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/PeriodCardsRow.css`
- `frontend/src/components/prediction/SectionTitle.css`
- `frontend/src/components/prediction/TimelineRail.css`
- `frontend/src/components/prediction/TurningPointsList.css`
- `frontend/src/components/settings/DeleteAccountModal.css`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Button/Button.css`
- `frontend/src/components/ui/Card/Card.css`
- `frontend/src/components/ui/EmptyState/EmptyState.css`
- `frontend/src/components/ui/ErrorState/ErrorState.css`
- `frontend/src/components/ui/Field/Field.css`
- `frontend/src/components/ui/Form/Form.css`
- `frontend/src/components/ui/LockedSection/LockedSection.css`
- `frontend/src/components/ui/Modal/Modal.css`
- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/components/ui/UpgradeCTA/UpgradeCTA.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/features/chat/components/ChatComposer.css`
- `frontend/src/features/chat/components/ChatPageHeader.css`
- `frontend/src/features/chat/components/ChatQuotaBanner.css`
- `frontend/src/features/chat/components/ChatWindow.css`
- `frontend/src/features/chat/components/ConversationItem.css`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/pages/AstrologerProfilePage.css`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/DashboardPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/pages/PrivacyPolicyPage.css`
- `frontend/src/pages/billing/billing-return.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/admin/AdminAiGenerationsPage.css`
- `frontend/src/pages/admin/AdminContentPage.css`
- `frontend/src/pages/admin/AdminDashboardPage.css`
- `frontend/src/pages/admin/AdminEntitlementsPage.css`
- `frontend/src/pages/admin/AdminLogsPage.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/admin/AdminSamplePayloadsAdmin.css`
- `frontend/src/pages/admin/AdminSettingsPage.css`
- `frontend/src/pages/admin/AdminSupportPage.css`
- `frontend/src/pages/admin/AdminUserDetailPage.css`
- `frontend/src/pages/admin/AdminUsersPage.css`
- `frontend/src/pages/admin/PersonasAdmin.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/pages/landing/sections/LandingFooter.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/ProblemSection.css`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/SolutionSection.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
