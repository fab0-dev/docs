# Artifact: `.fab0/artifacts/<name>.yaml`

A piece of state that steps pass on. Its kind says where it lives, and how it is hashed to tell whether work that read it is stale. fab0 prescribes no formats: a factory chooses them, and may give its own schema. The schema is `plugins/fab0/schemas/artifact.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For how artifacts are used, see [artifacts and the ledger](../explanation/artifacts-and-ledger.md).

```yaml
artifact: tasks
kind: store
store: {format: yaml}
schema: .fab0/schemas/tasks.json
elements: {id: id, title: title, repo: repo, after: depends_on, paths: files}
```

## Top level

| Field | Required | Meaning |
|---|---|---|
| `artifact` | yes | Its name, the same as the file's |
| `kind` | yes | `file` (in a product repository), `store` (in the run store), `issue`, `pr`, `tool` or `none`. The field of the same name says where it is; `none` has none |
| `file` | for `file` | See below |
| `store` | for `store` | See below |
| `issue` | for `issue` | See below |
| `pr` | for `pr` | See below |
| `tool` | for `tool` | See below |
| `schema` | no | A project-relative JSON Schema, for `yaml` and `json` files and store artifacts |
| `elements` | no | For a list used by `foreach`: which field of an element holds what. See below |
| `verify` | no | Checks of the file a step writes. See below |

fab0 0.6's `keep` is gone: `validate` refuses it, with a hint. A working file, such as a task list, is `kind: store` instead, so it never reaches a product repository and nothing has to remove it.

## `file`

| Field | Required | Meaning |
|---|---|---|
| `repo` | yes | A repository name, or `unit.<field>` |
| `path` | yes | A file or directory, with `{run}` and `{unit}` filled in |
| `format` | no | `yaml` and `json` are parsed, and `markdown` is read by section. Any other value is opaque |

## `store`

A file a run produces for itself, kept in the run store and never in a product repository: see [the `store` block](project.md#store). The step writes it in its **outbox**, a folder outside every repository that the brief names. `record` checks it like any output, then keeps it in the run store as an object named by its hash, so each version is immutable. A file in the outbox that is no output of the step is a finding.

| Field | Required | Meaning |
|---|---|---|
| `format` | yes | Lowercase letters and digits. `yaml` and `json` are parsed, and `markdown` is read by section; any other value is opaque. It also names the file's extension: `markdown` is `.md`, `text` is `.txt`, any other format is its own name. The step writes `<artifact>.<extension>`, such as `tasks.yaml` |

A store artifact's latest version is the output of the most recent attempt that wrote it and passed its checks: per element for a `foreach` unit, else the run's. Briefs show it, `foreach` reads its elements from it, conditions read it, and staleness hashes it. A run has one latest version, not one per branch, so every unit that reads it sees a new version at once.

When a step with a `human` gate decided by a pull request writes only store artifacts and no repository, a person reviews them in a pull request of the runs repository: see [gates](../explanation/gates.md).

## `issue`

A part of a tracker item, read and never written by a step.

| Field | Required | Meaning |
|---|---|---|
| `of` | no | `run` (default): the run's item. `unit`: the current element's item. `parent`: the item the run's item is a sub-issue of, such as the Feature a Story belongs to |
| `part` | yes | `body`, `title`, `comments`, `labels`, or `field` |
| `field` | with `part: field` | The board field |

## `pr`

| Field | Required | Meaning |
|---|---|---|
| `of` | no | `run` (default): the run's pull request into the base branch, in the home repo. `unit`: the current unit's pull requests. For a unit reviewed in the runs repository, they are its review pull requests there |
| `part` | yes | `body`, `reviews` (reviews that ask for changes or comment, and people's conversation comments, from every pull request of the unit's branch, oldest first; comments fab0 posts, whose body starts with `<!-- fab0:`, are left out, and a merged pull request's stop counting), or `diff` |

## `tool`

A value an agent reads through a tool call. The engine can't call tools; it hashes the call itself.

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | The tool's name, such as `mcp__tracker__search_issues` |
| `with` | no | Its arguments. Strings may use the [step placeholders](step.md#placeholders) |

## `elements`

For a list artifact read by `foreach`. Each field names the key of an element that holds the value; the default is the key of the same name.

| Field | Meaning |
|---|---|
| `at` | A dotted path to the list, if it isn't the top level |
| `id` | The element's id: letters, digits, `.`, `_` and `-`. It names the element's units |
| `title` | Its title, for example for its tracker item |
| `repo` | The repository its units write |
| `after` | The ids of elements it comes after |
| `paths` | The paths its units claim |

## `verify`

Each check is one of:

| Field | Meaning |
|---|---|
| `sections` | Markdown headings the file must have |
| `lint` | A shell command with `{path}`, run in the unit's worktree, or in its outbox for a store artifact. A non-zero exit fails |
| `script` | A program on `PATH`, given the file's path. A non-zero exit fails |
