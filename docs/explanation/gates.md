# Gates

Every step and call declares its **definition of done**, `done`: what must hold for it to be done. Its **gate** says who makes that hold: nobody, an agent or a command, or a person. Together they decide everything about a step's acceptance, its merge included, and no rule above them reserves anything for anyone. Gates and definitions belong to the pipeline, not to a step, because the same step may need a different one in another pipeline. The [pipeline reference](../reference/pipeline.md#gate) lists the fields.

## Definitions of done

A definition is one of two kinds:

| Kind | Holds when |
|---|---|
| `pr: {state: approved}` | The gate's owner approved the step's pull request at the head the step recorded. `apply` then merges it |
| `pr: {state: merged}` | The step's pull request is merged |
| `issue: {status: …}` | An issue reaches the status: the step's own Pipeline Step (the default), which `apply` sets `Done` once the step's work is in; a call's child run (`run: child`); or a named issue, found by `repo`, `type` and `fields` |

`pr` may name the `repo` and `head` of another pull request than the step's own. Strings may use `{run}` and `{step}`.

`validate` refuses a step or call without `done`, a `pr` definition on a step that writes no repository and so has no pull request, and `approved` without a person deciding in a pull request. Every step defines its done because the engine and the inbox read it to know when a step is done, and so what comes next. Before 0.10, a merge decided that by convention, which nobody could read in the pipeline.

Two kinds are enough for now. Others wait until a run needs them.

## The three gates

| Gate | Who decides | With a `pr` definition | With an `issue` definition |
|---|---|---|---|
| `none` (default) | Nobody: the work moves on | `apply` merges the unit's branch into its parent; with `merged`, a person merges | `apply` sets the step `Done` |
| `auto` | An agent's verdict, or a command's exit code | On approval, `apply` merges once the required checks pass; with `merged`, a person merges | On approval, `apply` sets the step `Done` |
| `human` | A person, `via` a pull request, an issue, the prompt or a label | `apply` merges once the owner approves (`approved`), or the owner merges (`merged`) | `apply` sets the step `Done` once the owner decides |

Agents do as much of the work as the gates allow. People take part where a gate is `human`, or where an `auto` gate hands over to them. A pipeline names a person only for decisions that need one.

## Auto gates

An auto gate is an agent or a command:

- **An agent**, such as a reviewer, gets a brief with the unit's inputs, the producer's summary and the command that shows the change. It replies with a verdict: `approve`, `reject` or `escalate`, with reasons and findings. It runs on the gate's own model class, else the step's, so a factory can review on a different model from the one that produced the work.
- **A command**, such as a project's own check, runs in the unit's worktree. Exit 0 approves; anything else rejects, with the command's output as the finding.

What follows a verdict:

- `approve`: `apply` marks the unit's pull request ready, waits for its required checks, and merges it into its parent, unless the definition is `pr: merged`, which leaves the merge to a person.
- `reject`: the unit is attempted again with the findings in its brief, and its Revision rises, up to `retry` times in a row (default 2). After that, `then` decides: `human` (default) hands it to a person, `fail` stops the unit.
- `escalate`: a person decides. The gate's reasons are posted on the unit's pull request.

## Human gates

A human gate waits for the gate's `owner`, a role. How they decide is its `via`:

| `via` | The owner decides by | For |
|---|---|---|
| `pr` (default) | Reviewing the unit's pull request: an approving review or `/approve` approves it, as `approved` asks, or merging it, as `merged` asks | An essential review, such as a spec |
| `issue` | Setting the step's Pipeline Step `Done` | A decision recorded on the run tracker |
| `prompt` | Confirming in the run session, with no pull request | A small, transactional decision, such as a task list |
| `label` | Adding a label to the run's item | Work recorded only in the tracker |

**In a pull request.** Only an approval by someone in the owner role, of the head the step recorded, counts. GitHub doesn't let a person approve a pull request they opened, and fab0 opens pull requests with the login of whoever runs it, often the reviewer. So that person approves with `/approve` instead: a conversation comment, or a Comment review, whose first line is `/approve` or `/approved`. Any other review or conversation comment asks for changes, when the step lists its pull request's reviews among its inputs (a `pr` artifact with `part: reviews`): the unit goes back to its agent, with them in its brief. A later request for changes takes an approval back.

A person may also fix the files on the step's branch themselves. Their edit is then in what is merged, and since `apply` merges only the head the step recorded, the owner who edits merges it.

**At the prompt.** `/fab0:run` shows what the unit produced and asks the person whether to accept it. It records the answer with `fab0-resolve confirm <run> <unit>`, or `--reject` with what should change, which sends the unit back to its agent with those words. Only a login in the owner role may confirm; for anyone else, the unit waits for its owner. A pull request would add a review round to a decision that needs only a yes or a no, and a run whose plan waited in one stalled: so the examples confirm plans at the prompt.

## Questions

An agent may return `questions` when it can't decide something only a person can. The unit then waits, and its questions are posted once on its pull request. A unit whose attempt changed nothing has no pull request, so its questions are posted on the run's item instead, and so is an escalation. A person answers by changing an input: the tracker item, a review or a conversation comment on the pull request, or a file. The changed input sends the unit back to its agent. Its failed checks don't count against it meanwhile.

## Accepting what a child hands back

A [call](connected-factories.md)'s gate decides what its child run hands back, once that run reaches the call's `done`, `issue: {run: child, status: …}`:

- `none` accepts it. The child already checked it against the format the call accepts.
- An `auto` gate is an agent, an acceptor, that judges it against what the call asked for. A command can't judge a child's work.
- A `human` gate is decided `via: issue`, by setting the call's Pipeline Step `Done`, or `via: prompt`. A call has no pull request of its own, so `via: pr` and `via: label` don't apply.

A rejection opens the child run again, and the child units that produced what was rejected rework under their own gates, whose `retry` and `then` decide what follows. So a call's gate takes neither.

## Gated blocks

A `foreach`, `parallel` or `when` block may have a gate of its own. It gets a branch of its own, its units branch from it, and its gate governs the block's pull request into its parent. A block's agent gate judges the block's units as they are. It isn't retried as a whole: after a rejection or an escalation, a person decides which unit to redo.

## Who merges

Who merges follows the gate and `done`, and nothing else:

| The gate and `done` | Who merges the unit |
|---|---|
| `done: {pr: {state: merged}}` on the unit's own pull request, whatever the gate | A person |
| Gate `none` | `apply`, directly |
| An `auto` gate that approved | `apply`, once the required checks pass |
| A person's decision by label, issue or prompt | `apply` |
| `done: {pr: {state: approved}}`, once the owner approved | `apply` |

The run's merge into the base branch is the pipeline's end. With `pr.merge` in `onEnd`, `apply` merges each run pull request through GitHub once its required checks pass, after opening any a repository still lacks, so a ruleset that requires a pull request into the base applies to it. With `pr.ready`, it marks them ready, and a person merges them.

No rule above the gates holds anything back for a person. `git.auto_merge`, `allow_base`, the default that only a person merges into the base branch, and a gate's `merge` are gone in 0.10, and `validate` refuses them with a hint: they were a second place that decided, which the pipeline didn't show. A person decides only where a gate is `human`.

A unit whose recorded commits are already in the branch it merges into is done, whoever merged them. So a person can still merge a unit's pull request by hand; the engine then reads the merge, and moves on.

A model never merges by itself, so merges happen in two places only: `apply`, which merges what the gates leave to it, and people. The [examples](examples.md) add a merge guard: a Claude Code hook, with deny rules in the settings, that blocks any merge, push to the base branch or force push that a model issues. `apply` merges through its own git and GitHub calls, so it isn't blocked. A person may lift the deny rule in their own session, to let Claude merge after they confirm at the prompt. A branch whose ruleset refuses `apply`'s merge, such as a protected base branch, stops the unit, so units merge into run branches, and only the run's pull requests reach a protected base.
