"""Backward-compatible wrapper toward canonical ops path."""

from app.ops.llm.release.build_release_candidate import main

if __name__ == "__main__":
    raise SystemExit(main())
