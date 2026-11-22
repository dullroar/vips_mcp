# Agent contract

A FastMCP adapter over the installed libvips command-line tools.

## Standing rules

- Before changing this repository's structure, read [repo-template](https://github.com/dullroar/repo-template) and [ralph-looper](https://github.com/dullroar/ralph-looper). Account for their layout, plan format, generated indexes, worktree rules, and validation commands in the change.
- Do work on a branch. Use a separate worktree and branch for each Ralph step. Do not commit directly to `main`.
- Write in Simplified Technical English. Use short sentences, active voice and consistent terms.

## Load context in this order

1. Read this file.
2. Read the short indexes in full. See [README.md](./README.md), [docs/README.md](./docs/README.md), [memory/AGENTS.md](./memory/AGENTS.md), [plans/AGENTS.md](./plans/AGENTS.md) and [scripts/AGENTS.md](./scripts/AGENTS.md).
3. Match the task against the routing entries in each index and open only matching documents.
4. For a large file, search its headings and read only the relevant ranges.
5. Stop loading when the decision, intended files, constraints and validation method are known.

User instructions take precedence over repository guidance. When sources conflict, prefer: user
instruction, this file, `docs/design/`, the named plan, domain documentation and references,
`memory/`, implementation and tests, historical notes.

## Context ownership

- Universal rules belong here.
- Architectural reasons belong in `docs/design/` (one premise per file).
- Non-obvious findings that cost time to discover belong in `memory/` (one topic per file; edit the existing topic, do not append a rival).
- Execution state belongs in `plans/`; deterministic automation in `scripts/`.
- Start each routed Markdown file with `gist: "Read me when: ..."` front matter. Start each script with a `Run me when:` comment or docstring in the first 25 lines. Run `python3 scripts/build_indexes.py` to update generated index sections.

Do not duplicate a fact across layers. Correct its canonical source.

## Planned work (spec-driven)

- Work only on a named plan in `plans/<plan>/` or an explicitly identified off-plan task. Copy [plans/for-each-plan/](./plans/for-each-plan/) to start a plan. Keep the goal and loop prompt in `goal.md`, the approach in `plan.md`, the requirements in `spec.md` and the steps in `steps/`.
- Once its spec is approved, proceed through the steps without asking permission for routine work. Failed tests and dead ends inside scope: diagnose, repair, continue. Return to the user only for a new decision: contradictory requirements, scope expansion, or an action outside the spec's delegated authority.
- Acceptance checks named in the spec are protected. Never weaken, skip or delete one to get green; if one cannot pass as written, escalate.
- Parallel steps must have no dependency between them and no overlapping `touches`; if independence is uncertain, serialize. After parallel steps merge, run the spec's combined validation.
- A step is done only with recorded evidence. Keep status, evidence and resume notes in the step file. Keep logs, locks and other runtime files outside the repository.
- Retiring a rule, correcting documentation, and tolerating a known violation are different outcomes; record which one. See the [spec template](./plans/for-each-plan/spec.md).

## Validation

Run the smallest check that proves the change, then `python3 scripts/check_context.py` for any change to context files.

## Safety

Do not commit credentials, personal data, personal filesystem paths, private host names or sensitive record-level examples. Use placeholders and aggregate evidence. Do not push, publish, force-push or add a remote without authorization.
