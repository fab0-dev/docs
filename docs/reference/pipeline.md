# Pipeline: `.fab0/pipelines/<name>.yaml`

A tree of steps and operators, with a gate on every transition and actions when the run starts and ends. The schema is `plugins/fab0/schemas/pipeline.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For how the parts work together, see [pipelines and steps](../explanation/pipelines.md).

## Top level

| Field | Required | Meaning |
|---|---|---|
| `pipeline` | yes | Its name, the same as the file's |
| `trigger` | yes | What starts a run, and what its id is. See below |
| `git` | no | Overrides the project's `branching` and `auto_merge` for this pipeline |
| `onStart` | yes | Actions when the run starts, in order. `[]` for none |
| `steps` | yes | The nodes of the pipeline, in order |
| `onEnd` | yes | Actions when the run's steps are done, in order. `[]` for none |
| `inputs` | no | What a caller may bind, when another factory calls this pipeline. See below |
| `outputs` | no | What this pipeline can hand back to a caller: artifacts its steps write. See below |

## `trigger`

Exactly one of:

| Field | Meaning |
|---|---|
| `issue` | A tracker item starts a run, and the run id is its number. Give `type` (an issue type, such as `Story`), `label`, or both |
| `manual` | A person starts the run and names its id. `id` is a regular expression the id must match, for example `^docs-` |

## `inputs` and `outputs`

A pipeline that another factory may [call](#call) declares what the caller may pass in and what it can hand back. For how they are used, see [connected factories](../explanation/connected-factories.md).

```yaml
inputs:
  spec: {default: request}
  upstream: {optional: true}
outputs: [contract, feedback]
```

`inputs` maps each input to how it is read. An input is a `store` [artifact](artifact.md) of this factory that no step of the pipeline writes, and steps read it like any other artifact:

| Field | Meaning |
|---|---|
| `default` | The artifact read when no caller binds the input, as when the pipeline runs on its own, for example the run's own item |
| `optional` | `true`: the input may stay unbound, and a step that reads it goes ahead without it |

A bound input reads the caller's latest version of the artifact bound to it. An input with no binding, no `default`, and not `optional` holds the steps that read it, as `data`.

`outputs` lists artifacts this pipeline's steps write, of kind `file` or `store`. Each one a caller takes is handed back once the unit that wrote it is done.

## Actions

`onStart` and `onEnd` are lists of [actions](actions.md). An action is its name, or a one-key map from its name to its arguments:

```yaml
onStart:
  - git.run-branch
  - pr.open-run: {draft: true}
```

## Nodes

A node is one of:

- a step's name, for `.fab0/steps/<name>.yaml`;
- a step node;
- a `foreach`, `parallel`, `when` or `call` block.

### Step node

| Field | Required | Meaning |
|---|---|---|
| `step` | yes | The step's name. With only `step`, `gate` and `after`, the step is `.fab0/steps/<step>.yaml`. With an executor (`agent`, `action`, `command` or `tool`), the step is defined here, with the fields of a [step file](step.md) |
| `gate` | no | The gate after the step. See below |
| `after` | no | Inside a `parallel` block: the steps, blocks or branches that must be done first. The whole branch this node is in waits for them |

### `foreach`

| Field | Required | Meaning |
|---|---|---|
| `foreach` | yes | A list artifact, or a list inside one (`tasks.items`). Its steps run once per element |
| `id` | no | The block's name, used in its units' ids when it has a gate. Default `foreach-<position>` |
| `max` | no | Units of this block that may run at once, per step |
| `onStart` | no | Actions before the block's units start, such as `tracker.child.sync` |
| `steps` | yes | The nodes to run for each element |
| `onEnd` | no | Actions once every element's units are done, such as `tracker.child.close` |
| `gate` | no | A gate on the block as a whole |
| `after` | no | As for a step node |

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

### `call`

Runs a pipeline of a [connected factory](project.md#factories) as a child run: it files the child run's item, binds the child's inputs, receives what the child hands back, and acknowledges each output. The node is done once every output it takes, but the optional ones, has an accepted version. See [connected factories](../explanation/connected-factories.md).

```yaml
- call: {factory: service, pipeline: delivery}
  id: service
  inputs: {spec: spec}
  outputs: {contract: contract, feedback: service-feedback}
  gate: {auto: {agent: acceptor}}
```

| Field | Required | Meaning |
|---|---|---|
| `call` | yes | `factory`: a connected factory from `factories`, or `unit.<field>` inside a `foreach`; and `pipeline`: one of its pipelines |
| `id` | no | The call's name, in its units' ids. Default `call-<factory>` |
| `inputs` | no | Per child input, the artifact of this factory bound to it. It may be an artifact another call receives: the child's steps that read it wait until it is accepted |
| `outputs` | no | Per child output this factory takes, the `store` artifact of this factory that receives it, which is the format it accepts; or `artifact` and `optional: true`, for an output the call doesn't wait for |
| `gate` | no | The acknowledgement of what the child hands back. `none` (default) accepts an output in the accepted format. `auto` with an `agent`, or `human`, answers each one. It takes no `merge`, `retry` or `then` |
| `after` | no | As for a step node |

A called pipeline may not call another factory itself, and a call's `auto` gate is an agent, not a command; `validate` refuses both until a factory needs them. A person acknowledges in a review pull request of the runs repository, not by a label, so a `human` gate on a call needs `store.github`.

## `gate`

One of:

- `none` (default): the work moves on, and `apply` merges it;
- `human`: a person decides, by merging the unit's pull request;
- a map with `human`;
- a map with `auto`.

A human gate:

| Field | Meaning |
|---|---|
| `owner` | The role whose turn it is. Default: the repository's owner |
| `via` | `pr` (default): a person merges the unit's pull request. `label`: a person adds `label` to the run's item, for units without a pull request |
| `label` | The label, with `via: label` |

An auto gate:

| Field | Meaning |
|---|---|
| `auto` | Either an agent, with `agent` (any Claude Code agent), `model` (a model class), `skills` and `instructions`, or a `command` whose exit code decides |
| `merge` | Who merges the unit's pull request once the gate approves: `auto` (`apply`, within `git.auto_merge`) or `human` (default) |
| `retry` | Re-runs of the producing step after a reject. Default 2 |
| `then` | What happens when the retries run out: `human` (default) or `fail` |

## Conditions

A condition is one of:

| Field | Meaning |
|---|---|
| `all` | Every condition in the list holds |
| `any` | At least one holds |
| `not` | The condition doesn't hold |
| `artifact` | An artifact, with one of: `exists` (`true` or `false`); `section` (a Markdown heading it has); or `path` (a dotted path into its YAML or JSON) with `equals` (a value) or `in` (a list of values) |
| `verdict` | A step outside a `foreach` whose last auto-gate decision `is` `approve`, `reject` or `escalate` |
| `tracker` | A fact of the run's item, exactly one of: `label`, `type`, or `field` with `name` (a board field purpose or name) and `equals` |

An artifact that is missing or doesn't parse, and a step with no verdict yet, make their conditions false. A `tracker` condition on a run without a tracker item can't be decided, and holds the block with `condition`.
