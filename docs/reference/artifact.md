# Artifact: `.fab0/artifacts/<name>.yaml`

A piece of state that steps pass on. Its kind says where it lives, and how it is hashed to tell whether work that read it is stale. fab0 prescribes no formats: a factory chooses them, and may give its own schema. The schema is `plugins/fab0/schemas/artifact.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For how artifacts are used, see [artifacts and the ledger](../explanation/artifacts-and-ledger.md).

```yaml
artifact: tasks
kind: file
file: {repo: home, path: "work/{run}/tasks.yaml", format: yaml}
schema: .fab0/schemas/tasks.json
elements: {id: id, title: title, repo: repo, after: depends_on, paths: files}
keep: run
```

## Top level

| Field | Required | Meaning |
|---|---|---|
| `artifact` | yes | Its name, the same as the file's |
| `kind` | yes | `file`, `issue`, `pr`, `tool` or `none`. The field of the same name says where it is; `none` has none |
| `file` | for `file` | See below |
| `issue` | for `issue` | See below |
| `pr` | for `pr` | See below |
| `tool` | for `tool` | See below |
| `schema` | no | A project-relative JSON Schema, for `yaml` and `json` files |
| `elements` | no | For a list used by `foreach`: which field of an element holds what. See below |
| `verify` | no | Checks of the file a step writes. See below |
| `keep` | no | For files: `durable` (default) stays in the result; `run` is removed by `git.remove-run-artifacts`, unless its path has `{unit}` or its repository is the element's |

## `file`

| Field | Required | Meaning |
|---|---|---|
| `repo` | yes | A repository name, or `unit.<field>` |
| `path` | yes | A file or directory, with `{run}` and `{unit}` filled in |
| `format` | no | `yaml` and `json` are parsed, and `markdown` is read by section. Any other value is opaque |

## `issue`

A part of a tracker item, read and never written by a step.

| Field | Required | Meaning |
|---|---|---|
| `of` | no | `run` (default): the run's item. `unit`: the current element's item |
| `part` | yes | `body`, `title`, `comments`, `labels`, or `field` |
| `field` | with `part: field` | The board field |

## `pr`

| Field | Required | Meaning |
|---|---|---|
| `of` | no | `run` (default): the run's pull request. `unit`: the current unit's pull requests |
| `part` | yes | `body`, `reviews` (reviews that ask for changes or comment, from every pull request of the unit's branch), or `diff` |

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
| `lint` | A shell command with `{path}`, run in the unit's worktree. A non-zero exit fails |
| `script` | A program on `PATH`, given the file's path. A non-zero exit fails |
