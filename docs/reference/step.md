# Step: `.fab0/steps/<name>.yaml`

One piece of work with exactly one executor. A step is a file in `.fab0/steps/`, or defined inline in a pipeline. Its gate belongs to the pipeline, not here, because a gate is a transition between steps. The schema is `plugins/fab0/schemas/step.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core).

```yaml
step: implement
agent: implementer
model: balanced
inputs: [spec, tasks, unit, reviews]
repos: {write: [unit.repo], read: [all]}
paths: unit.paths
return: {questions: optional}
owner: repo-owner
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `step` | yes | Its name, the same as the file's |
| `agent` | one executor | Any Claude Code agent: `plugin:agent`, or the name of a file in `.claude/agents/` |
| `action` | one executor | An [action](actions.md), performed by the engine |
| `command` | one executor | A shell command, run in the unit's worktree. Its exit code is its result |
| `tool` | one executor | A tool the session calls, such as an MCP tool. Its result is recorded like an agent's reply |
| `with` | no | Arguments for an action or a tool. See placeholders below |
| `model` | with `agent` | A model class from `models` in `fab0.yaml` |
| `skills` | no | Skills the agent loads first: `plugin:skill`, or a skill in `.claude/skills/` |
| `instructions` | no | Extra text for the agent's brief, for an agent that isn't written for this step |
| `inputs` | no | Artifacts the step reads, or `unit` (the current element of a `foreach`) |
| `outputs` | no | Artifacts the step writes: a `file` artifact in a repository it writes, or a `store` artifact in its outbox, outside every repository |
| `repos` | no | `write`: the repositories the step may change, or `unit.<field>` for the element's repository. `read`: the repositories it may read, or `all` |
| `paths` | no | The step's claim: a list of globs (`{run}` and `{unit}` are filled in), or `unit.<field>` for the element's own list. Without it, a step claims every file of the repositories it writes |
| `return` | no | What the reply may or must carry beyond `summary`: `questions` (`optional` or `required`), and `schema`, a project-relative JSON Schema the reply's `data` must match |
| `owner` | no | The role whose turn the step is, or `repo-owner` for the owner of the repository it writes |

A step has exactly one of `agent`, `action`, `command` and `tool`.

## Placeholders

Strings in `with` may use:

| Placeholder | Value |
|---|---|
| `{run}` | The run id |
| `{run.<field>}` | A field of the run's tracker item: `title`, `body`, `number`, `state`, `type` |
| `{unit}` | The current element's id |
| `{unit.<field>}` | A field of the current element |
| `{<step>.<field>}` | A field of an earlier agent or tool step's reply `data` |

## Replies

An agent or tool step replies with a JSON object: `summary` always, `questions` and `data` when `return` asks for them. See [returns and verdicts](returns-and-verdicts.md).
