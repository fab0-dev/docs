# What fab0 is

fab0 is a toolkit for building and operating software factories. A **factory** is a set of pipelines that turn a work item into a result: a Story into merged code, a bug report into a triaged issue, a Docs issue into published pages. fab0 gives you the parts to build one, and the engine that runs it. It isn't a factory itself.

## Building blocks

A factory lives in a project's `.fab0/` directory, as short YAML files:

| Block | File | What it is |
|---|---|---|
| Project | `.fab0/fab0.yaml` | The repositories, the people and their roles, the tracker of work items, the run tracker, the git workflow, the model classes and the pipelines |
| Pipeline | `.fab0/pipelines/<name>.yaml` | What starts a run, the actions at its start and end, and a tree of steps, each with its gate and its definition of done |
| Step | `.fab0/steps/<name>.yaml`, or inline in a pipeline | One piece of work, done by an agent, an action, a command or a tool |
| Artifact | `.fab0/artifacts/<name>.yaml` | Something steps read and write: a file in a repository, a part of an issue or a pull request, a tool's value |

Around the steps are the **operators**: a sequence, `foreach` over a list, `parallel` branches, `when` for a condition, and `call`, which runs a pipeline of a [connected factory](connected-factories.md). Every step and call declares its **definition of done**, `done`: a pull request's state or an issue's status. Its **gate**, `none`, `auto` or `human`, says who makes that definition hold. See [pipelines and steps](pipelines.md) and [gates](gates.md).

The engine, `fab0-resolve`, reads these files at run time. Nothing is compiled. It works out which work is due, hands it to a Claude Code session, checks what comes back, and performs every write to git and GitHub that can be done exactly. Each run is an issue on the **run tracker**, with an issue for each of its steps, and those issues carry the run's state from step to step and from factory to factory. See [running a pipeline](execution.md) and [the tracker](tracker.md).

## Principles

fab0's design follows a few principles. Each has a reason.

- **Building blocks, not a factory.** The core holds only what executes, validates and connects pipelines. Agents, skills, artifact formats and processes belong to a factory, because no single way of working suits every team.
- **Any agent can be a step.** A step names any Claude Code agent. fab0 passes everything the agent needs in a brief, so the agent doesn't have to know fab0.
- **The model doesn't route.** The engine decides what runs next; the session only carries it out. Routing by a deterministic program is repeatable and can be checked.
- **GitHub is the truth.** Git holds the content, the run's issues on the run tracker hold its state and history, and pull requests hold review. The board is a projection. So people see where a run is where they already work, and every machine and every factory reads the same state.
- **Configuration decides.** Every step defines its done, and its gate alone says who makes it hold. Nothing that decides is a convention of the engine, because a rule nobody can read in the pipeline can't be reviewed or changed. See [gates](gates.md).
- **A product repository receives only product changes.** What a run produces for itself, such as a spec and its task list, is a file in the runs repository, and its record is on the run tracker. So a product's history and pull requests show only the product. See [artifacts](artifacts.md).
- **Verify at the source, cheaply.** Returns are checked against schemas, outputs by linters, and judgment by a review agent, each as soon as the work is done.
- **Agents do as much as the gates allow.** A person takes part only where a gate is `human`, or where an `auto` gate hands over. A small, transactional decision is confirmed at the prompt, with no pull request. A model never merges by itself: `apply` merges what a step's gate and `done` leave to it, and a person merges where they leave it to a person. See [who merges](gates.md#who-merges).
- **A run works on its own branch.** Steps work on sub-branches that merge into it, so work runs in parallel. Only the finished run reaches the base branch, through its pull request, as the pipeline's end says.
- **Dependencies are respected wherever they are declared:** in the data steps pass, in the order a pipeline gives, in the files a step claims, and in the tracker's own relations. See [dependencies and blocking](dependencies.md).

## Glossary

| Term | Meaning |
|---|---|
| **factory** | A project's `.fab0/`: its pipelines, steps and artifacts, with the agents and skills they use. Its name on the run tracker is its home repository's name |
| **home repo** | The repository that holds `.fab0/` |
| **item** | A work item on the tracker, such as a Story or a bug report, that a run starts from |
| **tracker** | Where the work items are: their types, labels, relations and board, set up under `tracker` in `fab0.yaml`. Not the run tracker |
| **run** | One execution of a pipeline for one item. Its **run id** is the number of its Pipeline Run; a child run carries its parent's. A manual run's id is a name a person gives. See [run ids](pipelines.md#run-ids) |
| **run tracker** | Where each run's state and history are kept, set up under `tracking` in `fab0.yaml`: a Pipeline Run for each run and a Pipeline Step for each of its units, with their fields, assignees and comments. GitHub issues are the first kind. See [the tracker](tracker.md) |
| **Pipeline Run** | The issue type of a run on the run tracker: a sub-issue of the item the run started from, or of its parent's Pipeline Run for a child run |
| **Pipeline Step** | The issue type of one unit of a run, a sub-issue of its Pipeline Run. Its fields hold the unit's state, and its comments hold the unit's facts |
| **runs repository** | The repository that every factory of a product shares. It holds the run tracker's issues and, as an ordinary entry of `repos`, the files runs produce for themselves, such as specs and task lists |
| **position** | One line that says where a run is: what each part of it is doing or waits on |
| **step** | One piece of work, done by exactly one **executor**: an agent, an action, a command or a tool |
| **unit** | A step as it runs: one step, or one step for one element of a `foreach`. Each unit has its own branch, attempts, gate and Pipeline Step. Its branch gets a commit only when the unit changes something |
| **attempt** | One go at a unit. A unit is attempted again when its checks fail, its gate or a person rejects it, a person asks for changes, or its branch conflicts or its checks fail before a merge |
| **Revision** | A unit's attempt count, a field of its Pipeline Step, raised on each rework |
| **definition of done** | A step's or call's `done`: the pull request state (`approved` or `merged`) or the issue status that makes it done. Every step and call declares one |
| **gate** | Who makes a step's definition of done hold: `none`, `auto` or `human` |
| **Output** | Where a unit's result is, a field of its Pipeline Step: its pull request while it is in review, then the commit it was accepted at |
| **fact** | One attempt, gate decision or claim of a unit, written once as a comment on its Pipeline Step: a line for people and a YAML block for the engine |
| **artifact** | Something steps pass on: a file in a repository, a part of an issue or pull request, a tool's value, or nothing |
| **action** | A built-in operation of fab0 on git or the tracker, such as opening the run's pull request. The engine performs actions itself |
| **run branch** | The branch a run works on, `fab0/<run>/base` by default. Once it has work, its pull request into the base branch is the run's result |
| **hand-out** | What the engine gives the session for a unit: its branches, its worktree, its brief, the schema of its reply |
| **brief** | The text an agent receives: its inputs, what to write where, what it may change, and how to reply |
| **claim** | The paths a unit may write. Units whose claims overlap don't run at the same time. Taking an attempt is claimed too: its Pipeline Step is assigned to the session's login, with a claim fact that names the machine, so two machines never run the same attempt |
| **connected factory** | Another repository with a factory of its own, which this factory calls. It stays complete on its own: its own wiring, agents, people and runs |
| **parent**, **child** | The run that holds a `call`, and the run it starts in a connected factory |
| **call** | A pipeline node that starts a child run, as a Pipeline Run under the parent's, binds its inputs, and accepts or rejects what it hands back |
| **binding** | What a call passes to a child's input: a file of the parent, which the child reads where the parent wrote it |
| **acceptance** | The call's gate deciding what a child run handed back, once that run is done. A rejection opens the child run again |
| **example** | A complete factory in [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples), to copy into a project. See [examples](examples.md) |

## Where to go next

- To use a ready-made factory, see [use an example](../how-to/use-an-example.md).
- To build your own, see [build your first factory](../how-to/build-your-first-factory.md).
- Coming from fab0 0.9, see [upgrade from 0.9](../how-to/upgrade-from-0.9.md).
- To look up a field, see the [reference](../index.md#reference).
