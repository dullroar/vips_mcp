# MEMORY.md

Non-obvious findings about this codebase and its operating environment, discovered during work but not designed for anywhere else — not in README.md (what it is and how to use it), DESIGN.md (architectural decisions), or agent-instruction files (rules). This is background context for whichever LLM works in this repository next, so it does not have to rediscover these findings the hard way.

If you (an LLM) make a finding like the ones below — a gotcha, an environment quirk, or a non-obvious reason one component reads or uses another — add it here rather than only mentioning it in chat. Keep entries factual and dated; note when something might have been fixed since.

## Findings

- 2026-05-26 — The `vips` CLI's real surface differs from what its subcommand names suggest (commits 6b4a180, 13f8185): format conversion is driven by the output file's extension (`vips copy in.tiff out.jpg`), not a `vips save -o` flag; resizing goes through `vips thumbnail in out WIDTH [height=H] [size=force|both|up|down]`, not a `vips resize --fit=` option; and header/metadata inspection is the separate `vipsheader` binary — `vips header` fails with "unknown action". Re-verify against `vips --help`/`man vips` if extending this server to more subcommands rather than assuming flag names by analogy with ImageMagick or ffmpeg conventions.
