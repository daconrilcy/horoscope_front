# Dev Log

## 2026-05-23

- Initial dirty worktree before editing included `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md`, untracked `.agents/skills/condamad-product-architecture/`, and several untracked `_story_briefs/cs-246..cs-254` files. These were treated as pre-existing user/context changes and not reverted.
- The capsule initially lacked required generated files. `condamad_prepare.py` generated a parallel title-derived capsule; required generated files were copied into the target CS-246 capsule and the parallel capsule was removed after path verification.
- Added the canonical typed registry module and tests.
- First targeted pytest failed because `_build_registry` was initialized after use; moved registry initialization below the function.
- Full backend pytest then failed on the existing structural runtime token guard because CS-246 requires `narrative_generation_v1`. Removed non-required `narrative` internal names and added a permanent architecture allowlist only for the required CS-246 family code.
- Review/fix iteration 1 found that `profection_v1` had a temporal owner but was missing from the astronomical blocker
  invariant. The registry, test, and evidence now include it.
- Review/fix iteration 2 found that cache blockers were only implicit in `cache_invalidation_boundary`. Blocked families
  now carry the explicit cache policy blocker required by the brief.
- Feedback-loop routing decision: no-propagation. The corrections were local implementation/guard evidence adjustments
  inside CS-246 and did not reveal a reusable skill or AGENTS.md update.
