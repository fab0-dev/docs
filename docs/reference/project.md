# Project file: `.fab0/fab0.yaml`

The one project file, in the home repo. It names the repositories, the people, the tracker, the git policy, the model classes and the pipelines of a factory. The schema is `plugins/fab0/schemas/project.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core); when this page and the schema disagree, the schema is right.

```yaml
schema: 3
repos:
  home:    {path: ., github: acme/product, owner: product-owner}
  backend: {path: ../backend, github: acme/backend, owner: backend}
  runs:    {path: ../product-runs, github: acme/product-runs}
people:
  product-owner: {github: [po-user]}
  backend:       {github: [be-user]}
tracker: {kind: github, owner: acme, project: 7, fields: {signal: fab0}}
git:
  base: main
  branching: run
parallel: {max: 3, cross_run: warn}
tracking: {kind: github, github: acme/product-runs}
models:
  claude-code: {deep: opus, balanced: sonnet, fast: haiku}
profiles:
  cheap: {models: {claude-code: {deep: sonnet}}}
pipelines: [story]
```

## Top level

| Field | Required | Meaning |
|---|---|---|
| `schema` | yes | `3`. The engine refuses other versions: for `schema: 2`, the wiring of fab0 0.6 to 0.9, it points to the [upgrade notes](../how-to/upgrade-from-0.9.md) |
| `repos` | yes | The repositories the factory reads and writes, by name, the runs repository among them. See below |
| `factories` | no | Connected factories: other repositories with a factory of their own, whose pipelines this factory calls. See below |
| `people` | no | Roles, each mapped to GitHub users |
| `tracker` | no | The tracker of work items: the issues that start runs, such as Stories, their sub-issues, labels and board fields. Without it, a factory has manual triggers only |
| `git` | no | The git workflow |
| `parallel` | no | Limits and policy for parallel units |
| `tracking` | no | The run tracker: an issue for each run and each of its units, whose fields carry the run's state. A run needs it: `start` refuses to start one without it. See below |
| `pipelines` | yes | The names of the pipelines, each a file in `.fab0/pipelines/` |
| `models` | yes | Model classes, per harness |
| `profiles` | no | Changes to this file, chosen at run time |

Names of repositories, roles, pipelines, model classes and profiles are lowercase letters, digits and hyphens, starting with a letter.

`validate` refuses the `store` and `ledger` blocks of earlier releases, with a hint: a run's facts are on the run tracker, and what it produces for itself are files in the runs repository.

## `repos`

One entry per repository. `home` is required: it holds `.fab0/`. A repository can't be named `all`, `unit` or `run`, which have a meaning in steps.

The runs repository is an ordinary entry, such as `runs` above, for a factory that keeps files there: its specs, its task lists, and the files its calls exchange. Steps write it like any other repository, so your product repositories receive only product changes. It is usually the repository that `tracking.github` names too.

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
| `github` | yes | Its home repository on GitHub, as `owner/name`. Its name is the connected factory's name on the run tracker, the `Factory` of its runs |
| `path` | no | Its checkout, relative to the home repo. `validate` reads its wiring there, and a call needs it to start a child run. Without it, `validate` warns that the connection isn't checked |
| `base` | no | The branch its wiring is read at. Default `main`: what its own engine reads |
| `owner` | no | The role whose turn it is while the child run works |

A call opens the child run as a Pipeline Run under this run's, on the run tracker they share; it makes no issue in the connected factory's repository. `validate` checks each connection, reading the connected factory's `.fab0/` at its base branch:

- its wiring is valid;
- its name, its home repository's name, isn't this factory's;
- it uses this factory's run tracker: the same `tracking.kind` and `tracking.github`;
- its home repository is the one `github` names;
- where it lists a repository this factory lists too, it names its branches apart from this factory's with `git.branches`, since a child run has its parent's run id; two connected factories that share a repository name their branches apart from each other too;
- each call fits the called pipeline: the pipeline exists and calls no factory itself, the call binds only its inputs and all of its required ones, takes only its outputs in the same format, and every file they exchange is in a repository both factories list.

`validate` lists each connected factory under `factories`, with `checked` and, when it couldn't check, `why`.

## `people`

Each role maps to its users:

| Field | Required | Meaning |
|---|---|---|
| `github` | yes | The role's GitHub logins, at least one |

## `tracker`

The tracker of work items: the issues people file, such as Stories and Features, that start runs and that runs read, label and close. It is a different thing from the [run tracker](#tracking), which holds the runs themselves.

| Field | Required | Meaning |
|---|---|---|
| `kind` | yes | `github` |
| `owner` | no | The organisation or user that owns the issues and the project |
| `project` | no | A GitHub Projects number, if the factory shows its state on a board |
| `fields` | no | Board field names, by purpose: `{<purpose>: <field name>}`. `tracker.field` actions and `when` conditions use the purposes. `signal` is special: a text field where `apply` shows where the run's item and each element's item are: `done`, or the first unit that isn't and why |

## `git`

A pipeline may override `branching` in its own `git`.

| Field | Default | Meaning |
|---|---|---|
| `base` | `main` | The base branch |
| `branching` | `run` | `run`: the run works on a run branch, each unit on a sub-branch whose pull request targets its parent, and only the run's pull request reaches the base branch. `flat`: each unit's pull request targets the base branch |
| `branches` | | Branch name templates: `run` (default `fab0/{run}/base`, must contain `{run}`) and `unit` (default `fab0/{run}/{unit}`, must contain `{unit}`). Connected factories that share a repository need templates of their own, such as `{run: "service/{run}/base", unit: "service/{run}/{unit}"}`, because a child run has its parent's run id |

Who merges is no setting here: it follows each step's gate and `done`. See [`gate`](pipeline.md#gate) and [`done`](pipeline.md#done). fab0 0.9's `git.auto_merge`, with `into` and `allow_base`, is gone, and `validate` refuses it with a hint.

## `parallel`

| Field | Default | Meaning |
|---|---|---|
| `max` | no limit | Units of one run that may run at once |
| `cross_run` | `warn` | What an overlap of claims with another open run does: `warn`, or `block` |

## `tracking`

The run tracker keeps each run as an issue, a Pipeline Run, and each of its units (a step, a foreach element, a call) as a Pipeline Step sub-issue of it. The issues' fields carry the run's state between steps and between factories, and their comments are its log: each attempt, gate decision and claim is one comment. A root run's id is its Pipeline Run's number, and a child run is a sub-issue of its parent's run with the parent's Run ID. For the issues, their lifecycle and the facts on their comments, see [the run tracker](tracker.md).

The first kind is `github`: issues of two issue types of the organization, with its native Issue Fields, in one repository that every factory of a product shares, so run ids are unique across them. An organization admin creates the types and fields once, under Settings → Planning, and pins each field to the types that carry it. The `fab0:github` skill checks the runs repository; see [set up GitHub](../how-to/github-setup.md).

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
| `run_id` | Run ID | text | run, step | The run id: the root run's number, or the id a person gave a manual run |
| `status` | Stage | single select | run, step | The state: the values of `status`. GitHub reserves the name Status |
| `pipeline` | Pipeline | text | run | The pipeline the run runs |
| `factory` | Factory | text | run | The factory whose run it is |
| `step` | Step | text | run, step | On a run, its steps in progress; on a step, its unit |
| `waiting` | Waiting on | text | run, step | The `@login` or role it waits on |
| `revision` | Revision | number | step | The step's attempt, raised on each rework |
| `output` | Output | text | step | The step's pull request in review, then the commit it was accepted at |

`validate` reads the organization's issue types and fields. A missing or disabled type, a missing field, a field of another type, or a status value the field has no option for is invalid wiring. A field that isn't pinned to a type that carries it is a warning, since GitHub then shows it only on demand. A tracker `validate` can't read, with no `gh` login or no network, is a warning too: it isn't checked.

## `models`

Model classes, per harness. `claude-code` is required: `{<class>: <model>}`, for example `{deep: opus, balanced: sonnet, fast: haiku}`. Steps and gates ask for a class, so one change here moves every step.

## `profiles`

Named changes to this file, applied as a JSON Merge Patch when a command is given `--profile <name>`. For example, `cheap: {models: {claude-code: {deep: sonnet}}}` runs the deep steps on a cheaper model.
