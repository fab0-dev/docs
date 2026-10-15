# Artifacts and the ledger

Steps pass work on through **artifacts**, and every attempt is recorded in the **ledger**. Together they let the engine tell whether a unit's work still stands. The [artifact reference](../reference/artifact.md) and the [ledger reference](../reference/ledger.md) list the fields.

## Artifact kinds

fab0 prescribes no formats: a factory chooses them, and may give its own JSON Schema. What fab0 needs to know is where an artifact lives and how to hash it.

| Kind | What it is | Hashed by |
|---|---|---|
| `file` | A file or directory in a repository, with `{run}` and `{unit}` in its path | Its content, at the parent branch's head |
| `issue` | A part of a tracker item: its body, title, labels, comments or a board field | That part's value |
| `pr` | A part of a pull request: its body, its reviews (with people's conversation comments) or its diff | That part's value. A unit's reviews and conversation comments are read from every pull request of its branch, oldest first. fab0's own comments don't count, and a merged pull request's stop counting |
| `tool` | A value an agent reads through a tool call | The call itself: the tool's name and arguments |
| `none` | Nothing to read, for a step whose effect is elsewhere | Nothing |

The engine can't call tools, so an agent reads a `tool` artifact itself, and a change in the outside value doesn't make work stale. `foreach` lists and `when` conditions read file artifacts only.

A list artifact used by `foreach` keeps the factory's own format. Its `elements` say which field of an element is its id, title, repository, `after` and paths.

## When work stands, and when it doesn't

A recorded attempt stands while its inputs and outputs stand. Its ledger entry keeps the hash of every input at the time it ran. The unit is attempted again, with the reason in its brief, when:

- **an input changed** (`stale`), such as a revised spec or a new review or conversation comment;
- **an output it wrote is gone** (`missing`);
- **its checks failed** (`verify`);
- **its gate rejected it** (`rejected`);
- **its branch conflicts with its parent** (`conflict`), or **its required checks fail** (`checks`).

A person's edit of an output isn't a reason: it is reviewed with the rest, and anything that reads the output goes stale.

## Checking outputs

When a unit is recorded, its outputs are checked, cheapest first:

1. **The reply** matches its schema: fab0's base with `summary`, plus `questions` and the step's own `data` schema when the step asks for them. A reply that doesn't is refused, and nothing is recorded; the session gives the agent one more try.
2. **Each output file** exists, parses as its `format` (`yaml` or `json`), and matches its `schema`.
3. **The artifact's own checks** pass: required Markdown `sections`, a `lint` command, or a `script`.

A failed output check is recorded, and the unit goes back to its agent with the errors. When the checks fail more times in a row than the gate's `retry` (default 2), the unit is blocked as `failed` until an input changes. Writes outside the unit's claims are findings too. A change in a repository the unit may not write refuses the record, because it can't be told apart from a person's own work there.

## Keeping or removing

An artifact is `durable` by default and stays in the result. A working file, such as a task list, is `keep: run`: `git.remove-run-artifacts` removes it at the run's end. A per-element file, whose path has `{unit}` or whose repository is the element's, stays. Work that read it still stands, because the engine reads it as it was before its removal.

## The ledger

The ledger is a folder of YAML files, one per attempt and one per auto gate's decision, under `ledger.path` (for example `work/{run}/ledger`). An entry records who ran the attempt, on which branch, at which commit of its parent, the hashes of its inputs and outputs, its checks, its claims, its gate, and its reply.

Entries are written on the unit's branch and travel with the work, through merges, to the run branch and the base. So the ledger is in git, and the base branch holds the history of every run that reached it. A unit is done when its entry is on the branch it targets. The ledger is append-only: an attempt is never rewritten.
