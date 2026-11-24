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

## Probes

Date of the runs (UTC): 2026-11-24. Each probe ran in its own clone of `HEAD` under `.probe/`. The command was `python3 -m deterministic_controls check --root <copy> --profile ci --format json`. The real tree was not changed. The planted token was built at run time and was never written in a tracked file of this repository. `.probe/` was deleted before the gate.

| Probe | Expected rule ID | Rule ID found | Exit code | Result |
| --- | --- | --- | --- | --- |
| Clean copy of `HEAD` | none | none | 0 | pass |
| Broken relative link in a Markdown file | `markdown.local-links` | `markdown.local-links.missing-file` | 1 | fail, as expected |
| Stale generated index (a script line changed, index not rebuilt) | `context.index-freshness` | `context.index-freshness.stale` | 1 | fail, as expected |
| Plan step without `gate` | `plans.schema` | `plans.schema.missing-gate` | 1 | fail, as expected |
| Synthetic token in a Markdown file (committed in the copy) | `security.secrets` | `security.secrets.github-token` (also `security.personal-data.token`) | 1 | fail, as expected |
| Tracked `driver.out` file | `repo.forbidden-artifacts` | `repo.forbidden-artifacts.tracked` | 1 | fail, as expected |
| Internal error (Markdown file with invalid UTF-8) | no pass | `markdown.local-links` and `security.personal-data` status `error` | 3 | no pass, as expected |

- The shim `python3 scripts/check_context.py` ran in the copy with the bad plan step. It printed `FAIL check_plan.py` and exited `1`.
- After each probe the copy was discarded. A clean copy of `HEAD` passes with exit `0`. The shim also passes there.

## Rollback

Date of the test (UTC): 2026-11-24.

There is no earlier pin. The rollback target is the set of pre-adoption scripts. The base commit is the parent of the `adopt apply` commit.

Test result:

- A clone checked out at the base commit ran the old `python3 scripts/check_context.py` on a clean tree. It passed (`ok` for all four scripts).
- A clean clone of `HEAD` ran the new shim `python3 scripts/check_context.py`. It passed.

Files of the adoption (`adopt apply` commit):

- Added: `controls.toml`, `scripts/controls-requirements.txt`, `docs/controls-adoption.md`.
- Changed: `scripts/check_context.py` (now a shim), `.github/workflows/context.yml` (new `controls` job), `Dockerfile` (shim cache at build time, `git`), `AGENTS.md` (routing rule), `docs/README.md` and `scripts/AGENTS.md` (index entries).
- Kept: all old check scripts in `scripts/`, `scripts/test_docker.sh`, the `check` CI job, the tests and the product code.

Steps to roll back:

1. Create a new branch. Do not work on `main`.
2. Option A, change the pin: edit `scripts/controls-requirements.txt`, put another commit in the install line, and run `python3 scripts/check_context.py` once to build the new environment.
3. Option B, remove the adoption: run `git revert` on the adoption commits, or restore the changed files from the base commit with `git checkout <base> -- <file>` and delete the added files.
4. Run `python3 scripts/check_context.py`. It must pass.
5. The cache under `$XDG_CACHE_HOME/deterministic-controls/<commit>/` is safe to delete. The shim builds it again when it needs it.

## Receipt

Date of the run (UTC): 2026-11-24. Command, run in a clean clone of `HEAD` under `.probe/`:

`python3 -m deterministic_controls adopt receipt --root <clean clone> --commit 3a2e9f3d95136958c54f73c831e84b971fc9a054`

```json
{
  "base_revision": "fb8c0dd9146656390f615e7290a1e44a4d499384",
  "checks_run": [
    {"check_id": "context.index-freshness", "status": "passed"},
    {"check_id": "markdown.local-links", "status": "passed"},
    {"check_id": "plans.graph", "status": "passed"},
    {"check_id": "plans.schema", "status": "passed"},
    {"check_id": "repo.forbidden-artifacts", "status": "passed"},
    {"check_id": "security.personal-data", "status": "passed"},
    {"check_id": "security.secrets", "status": "passed"}
  ],
  "control_pin": "3a2e9f3d95136958c54f73c831e84b971fc9a054",
  "date": "2026-11-24",
  "enabled_checks": [
    "context.index-freshness",
    "markdown.local-links",
    "plans.graph",
    "plans.schema",
    "repo.forbidden-artifacts",
    "security.personal-data",
    "security.secrets"
  ],
  "enforcement_state": "advisory",
  "files_added": [],
  "files_changed": [],
  "profile": "ci",
  "repository": "good",
  "schema_version": 1
}
```

Notes:

- The JSON above is shortened. The fields `commands_kept` and `rollback` of the full output are left out. The Rollback section above replaces them.
- `repository` is the name of the temporary clone, not of this repository.
- `files_added` and `files_changed` are empty in a clean clone. This is a known library defect. The Rollback section lists the files of the adoption.
- `enforcement_state` is `advisory`.

## Secret guard exceptions

none
