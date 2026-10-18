# What fab0 is

fab0 is a toolkit for building and operating software factories. A **factory** is a set of pipelines that turn a work item into a result: a Story into merged code, a bug report into a triaged issue, a Docs issue into published pages. fab0 gives you the parts to build one, and the engine that runs it. It isn't a factory itself.

## Building blocks

A factory lives in a project's `.fab0/` directory, as short YAML files:

| Block | File | What it is |
|---|---|---|
| Project | `.fab0/fab0.yaml` | The repositories, the people and their roles, the tracker, the git policy, the model classes and the pipelines |
| Pipeline | `.fab0/pipelines/<name>.yaml` | What starts a run, the actions at its start and end, and a tree of steps |
| Step | `.fab0/steps/<name>.yaml`, or inline in a pipeline | One piece of work, done by an agent, an action, a command or a tool |
| Artifact | `.fab0/artifacts/<name>.yaml` | Something steps read and write: a file in a repository, a file kept in the run store, a part of an issue or a pull request, a tool's value |

Around the steps are the **operators**: a sequence, `foreach` over a list, `parallel` branches, `when` for a condition, and `call`, which runs a pipeline of a [connected factory](connected-factories.md). Every transition has a **gate**: `none`, `auto` or `human`. See [pipelines and steps](pipelines.md) and [gates](gates.md).

The engine, `fab0-resolve`, reads these files at run time. Nothing is compiled. It works out which work is due, hands it to a Claude Code session, checks what comes back, and performs every write to git and the tracker that can be done exactly. See [running a pipeline](execution.md).

## Principles

fab0's design follows a few principles. Each has a reason.

- **Building blocks, not a factory.** The core holds only what executes, validates and connects pipelines. Agents, skills, artifact formats and processes belong to a factory, because no single way of working suits every team.
- **Any agent can be a step.** A step names any Claude Code agent. fab0 passes everything the agent needs in a brief, so the agent doesn't have to know fab0.
- **The model doesn't route.** The engine decides what runs next; the session only carries it out. Routing by a deterministic program is repeatable and can be checked.
- **Git is the truth for content; the tracker is the truth for human decisions.** Branches, pull requests and merges carry the work. Labels, relations and reviews carry what people decide. The board is a projection of both.
- **A product repository receives only product changes.** What a run produces for itself (its ledger, and working files such as a task list) goes into the run store, a repository of its own. So a product's history and pull requests show only the product, and a run leaves nothing behind to clean up. See [artifacts and the ledger](artifacts-and-ledger.md).
- **Verify at the source, cheaply.** Returns are checked against schemas, outputs by linters, and judgment by a review agent, each as soon as the work is done.
- **Agents do as much as the gates allow.** People take part where a gate is `human`, or where an `auto` gate hands over.
- **A run works on its own branch.** Steps work on sub-branches that merge into it, so work runs in parallel. Only the finished run reaches the base branch, through a pull request a person merges.
- **Dependencies are respected wherever they are declared:** in the data steps pass, in the order a pipeline gives, in the files a step claims, and in the tracker's own relations. See [dependencies and blocking](dependencies.md).

## Glossary

| Term | Meaning |
|---|---|
| **factory** | A project's `.fab0/`: its pipelines, steps and artifacts, with the agents and skills they use |
| **home repo** | The repository that holds `.fab0/` |
| **run** | One execution of a pipeline for one work item. Its **run id** is the tracker item's number, or a name a person gives |
| **step** | One piece of work, done by exactly one **executor**: an agent, an action, a command or a tool |
| **unit** | A step as it runs: one step, or one step for one element of a `foreach`. Each unit has its own branch, attempts and gate. Its branch gets a commit only when the unit changes something |
| **attempt** | One go at a unit. A unit is attempted again when its inputs change, its checks fail, or its gate rejects it |
| **gate** | The transition after a step or a block: `none`, `auto` or `human` |
| **artifact** | Something steps pass on: a file in a repository, a file in the run store, a part of an issue or pull request, a tool's value, or nothing |
| **action** | A built-in operation of fab0 on git or the tracker, such as opening the run's pull request. The engine performs actions itself |
| **run branch** | The branch a run works on, `fab0/<run>/base` by default. Once it has work, its pull request into the base branch is the run's result |
| **hand-out** | What the engine gives the session for a unit: its branches, its worktree, its brief, the schema of its reply |
| **brief** | The text an agent receives: its inputs, what to write where, what it may change, and how to reply |
| **ledger** | The record of a run: one fact per attempt, gate decision and claim, kept in the run store |
| **run store** | Where a run keeps what it produces for itself: its ledger, and the artifacts of kind `store`. The engine alone reads and writes it |
| **runs repository** | The git repository that holds the run store, one per product, shared by its factories. Each factory's runs are under their own project key |
| **claim** | The paths a unit may write. Units whose claims overlap don't run at the same time. Taking an attempt of a unit is also claimed, as a fact in the run store, so two machines never run the same attempt |
| **connected factory** | Another repository with a factory of its own, which this factory calls. It stays complete on its own: its own wiring, agents, people and runs |
| **parent**, **child** | The run that holds a `call`, and the run it starts in a connected factory |
| **call** | A pipeline node that starts a child run, binds its inputs, and receives and acknowledges what it hands back |
| **binding** | What a call passes to a child's input: an artifact of the parent |
| **export** | One version of a child's output, handed back once the unit that wrote it is done |
| **acknowledgement** | The parent's answer to an export, accepted or rejected, which the call's gate decides |
| **join** | A call is done once every output it waits for has an accepted version. Then the parent's next step starts |
| **example** | A complete factory in [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples), to copy into a project. See [examples](examples.md) |

## Where to go next

- To use a ready-made factory, see [use an example](../how-to/use-an-example.md).
- To build your own, see [build your first factory](../how-to/build-your-first-factory.md).
- To look up a field, see the [reference](../index.md#reference).
