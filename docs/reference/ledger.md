# Ledger entry

One attempt of a step, one auto gate's decision on it, or one claim, as a YAML file: a **fact** in the run store. A person's decision is a merge or a label, so it is in git and the tracker, not here. The engine writes facts, and pushes them to the runs repository; they never reach a product repository. Facts are create-only: writing a fact whose name exists changes nothing, and is how two machines find out that one of them came first. The schemas are `plugins/fab0/schemas/ledger-entry.json` and `plugins/fab0/schemas/claim.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For what the ledger is for, see [artifacts and the ledger](../explanation/artifacts-and-ledger.md#the-ledger).

## Where entries are

In the runs repository that `store` names in `fab0.yaml`, in the run's folder `runs/<project>/<run>/ledger/`:

| File | What | Written by |
|---|---|---|
| `<unit>-<attempt>.yaml` | An attempt, for example `implement-T2-1.yaml` | `record`, or `apply` for a person's edit |
| `<unit>-<attempt>-gate.yaml` | The auto gate's decision on that attempt | `record --gate` |
| `<unit>-<attempt>-claim.yaml` | Who took that attempt. See [claims](#claims) | `next`, before the hand-out |

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
| `gate` | yes | The gate: `type` (`none`, `human` or `auto`). A gate entry adds the `agent` or `command`, the `decision` (`approve`, `reject` or `escalate`), who merges after an approval (`merge`: `auto` or `human`), and the branch it merges `into` |
| `summary` | no | The return's summary, or a command's exit |
| `edited` | no | A person's edit: the `commit` on the review branch it was read from, and the review pull request, `pr`, as `owner/name#number` |
| `questions` | no | The return's questions |
| `verdict` | no | A gate agent's verdict, as returned |
| `data` | no | The return's `data` |
| `exit` | no | A command step's exit code |
| `rework` | no | Why this attempt was made, when it isn't the first: `stale`, `missing`, `verify`, `rejected`, `conflict` or `checks` |

The ledger keeps no duration: it is `ended` minus `started`, never below 0. `fab0-resolve status` adds up the durations of a unit's attempts and gate decisions. Entries without times stay valid, and an engine older than the times rejects an entry that carries them.

A command gate's entry keeps its command with `{attempt}`, not the path the command ran with, because the path is one machine's and the ledger is everyone's.

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
