---
gist: "Read when: extending the server to more vips subcommands, or building a vips command by analogy with ImageMagick or ffmpeg flags."
---

# The vips CLI differs from what subcommand names suggest

- 2026-05-26 - Format conversion is driven by the output file's extension (`vips copy in.tiff out.jpg`), not a `vips save -o` flag. Resizing goes through `vips thumbnail in out WIDTH [height=H] [size=force|both|up|down]`, not a `vips resize --fit=` option. Header/metadata inspection is the separate `vipsheader` binary; `vips header` fails with "unknown action" (commits 6b4a180, 13f8185). Re-verify against `vips --help` / `man vips` when adding subcommands rather than assuming flag names by analogy.
