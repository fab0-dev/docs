# Verification

Verification is a ladder. Each rung is used only when the rungs below it can't express the check (P4).

| Rung | Mechanism | Runs | Cost | Example |
|---|---|---|---|---|
| 1 | Return schema | the resolver, on `record` | none | a reviewer's decision is `approve`, `escalate` or `reject` |
| 2 | Artifact schema | the resolver, on `record` | none | each task in `tasks.yaml` has `files` |
| 3 | Off-the-shelf linter | an artifact's `lint` verifier, on `record`; optionally a project hook on write | milliseconds | `yamllint`, `ruff`, a Markdown linter |
| 4 | The project's own build and tests | the implementing agent; CI | seconds to minutes | `npm test`, `pytest` |
| 5 | Review agent | the agent gate of a stage | tokens | does the change meet the spec's scenarios? |
| 6 | GitHub required checks | CI on the pull request | CI minutes | the same linters and tests, as the merge gate |
| 7 | Custom check script | a plugin's `bin/`, declared as a `script` verifier | maintenance | only when rungs 1–6 can't express it |

Most checks need no custom code because the artifact is structured (P5). For example, a rule that tasks touching the same files must not run in parallel is a schema plus one set comparison in the resolver.

## Verifiers on an artifact type

An artifact type's `schema` key is validated for YAML and JSON. Its `verify` list adds:

- `sections: [...]`: required Markdown headings, matched by exact text. Built into the resolver; files only.
- `lint: "<command> {path}"`: a command run from the repository root; a non-zero exit fails.
- `script: <name>`: an executable on the `PATH`, usually from a plugin's `bin/`, given the path.

A rung-7 script should say in its header which rung it would move down to if the artifact became structured.

A failed verification doesn't stop the run. `record` marks the attempt unverified, and the next `next` hands the stage out again with the errors in its brief.

## Write scope

Write scope is checked after a stage, not intercepted during it.

1. When `next` hands out a stage, the resolver records the working-tree state of every repository that the stage's `repos.write` doesn't list.
2. `record` compares against that state and refuses the attempt if any of those repositories changed.

So a person's unrelated local edits made earlier don't fail the stage.

The project's `.claude/settings.json` denies the few actions forbidden everywhere: merging pull requests, force pushes, pushes to `main`, and edits under `.github/`.

Whether write scope also needs to be intercepted during a stage, by a `PreToolUse` hook keyed on the agent, is an [open decision](decisions.md).
