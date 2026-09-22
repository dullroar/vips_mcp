# DESIGN.md

# vips-mcp Design

## Boundary

vips-mcp is a FastMCP adapter over the installed libvips CLI. README.md provides tool usage and setup; this document records the delegation and API-shape decisions.

## Core decisions

- Delegate image operations to libvips, which is designed for streaming large images rather than loading full images into a Python process.
- Offer focused tools for common image tasks and `vips_passthrough` for native operations not worth duplicating in a curated wrapper.
- Expand glob inputs in the server so batch image work is represented as one MCP operation with deterministic per-file outputs.
- Use `vipsheader` as its own executable for image information rather than treating it as a `vips` subcommand.

## Constraints

This is not a Python image-processing library or a replacement for the full libvips command surface. The host must provide libvips, and callers remain responsible for choosing output formats and preserving any required image semantics.


