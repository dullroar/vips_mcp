---
gist: "Read when: reimplementing image operations in Python, adding a curated tool, changing vips_passthrough, or altering glob/batch behavior."
---

# Delegate image operations to libvips

**Decision.** Image operations go to libvips, which streams large images instead of loading them into a Python process. Focused tools cover common tasks and `vips_passthrough` reaches native operations not worth duplicating. Glob inputs expand in the server so batch work is one MCP operation with deterministic per-file outputs. `vipsheader` is its own executable for image information, not a `vips` subcommand.

**Boundary.** Not a Python image-processing library or a replacement for the full libvips surface. The host must provide libvips; callers choose output formats and preserve required image semantics.
