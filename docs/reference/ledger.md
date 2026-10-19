# Ledger entry

One attempt of a step, one gate's decision on it, or one claim, as a YAML file: a **fact** in the run store. A person's approving review of a review pull request in the runs repository is recorded here too, as the gate decision `apply` writes; a person's other decisions are merges or labels, in git and the tracker. The runs repository's root also holds the [register](#the-register), which gives each run its id. The engine writes facts, and pushes them to the runs repository; they never reach a product repository. Facts are create-only: writing a fact whose name exists changes nothing, and is how two machines find out that one of them came first. The schemas are `plugins/fab0/schemas/ledger-entry.json`, `plugins/fab0/schemas/claim.json`, `plugins/fab0/schemas/register.json` and, for the [link facts](#link-facts), `plugins/fab0/schemas/link-*.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For what the ledger is for, see [artifacts and the ledger](../explanation/artifacts-and-ledger.md#the-ledger).

## Where entries are

In the runs repository that `store` names in `fab0.yaml`, in the run's folder `runs/<project>/<run>/ledger/`:

| File | What | Written by |
|---|---|---|
| `<unit>-<attempt>.yaml` | An attempt, for example `implement-T2-1.yaml` | `record`, or `apply` for a person's edit |
| `<unit>-<attempt>-gate.yaml` | The gate's decision on that attempt: an auto gate's, or a person's approving review in the runs repository | `record --gate`, or `apply` for a person's approval |
| `<unit>-<attempt>-claim.yaml` | Who took that attempt. See [claims](#claims) | `next`, before the hand-out |
| `<kind>@<key>.yaml` | A link between a parent run and a child run. See [link facts](#link-facts) | `apply`, or `record --gate` for an agent's acknowledgement |

The run's folder also holds its store artifacts, `objects/sha256-<hex>.<ext>`, and the readable copies of a unit's outputs that reached `main` through its review pull request, `review/<unit>/`.

## Fields

```yaml
step: implement
unit: T2
attempt: 1
executor: agent
actor: be-user
model: sonnet
branch: fab0/412/implement-T2
base: {branch: fab0/412/base, sha: 4c80e8a0a1b2c3d4e5f60718293a4b5c6d7e8f90}
inputs:
  spec: sha256:d93b…
claims: ["backend:src/pricing.py", "backend:tests/test_pricing.py"]
heads: {backend: 9f1c2d3e4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d}
gate: {type: auto}
started: '2026-10-15T10:00:00Z'
ended: '2026-10-15T10:04:12Z'
summary: Added the pricing rules with tests; all tests pass.
```

| Field | Required | Meaning |
|---|---|---|
| `step` | yes | The step |
| `unit` | no | The `foreach` element's id |
| `attempt` | yes | The attempt's number, from 1 |
| `executor` | yes | `agent`, `action`, `command` or `tool`; `person` for a person's edit of the outputs on the unit's review pull request, which `apply` records as an attempt of that person |
| `actor` | yes | The tracker user who ran it |
| `model` | no | The model the agent ran on |
| `branch` | yes | The branch the attempt was made on; for a person's edit, the review branch |
| `heads` | no | Per repository, the commit the attempt left its branch at, when the branch has commits its parent lacked at the hand-out. The unit is done once these commits are in the branch it merges into, or once GitHub reports its pull request merged at them, as after a person's squash merge. An attempt without `heads` changed nothing, so its gate is the decision |
| `base` | yes | The parent branch (`branch`) and the commit (`sha`) the inputs were read at |
| `inputs` | no | The hash of each input, by name, as `sha256:<hex>` |
| `outputs` | no | The hash of each output, by name. A store artifact's hash names its object in the run store |
| `claims` | no | The paths the unit claimed, as `<repo>:<glob>` |
| `verify` | no | The checks of each output, by its name: `pass`, or the list of errors. Writes outside the claims add `claims:<repo>` with the files |
| `started` | no | When the attempt or the gate decision was handed out, as a UTC time to the second, such as `2026-10-15T10:00:00Z`. A hand-out given again starts again. A refused `record` keeps it. Left out of entries written before times were kept |
| `ended` | no | When it was recorded, in the same form. Written with `started` |
| `gate` | yes | The gate: `type` (`none`, `human` or `auto`). An auto gate's entry adds the `agent` or `command`, the `decision` (`approve`, `reject` or `escalate`), who merges after an approval (`merge`: `auto` or `human`), and the branch it merges `into`. A human gate decided in a review pull request adds `decision: approve` and `review`: the `pull` request, and the `commit` of its branch the owner approved. The decision is this fact: `apply` merges the pull request after writing it, and a merge that a branch protection refuses leaves the unit done |
| `summary` | no | The return's summary, or a command's exit |
| `edited` | no | A person's edit: the `commit` on the review branch it was read from, and the review pull request, `pr`, as `owner/name#number` |
| `questions` | no | The return's questions |
| `verdict` | no | A gate agent's verdict, as returned |
| `data` | no | The return's `data` |
| `exit` | no | A command step's exit code |
| `rework` | no | Why this attempt was made, when it isn't the first: `stale`, `missing`, `verify`, `rejected`, `conflict` or `checks` |

The ledger keeps no duration: it is `ended` minus `started`, never below 0. `fab0-resolve status` adds up the durations of a unit's attempts and gate decisions. Entries without times stay valid, and an engine older than the times rejects an entry that carries them.

A command gate's entry keeps its command with `{attempt}`, not the path the command ran with, because the path is one machine's and the ledger is everyone's.

## The register

`register/<run>.yaml`, at the root of the runs repository, gives a run started from an item its id: the next free number, one more than every register fact and every run folder of every project, so a new id never names a run of 0.8. `fab0-resolve start #<n>` writes it and pushes it at once. It is create-only: a start that lost the race to another machine takes the next number. One number names the run in every factory that shares the runs repository, and a [call](#link-facts)'s child run takes its parent's id, so the child has no register fact of its own.

```yaml
project: shop
item: acme/shop#52
pipeline: story
actor: po-user
at: '2026-10-19T10:00:00Z'
```

| Field | Required | Meaning |
|---|---|---|
| `project` | yes | The store project of the factory the run belongs to: its folder under `runs/` |
| `item` | yes | The run's tracker item, `owner/repo#n`. The run's item is read from here, not from its id |
| `pipeline` | yes | The pipeline the run runs, picked by the item's trigger when it started |
| `actor` | yes | The tracker user who started it |
| `at` | yes | When, as a UTC time to the second |

A run with no register fact is a run of 0.8 or before, whose id is its item's number, or a manual run, whose id a person gave.

## Claims

Before `next` hands an attempt out, it writes a claim fact and pushes it, so two machines never run the same attempt. The first claim pushed stands. A machine whose claim lost, or that finds another machine's, doesn't hand the attempt out: the unit shows as `running`, with `claimed: elsewhere`.

```yaml
actor: po-user
machine: 3f2a9c0d4b5e6f708192a3b4c5d6e7f8
at: '2026-10-15T10:00:00Z'
```

| Field | Required | Meaning |
|---|---|---|
| `actor` | yes | The tracker user who took it |
| `machine` | yes | The checkout that took it: an id kept in the home repo's git directory, so a checkout knows its own claim |
| `at` | yes | When, as a UTC time to the second |

## Link facts

A [call](pipeline.md#call) links a run of one factory, the parent, to a run of a connected factory, the child. Both runs keep their own folder in the same runs repository, and each writes facts only in its own. The facts that link them are named `<kind>@<key>`. A unit id never holds `@`, so a link fact never reads as an attempt, a gate decision or a claim. For how calls work, see [connected factories](../explanation/connected-factories.md).

| Fact | In whose folder | What | Written by |
|---|---|---|---|
| `call@<call>` | The parent's | The call started its child run | The parent's `apply`, once it has filed the child run's item |
| `bound@parent` | The child's | Its copy of what the call binds and accepts, so `record` reads it without the tracker | The child's `apply` (`call.bind`) |
| `export@<unit>-<attempt>+<output>` | The child's | One version of an output the caller takes | The child's `apply`, once the unit is done |
| `ack@<call>+<unit>-<attempt>+<output>` | The parent's | The parent's answer to that export | `record --gate` for an agent, `apply` for a person's review in a review pull request |

### `call@<call>`

| Field | Required | Meaning |
|---|---|---|
| `factory` | yes | The connected factory, as `factories` names it |
| `pipeline` | yes | The child pipeline |
| `unit` | yes | The call's unit in the parent run |
| `element` | no | Inside a `foreach`, the element the call is for |
| `item` | yes | The child run's item, `owner/repo#n` |
| `project` | yes | The child factory's `store.project` |
| `run` | yes | The child run's id: the parent run's own, so one id names the work in every factory. The child's folder is `runs/<project>/<run>/` and its branches `fab0/<run>/…`. A call made before 0.9 gave the child its item's number |
| `bindings` | yes | Per child input, the parent's artifact bound to it |
| `formats` | yes | Per output the parent takes, its accepted format: `artifact`, the parent's artifact; `schema`, its schema as an object in the parent's folder, when it has one; `sections`, the Markdown sections its checks ask for; and `optional` |
| `acknowledge` | no | How the call answers what comes back: `none`, `auto` or `human`, by its gate |
| `actor` | yes | The tracker user whose command wrote it |
| `at` | yes | When, as a UTC time to the second |

### `bound@parent`

| Field | Required | Meaning |
|---|---|---|
| `parent` | yes | The call: the parent's store `project`, its `run`, the call's `unit`, the parent run's `item`, and the call's `element`, if any |
| `bindings` | yes | As in `call@<call>` |
| `formats` | yes | As in `call@<call>` |
| `acknowledge` | no | As in `call@<call>` |
| `actor` | yes | As above |
| `at` | yes | As above |

### `export@<unit>-<attempt>+<output>`

| Field | Required | Meaning |
|---|---|---|
| `output` | yes | The child pipeline's output |
| `unit` | yes | The child unit whose attempt produced it |
| `attempt` | yes | That attempt |
| `object` | yes | The output, as an object in the child's folder. A `file` output is copied there from the unit's commit |
| `actor` | yes | As above |
| `at` | yes | As above |

### `ack@<call>+<unit>-<attempt>+<output>`

| Field | Required | Meaning |
|---|---|---|
| `export` | yes | The export answered: the child's store `project`, its `run`, and the export fact's `name` |
| `decision` | yes | `accepted` or `rejected` |
| `findings` | no | What the parent found, for the child's next attempt |
| `reviews` | no | A person's answer: the review pull request's reviews it comes from, so none counts twice |
| `actor` | yes | Who decided |
| `at` | yes | As above |
