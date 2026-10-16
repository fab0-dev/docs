# Ledger entry

One attempt of a step, or one auto gate's decision on it, as a YAML file. A person's decision is a merge or a label, so it is in git and the tracker, not here. The engine writes it at `record`; the session commits it with the work; merges carry it to the base branch. The ledger is append-only. The schema is `plugins/fab0/schemas/ledger-entry.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For what the ledger is for, see [artifacts and the ledger](../explanation/artifacts-and-ledger.md#the-ledger).

## Where entries are

Under `ledger.path` from `fab0.yaml` (default `work/{run}/ledger`), in the repository the unit ran in: the first one it writes, else the home repo. A pipeline whose steps write no files keeps its entries on `ledger.branch`.

| File | What |
|---|---|
| `<unit>-<attempt>.yaml` | An attempt, for example `implement-T2-1.yaml` |
| `<unit>-<attempt>-gate.yaml` | The auto gate's decision on that attempt |

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
gate: {type: auto}
started: 2026-10-15T10:00:00Z
ended: 2026-10-15T10:04:12Z
summary: Added the pricing rules with tests; all tests pass.
```

| Field | Required | Meaning |
|---|---|---|
| `step` | yes | The step |
| `unit` | no | The `foreach` element's id |
| `attempt` | yes | The attempt's number, from 1 |
| `executor` | yes | `agent`, `action`, `command` or `tool` |
| `actor` | yes | The tracker user who ran it |
| `model` | no | The model the agent ran on |
| `branch` | yes | The branch the attempt was made on |
| `base` | yes | The parent branch (`branch`) and the commit (`sha`) the inputs were read at |
| `inputs` | no | The hash of each input, by name, as `sha256:<hex>` |
| `outputs` | no | The hash of each output file, by name |
| `claims` | no | The paths the unit claimed, as `<repo>:<glob>` |
| `verify` | no | The checks of each output, by its name: `pass`, or the list of errors. Writes outside the claims add `claims:<repo>` with the files |
| `started` | no | When the attempt or the gate decision was handed out, as a UTC time to the second, such as `2026-10-15T10:00:00Z`. A hand-out given again starts again. A refused `record` keeps it. Left out of entries written before times were kept |
| `ended` | no | When it was recorded, in the same form. Written with `started` |
| `gate` | yes | The gate: `type` (`none`, `human` or `auto`). A gate entry adds the `agent` or `command`, the `decision` (`approve`, `reject` or `escalate`), who merges after an approval (`merge`: `auto` or `human`), and the branch it merges `into` |
| `summary` | no | The return's summary, or a command's exit |
| `questions` | no | The return's questions |
| `verdict` | no | A gate agent's verdict, as returned |
| `data` | no | The return's `data` |
| `exit` | no | A command step's exit code |
| `rework` | no | Why this attempt was made, when it isn't the first: `stale`, `missing`, `verify`, `rejected`, `conflict` or `checks` |

The ledger keeps no duration: it is `ended` minus `started`, never below 0. `fab0-resolve status` adds up the durations of a unit's attempts and gate decisions. Entries without times stay valid, and an engine older than the times rejects an entry that carries them.
