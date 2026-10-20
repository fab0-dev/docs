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
store: {github: acme/product-runs}
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
| `factories` | no | Connected factories: other repositories with a factory of their own, whose pipelines this factory calls. See below |
| `people` | no | Roles, each mapped to tracker users |
| `tracker` | no | Where runs, human decisions and dependencies are tracked. Without it, a factory has manual triggers only |
| `git` | no | The git workflow |
| `parallel` | no | Limits and policy for parallel units |
| `store` | yes | The run store: the runs repository that holds what runs produce for themselves. See below |
| `tracking` | no | The run tracker: an issue for each run and each of its steps, whose fields carry the run's state. See below |
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

## `factories`

A connected factory is another repository with its own `.fab0/`, agents and people. A [`call`](pipeline.md#call) in this factory's pipelines starts a run of one of its pipelines, as a child run. This factory never writes a connected factory's repositories, so none of them is also in `repos`: `validate` refuses one that is. For how calls work, see [connected factories](../explanation/connected-factories.md).

```yaml
factories:
  service: {github: acme/service, path: ../service, owner: service-developer}
  web:     {github: acme/web, path: ../web, owner: web-developer}
```

| Field | Required | Meaning |
|---|---|---|
| `github` | yes | Its home repository on GitHub, as `owner/name`. A call files the child run's item there |
| `path` | no | Its checkout, relative to the home repo. `validate` reads its wiring there, and a call needs it to start a child run. Without it, `validate` warns that the connection isn't checked |
| `base` | no | The branch its wiring is read at. Default `main`: what its own engine reads |
| `owner` | no | The role whose turn it is while the child run works |

`validate` checks each connection, reading the connected factory's `.fab0/` at its base branch: its wiring is valid; it uses this factory's runs repository, under a `store.project` of its own; it uses the same tracker kind and owner; its home repository is the one `github` names; and each call fits its pipeline. `validate` lists each connected factory under `factories`, with `checked` and, when it couldn't check, `why`.

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
| `auto_merge` | `{into: [run]}` | Where `apply` may merge without a person: `into`, a list of `run` and `base`, and `allow_base`. `validate` requires `run` in `into` for every `merge: auto` gate under `run` branching and for every one inside a gated block, whatever the branching; for any other `merge: auto` gate under `flat`, it requires `base`. `into: [base]` with `allow_base: true` covers every merge into the base branch: a unit with gate `none`, a label-decided human gate or `merge: auto` whose parent is the base branch (under `flat` branching), and `pr.merge`. Without both, a person merges into the base branch: a unit's pull request that targets it waits for a person, and `pr.merge` is refused. Units inside a gated block merge into the block's branch, so the base-branch rule does not hold them. |

## `parallel`

| Field | Default | Meaning |
|---|---|---|
| `max` | no limit | Units of one run that may run at once |
| `cross_run` | `warn` | What an overlap of claims with another open run does: `warn`, or `block` |

## `store`

The run store is a git repository, the **runs repository**, that holds what runs produce for themselves: each run's ledger, its store artifacts, and the review pull requests of units whose outputs are all in the store. Your product repositories then receive only product changes. One runs repository serves every factory of a product, each in its own folder, `runs/<project>/`. Its root holds the [register](ledger.md#the-register), which gives every run started from an item an id that no other factory's run has. fab0 alone writes it: people review its pull requests, and an approving review is the decision, which `apply` records before it merges. Give `github`, `path`, or both.

| Field | Required | Meaning |
|---|---|---|
| `github` | one of the two | The runs repository on GitHub, as `owner/name`, for example `acme/product-runs`. The engine reaches it over the same protocol as the home repo's `origin` |
| `project` | no | This factory's folder in the runs repository, `runs/<project>/`. Default: the home repository's name on GitHub, so `acme/docs` keeps its runs under `runs/docs/` |
| `path` | one of the two | A checkout of the runs repository, relative to the home repo. Without it, the engine keeps its own clone in `<home git dir>/fab0/store`. With `path` and no `github`, the store is a local repository, as in tests |

`validate` checks that the store can be reached: through its checkout's `origin`, else through `github`. A store it can't reach is invalid wiring. A store with no remote is local, and one with no checkout yet is started by its first write. The `fab0:github` skill creates the runs repository and its ruleset; see [set up GitHub](../how-to/github-setup.md).

fab0 0.6's `ledger` block (`path` and `branch`) is gone: `validate` refuses it, with a hint to use `store`.

## `tracking`

The run tracker keeps each run as an issue, and each of its units (a step, a foreach element, a call) as a sub-issue of it. The issues' fields carry the run's state between steps and between factories, and their comments are its log. A root run's id is its issue's number, and a child run is a sub-issue of its parent's run with the parent's Run ID. fab0 0.10 runs on it; in this release `validate` checks it, and runs don't use it yet.

The first kind is `github`: issues of two issue types of the organization, with its native Issue Fields, in one repository that every factory of a product shares. An organization admin creates the types and fields once, under Settings → Planning, and pins each field to the types that carry it.

```yaml
tracking:
  kind: github
  github: acme/product-runs
```

| Field | Required | Meaning |
|---|---|---|
| `kind` | yes | `github` |
| `github` | yes | The repository that holds the runs' issues, as `owner/name` |
| `types` | no | The issue types, by `run` and `step`. Default: `Pipeline Run`, `Pipeline Step` |
| `fields` | no | The issue fields' names, by what they hold. Default: the table below |
| `status` | no | The values of the status field, by state: `todo`, `in_progress`, `done`, and any more a factory adds, such as `blocked`. Default: `Todo`, `In Progress`, `Done` |

| Field | Default name | Type | On | Holds |
|---|---|---|---|---|
| `run_id` | Run ID | text | run, step | The root run's number |
| `status` | Stage | single select | run, step | The state: the values of `status`. GitHub reserves the name Status |
| `pipeline` | Pipeline | text | run | The pipeline the run runs |
| `factory` | Factory | text | run | The factory whose run it is |
| `step` | Step | text | run, step | On a run, its steps in progress; on a step, its unit |
| `waiting` | Waiting on | text | run, step | The `@login` or role it waits on |
| `revision` | Revision | number | step | The step's attempt, raised on each rework |
| `output` | Output | text | step | The step's pull request in review, then the commit it was accepted at |

`validate` reads the organization's issue types and fields. A missing or disabled type, a missing field, a field of another type, or a status value the field has no option for is invalid wiring. A field that isn't pinned to a type that carries it is a warning, since GitHub then shows it only on demand.

## `models`

Model classes, per harness. `claude-code` is required: `{<class>: <model>}`, for example `{deep: opus, balanced: sonnet, fast: haiku}`. Steps and gates ask for a class, so one change here moves every step.

## `profiles`

Named changes to this file, applied as a JSON Merge Patch when a command is given `--profile <name>`. For example, `cheap: {models: {claude-code: {deep: sonnet}}}` runs the deep steps on a cheaper model.
