# Pipelines and steps

A pipeline says what starts a run, which steps it has and in what shape, what makes each step done and who decides, and what happens at its start and end. This page explains the parts. The [pipeline reference](../reference/pipeline.md) and the [step reference](../reference/step.md) list every field.

```yaml
pipeline: story
trigger: {issue: {type: Story}}
onStart:
  - git.run-branch
  - pr.open-run: {draft: true}
steps:
  - step: spec
    gate: {human: {owner: product-owner, via: pr}}
    done: {pr: {repo: runs, state: approved}}
  - step: plan
    gate: {human: {owner: product-owner, via: prompt}}
    done: {issue: {status: Done}}
  - foreach: tasks
    onStart:
      - tracker.child.sync: {type: Task, title: "{unit.title}"}
    steps:
      - step: implement
        gate: {auto: {agent: reviewer}, retry: 2, then: human}
        done: {issue: {status: Done}}
    onEnd:
      - tracker.child.close: {type: Task}
onEnd:
  - git.sync-base
  - pr.merge
```

## Triggers

A **trigger** says what starts a run:

- `issue`: a tracker item of a type, or with a label. `/fab0:run #412` starts a run from item `#412`, and the run takes its id from the run tracker: see [run ids](#run-ids).
- `manual`: a person starts the run and names its id, optionally matching a pattern, for example `docs-1`.

A project may have several pipelines. The engine picks the one whose trigger matches the run, and asks for `--pipeline` when none or several match. A pipeline named with `--pipeline`, or a project's only pipeline once a run exists, is used without checking an issue trigger; starting from an item checks the trigger otherwise. A manual trigger's id pattern is always checked. Once a run has started, its Pipeline Run names its pipeline. A pipeline that a connected factory calls needs no issue trigger: the call opens its run.

## Run ids

A run started from an item takes its id when it starts: `/fab0:run #412` opens the item's **Pipeline Run** on the run tracker, in the runs repository, as a sub-issue of `#412`. Its issue number is the run id. Every later command reaches the run by that id, `/fab0:run 12`, or by no argument at all: a bare `/fab0:run` goes on with the only run that has work in this checkout, and asks which when several have. `#412` again goes on with the open run the item has; once that run is closed, `#412` starts another.

Every factory of a product shares the runs repository, so the id is unique across all of them. A [call](connected-factories.md)'s child run carries its parent's id. So run 12 is one piece of work everywhere: its issues on the run tracker, and its branches in every repository, `fab0/12/…`, or the child factory's own names for them.

Why not the item's number, as before 0.9: two factories sharing the runs repository, or a child factory's own runs, would have runs of the same number for different work. A manual run's id is the name a person gives; its Pipeline Run is opened on its own, with that id.

`status` and the inbox give each run its **position**, one line that says where it is: `run 12 · feature · acme/product#52 · pass 3 · at service (child acme/runs#14) | web (implement 1/2)`. A pass is one session taking the run up.

## Steps and their executors

A step is one piece of work, done by exactly one executor:

| Executor | Who does the work | Its record |
|---|---|---|
| `agent` | Any Claude Code agent, as a subagent of the session, with a brief from the engine | The agent's JSON reply |
| `action` | The engine, from fab0's [catalogue of actions](../reference/actions.md) | None: the action's check is its record |
| `command` | A shell command the session runs in the unit's worktree | Its exit code |
| `tool` | A tool the session calls, such as an MCP tool | A reply the session writes from the tool's result |

A step declares what it reads (`inputs`), what it writes (`outputs`), the repositories it may change and read (`repos`), and the paths it claims (`paths`). An agent step also names a model class and the skills the agent loads. Where the step stands in a pipeline, that pipeline gives it its gate and its `done`. See [gates](gates.md).

Steps pass state through [artifacts](artifacts.md), or through the `data` field of their reply. A later step reads `data` in its `with` arguments as `{<step>.<field>}`. Other placeholders are `{run}`, `{run.<field>}` (a field of the run's item), `{unit}` and `{unit.<field>}` (the current element of a `foreach`). An auto gate's `command` may also use `{attempt}`: the path of a local copy of the fact of the attempt it judges, so a project's own check can read the reply's `data`. The gate's own fact keeps `{attempt}`, not the path, because the path is one machine's.

## Operators

- **Sequence.** A list of nodes runs in order. Each starts when the one before it is done.
- **`foreach`.** Runs its steps once per element of a list artifact, such as a task list. Each element's steps are units of their own, with their own branches and Pipeline Steps. Elements run in parallel, as far as their order and their claims allow. An element may name the elements it comes `after`, and the paths it claims. `max` limits how many run at once.
- **`parallel`.** Named branches that run at the same time. The block is done when every branch is done. A node may name the branches or steps it comes `after`; the whole branch it is in then waits for them.
- **`when`.** Runs its steps if a condition holds, and `else` if it doesn't. A condition is a small closed language: an artifact exists, has a Markdown section or has a value; a step's gate gave a verdict; the run's item has a label, a type or a board field value. Conditions combine with `all`, `any` and `not`. What a branch that wasn't taken would have made is absent, like an unbound optional input, so a later step that reads it isn't held back.
- **`call`.** Runs a pipeline of a connected factory, another repository with a factory of its own, as a child run under this run's Pipeline Run. It binds the child's inputs to files of this run, and its gate accepts or rejects what the child hands back once the child's run is done. See [connected factories](connected-factories.md).

A block may have a gate of its own and an `id`. A `foreach` or `parallel` block may also have its own `onStart` and `onEnd` actions.

## Units

A **unit** is a step as it runs: one step, or one step for one element of a `foreach`. Its id names its branch, its Pipeline Step and its facts: `implement-T2` is the step `implement` for element `T2`. Inside a gated block, the block's id comes first: `pages--write-intro`.

Every unit has a state that the engine works out on each call: `ready`, `running`, `waiting` on a gate or a person, `blocked` with a reason, or `done`. See [dependencies and blocking](dependencies.md).

## Start and end: lifecycle actions

Every pipeline has `onStart` and `onEnd`, even if empty, because a run without a start and an end leaves branches and items behind. They hold [actions](../reference/actions.md):

- `onStart` prepares the run, for example its branch, its draft pull request and a label. `pr.open-run` opens a repository's run pull request only once its run branch has work, because GitHub opens no pull request without a change. `apply` checks it again during the run, so a repository the run changes later gets its pull request then.
- `onEnd` finishes it, for example bringing in the base branch and merging the run's pull requests (`pr.merge`) or marking them ready for a person (`pr.ready`). Nothing needs removing: what a run produces for itself is files in the runs repository, and its record is on the run tracker.

A `foreach` or `parallel` block may have its own: a `foreach`'s `onStart` typically creates a tracker item per element, and its `onEnd` closes them.

An action is done when its check passes, because its result is a fact in git or the tracker. So it writes no record, and performing it twice changes nothing. A pipeline's `onStart` stops being checked once the run has recorded work: what it did may be undone on purpose later, for example a working label its `onEnd` removes. `pr.open-run` is the exception: `apply` checks it again, and opens only pull requests that never existed, so one a person closed stays closed.

Actions that act on the whole run, such as `pr.merge`, belong in the pipeline's `onStart` or `onEnd`, not in a step, so the run's merge into the base is its end, not a step of its own.

## What `validate` refuses

`fab0-resolve validate` checks the whole factory before anything runs: every file against its schema, the connections between them, and the run tracker's issue types and fields. It refuses:

- `schema: 2` or older, with a pointer to [upgrade from 0.9](../how-to/upgrade-from-0.9.md), and keys that 0.10 removed, such as `store`, `kind: store`, `git.auto_merge` and a gate's `merge`, each with a hint that says what replaces it;
- a step or call without `done`, a `pr` definition on a step that has no pull request, `approved` without a person deciding in a pull request, and a step decided by a person in a pull request that writes no repository;
- a step used twice in one pipeline, because its Pipeline Steps and facts would collide;
- `after` outside a `parallel` block, because a sequence already orders its steps;
- a `{<step>.<field>}` placeholder that doesn't point at an earlier agent or tool step;
- an action in the wrong place, such as a run-wide action inside a block;
- a run tracker that lacks its issue types or fields. When it can't read the tracker, such as in CI with no `gh` login, it warns instead;
- a connected factory whose wiring doesn't fit a call to it. See [connected factories](connected-factories.md#what-validate-checks).

It also refuses, until a factory needs them, a `foreach` inside a `foreach`, a call inside a `foreach`, a called pipeline that calls another factory itself, and a call's gate that is a command.
