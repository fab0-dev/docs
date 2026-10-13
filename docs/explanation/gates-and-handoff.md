# Gates and handoff

In a team, one run passes through several people, each on their own machine and often in different repositories. The rule is: **nothing that lives on one machine is handed to another.**

No session, transcript, local state or claim crosses machines. A person picks a run up with exactly what is on GitHub: the issue, the merged artifacts, the open pull requests and their reviews. The resolver rebuilds the brief from those every time, so it doesn't matter who ran the previous stage, or where.

## Gates

- **`none`**: the pipeline moves on.
- **Agent gate** (`gate: {agent: fab0:reviewer, model: deep}`): a second agent, different from the producer, returns a review: `approve`, `escalate` or `reject`, with reasons and findings.
  - `reject` runs the producer again with the findings in its brief. This happens at most twice; the next reject escalates.
  - `escalate` hands the stage to a person.
  - This is fab0's only rework loop. There is no loop construct in pipelines.
- **`human`**: the orchestrator pushes the stage branch, opens or updates its pull request and stops with `wait`.
  - **Approval is merging that pull request.** Branch protection decides who may merge and which reviews are required.
  - When the owner runs the stage again, the requested-changes reviews on the pull request go into the brief.
  - There is no approve command, and fab0 never merges.

A stage has one gate. A `foreach` can add `gate: human` for each element, which is how a task gets both an agent review and a human merge.

### Clarification

An agent stage may return `questions` when its stage allows it (`return: {questions: optional}`). The orchestrator then:

1. opens the pull request as an unreviewed draft;
2. posts the questions as one comment on it;
3. assigns the item to the stage's owner, and stops.

The person answers by editing the artifact or the issue, or with a pull request review, and the stage runs again. Comments are never read back; only reviews are.

### Done

A task or a run is done when its last human-gated pull request is merged, and the resolver reads that from GitHub. Issues close as a consequence: `Closes #413` in a task pull request, and `Closes #412` in the deliver pull request. An issue closed by hand without a merged pull request is reported, not counted.

## The unit of handoff is a stage pull request

A person's run executes the consecutive stages they own, on their machine, and ends at the next human gate. Reaching that gate means a pull request, so every handoff is a pull request. Merging it does three things at once:

- it approves the stage;
- it delivers the artifacts to the base branch, where the next person reads them;
- it signals that the next stage may start.

Stages without a human gate (agent gates, verifiers) run inside the same person's run, before the pull request opens. Nobody hands off half a stage.

## Ownership and claims

- **Owners.** Each agent stage names an owner role, and `fab0.yaml` maps roles to GitHub users. `owner: repo-owner` means the owner role of the repository a task belongs to.
- **Actions.** Action stages have no owner. `/fab0:run` runs any pending action before it looks for a stage the person may run. Actions are safe to repeat, so two people running one at once does no harm.
- **Assignment is the claim.** `/fab0:run 412 --task T1` refuses a task assigned to someone else unless the person passes `--take`, which reassigns it on GitHub first. This is a social lock, not an atomic one, which is enough for a team that can see each other's assignments.
- **Task order.** Without `--task`, `/fab0:run` takes the runnable tasks the person owns, one after another. Order between tasks comes from blocked-by: a task isn't offered until its blockers are done.
- **Parallel tasks** (Planned). The resolver already computes lanes, sets of tasks in one repository with disjoint `files`. Running lanes at once as worktree-isolated subagents is still to come.
- **A spec that changes after tasks started.** Each task's ledger entry records the hash of the spec it was built from. When a new spec pull request is merged:
  - the affected open tasks go stale, and `/fab0:inbox` lists them;
  - the `plan` check fails, so `plan` reconciles the sub-issues: new tasks are created, removed ones closed, changed ones updated.

## How people see their turn

There is no live dashboard to maintain. People get GitHub's own notifications (assignments, review requests), the board's **My turn** view, and one handoff comment on the item each time a stage pull request opens or updates. On top of that:

- **`/fab0:inbox`** is a read-only hint across all open runs, from the same resolver, so a suggestion is exactly what `/fab0:run` will do:

  ```text
  Ready for you (backend-dev):
    /fab0:run 412 --task T1   Task: booking API extension   implement
  Pending actions (anyone may run):
    /fab0:run 412             Story: Booking extension      plan
  Waiting on others:
    412 T2   Task: booking screen   blocked by T1
    409      Story: Invoices        spec PR awaiting review
  ```

- **The ledger** in `work/{run}/ledger/` of each repository is the full history: who ran what, on which model, from which inputs.

## A Story from start to done

| Step | Who, where | What they do | What GitHub shows | What lets the next step start |
|---|---|---|---|---|
| Intake | Product owner, browser | Opens Story #412 with the intent in the body | The issue, on the board | The issue exists |
| Spec | Product owner, home repo | `/fab0:run 412`: the spec author writes the spec and `tasks.yaml`, and the spec pull request opens | Spec pull request referring to #412 | The spec pull request is merged |
| Rework | Product owner | Reviewers request changes; `/fab0:run 412` revises the spec on the same branch, with the reviews in the brief | New commits on the same pull request | Same |
| Plan | Anyone; `/fab0:inbox` suggests it | The `plan` action creates T1 as #413 (backend) and T2 as #414 (web), with blocked-by links, each assigned to its repository's owner | Sub-issues under #412 with a progress bar | Each task's blockers are done |
| Implement | Backend developer, backend repo | `/fab0:run 412 --task T1`: the implementer and its reviewer gate run locally; the pull request opens with the review statement | Pull request "Closes #413" | It is merged under branch protection; #413 closes |
| Implement | Frontend developer, web repo | `/fab0:run 412 --task T2` once T1 is done | Same | #414 closes |
| Deliver | Anyone; `/fab0:inbox` suggests it | The `deliver` action appends the delivered tasks to the spec and removes `keep: run` artifacts, in a pull request "Closes #412" | Delivery pull request | The home repo's owner merges it; #412 closes |
