# Artifacts

Steps pass work on through **artifacts**. GitHub carries them: git holds the content and its history, issues hold discovery and metadata, and pull requests hold review and acceptance. A run's record is on the [run tracker](tracker.md), not beside its artifacts. The [artifact reference](../reference/artifact.md) lists the fields.

## Artifact kinds

fab0 prescribes no formats: a factory chooses them, and may give its own JSON Schema. What fab0 needs to know is where an artifact lives and how to read it.

| Kind | What it is | Read |
|---|---|---|
| `file` | A file or directory at a `repo` and a `path`, with `{run}` and `{unit}` in its path. A file another factory writes names only its `format` | Within a run, at the head of the unit's parent branch. Across factories, at the commit of its producer's latest attempt |
| `issue` | A part of a tracker item: its body, title, labels, comments or a board field | As the tracker has it now |
| `pr` | A part of a pull request: its body, its reviews (with people's conversation comments) or its diff | As GitHub has it now. A unit's reviews and conversation comments are read from every pull request of its branch, oldest first. fab0's own comments don't count |
| `tool` | A value an agent reads through a tool call | By the agent itself: the engine can't call tools |
| `none` | Nothing to read, for a step whose effect is elsewhere | — |

`foreach` lists and `when` conditions read `file` artifacts only, because the engine parses them itself. A list keeps the factory's own format: its `elements` say which field of an element is its id, title, repository, `after` and paths.

## Where a file lives

A factory chooses each file's home, and the engine predefines none:

- **In a product repository**, for what the product keeps: code, docs, or a spec the team wants beside its code. It reaches the base branch through the unit's pull request and the run's.
- **In the runs repository**, for what a run produces for itself: a spec that is reviewed and then left behind, a task list, a contract between factories, a report. The examples keep them under `runs/<factory>/<run>/`. So the product's history shows only the product, and nothing has to remove these files at the run's end.

A step that a person reviews in a pull request must write files in a repository, the runs repository included, because a pull request needs a change to show. `validate` refuses a step decided `via: pr` that writes none.

## The runs repository

The runs repository is one per product, and every factory of the product shares it. It holds two things:

- the run tracker's issues: every run's Pipeline Run and Pipeline Steps;
- the files runs produce for themselves, when a factory lists it in `repos`, like any other repository.

As an entry of `repos` it is ordinary: a run gets a run branch there, its units get branches and pull requests there, and its files reach `main` there as the pipeline's end says. A step that writes a spec there has its own pull request there, into the run branch, and a person reviews it like any other. Factories that share it give their branches names of their own (`git.branches`), because a child run has its parent's id. See [branches and merges](branching.md).

Because it is shared, it is also where factories exchange files: a file a call binds or receives is read in each factory's own checkout of it. See [connected factories](connected-factories.md#files-across-factories).

## Reading an input

Within a run, a unit reads its inputs at its parent's head: the run branch, or the branch of a gated block around it. A producer's work is merged there once it is done, so that head holds the commit the producer was accepted at, which is its Output. A unit sees exactly what was accepted before it, and its fact records the commit it started from.

Across factories, there is no common branch. A file the child hands back, or the parent binds, is read at the commit of its producer's latest attempt, which that attempt's fact names. A file a call receives counts only once the call has accepted it.

## When work is redone

A unit is attempted again, with the reason in its brief, when:

- **its checks failed** (`verify`);
- **an output it wrote is gone** (`missing`);
- **an input people write changed** (`stale`): a review or a conversation comment on its pull request, which asks for changes, or an issue it reads, such as an answer to its questions;
- **its gate or a person rejected it** (`rejected`), or a parent rejected what it handed back;
- **its branch conflicts with its parent** (`conflict`), or **its required checks fail** (`checks`).

Its Pipeline Step's Revision counts each attempt. Once its own pull request is merged, the reviews on it stop asking for rework.

A change to a file another step produced is no reason. Before 0.10 the engine compared the hash of every input on every evaluation, and reworked a step whose input had changed, even one that was done. That is dropped until a run needs it (P8): a step reworks when someone or something asks it to, and nothing else.

A person's edit of an output isn't a reason either. Their edit on the unit's branch is part of what is merged, so it is reviewed with the rest.

## Checking outputs

When a unit is recorded, its outputs are checked, cheapest first:

1. **The reply** matches its schema: fab0's base with `summary`, plus `questions` and the step's own `data` schema when the step asks for them. A reply that doesn't is refused, and nothing is recorded; the session gives the agent one more try.
2. **Each output file** exists in the unit's checkout, parses as its `format` (`yaml` or `json`) and matches its `schema`.
3. **The artifact's own checks** pass: required Markdown `sections`, a `lint` command, or a `script`.

A failed output check is recorded, and the unit goes back to its agent with the errors. When the checks fail more times in a row than the gate's `retry` (default 2), the unit is blocked as `failed`. Writes outside the unit's claims are findings too. A change in a repository the unit may not write refuses the record, because it can't be told apart from a person's own work there.

A file the parent takes from a child is also checked against the parent's accepted format, in the child, when it is recorded: a mismatch fails the attempt where it can be fixed.

## Why there is no ledger

Up to 0.9, a run's record was a ledger: create-only facts in a run store in the runs repository, with a register that gave each run its id, link facts between factories (`call@`, `bound@`, `export@`, `ack@`), store objects for working files, an outbox for agents to write them, and review branches to show them to people. The engine alone read it.

A real connected run showed what that cost. A child's plan waited in a review pull request that already carried its approval, and the run didn't move on: it moved through conventions the engine kept to itself, which nobody could see where they work. So 0.10 puts each part where GitHub already keeps that kind of thing:

| What the ledger held | Where it is in 0.10 |
|---|---|
| A run's id and its item (the register) | The Pipeline Run: its number is the run id, and it is a sub-issue of its item |
| Attempts, gate decisions and claims | Facts: one comment each on the unit's Pipeline Step, a line for people and a YAML block for the engine |
| Links between a parent and a child | The child's Pipeline Run, a sub-issue of the parent's, with a `call` comment and `rejected-<n>` comments |
| Working files, as store objects and outbox files | Files in the runs repository, an entry of `repos` |
| Review branches for store outputs | The step's own pull request, in the repository it writes |

A fact is still written once: the first comment of a name stands, and later ones of that name are ignored. It is checked against its schema, as the ledger's entries were. Only comments by the runs repository's owner, members and collaborators count, since anyone may comment on a public repository. The [run tracker reference](../reference/tracker.md) lists the facts and their fields, and [upgrade from 0.9](../how-to/upgrade-from-0.9.md) says what replaces each removed key.
