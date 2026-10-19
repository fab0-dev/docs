# Artifacts and the ledger

Steps pass work on through **artifacts**, and every attempt is recorded in the **ledger**. Together they let the engine tell whether a unit's work still stands. The [artifact reference](../reference/artifact.md) and the [ledger reference](../reference/ledger.md) list the fields.

## Artifact kinds

fab0 prescribes no formats: a factory chooses them, and may give its own JSON Schema. What fab0 needs to know is where an artifact lives and how to hash it.

| Kind | What it is | Hashed by |
|---|---|---|
| `file` | A file or directory in a repository, with `{run}` and `{unit}` in its path | Its content, at the parent branch's head |
| `store` | A file a run produces for itself, kept in the run store and never in a repository. A step writes it in its outbox, a folder outside every repository that its brief names | Its latest version: one immutable object per version, named by the hash of its content |
| `issue` | A part of a tracker item: its body, title, labels, comments or a board field | That part's value |
| `pr` | A part of a pull request: its body, its reviews (with people's conversation comments) or its diff | That part's value. A unit's reviews and conversation comments are read from every pull request of its branch, oldest first. fab0's own comments don't count, and a merged pull request's stop counting |
| `tool` | A value an agent reads through a tool call | The call itself: the tool's name and arguments |
| `none` | Nothing to read, for a step whose effect is elsewhere | Nothing |

The engine can't call tools, so an agent reads a `tool` artifact itself, and a change in the outside value doesn't make work stale. `foreach` lists and `when` conditions read `file` and `store` artifacts only.

A `store` artifact's latest version is the output of the most recent attempt that wrote it and passed its checks. A version that failed its checks never becomes the latest, so nothing reads it. A unit of a `foreach` reads its own element's version; any other unit reads the run's. There is one latest version per run, not one per branch: a new version reaches every unit that reads it at once, wherever it works. Briefs show it inline.

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
2. **Each output file** exists, in the unit's checkout or, for a `store` artifact, in its outbox. It parses as its `format` (`yaml` or `json`) and matches its `schema`. A file in the outbox that is no output of the step is a finding.
3. **The artifact's own checks** pass: required Markdown `sections`, a `lint` command, or a `script`.

A failed output check is recorded, and the unit goes back to its agent with the errors. When the checks fail more times in a row than the gate's `retry` (default 2), the unit is blocked as `failed` until an input changes. Writes outside the unit's claims are findings too. A change in a repository the unit may not write refuses the record, because it can't be told apart from a person's own work there.

## Where an artifact lives

A factory chooses each artifact's home, and the engine predefines none:

- **`kind: file`** for what the product keeps, such as code, docs or a spec the team wants beside its code. It reaches the base branch through the unit's pull request.
- **`kind: store`** for a run's working files, such as a task list or a spec that is reviewed and then left behind. It stays out of every product repository, so nothing has to remove it at the run's end, and the product's history shows only the product.

A unit whose outputs are all `store` artifacts, with a human gate, is reviewed in a pull request of the runs repository. See [gates](gates.md#review-pull-requests).

What a [call](connected-factories.md) receives is a `store` artifact of the parent too, but its versions stay in the child's folder of the runs repository: the latest is the latest export the parent accepted. The facts that link a parent run and a child run, `call@*`, `bound@parent`, `export@*` and `ack@*`, are in the ledger beside the attempts. See [link facts](../reference/ledger.md#link-facts).

## The ledger

The ledger of a run is a set of facts in the run store: one per attempt, one per gate decision (an auto gate's, or a person's approving review in the runs repository), and one per claim. An attempt's fact records who ran it, on which branch, at which commit of its parent, the hashes of its inputs and outputs, its checks, its claims, its gate and its reply. The [ledger reference](../reference/ledger.md) lists the fields.

The run store is a folder per run in the **runs repository**, one git repository per product, which every factory of the product shares under its own project key. It holds the run's facts and the objects of its `store` artifacts. It keeps them out of the product repositories, because a product's branches, pull requests and history should show the product's changes only, and because a record that travels with the work through merges is hard to read and never goes away. The engine keeps its own clone of the runs repository, pulls it before it reads a run, and pushes it after each record. People push with their own login, so a commit's author is the person who ran the attempt. Only fab0 writes the runs repository: people read it and review its pull requests, and an approving review is their decision, which `apply` records and then merges. Its root holds the [register](../reference/ledger.md#the-register), which gives each run its id.

Facts and objects are never changed or removed:

- A fact is **create-only**. Writing one whose name exists is refused. That is the store's only concurrency control: when two machines write the same fact, the first one pushed stands, and the other is told.
- An object is named by the hash of its content, so writing the same content twice is a no-op, and a read fails when the content doesn't match its name.
- The runs repository's ruleset blocks force pushes to `main` and its deletion, so its history stays append-only. See [set up GitHub](../how-to/github-setup.md).

`record` commits a unit's changes on its branch, then appends the attempt's fact with `heads`: per repository, the commit the branch is at, when the branch has commits its parent lacked. A unit is done when those commits are in the branch it merges into. It is also done when GitHub reports its pull request merged at those commits, which covers a person's squash merge, since that leaves the commits themselves out of the parent. An attempt with no `heads` changed nothing, so nothing is merged, and its gate decides: `none` passes, an `auto` gate passes when it approves, and a `human` gate passes through a label or a review pull request.

A person's own commit on a unit's review pull request is recorded too, as the next attempt, by that person. Their version of the outputs is checked like an agent's, and it becomes the latest version that later steps read. So a product owner can fix a spec in place, and the record still says who wrote what.
