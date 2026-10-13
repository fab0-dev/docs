# Wiring reference

A project's wiring is four kinds of YAML file in `.fab0/` of the home repo. Each is validated against a JSON Schema in the core plugin (`plugins/fab0/schemas/` in [`fab0-core`](https://github.com/fab0-dev/fab0-core)), and then cross-checked by `fab0-resolve validate`. The schemas are authoritative; this page explains them.

| File | Schema | One per |
|---|---|---|
| `.fab0/fab0.yaml` | `fab0.json` | project |
| `.fab0/artifacts/<name>.yaml` | `artifact.json` | artifact type |
| `.fab0/stages/<name>.yaml` | `stage.json` | stage |
| `.fab0/pipelines/<name>.yaml` | `pipeline.json` | pipeline |

Names (of repositories, roles, stages, artifact types, pipelines and model classes) are lower case: a letter, then letters, digits or `-`. A file's name must match the name inside it.

## `fab0.yaml`

```yaml
schema: 1
repos:
  home:    {path: ., github: acme/product, owner: product-owner}
  backend: {path: ../backend, github: acme/backend, owner: backend, key: BE}
people:
  product-owner: {github: [po-user]}
  backend:       {github: [backend-dev]}
tracker:
  kind: github-projects
  owner: acme
  project: 7
  fields: {stage: Stage, run: Run, waiting: Waiting on}
pipelines: [story]
models:
  claude-code: {deep: opus, balanced: sonnet, fast: haiku}
profiles:
  cheap: {models: {claude-code: {deep: sonnet}}}
```

| Key | Required | Meaning |
|---|---|---|
| `schema` | yes | Always `1` |
| `repos` | yes | Repositories by name. `home` is required. `all`, `task` and `each-touched` are reserved names |
| `repos.<name>.path` | yes | Local checkout, relative to the home repo |
| `repos.<name>.github` | yes | `owner/name` on GitHub |
| `repos.<name>.owner` | yes | The role that owns the repository: it gets its tasks, and the deliver pull request for `home` |
| `repos.<name>.key` | no | Two or three capital letters, unique. Reserved for child run ids of nested pipelines (Planned) |
| `repos.<name>.base` | no | The base branch. Default `main` |
| `people` | yes | Roles, each mapped to `github: [users]` |
| `tracker` | no | The Projects board: `kind: github-projects`, `owner`, `project` (number) and `fields` (`stage`, `run`, `waiting` → field names) |
| `pipelines` | yes | The pipelines this project runs. Each needs a file in `.fab0/pipelines/` and its own issue type |
| `models` | yes | Per harness, model classes → model names. `claude-code` is required |
| `profiles` | no | Named JSON Merge Patches (RFC 7396) over this file, applied with `--profile`. The patched file must still be valid |

## Artifact types

```yaml
artifact: spec
format: markdown
location: {repo: home, path: "specs/{run}.md"}
verify:
  - sections: [Intent, Scope, Scenarios, Constraints, Decisions, Open questions]
keep: durable
```

| Key | Required | Meaning |
|---|---|---|
| `artifact` | yes | The name stages use |
| `format` | yes | `markdown`, `yaml`, `json`, `gherkin`, `openapi`, `file` or `dir`. Only `yaml` and `json` are parsed; `dir` is every file under the path |
| `location` | yes | `{repo, path}` or `{github: issue-body \| pr-review}` |
| `location.repo` | | A repository name, or `task` inside a `foreach` (the task's repository) |
| `location.path` | | May use `{run}`, and `{task}` inside a `foreach` |
| `location.github` | | `issue-body`: the item's body. `pr-review`: reviews on the stage pull request. `pr` is reserved (Planned). GitHub locations can't be stage outputs |
| `schema` | no | `yaml` and `json` only. `plugin:path` inside a plugin, for example `fab0:schemas/tasks.json`. Only the `fab0` plugin's schemas resolve today |
| `verify` | no | A list of `sections: [...]`, `lint: "<command> {path}"` or `script: <name>` (see [verification](../explanation/verification.md)) |
| `keep` | no | `run`: removed from the base branch by the deliver pull request (home repo only). `durable`, or no `keep`: kept |

## Stages

```yaml
stage: implement
agent: fab0:implementer
model: balanced
inputs: [spec, tasks]
repos: {write: [task], read: [all]}
skills: [fab0:spec-format]
return: {questions: optional}
owner: repo-owner
gate: {agent: fab0:reviewer, model: deep}
```

A stage has exactly one of `agent` or `action`.

| Key | Applies to | Meaning |
|---|---|---|
| `stage` | all | The name |
| `agent` | agent stage | `plugin:name`, or a bare name that must be a file in `.claude/agents/` |
| `action` | action stage | `plan` or `deliver` |
| `model` | agent stage, required | A model class from `models` |
| `owner` | agent stage, required | A role from `people`, or `repo-owner` inside a `foreach` |
| `inputs` | all | Artifact types read. Each must be written by an earlier stage, or exist already |
| `outputs` | agent stage | Artifact types written |
| `repos.write` | agent stage | Repositories the stage may change. Default: the task's repository inside a `foreach`, otherwise `home` |
| `repos.read` | agent stage | Repositories it may read; `all` for every one |
| `skills` | agent stage | `plugin:skill` names. They are listed in the brief, not loaded by fab0 |
| `return` | agent stage | Extra return fields, each `optional` or `required`. Only `questions` exists |
| `gate` | all | `none` (default), `human`, or `{agent, model}`. Action stages can't have an agent gate |

Action stages take no `model`, `owner`, `skills`, `return`, `outputs` or `repos`.

- `plan` takes exactly one input: the YAML or JSON task list. A later `foreach` must run over it.
- `deliver` takes exactly one input: the Markdown document the delivered tasks are appended to. It must be the pipeline's last stage.

## Pipelines

```yaml
pipeline: story
item: {issue_type: Story}
stages:
  - spec
  - plan
  - foreach: tasks
    item: {issue_type: Task}
    stages: [implement]
    gate: human
  - deliver
```

| Key | Meaning |
|---|---|
| `pipeline` | The name, listed in `fab0.yaml` |
| `item.issue_type` | The GitHub issue type this pipeline runs for. Unique across the project's pipelines |
| `stages` | Steps in order: a stage name, or a `foreach` |
| `foreach` | A YAML or JSON artifact to fan out over, for example `tasks` |
| `foreach.item.issue_type` | The issue type of each element's sub-issue |
| `foreach.stages` | Agent stages run for each element |
| `foreach.gate` | `none` or `human`: a gate per element, after its stages |

A stage may appear once in a pipeline. Refused as "not supported yet" (Planned): `when` on any step, `call` and `inputs` on a `foreach`, and pipeline-level `inputs` and `outputs` (see [nesting](../explanation/nesting.md)).
