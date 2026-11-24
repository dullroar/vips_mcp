---
gist: "Read me when: you run, change or roll back the pinned deterministic-controls checks, or you want to know how they were adopted."
---

# Controls adoption

This repository uses the `deterministic-controls` library at release `v0.1.2`. The adoption is advisory. The `controls` CI job is not a required check yet. All old gates and job names stay.

## How it works

- `scripts/check_context.py` is a shim. It runs the library through `python3 -m deterministic_controls check --profile ci`.
- `scripts/controls-requirements.txt` holds the pin: the install line with a full commit.
- `controls.toml` lists the enabled checks.
- The shim runs the library from a cached virtual environment. The path is `$XDG_CACHE_HOME/deterministic-controls/<commit>/`. The default is `~/.cache/deterministic-controls/<commit>/`.
- The first run for a commit needs the network. The shim builds the cache then.
- If the library cannot run, the shim exits `2`. It never passes without a result. It never falls back to the old scripts.
- The shim keeps the old output lines (`ok  <script>` or `FAIL <script>`) and the exit codes `0` and `1`.
- The old check scripts stay in `scripts/`. This adoption does not delete them.

## How the adoption was made

1. `adopt audit` made a read-only report (`docs/controls-audit.json`).
2. `adopt plan --commit <pinned commit>` gave a dry-run diff.
3. `adopt apply --commit <pinned commit>` wrote the shim, the pin, `controls.toml` and the `controls` CI job.
4. The step then added the Dockerfile change, the `AGENTS.md` rule and this document by hand.

## Where the tools did not fit

- **Dockerfile.** The Docker gate runs with `--network none --read-only`. The shim needs the network once. So the Dockerfile builds the shim cache at image build time, as user `vips`. The build has network. The image also installs `git`. The shim setup and `tests/test_secret_guard.py` need it. The run command, `--read-only` and `scripts/test_docker.sh` are unchanged.
- **`scripts/install_hooks.sh`.** `adopt apply` rewrote it (a `secretguard.path` fallback). The file is outside the `touches` of this step. The step restored it from the commit before `apply`.
- **`scripts/controls-requirements.txt`.** `apply` wrote a `Run me when:` line, so no manual fix was needed.
- **`controls` job.** `apply` repeats the secret guard steps of the `check` job. The repeat is accepted.
- **Cache write at run time.** The Docker run is expected to write nothing outside `/tmp`. Step `a04-verify` confirms this with the full Docker gate.

## Secret guard exceptions

none
