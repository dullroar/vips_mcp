---
id: 03-verify-integration
status: done
depends_on: [02-build-and-test]
touches:
  - plans/ralphify/steps/03-verify-integration.md
lane: none
requirements: [R3]
gate: python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check
evidence: gate passed 2026-11-22 (driver-verified)
claimed_by: codex cli-default
claimed_at: "2026-11-22T22:16:28Z"
---

# 03-verify-integration

Depends on `02-build-and-test`. Update only the step file. Rerun the context and Docker gate from the integrated worktree as the driver would. Check the template and runner links in `AGENTS.md` and the structural-change rule. Verify README commands and the existing entry points. Record the worktree base commit, exact commands, build result, test counts or concrete smoke assertions, expected opt-in skips, real FUSE result where required, and UTC date. Keep logs outside Git. Gate: `python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check`.

The driver writes its own `evidence` field. Put detailed test evidence in the body of the verification step and commit it. The parent verifies the final child commit and result. A green build alone cannot satisfy R2 or R3.

## Repository gate

Install the libvips CLI and the existing Python requirements. Add a stdio test under `tests/` that initializes and uses a real image operation on a synthetic local image. Verify output dimensions or format using the native CLI. Document the stdio container command with stdin open. Preserve existing tool names and arguments.

Run `git merge-base HEAD plan/ralphify` to identify the integrated base commit. Replace each pending value in the results below. For each passing check, put details after `PASS`. Include the actual Docker commands or image reference and test counts or concrete smoke results. Record `n/a` in the FUSE field for other repos. If a required test fails or skips, record that in resume notes and leave the result pending.

## Results

- Base commit: `4536603e5cf1a3198dd8fbc7ae8d48133a0e6471` from `git merge-base HEAD plan/ralphify`.
- Commands: PASS `python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check`.
- Docker build: PASS The gate ran `docker build --tag "$image" "$snapshot"`.
  The tag and snapshot were specific to the run. The README command
  `docker build -t vips-mcp .` also passed.
- Tests: PASS The context checks passed on the host and in the container.
  The gate ran `python -m unittest discover -s tests -v` in a read-only
  container with `--network none`. One test passed. It initialized MCP over
  stdio, called `resize_image` on a synthetic 40 × 30 PNG, and verified a
  20 × 15 PNG with `vipsheader`.
- Skips: 0. The suite has no opt-in checks.
- FUSE: n/a.
- UTC date: 2026-11-22.

## Links and entry points

- Both GitHub links in `AGENTS.md` returned HTTP 200. The structural-change
  rule requires both references and covers layout, plan format, generated
  indexes, worktrees and validation commands.
- `docker run --rm -i vips-mcp` accepted an MCP `initialize` request through
  the default container command. `python /app/server.py --help` listed stdio,
  SSE, host and port options. A Git comparison with `dfe242e` showed no changes
  to `server.py` or `requirements.txt`.
- The runner accepted the README flags `--repo`, `--plan ralphify` and
  `--agent codex` with `--help`. A `--status` check from the step worktree
  could not use the plan worktree. The README directs the runner command to
  the main checkout. The active driver owns the plan run.
