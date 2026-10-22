#!/usr/bin/env python3
"""Self-test the bundled diagram renderer, as CI runs it.

Two things this check exists to prevent:

* a renderer that "succeeds" while writing empty or absurdly small PNGs — every
  report would then claim figures it never drew;
* a spec that omits the traceable `source` line slipping through, which is the
  one rule that keeps a diagram honest.

(The first version of this check lived inline in ci.yml as a shell heredoc, which
is invalid bash inside an indented YAML block scalar, and it also demanded
1200 px from a 1020 px sample. Both are why this is a real script with real
thresholds.)

Usage: python scripts/check-render-selftest.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERER = os.path.join(
    REPO, "presets", "deep-paper-reading", "skills", "deep-paper-reading",
    "scripts", "render-diagram.py",
)

# Actual widths of the four built-in samples at the default --scale 2. The floor
# is a floor: anything narrower than the measured size minus a little slack means
# the layout collapsed.
KINDS = ("flow", "matrix", "scatter", "timeline")
MIN_WIDTH = 900
MIN_HEIGHT = 500


def run(*args):
    return subprocess.run([sys.executable, RENDERER, *args],
                          capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    from PIL import Image

    if not os.path.isfile(RENDERER):
        print(f"renderer missing: {RENDERER}", file=sys.stderr)
        return 1

    failures = []
    with tempfile.TemporaryDirectory(prefix="render-selftest-") as tmp:
        result = run("--selftest", "--tmp", tmp)
        print(result.stdout.strip() or "(no stdout)")
        if result.stderr.strip():
            print("stderr:", result.stderr.strip())
        if result.returncode != 0:
            failures.append(f"--selftest exited {result.returncode}")

        for kind in KINDS:
            path = os.path.join(tmp, f"selftest-{kind}.png")
            if not os.path.isfile(path):
                failures.append(f"{kind}: no PNG written")
                continue
            with Image.open(path) as probe:
                width, height = probe.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                failures.append(f"{kind}: {width}x{height} below {MIN_WIDTH}x{MIN_HEIGHT}")
            print(f"  {kind:9s} {width}x{height} ok")

    # the source-line rule must actually bite
    with tempfile.TemporaryDirectory(prefix="render-guard-") as tmp:
        spec = os.path.join(tmp, "no-source.json")
        with open(spec, "w", encoding="utf-8") as handle:
            json.dump({
                "kind": "flow", "lang": "zh",
                "title": "no source line",
                "layers": [{"name": "a", "nodes": ["n1"]}],
                "nodes": {"n1": {"label": "x", "role": "context"}},
                "edges": [],
            }, handle, ensure_ascii=False)
        result = run(spec, "--out", os.path.join(tmp, "out.png"))
        if result.returncode == 0:
            failures.append("a spec without `source` was accepted — the traceability rule is broken")
        else:
            print("  source guard rejects a spec without `source`: ok")

    if failures:
        print("\nrenderer self-test failed:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("renderer self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
