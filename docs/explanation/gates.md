# Gates

Every transition in a pipeline has a gate. It says who decides that a unit's work is accepted, and who merges it. Gates belong to the pipeline, not to a step, because the same step may need a different gate in another pipeline. The [pipeline reference](../reference/pipeline.md#gate) lists the fields.

## The three gates

| Gate | Who decides | When the work is accepted |
|---|---|---|
| `none` (default) | Nobody: the work moves on | `apply` merges the unit's branch into its parent directly, without a pull request |
| `auto` | An agent's verdict, or a command's exit code | On `approve`, the unit is merged by `apply` (`merge: auto`) or by a person (`merge: human`) |
| `human` | A person | A person merges the unit's pull request, or adds a label to the run's item |

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

- **Through a pull request** (default). The unit's pull request is ready for review, and merging it accepts the work. The `owner` role is whose turn it is.
- **Through a label** (`via: label`), for units without a pull request, such as work recorded only in the tracker. Adding the label to the run's item accepts the work.

To ask for changes, a person leaves a review on the pull request. When the step lists its pull request's reviews among its inputs (a `pr` artifact with `part: reviews`), the review sends the unit back to its agent, with the review in its brief. On their own pull request, GitHub lets a person leave only a **Comment** review, and that counts. A conversation comment doesn't.

## Whoever merges decides

A unit whose work is merged into the branch it targets is done, whatever its gate said. A person who merges an escalated or rejected unit overrides the gate, because the tracker and git are where people's decisions live. For the same reason, reviews on a unit's pull request stop counting once it is merged.

## Questions

An agent may return `questions` when it can't decide something only a person can. The unit then waits, and its questions are posted once on its pull request. A person answers by changing an input: the tracker item, a review on the pull request, or a file. The changed input sends the unit back to its agent. Its failed checks don't count against it meanwhile.

## Gated blocks

A `foreach`, `parallel` or `when` block may have a gate of its own. It gets a branch of its own, its units branch from it, and its gate governs the block's pull request into its parent. A block's agent gate judges the block's units as they are. It isn't retried as a whole: after a rejection or an escalation, a person decides which unit to redo.

## Nobody merges what they shouldn't

Merges happen in two places only: `apply`, within the policy above, and people. The [examples](examples.md) add a merge guard: a Claude Code hook that blocks any merge, push to the base branch or force push that a model issues. `apply` merges through its own git calls, so it isn't blocked.
