#!/usr/bin/env python3
"""Rebuild the generated index in memory/AGENTS.md, plans/AGENTS.md and scripts/AGENTS.md.

Run me when: I added, renamed, deleted or changed the gist of a memory, a plan or a script, and before every pull request.

Rules:
- README indexes with context markers keep their routing rules.
- Memory files: front matter key `gist: "Read me when: ..."`.
- plans/<plan>/plan.md: front matter key `gist: "Read me when: ..."`.
- Files in scripts/, except the indexes: a line `Run me when: ...` in the first 25 lines (any comment style).
- Only the text between the BEGIN and END markers changes. The text above is fixed.
- The old wording `Read when:` is accepted as a gist.

Usage: build_indexes.py [--check] [ROOT]   (--check changes nothing; exit 1 if stale)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from ctx_common import (
    BEGIN, END, LEGACY_BEGIN, LEGACY_END, SKIP_DIRS, repo_root, split_frontmatter,
)

RUN_ME = re.compile(r"Run me when:\s*(.+?)\s*(?:\*/|#>|-->|\"\"\")?\s*$")
PLAN_SKIP = {"archive"}


def has_markers(readme: Path) -> bool:
    return readme.is_file() and LEGACY_BEGIN in readme.read_text(encoding="utf-8")


def collect(folder: Path) -> list[Path]:
    found: list[Path] = []
    for child in sorted(folder.iterdir()):
        if child.name in SKIP_DIRS:
            continue
        if child.is_dir():
            if has_markers(child / "README.md"):
                found.append(child / "README.md")
            else:
                found.extend(collect(child))
        elif child.suffix == ".md" and child.name != "README.md":
            found.append(child)
    return found


def excluded(readme: Path) -> set[str]:
    found = re.search(r"<!--\s*index-exclude:\s*(.*?)\s*-->", readme.read_text(encoding="utf-8"))
    return {p.strip() for p in found.group(1).split(",")} if found else set()


def md_gist(path: Path, errors: list[str]) -> str | None:
    meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    gist = meta.get("gist")
    if not isinstance(gist, str) or not gist.strip():
        errors.append(f"{path}: missing 'gist' front matter")
        return None
    return gist.strip()


def script_gist(path: Path, errors: list[str]) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").split("\n")[:25]
    except UnicodeDecodeError:
        errors.append(f"{path}: not a text file")
        return None
    for line in lines:
        found = RUN_ME.search(line)
        if found:
            return "Run me when: " + found.group(1)
    errors.append(f"{path}: missing 'Run me when:' line in the first 25 lines")
    return None


def entries(folder: Path, errors: list[str]) -> list[tuple[str, str]]:
    kind = folder.name
    out: list[tuple[str, str]] = []
    if kind == "memory":
        for p in sorted(collect(folder)):
            if p != folder / "AGENTS.md" and (gist := md_gist(p, errors)):
                out.append((p.relative_to(folder).as_posix(), gist))
    elif kind == "plans":
        for d in sorted(x for x in folder.iterdir() if x.is_dir() and x.name not in PLAN_SKIP | SKIP_DIRS):
            if (d / "plan.md").is_file():
                if g := md_gist(d / "plan.md", errors):
                    out.append((f"{d.name}/plan.md", g))
            else:
                errors.append(f"{d}: plan folder has no plan.md")
    elif kind == "scripts":
        for p in sorted(folder.iterdir()):
            if p.is_file() and p.name not in {"AGENTS.md", "README.md"} and not p.name.startswith("."):
                if g := script_gist(p, errors):
                    out.append((p.name, g))
    return out


def render(items: list[tuple[str, str]]) -> str:
    if not items:
        return "<!-- Nothing to list yet. -->"
    return "\n".join(f"* [{name}](./{name})\n  {gist}" for name, gist in items)


def legacy_entries(readme: Path, errors: list[str]) -> str:
    skip = excluded(readme)
    entries = []
    paths = sorted(collect(readme.parent), key=lambda p: p.relative_to(readme.parent).as_posix())
    for path in paths:
        rel = path.relative_to(readme.parent).as_posix()
        if rel not in skip and (gist := md_gist(path, errors)):
            entries.append(f"* [{rel}](./{rel}).\n  {gist}")
    return "\n".join(entries) if entries else "<!-- No routed files yet. -->"


def main(argv: list[str]) -> int:
    check = "--check" in argv
    args = [a for a in argv if not a.startswith("--")]
    root = repo_root(Path(args[0]) if args else None)
    errors: list[str] = []
    stale: list[str] = []

    def update(index: Path, begin: str, end: str, body: str) -> None:
        text = index.read_text(encoding="utf-8")
        head, marker, rest = text.partition(begin)
        if not marker or end not in rest:
            errors.append(f"{index}: missing BEGIN/END markers")
            return
        _, tail = rest.split(end, 1)
        new = f"{head}{begin}\n\n{body}\n\n{end}{tail}"
        if new != text:
            stale.append(index.relative_to(root).as_posix())
            if not check:
                index.write_text(new, encoding="utf-8")

    for name in ("memory", "plans", "scripts"):
        folder = root / name
        index = folder / "AGENTS.md"
        if index.is_file():
            update(index, BEGIN, END, render(entries(folder, errors)))
        elif folder.is_dir():
            errors.append(f"{index}: missing generated index")
    for readme in sorted(root.rglob("README.md")):
        if not SKIP_DIRS & set(readme.relative_to(root).parts) and has_markers(readme):
            update(readme, LEGACY_BEGIN, LEGACY_END, legacy_entries(readme, errors))

    for err in errors:
        print(f"ERROR {err}")
    if check and stale:
        print("STALE index (run: python3 scripts/build_indexes.py): " + ", ".join(stale))
    return 1 if errors or (check and stale) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
