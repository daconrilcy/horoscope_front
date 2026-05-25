# Dev Log

- Initial `git status --short`: clean.
- Capsule generated after `.venv` activation because required `generated/*.md` files were missing.
- `condamad_prepare.py` first required explicit `--story-key` because multiple `CS-xxx` identifiers were present; rerun with `CS-306` succeeded.
- Browser plugin control surface was not available through tool discovery; used local Playwright Chromium for real-browser `/natal` QA.
- `pnpm lint` first failed on Windows `node_modules/.pnpm/lock.yaml` EPERM rename before lint; retry passed.
- Browser QA script first failed on Windows `fileURL` path handling, then on an ambiguous text locator; both were fixed in the evidence script and final run passed.
- No application source code was changed.
