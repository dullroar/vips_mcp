---
id: 01-backend-evidence
status: pending
depends_on: []
touches:
  - docs/backend-notes.md
  - docs/README.md
  - plans/sharpen-mcp/steps/01-backend-evidence.md
lane: none
requirements: [R1]
gate: test -s docs/backend-notes.md && python3 scripts/check_context.py && git diff --check
evidence: ""
---

# Verify the backend capabilities

Use `man vips`, `man vipsheader`, `man vipsthumbnail`, `vips -l`, and `vips --version` with the actual image build. Walk the published function list by family and write a disposition for each relevant family. Make this catalog the example for the other three repositories. Verify thumbnail resize behavior, loader shrink-on-load, crop strategies, output codecs, profile policy, tiff tile behavior, and operations which require optional delegates.

Build a small synthetic corpus in temporary storage. Record installed versions, official references with sections, real operation examples, output fields and tolerances, and options that do not work. Compare the proposed catalog against actual native behavior. For each tool, identify its finite parameter schema, numeric limits, output contract, examples, and the exact backend feature that supports it. Treat community examples as leads and verify behavior against the official backend and installed build.

Offer aspect-preserving scale and fit by default, explicit crop-to-fill or padding, bounded target dimensions, and deterministic rounding. Explain that reducing by 75 percent leaves 25 percent of each dimension, while resizing to 75 percent leaves 75 percent. Honor orientation before geometry, with deterministic page/frame defaults and explicit selection for multi-page formats. Publish chosen MIME/profile/alpha handling and limits for decoded pixels, frames, batch files, time, temp space, and output sizes. Limit named loader/saver formats to capabilities tested in the image. Verify with vipsheader plus chosen pixel/alpha/color fixtures.

Use the libvips capability map as the model for coverage. Give each public operation family a disposition with an example or a reason to defer it.

Write the results to `docs/backend-notes.md` and link it from `docs/README.md`. Record the exact commands and results for successful and unsupported cases.

## Resume notes

Pending.
