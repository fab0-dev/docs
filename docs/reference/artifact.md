# Artifact: `.fab0/artifacts/<name>.yaml`

A piece of state that steps pass on. Its kind says where it lives: a file in a repository, the runs repository among them, a part of a tracker item or a pull request, or a tool's value. fab0 prescribes no formats: a factory chooses them, and may give its own schema. The schema is `plugins/fab0/schemas/artifact.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For how artifacts are used, see [artifacts](../explanation/artifacts.md).

```yaml
artifact: tasks
kind: file
file: {repo: runs, path: "runs/product/{run}/tasks.yaml", format: yaml}
schema: .fab0/schemas/tasks.json
elements: {id: id, title: title, repo: repo, after: depends_on, paths: files}
```

## Top level

| Field | Required | Meaning |
|---|---|---|
| `artifact` | yes | Its name, the same as the file's |
| `kind` | yes | `file` (in a repository), `issue`, `pr`, `tool` or `none`. The field of the same name says where it is; `none` has none |
| `file` | for `file` | See below |
| `issue` | for `issue` | See below |
| `pr` | for `pr` | See below |
| `tool` | for `tool` | See below |
| `schema` | no | A project-relative JSON Schema, for `yaml` and `json` files |
| `elements` | no | For a list used by `foreach`: which field of an element holds what. See below |
| `verify` | no | Checks of the file a step writes. See below |

Steps write `file` artifacts. They only read `issue`, `pr` and `tool` artifacts: `validate` refuses a step that names one in its `outputs`.

Each attempt records a hash of every input it read. A change of an `issue` or `pr` input, such as a request for changes or an answer, asks for a new attempt; a change of a file or a tool's value doesn't, since another step's work is read as it is.

`validate` refuses the kinds and fields of earlier releases, each with a hint: `kind: store` (fab0 0.7 to 0.9), now a `file` at a path in a repository, the runs repository for a working file such as a task list; and `keep` (fab0 0.6).

## `file`

A file or directory in a repository. A file at a location names its `repo` and its `path`. A file that another factory writes names neither: only its `format`.

| Field | Required | Meaning |
|---|---|---|
| `repo` | with `path` | A repository name, or `unit.<field>` |
| `path` | with `repo` | A file or directory, with `{run}` and `{unit}` filled in |
| `format` | no | `yaml` and `json` are parsed, and `markdown` is read by section. Any other value is opaque |

A file with no location is one another factory's step writes: what a [`call`](pipeline.md#call) receives from its child run, or a pipeline [input](pipeline.md#inputs-and-outputs) a caller binds. It is read where its producer wrote it, at the commit of the producer's latest attempt, in this factory's checkout of that repository, so both factories list it in `repos`: the runs repository. Its `format`, with its `schema` and `verify` sections, is the format this factory accepts. A step can't write it.

## `issue`

A part of a tracker item, read and never written by a step.

| Field | Required | Meaning |
|---|---|---|
| `of` | no | `run` (default): the run's work item. `unit`: the current element's item. `parent`: the item the run's item is a sub-issue of, such as the Feature a Story belongs to. A manual run and a child run have no work item |
| `part` | yes | `body`, `title`, `comments`, `labels`, or `field` |
| `field` | with `part: field` | The board field |

## `pr`

| Field | Required | Meaning |
|---|---|---|
| `of` | no | `run` (default): the run's pull request into the base branch, in the home repo. `unit`: the current unit's own pull requests, in the repository it writes first, the runs repository too |
| `part` | yes | `body`, `reviews` (reviews that ask for changes or comment, and people's conversation comments, from every pull request of the unit's branch, oldest first; comments fab0 posts, whose body starts with `<!-- fab0:`, and approvals by `/approve` are left out), or `diff` |

A change of the reviews of a unit's own pull request asks for a new attempt until the unit is merged: after that, the merge has decided.

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
