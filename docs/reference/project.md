# Project file: `.fab0/fab0.yaml`

The one project file, in the home repo. It names the repositories, the people, the tracker, the git policy, the model classes and the pipelines of a factory. The schema is `plugins/fab0/schemas/project.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core); when this page and the schema disagree, the schema is right.

```yaml
schema: 2
repos:
  home:    {path: ., github: acme/product, owner: product-owner}
  backend: {path: ../backend, github: acme/backend, owner: backend}
people:
  product-owner: {github: [po-user]}
  backend:       {github: [be-user]}
tracker: {kind: github, owner: acme, project: 7, fields: {signal: fab0}}
git:
  base: main
  branching: run
  auto_merge: {into: [run]}
parallel: {max: 3, cross_run: warn}
ledger: {path: "work/{run}/ledger"}
models:
  claude-code: {deep: opus, balanced: sonnet, fast: haiku}
profiles:
  cheap: {models: {claude-code: {deep: sonnet}}}
pipelines: [story]
```

## Top level

| Field | Required | Meaning |
|---|---|---|
| `schema` | yes | `2`. The engine refuses other versions |
| `repos` | yes | The repositories the factory reads and writes, by name. See below |
| `people` | no | Roles, each mapped to tracker users |
| `tracker` | no | Where runs, human decisions and dependencies are tracked. Without it, a factory has manual triggers only |
| `git` | no | The git workflow |
| `parallel` | no | Limits and policy for parallel units |
| `ledger` | no | Where ledger entries go |
| `pipelines` | yes | The names of the pipelines, each a file in `.fab0/pipelines/` |
| `models` | yes | Model classes, per harness |
| `profiles` | no | Changes to this file, chosen at run time |

Names of repositories, roles, pipelines, model classes and profiles are lowercase letters, digits and hyphens, starting with a letter.

## `repos`

One entry per repository. `home` is required: it holds `.fab0/`. A repository can't be named `all`, `unit` or `run`, which have a meaning in steps.

| Field | Required | Meaning |
|---|---|---|
| `path` | yes | The checkout's path, relative to the home repo, for example `../backend`. Every machine that runs fab0 has the same sibling layout |
| `github` | yes | The repository on GitHub, as `owner/name` |
| `owner` | no | The role whose turn a human gate in this repository is |
| `key` | no | **Planned:** a short key of two or three capital letters, for unit names that span repositories. `validate` checks that keys are unique; nothing uses them yet |
| `base` | no | The base branch, if not `git.base` |

## `people`

Each role maps to its users:

| Field | Required | Meaning |
|---|---|---|
| `github` | yes | The role's GitHub logins, at least one |

## `tracker`

| Field | Required | Meaning |
|---|---|---|
| `kind` | yes | `github` |
| `owner` | no | The organisation or user that owns the issues and the project |
| `project` | no | A GitHub Projects number, if the factory shows its state on a board |
| `fields` | no | Board field names, by purpose: `{<purpose>: <field name>}`. `tracker.field` actions and `when` conditions use the purposes. `signal` is special: a text field where `apply` shows where the run's item and each element's item are |

## `git`

A pipeline may override `branching` and `auto_merge` in its own `git`.

| Field | Default | Meaning |
|---|---|---|
| `base` | `main` | The base branch |
| `branching` | `run` | `run`: the run works on a run branch, each unit on a sub-branch whose pull request targets its parent, and only the run's pull request reaches the base branch. `flat`: each unit's pull request targets the base branch |
| `branches` | | Branch name templates: `run` (default `fab0/{run}/base`, must contain `{run}`) and `unit` (default `fab0/{run}/{unit}`, must contain `{unit}`) |
| `auto_merge` | into run branches | Where an auto gate with `merge: auto` may merge: `into`, a list of `run` and `base`. Merging into the base branch also needs `allow_base: true` |

## `parallel`

| Field | Default | Meaning |
|---|---|---|
| `max` | no limit | Units of one run that may run at once |
| `cross_run` | `warn` | What an overlap of claims with another open run does: `warn`, or `block` |

## `ledger`

| Field | Default | Meaning |
|---|---|---|
| `path` | `work/{run}/ledger` | Where ledger entries go, in the repository a unit ran in. Must contain `{run}` |
| `branch` | | A branch for the ledger of runs that open no pull request, such as a pipeline whose artifacts all live in the tracker. It is pushed, never merged. Required when no step of a pipeline writes files |

## `models`

Model classes, per harness. `claude-code` is required: `{<class>: <model>}`, for example `{deep: opus, balanced: sonnet, fast: haiku}`. Steps and gates ask for a class, so one change here moves every step.

## `profiles`

Named changes to this file, applied as a JSON Merge Patch when a command is given `--profile <name>`. For example, `cheap: {models: {claude-code: {deep: sonnet}}}` runs the deep steps on a cheaper model.
