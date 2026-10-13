# Ledger reference

One YAML file per agent-stage attempt, in `work/{run}/ledger/` of the repository where the stage ran. Only `fab0-resolve record` writes these files, and they are never edited. Schema: `ledger-entry.json` in the core plugin.

## File names

| Entry | Name | Example |
|---|---|---|
| Attempt | `<stage>[-<task>]-<attempt>.yaml` | `spec-1.yaml`, `implement-T1-2.yaml` |
| Agent gate decision | `<stage>[-<task>]-<attempt>-gate.yaml` | `implement-T1-2-gate.yaml` |

Attempts are numbered from 1, without padding.

## Fields

| Field | Required | Meaning |
|---|---|---|
| `stage` | yes | The stage name |
| `task` | no | The task id, inside a `foreach` |
| `attempt` | yes | The attempt number |
| `actor` | yes | The GitHub user who ran it |
| `model` | yes | The model it ran on |
| `branch` | no | The branch it was committed on |
| `inputs` | no | Input artifact → `sha256:<hex>` at hand-out time |
| `outputs` | no | Output artifact → `sha256:<hex>` |
| `verify` | no | Artifact → `pass`, or a list of errors |
| `gate` | yes | `type` (`none`, `human` or `agent`); for an agent gate entry also `agent` and `decision` (`approve`, `escalate` or `reject`) |
| `summary` | no | The agent's one-paragraph summary |
| `questions` | no | Questions the agent returned |
| `review` | no | On a gate entry: the review (`decision`, `reasons`, `findings`, `unmet`) |

## Hashes

- **Files.** A file's hash is the SHA-256 of its bytes.
- **Directories.** A `dir` artifact's hash is the SHA-256 of its sorted lines `relpath\0sha256(file)\n`.
- **Staleness.** An output is stale when any input hash differs from the one recorded.
