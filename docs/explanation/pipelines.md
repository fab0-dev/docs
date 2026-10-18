# Pipelines and steps

A pipeline says what starts a run, which steps it has and in what shape, and what happens at its start and end. This page explains the parts. The [pipeline reference](../reference/pipeline.md) and the [step reference](../reference/step.md) list every field.

```yaml
pipeline: story
trigger: {issue: {type: Story}}
onStart:
  - git.run-branch
  - pr.open-run: {draft: true}
steps:
  - step: spec
    gate: {human: {owner: product-owner}}
  - foreach: tasks
    onStart:
      - tracker.child.sync: {type: Task, title: "{unit.title}"}
    steps:
      - step: implement
        gate: {auto: {agent: reviewer}, merge: auto}
    onEnd:
      - tracker.child.close: {type: Task}
onEnd:
  - git.sync-base
  - pr.ready
```

## Triggers

A **trigger** says what starts a run and what its id is:

- `issue`: a tracker item of a type, or with a label. The run id is the item's number, so `/fab0:run 412` runs item `#412`.
- `manual`: a person starts the run and names its id, optionally matching a pattern, for example `docs-1`.

A project may have several pipelines. The engine picks the one whose trigger matches the run, and asks for `--pipeline` when none or several match. A project's only pipeline, or one named with `--pipeline`, is used without checking an issue trigger; a manual trigger's id pattern is always checked.

## Steps and their executors

A step is one piece of work, done by exactly one executor:

| Executor | Who does the work | Its record |
|---|---|---|
| `agent` | Any Claude Code agent, as a subagent of the session, with a brief from the engine | The agent's JSON reply |
| `action` | The engine, from fab0's [catalogue of actions](../reference/actions.md) | None: the action's check is its record |
| `command` | A shell command the session runs in the unit's worktree | Its exit code |
| `tool` | A tool the session calls, such as an MCP tool | A reply the session writes from the tool's result |

A step declares what it reads (`inputs`), what it writes (`outputs`), the repositories it may change and read (`repos`), and the paths it claims (`paths`). An agent step also names a model class and the skills the agent loads.

Steps pass state through [artifacts](artifacts-and-ledger.md), or through the `data` field of their reply. A later step reads `data` in its `with` arguments as `{<step>.<field>}`. Other placeholders are `{run}`, `{run.<field>}` (a field of the run's tracker item), `{unit}` and `{unit.<field>}` (the current element of a `foreach`). An auto gate's `command` may also use `{attempt}`: the path of a YAML file that holds the ledger entry of the attempt it judges, so a project's own check can read the reply's `data`. The gate's own ledger entry keeps `{attempt}`, not the path, because the path is one machine's.

## Operators

- **Sequence.** A list of nodes runs in order. Each starts when the one before it is done.
- **`foreach`.** Runs its steps once per element of a list artifact, such as a task list. Each element's steps are units of their own, with their own branches. Elements run in parallel, as far as their order and their claims allow. An element may name the elements it comes `after`, and the paths it claims. `max` limits how many run at once.
- **`parallel`.** Named branches that run at the same time. The block is done when every branch is done. A node may name the branches or steps it comes `after`; the whole branch it is in then waits for them.
- **`when`.** Runs its steps if a condition holds, and `else` if it doesn't. A condition is a small closed language: an artifact exists, has a Markdown section or has a value; a step's gate gave a verdict; the run's tracker item has a label, a type or a board field value. Conditions combine with `all`, `any` and `not`.
- **`call`.** Runs a pipeline of a connected factory, another repository with a factory of its own, as a child run. It binds the child's inputs to artifacts of this run, receives the outputs it takes, acknowledges each one by its gate, and is done once every output it waits for is accepted. See [connected factories](connected-factories.md).

A block may have a gate of its own and an `id`. A `foreach` or `parallel` block may also have its own `onStart` and `onEnd` actions.

## Units

A **unit** is a step as it runs: one step, or one step for one element of a `foreach`. Its id names its branch and its ledger entries: `implement-T2` is the step `implement` for element `T2`. Inside a gated block, the block's id comes first: `pages--write-intro`.

Every unit has a state that the engine works out on each call: `ready`, `running`, `waiting` on a gate, `blocked` with a reason, or `done`. See [dependencies and blocking](dependencies.md).

## Start and end: lifecycle actions

Every pipeline has `onStart` and `onEnd`, even if empty, because a run without a start and an end leaves branches and items behind. They hold [actions](../reference/actions.md):

- `onStart` prepares the run, for example its branch, its draft pull request and a label. `pr.open-run` opens a repository's run pull request only once its run branch has work, because GitHub opens no pull request without a change. `apply` checks it again during the run, so a repository the run changes later gets its pull request then.
- `onEnd` finishes it, for example bringing in the base branch and marking the pull request ready. Nothing needs removing: what a run produces for itself is in the run store, not in a repository.

A `foreach` or `parallel` block may have its own: a `foreach`'s `onStart` typically creates a tracker item per element, and its `onEnd` closes them.

An action is done when its check passes, because its result is a fact in git or the tracker. So it writes no record, and performing it twice changes nothing. A pipeline's `onStart` stops being checked once the run has recorded work: what it did may be undone on purpose later, for example a working label its `onEnd` removes. `pr.open-run` is the exception: `apply` checks it again, and opens only pull requests that never existed, so one a person closed stays closed.

## What `validate` refuses

`fab0-resolve validate` checks the whole factory before anything runs: every file against its schema, and the connections between them. It refuses:

- a step used twice in one pipeline, because its ledger entries would collide;
- `after` outside a `parallel` block, because a sequence already orders its steps;
- a `{<step>.<field>}` placeholder that doesn't point at an earlier agent or tool step;
- an action in the wrong place, such as a run-wide action inside a block;
- a run store it can't reach, because every run records there;
- a connected factory whose wiring doesn't fit a call to it: another runs repository or tracker, a missing pipeline, input or output, or a format that differs. It reads that factory's `.fab0/` at its base branch, as its own engine does;
- `ledger`, `keep` and `git.remove-run-artifacts` from fab0 0.6, with a hint that says what replaces each.

It also refuses, until a factory needs them, a `foreach` inside a `foreach`, a called pipeline that calls another factory itself, and a call's gate that is a command or a label.
