# Gates

Every transition in a pipeline has a gate. It says who decides that a unit's work is accepted, and who merges it. Gates belong to the pipeline, not to a step, because the same step may need a different gate in another pipeline. The [pipeline reference](../reference/pipeline.md#gate) lists the fields.

## The three gates

| Gate | Who decides | When the work is accepted |
|---|---|---|
| `none` (default) | Nobody: the work moves on | `apply` merges the unit's branch into its parent directly, without a pull request |
| `auto` | An agent's verdict, or a command's exit code | On `approve`, the unit is merged by `apply` (`merge: auto`) or by a person (`merge: human`) |
| `human` | A person | A person merges the unit's pull request in a product repository, approves its review pull request in the runs repository for a unit whose outputs are all in the run store, or adds a label to the run's item |

Agents do as much of the work as the gates allow. People take part where a gate is `human`, or where an `auto` gate hands over to them.

## Auto gates

An auto gate is an agent or a command:

- **An agent**, such as a reviewer, gets a brief with the unit's inputs, the producer's summary and the command that shows the change. It replies with a verdict: `approve`, `reject` or `escalate`, with reasons and findings. It runs on the gate's own model class, else the step's, so a factory can review on a different model from the one that produced the work.
- **A command**, such as a project's own check, runs in the unit's worktree. Exit 0 approves; anything else rejects, with the command's output as the finding.

What follows a verdict:

- `approve`: with `merge: auto`, `apply` marks the unit's pull request ready, waits for its required checks, and merges it. The merge stays within the project's `git.auto_merge` policy, which allows run branches only unless a project explicitly allows its base branch. With `merge: human` (the default), the pull request becomes ready, and a person merges it.
- `reject`: the producing step runs again with the findings in its brief, up to `retry` times (default 2). After that, `then` decides: `human` (default) hands it to a person, `fail` stops the unit.
- `escalate`: a person decides. The gate's reasons are posted on the unit's pull request.

## Human gates

A human gate waits for a person:

- **Through a pull request** (default). The unit's pull request is ready for review, and merging it accepts the work. The `owner` role is whose turn it is. A unit whose outputs are all in the run store gets a review pull request in the runs repository instead, where an approving review accepts it; see [review pull requests](#review-pull-requests).
- **Through a label** (`via: label`), for units without a pull request, such as work recorded only in the tracker. Adding the label to the run's item accepts the work.

To ask for changes, a person leaves a review or a conversation comment on the pull request. When the step lists its pull request's reviews among its inputs (a `pr` artifact with `part: reviews`), the review or comment sends the unit back to its agent, with it in its brief. On their own pull request, GitHub lets a person leave only a **Comment** review, and that counts. A plain conversation comment counts too, whoever the author is, except the comments fab0 itself posts (their body starts with `<!-- fab0:`).

## Review pull requests

A unit whose work is all in the run store, such as a spec and its task list, has nothing in a product repository to review. It gets its pull request in the runs repository instead, when three things hold: its gate is `human` and decided by a pull request (not `via: label`), every output of its step is a `store` artifact, and the step writes no repository. `validate` asks for `store.github` for such a step, since the pull request lives there. A human-gated step that also writes a repository keeps its pull request in that repository.

- **The branch** is `fab0/<project>/<run>/<unit>`, one per unit. It holds readable copies of the unit's outputs under `runs/<project>/<run>/review/<unit>/`. `apply` adds one commit per attempt, so the pull request shows what changed since the last review.
- **Asking for changes** works as for any unit: a Comment review or a conversation comment brings a new attempt, with the review in its brief, because the unit's own `pr` artifact is this pull request.
- **A person's edit.** A person may fix the files on the branch directly. `apply` records their commit as the next attempt, by them, checks it like an agent's work, and makes it the latest version that later steps read.
- **An approving review decides.** The gate passes when someone in the owner role approves the commit of the branch that holds the latest attempt's outputs. GitHub doesn't let a person approve a pull request they opened, and fab0 opens review pull requests with the login of whoever ran it, so the person who ran it approves with `/approve` instead: a conversation comment, or a Comment review, whose first line is `/approve`. It approves the version the pull request holds when it is given, and it is no feedback: it brings no new attempt. `apply` then records the approval as the attempt's gate decision, in the ledger, and merges the pull request at that commit itself. Nobody merges or pushes in the runs repository by hand: it is fab0's, and people only review there. An approval of an older commit, or by anyone else, decides nothing, and a later review that asks for changes takes an approval back. If a branch protection refuses `apply`'s merge, the decision still stands, and `apply` says that a person merges it. A merge by an owner still decides too, as it did before 0.9.

## Whoever merges decides

A unit whose work is merged into the branch it targets is done, whatever its gate said. A person who merges an escalated or rejected unit overrides the gate, because the tracker and git are where people's decisions live. For the same reason, reviews and conversation comments on a unit's pull request stop counting once it is merged. A review pull request in the runs repository is the exception: there a review decides, and the merge is `apply`'s, after it has recorded the decision.

## Questions

An agent may return `questions` when it can't decide something only a person can. The unit then waits, and its questions are posted once on its pull request. A unit whose attempt changed nothing has no pull request, so its questions are posted on the run's item instead, and so is an escalation. A person answers by changing an input: the tracker item, a review or a conversation comment on the pull request, or a file. The changed input sends the unit back to its agent. Its failed checks don't count against it meanwhile.

## Acknowledging what a child hands back

A [call](connected-factories.md)'s gate is its acknowledgement of each output its child run hands back. `none` accepts one that is in the format the call accepts, which the child checked before handing it back. An `auto` gate is an agent that judges it. A `human` gate is a review pull request in the runs repository, as for a store-only unit: an approving review by the gate's owner, or `/approve` on a pull request they opened, accepts, and `apply` merges; a review that asks for changes, or comments, rejects. A rejection sends the output back to the child, whose own `retry` and `then` decide what follows, so a call's gate takes neither.

## Gated blocks

A `foreach`, `parallel` or `when` block may have a gate of its own. It gets a branch of its own, its units branch from it, and its gate governs the block's pull request into its parent. A block's agent gate judges the block's units as they are. It isn't retried as a whole: after a rejection or an escalation, a person decides which unit to redo.

## Who merges

Merge authority comes from the gates and the merge policy alone. A person approves only where a gate is `human`. Elsewhere `apply` merges what an `auto` gate approved, what a `none` gate allows, and a review pull request a person approved, within the project's `git.auto_merge`. Into the base branch that needs `into: [base]` with `allow_base: true`: with it, and `pr.merge` in place of `pr.ready` at the end of the pipeline, a run reaches the base branch once every gate has passed, and nobody merges. Without it, the default, a person merges the run's pull request.

A model never merges by itself, so merges happen in two places only: `apply`, which merges what the gates and the policy allow, and people. The [examples](examples.md) add a merge guard: a Claude Code hook that blocks any merge, push to the base branch or force push that a model issues, so every merge goes through `apply`. `apply` merges through its own git and GitHub calls, so it isn't blocked. A branch whose ruleset asks for a person's review refuses `apply`'s merge, and the unit shows as blocked, so the rulesets have to agree with the gates.
