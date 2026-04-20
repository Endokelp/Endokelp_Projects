#!/usr/bin/env python3
"""Gremlin hunt before you push. See README."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RULES: list[tuple[str, str, str]] = [
    (r"\bAI[- ]?generated\b", "says 'AI-generated'", "fail"),
    (r"\bChatGPT\b", "mentions ChatGPT", "fail"),
    (r"\bOpenAI\b", "mentions OpenAI", "warn"),
    (r"\bClaude\b", "mentions Claude", "warn"),
    (r"\bCopilot\b", "mentions Copilot", "warn"),
    (r"\bCursor\b", "mentions a known IDE name (tooling leak)", "warn"),
    (r"\bvibecod", "says vibecod*", "warn"),
    (r"\bMade-with:", "commit trailer / metadata leak", "fail"),
    (r"successfully demonstrated that", "stock phrase", "warn"),
    (r"\bcomprehensive quantitative analysis\b", "stock abstract phrase", "warn"),
    (r"\bIt is important to (note|acknowledge|remember) that\b", "filler lead-in", "warn"),
    (r"\bFurthermore,\b", "transition cliché (academic)", "warn"),
    (r"\bAdditionally,\b", "transition cliché", "warn"),
    (r"\bIn conclusion,\b", "essay sign-off", "warn"),
    (r"\bleverage (the|our|this)\b", "corporate 'leverage'", "warn"),
    (r"\bsynergy\b", "corporate 'synergy'", "warn"),
    (r"\brobust solution\b", "generic 'robust solution'", "warn"),
    (r"\bdelve into\b", "delve into", "warn"),
    (r"\butilize\b", "utilize → use", "warn"),
]

TEXT_GLOBS = ("*.py", "*.md", "*.txt", "*.toml", "*.yml", "*.yaml")
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "_Endokelp_Projects",
    "PythonProjects",
}


def should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or name.startswith(".")


def scan_file(path: Path, compiled: list[tuple[re.Pattern[str], str, str]]) -> list[tuple[str, str, str]]:
    hits: list[tuple[str, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return hits
    for rx, msg, sev in compiled:
        if rx.search(text):
            hits.append((str(path), msg, sev))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="tree to scan (default: repo root)",
    )
    ap.add_argument("--warn-only", action="store_true", help="report only, exit 0")
    args = ap.parse_args()
    root: Path = args.root

    compiled = [(re.compile(p, re.IGNORECASE), msg, sev) for p, msg, sev in RULES]

    failures: list[str] = []
    warnings: list[str] = []

    for pattern in TEXT_GLOBS:
        for path in root.rglob(pattern):
            if path.name == "vibe_detective.py":
                continue
            if any(should_skip_dir(p.name) for p in path.parents):
                continue
            rel = path.relative_to(root)
            if rel.parts and rel.parts[0] in SKIP_DIRS:
                continue
            for fpath, msg, sev in scan_file(path, compiled):
                line = f"{fpath}: {msg}"
                if sev == "fail":
                    failures.append(line)
                else:
                    warnings.append(line)

    for bad in ("cursor.rules", "AGENTS.md"):
        p = root / bad
        if p.is_file():
            failures.append(f"{p}: filename looks like agent scaffolding")

    if warnings:
        print("--- warnings ---", file=sys.stderr)
        for w in sorted(set(warnings)):
            print(w, file=sys.stderr)
    if failures:
        print("--- FAIL ---", file=sys.stderr)
        for f in sorted(set(failures)):
            print(f, file=sys.stderr)
        if not args.warn_only:
            return 1
    if not warnings and not failures:
        print("vibe_detective: clean", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
