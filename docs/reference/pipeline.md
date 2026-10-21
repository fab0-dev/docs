# Pipeline: `.fab0/pipelines/<name>.yaml`

A tree of steps and operators, with a gate on every transition and actions when the run starts and ends. Every step and call says what makes it done. The schema is `plugins/fab0/schemas/pipeline.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For how the parts work together, see [pipelines and steps](../explanation/pipelines.md) and [gates](../explanation/gates.md).

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
    id: tasks
    onStart:
      - tracker.child.sync: {type: Task, title: "{unit.title}"}
    steps:
      - step: implement
        gate: {auto: {agent: reviewer, model: deep}, retry: 2, then: human}
        done: {issue: {status: Done}}
    onEnd:
      - tracker.child.close: {type: Task}
onEnd:
  - git.sync-base
  - pr.merge
```

## Top level

| Field | Required | Meaning |
|---|---|---|
| `pipeline` | yes | Its name, the same as the file's |
| `trigger` | yes | What starts a run, and what its id is. See below |
| `git` | no | `branching`: overrides the project's [`git.branching`](project.md#git) for this pipeline |
| `onStart` | yes | Actions when the run starts, in order. `[]` for none |
| `steps` | yes | The nodes of the pipeline, in order |
| `onEnd` | yes | Actions when the run's steps are done, in order. `[]` for none |
| `inputs` | no | What a caller may bind, when another factory calls this pipeline. See below |
| `outputs` | no | What this pipeline can hand back to a caller: files its steps write. See below |

fab0 0.9's ways of saying who merges, `git.auto_merge` in a pipeline and a gate's `merge`, are gone: `validate` refuses them with a hint. Who merges follows each step's [gate](#gate) and [`done`](#done).

## `trigger`

Exactly one of:

| Field | Meaning |
|---|---|
| `issue` | A work item of the [tracker](project.md#tracker) starts a run: `/fab0:run #<n>` opens the run's Pipeline Run, a sub-issue of the item, and the run's id is that issue's number. Give `type` (an issue type, such as `Story`), `label`, or both. One type or label starts one pipeline only |
| `manual` | A person starts the run and names its id. `id` is a regular expression the id must match, for example `^docs-`. The run's Pipeline Run has that id as its Run ID |

A call's child run has its parent's id, whatever its trigger, and no work item: the call opens its Pipeline Run. See [the run tracker](tracker.md).

## `inputs` and `outputs`

A pipeline that another factory may [call](#call) declares what the caller may pass in and what it can hand back. For how they are used, see [connected factories](../explanation/connected-factories.md).

```yaml
inputs:
  spec: {default: request}
  upstream: {optional: true}
outputs: [contract, feedback]
```

`inputs` maps each input to how it is read. An input is a `file` [artifact](artifact.md) of this factory that names only its format, `file: {format: ...}`, and that no step of the pipeline writes. Steps read it like any other artifact:

| Field | Meaning |
|---|---|
| `default` | The artifact read when no caller binds the input, as when the pipeline runs on its own, for example the run's own item |
| `optional` | `true`: the input may stay unbound, and a step that reads it goes ahead without it |

A bound input is read where the caller's producer wrote it, at the commit of that producer's latest attempt. When the caller binds a file one of its own calls receives, the steps that read it wait until that call has accepted it. An input with no binding, no `default`, and not `optional` holds the steps that read it, as `data`.

`outputs` lists files this pipeline's steps write, at a location of their own (`repo` and `path`). A caller reads each one it takes where it was written, so it must be in a repository both factories list, such as the runs repository.

## Actions

`onStart` and `onEnd` are lists of [actions](actions.md). An action is its name, or a one-key map from its name to its arguments:

```yaml
onStart:
  - git.run-branch
  - pr.open-run: {draft: true}
```

Under `run` branching, `onStart` must have `git.run-branch`, which creates the run branch. A run's merge into the base branch is an action of `onEnd`, not a step:

- `pr.merge`: `apply` merges each run pull request into the base branch through GitHub, once its required checks pass;
- `pr.ready`: `apply` marks each run pull request ready, and a person merges it.

## Nodes

A node is one of:

- a step's name, for `.fab0/steps/<name>.yaml`; since such a node has no `done`, `validate` refuses it, and you write it as a step node, `{step: <name>, done: ...}`;
- a step node;
- a `foreach`, `parallel`, `when` or `call` block.

A step appears once in a pipeline, and an `id` once.

### Step node

| Field | Required | Meaning |
|---|---|---|
| `step` | yes | The step's name. With only `step`, `gate`, `done` and `after`, the step is `.fab0/steps/<step>.yaml`. With an executor (`agent`, `action`, `command` or `tool`), the step is defined here, with the fields of a [step file](step.md) |
| `gate` | no | The gate after the step. See below |
| `done` | yes | What makes the step done. The schema allows leaving it out; `validate` refuses a step without one. See below |
| `after` | no | Inside a `parallel` block: the steps, blocks or branches that must be done first. The whole branch this node is in waits for them |

### `foreach`

| Field | Required | Meaning |
|---|---|---|
| `foreach` | yes | A list artifact, a `yaml` or `json` file, or a list inside one (`tasks.items`). Its steps run once per element |
| `id` | no | The block's name, used in its units' ids when it has a gate. Default `foreach-<position>` |
| `max` | no | Units of this block that may run at once, per step |
| `onStart` | no | Actions before the block's units start, such as `tracker.child.sync` |
| `steps` | yes | The nodes to run for each element |
| `onEnd` | no | Actions once every element's units are done, such as `tracker.child.close` |
| `gate` | no | A gate on the block as a whole |
| `after` | no | As for a step node |

A `foreach` inside a `foreach` is **Planned**: `validate` refuses it.

### `parallel`

| Field | Required | Meaning |
|---|---|---|
| `parallel` | yes | Two or more named branches, each a list of nodes. The block is done when every branch is done |
| `id` | no | The block's name. Default `parallel-<position>` |
| `onStart` | no | Actions before the branches start |
| `onEnd` | no | Actions once every branch is done |
| `gate` | no | A gate on the block as a whole |
| `after` | no | As for a step node |

### `when`

| Field | Required | Meaning |
|---|---|---|
| `when` | yes | A condition. See below |
| `id` | no | The block's name. Default `when-<position>` |
| `steps` | yes | The nodes to run if the condition holds |
| `else` | no | The nodes to run if it doesn't |
| `gate` | no | A gate on the block as a whole |
| `after` | no | As for a step node |

An output that only the branch not taken writes is absent, not missing: a step that reads it goes ahead without it, as with an unbound optional input.

### `call`

Runs a pipeline of a [connected factory](project.md#factories) as a child run. It opens the child's Pipeline Run as a sub-issue of this run's, with a `call` comment that holds the bindings, where the child reads each bound file, and the formats the call accepts; it makes no issue in the child's repository. Then it waits while the child run works, and its gate accepts or rejects what the child hands back. See [connected factories](../explanation/connected-factories.md).

```yaml
- call: {factory: service, pipeline: delivery}
  id: service
  inputs: {spec: spec}
  outputs: {contract: contract, feedback: service-feedback}
  gate: {auto: {agent: acceptor, model: deep}}
  done: {issue: {run: child, status: Done}}
```

| Field | Required | Meaning |
|---|---|---|
| `call` | yes | `factory`: a connected factory from `factories`; and `pipeline`: one of its pipelines |
| `id` | no | The call's name, in its units' ids. Default `call-<factory>` |
| `inputs` | no | Per child input, the artifact of this factory bound to it. It may be a file another call receives: the child's steps that read it wait until this run has accepted it |
| `outputs` | no | Per child output this factory takes, the `file` artifact of this factory that receives it, which names only its format: that, with its `schema` and its `verify` sections, is the format the call accepts, and the child checks its output against it when it writes it. Or `artifact` and `optional: true`, for an output the call doesn't wait for |
| `gate` | no | What decides on what the child hands back, once its run is done. See below |
| `done` | yes | `{issue: {run: child, status: <value>}}`: the call waits until the child's Pipeline Run reaches that status. `validate` refuses a call without it |
| `after` | no | As for a step node |

Once the child's run reaches its `status`, the call's gate decides:

- `none` (default): accepts every output in the accepted format;
- `auto` with an `agent`: an acceptor judges what the child handed back against what the call accepts, and returns a [verdict](returns-and-verdicts.md#verdict);
- `human`, `via: issue`: the owner sets the call's own Pipeline Step to `Done`;
- `human`, `via: prompt`: the owner confirms in the run session with `fab0-resolve confirm <run> <unit>`, or rejects with `--reject <text>`.

A rejection goes to the child run as a `rejected-<n>` comment on its Pipeline Run, which `apply` opens again. The child's units that wrote the rejected outputs rework with the findings, up to their own gate's `retry`, then its `then`. A non-optional output the child didn't hand back blocks the call.

**Planned**, until a run needs them; `validate` refuses:

- a call's `auto` gate with a `command`, and a call's gate with `retry` or `then`, since the child's own gates decide what follows a rejection;
- a call's `human` gate via `pr` or `label`;
- a called pipeline that calls another factory itself;
- a second call to one factory in a pipeline, and a call in a `foreach`, since a child run has its parent's id;
- a call without a `tracker` in `fab0.yaml`.

## `done`

What makes a step or a call done: exactly one of `pr` and `issue`. `validate` requires one on every step and call. When it holds, `apply` sets the unit's Pipeline Step to `Done` and closes it, and the units after it can start. Strings may use `{run}` and `{step}`.

```yaml
done: {pr: {repo: runs, state: approved}}
```

`pr`: a pull request reaches a state.

| Field | Required | Meaning |
|---|---|---|
| `repo` | no | Where the pull request is: a key of `repos`, the runs repository's too. Default: the repository the step writes first |
| `head` | no | The pull request's branch. Default: the step's own branch |
| `state` | yes | `merged`: it is merged. `approved`: the gate's owner approved its head, with an approving review or a comment whose first line is `/approve` (or `/approved`), and `apply` merges it |

A step with `done: pr` must have a pull request: it writes a repository, or a file in one. An action step has none. `approved` needs a `human` gate via `pr`. A pull request named by `head`, or in another repository than the step's, holds once it is merged.

`issue`: an issue reaches a status.

| Field | Required | Meaning |
|---|---|---|
| `status` | yes | A value of the run tracker's status field ([`tracking.status`](project.md#tracking)), such as `Done`, or `closed` for the issue's own state |
| `run` | no | `child`: the call's child run. Required on a call, and only there |
| `repo` | with `type` | For a named issue: a key of `repos`, where the issue is |
| `type` | with `repo` | For a named issue: its issue type |
| `fields` | no | For a named issue: issue field names, and the values that tell this run's issue, such as `{Run ID: "{run}"}` |

With only `status`, the issue is the step's own Pipeline Step, which `apply` sets `Done` once the step's work is in. An action step has no Pipeline Step: its action's check decides, and its `done` is a formality `validate` asks for. A named issue is one or the other: the child run, or `repo`, `type` and `fields`.

## `gate`

One of:

- `none` (default): the work moves on, and `apply` merges it;
- `human`: a person decides, via `pr`, as below;
- a map with `human`;
- a map with `auto`.

A gate alone says who decides. Who merges a step's pull request follows its gate and its `done`: `apply` merges what a gate `none` or an approving `auto` gate lets through, what a person decided by label, issue or prompt, and what the gate's owner approved for `done: {pr: {state: approved}}`. A person merges where the step's `done` is `{pr: {state: merged}}`, and where a `human` gate via `pr` has any other `done`.

A human gate:

| Field | Meaning |
|---|---|
| `owner` | The role whose turn it is. Default: the step's `owner`, else the owner of the repository its pull request is in |
| `via` | How the owner decides. `pr` (default): on the unit's pull request, as its `done` says: by approving it (`approved`) or merging it (`merged`). `issue`: by setting the step's Pipeline Step `Done`. `prompt`: by confirming in the run session, with `fab0-resolve confirm <run> <unit>`, with no pull request; `--reject <text>` asks for changes instead, and the step reworks with those words. `label`: by adding `label` to the run's item, or to a child run's Pipeline Run |
| `label` | The label, with `via: label` |

`via: issue` and `via: prompt` decide without a pull request, so the step's `done` is `{issue: {status: ...}}`, and they need `tracking` in `fab0.yaml`. `via: label` needs a `tracker`. A step a person decides via `pr` must have a pull request: its outputs are files in a repository, the runs repository among them.

An auto gate:

| Field | Meaning |
|---|---|
| `auto` | Either an agent, with `agent` (any Claude Code agent), `model` (a model class), `skills` and `instructions`, or a `command` whose exit code decides. A command may use `{attempt}`, the path of a file that holds the attempt it judges |
| `retry` | Re-runs of the producing step after a reject. Default 2 |
| `then` | What happens when the retries run out: `human` (default), where a person decides, or `fail`, where the unit is blocked |

When an auto gate approves, `apply` merges the unit's pull request once its required checks pass. An agent that escalates hands the gate to a person.

A gate on a block judges the block's units together: they merge into the block's branch, and the block merges as one.

## Conditions

A condition is one of:

| Field | Meaning |
|---|---|
| `all` | Every condition in the list holds |
| `any` | At least one holds |
| `not` | The condition doesn't hold |
| `artifact` | A file artifact, with one of: `exists` (`true` or `false`); `section` (a Markdown heading it has); or `path` (a dotted path into its YAML or JSON) with `equals` (a value) or `in` (a list of values) |
| `verdict` | An earlier step with an auto gate, outside a `foreach`, whose last decision `is` `approve`, `reject` or `escalate` |
| `tracker` | A fact of the run's item, exactly one of: `label`, `type`, or `field` with `name` (a board field purpose or name) and `equals` |

An artifact that is missing or doesn't parse, and a step with no verdict yet, make their conditions false. A `tracker` condition on a run without a tracker item can't be decided, and holds the block with `condition`.
