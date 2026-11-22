---
id: 03-core-workflows
status: pending
depends_on: [02-tool-boundary]
touches:
  - server.py
  - mcp_tools/**
  - tests/**
  - requirements.txt
  - Dockerfile
  - scripts/test_docker.sh
  - plans/sharpen-mcp/steps/03-core-workflows.md
lane: none
requirements: [R3]
gate: bash scripts/test_docker.sh && python3 scripts/check_context.py && git diff --check
evidence: ""
---

# Deliver the core workflows

Implement every Core row of the [catalog](../catalog.md) with the schema and defaults documented in step 01. Preserve output semantics from supported existing workflows or record a migration mapping where the new contract is deliberately different.

Offer aspect-preserving scale and fit by default, explicit crop-to-fill or padding, bounded target dimensions, and deterministic rounding. Explain that reducing by 75 percent leaves 25 percent of each dimension, while resizing to 75 percent leaves 75 percent. Honor orientation before geometry, with deterministic page/frame defaults and explicit selection for multi-page formats. Publish chosen MIME/profile/alpha handling and limits for decoded pixels, frames, batch files, time, temp space, and output sizes. Limit named loader/saver formats to capabilities tested in the image. Verify with vipsheader plus chosen pixel/alpha/color fixtures.

Each workflow needs a successful real backend case and at least one applicable failure or unsupported case. Use MCP stdio to test representative calls and validate generated file contents or measured properties. Cover the explicitly named headline scenario end to end.

## Resume notes

Pending.
