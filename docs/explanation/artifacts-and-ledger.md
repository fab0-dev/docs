# Artifacts and the ledger

Stages pass **artifacts** to each other. The **ledger** records every attempt that produced them. Both live in git.

## Artifact types

An artifact type says what a thing is, where it lives, how it is checked and how long it is kept. Stages refer to artifacts by name.

```yaml
# .fab0/artifacts/tasks.yaml
artifact: tasks
format: yaml
location: {repo: home, path: "work/{run}/tasks.yaml"}
schema: fab0:schemas/tasks.json   # yaml and json only; validated by the resolver
keep: run                         # removed from the base branch by the deliver pull request
```

```yaml
# .fab0/artifacts/intent.yaml
artifact: intent
format: markdown
location: {github: issue-body}    # read from GitHub, never written by a stage
```

A location is either a path in a repository or a GitHub source. The path can use `{run}`, and `{task}` inside a `foreach`. Every field is in the [wiring reference](../reference/wiring.md).

Structured formats (YAML, JSON) are preferred wherever a tool can check them (P5). `foreach` reads only YAML or JSON artifacts for that reason.

### Core artifact types

| Type | Format | Contents |
|---|---|---|
| `intent` | Markdown, from the issue body | What the item asks for |
| `spec` | Markdown | The spec of one run |
| `tasks` | YAML, schema `fab0:schemas/tasks.json` | Per task: `id`, `title`, `repo`, `files`, `depends_on`, `traces_to` |
| `review` | JSON, schema `review.json` | An agent gate's `decision`, `reasons`, `findings` and `unmet` scenarios |

Every other type is declared in the project when a stage that produces it is added. The plugin that provides the agent documents the format in its skill, and may ship a JSON Schema for the project to point to.

A binary artifact too large for a normal commit is tracked with Git LFS through the repository's `.gitattributes`. fab0 needs no setting for it.

## The ledger

The ledger is the directory `work/{run}/ledger/` in the repository where a stage ran. It holds one file per agent-stage attempt, named `<stage>[-<task>]-<attempt>.yaml`, for example `spec-1.yaml` or `implement-T1-2.yaml`.

```yaml
# work/412/ledger/spec-1.yaml
stage: spec
attempt: 1
actor: po-user
model: opus
branch: spec/412-booking-extension
inputs:  {intent: "sha256:9f3c…"}
outputs: {spec: "sha256:41aa…", tasks: "sha256:c07e…"}
verify:  {spec: pass, tasks: pass}
gate:    {type: human}
summary: The spec has six scenarios for …
```

- **Committed with the work.** Entries are committed with the stage's artifacts on its branch and merged with its pull request.
- **No collisions.** Names can't collide across parallel branches, and order comes from git history.
- **Append-only.** Only the resolver writes the ledger, and an existing entry is never edited.
- **Agent gates.** A gate's decision goes in a file of its own beside the attempt it judged: `<stage>[-<task>]-<attempt>-gate.yaml`, with the decision and the review.
- **Human gates.** A merge is not recorded. GitHub is the truth for it (P3). The resolver reads it as "the attempt's entry is on the base branch".
- **Actions.** Actions write no ledger entries. Their results are GitHub facts (sub-issues, assignees, closed issues) that the resolver reads back. Every commit therefore stays inside the pull request flow, and fab0 never pushes to the base branch.

Because the ledger travels in git, anyone can pick a run up on any machine. The ledger also replaces metadata on every artifact, which would only work for formats that have a header.

The fields of an entry are in the [ledger reference](../reference/ledger.md).
