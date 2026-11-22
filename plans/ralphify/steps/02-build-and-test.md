---
id: 02-build-and-test
status: done
depends_on: [01-adopt-context]
touches:
  - Dockerfile
  - .dockerignore
  - README.md
  - scripts/test_docker.sh
  - scripts/AGENTS.md
  - .github/workflows/context.yml
  - tests/**
  - plans/ralphify/steps/02-build-and-test.md
lane: none
requirements: [R2]
gate: bash scripts/test_docker.sh && python3 scripts/check_context.py && git diff --check
evidence: gate passed 2026-11-22 (driver-verified)
claimed_by: codex cli-default
claimed_at: "2026-11-22T22:14:12Z"
---

# 02-build-and-test

Depends on `01-adopt-context`. Add a project Dockerfile, an appropriate `.dockerignore`, and `scripts/test_docker.sh`. Use project dependencies and current lockfiles. Run project tests as a normal container user where supported. Use synthetic fixtures, a temporary output directory, and no developer credentials. Put any new operational or test artifacts under the repo's existing conventions. Document build, test, and any device or platform requirements in `README.md`. Keep existing host usage working. Arrange for CI to call the same entry point wherever the runner supports that gate.

The Docker test script builds the image from the current step worktree and runs the repo-specific gates inside it. For context checks, use a complete source snapshot or an appropriate read-only checkout that works with linked Git worktrees. A linked worktree's `.git` pointer alone does not provide its Git metadata in the container. Keep the image usable without a sibling checkout, host venv, or mutable shared volume. Use repo- and run-specific names for any image tags, container names, and writable paths. Build dependencies can use package registries. The default test runtime uses local fixtures and an isolated container network. The FUSE mount gate is required for the two FUSE lanes, with the host requirements in their repo briefs.

Touches `Dockerfile`, `.dockerignore`, `README.md`, `scripts/test_docker.sh`, generated indexes, any necessary workflow updates, focused test/support paths from the repo brief, and this step file. Gate: `bash scripts/test_docker.sh && python3 scripts/check_context.py && git diff --check`.

## Repository gate

Install the libvips CLI and the existing Python requirements. Add a stdio test under `tests/` that initializes and uses a real image operation on a synthetic local image. Verify output dimensions or format using the native CLI. Document the stdio container command with stdin open. Preserve existing tool names and arguments.

## Results

- The full step gate passed on 2026-11-22 UTC. The image built from the linked
  worktree snapshot. The context checks passed inside and outside the container.
- The stdio test called `resize_image` on a synthetic 40 × 30 PNG.
  `vipsheader` confirmed the output dimensions of 20 × 15 pixels.
- The first run selected MCP 2.3.0 and failed at the server's `FastMCP` import.
  The Docker build and the host install command now require MCP 1.x. The
  passing build used MCP 1.30.0 with the existing requirements file.
