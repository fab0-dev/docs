# The tracker

fab0 works with GitHub issues in two roles, set up in two places in `fab0.yaml`:

| | The tracker (`tracker`) | The run tracker (`tracking`) |
|---|---|---|
| Holds | The work: items such as Stories, Tasks and bug reports, their labels, relations and board | The runs: a Pipeline Run for each run and a Pipeline Step for each of its units |
| Where | The repositories where a team files its work | The runs repository, which every factory of a product shares |
| Written by | People, and fab0 through actions | fab0's engine alone |
| Read by fab0 for | Triggers, inputs, conditions, dependencies, human gates by label | The run's state, its history, and what comes next |

They are different things, and this page keeps them apart: "the tracker" is where the work items are, and "the run tracker" is where the runs are. The [run tracker reference](../reference/tracker.md) lists its issue types, fields and lifecycle, and [set up GitHub](../how-to/github-setup.md) creates them.

## Why the run tracker exists

Up to 0.9, a run moved on through facts the engine kept in its own ledger, and through review pull requests, approvals and merge rules that worked differently in different places. None of it showed where people work, and none of it was declared in the pipeline. A real connected run stalled on it: a child's plan sat in a review pull request that already carried its approval, and nothing moved. A watch that tried to move runs on added a second set of rules on top, and was withdrawn in 0.9.1.

0.10 puts the run's state where people already look: in issues. The engine decides from the run's issues, the pipeline's definitions of done and its gates, and from nothing else. So:

- a person sees where a run is, and what it waits for, on GitHub, without a session;
- every machine and every factory reads the same state, and a run can stop and go on anywhere;
- a connected factory finds the runs it must work on in the same place as its own.

The run tracker sits behind an interface, `Tracking`, so another kind can follow. GitHub issues, `kind: github`, are the first.

## A run on the run tracker

Each run is an issue of type **Pipeline Run**, and each of its units an issue of type **Pipeline Step**, a sub-issue of it. GitHub's own features carry the rest:

- **Issue fields** hold the state: Run ID, Stage, Pipeline, Factory, the steps under way (Step) and whom it waits on (Waiting on) on the run; Run ID, Stage, Step, Waiting on, Revision and Output on a step. `apply` keeps them up to date. The lifecycle field is called Stage, with `Todo`, `In Progress` and `Done`, because GitHub reserves the name Status. A factory may rename the types, the fields and the values (`tracking.types`, `tracking.fields`, `tracking.status`), and `validate` checks that they exist with their data types.
- **Assignees are claims.** A step `In Progress` is assigned to the login of the session that runs it.
- **Sub-issues hold the tree.** A run's steps are its sub-issues; a child run is a sub-issue of its parent's run.
- **Comments are the log.** Each attempt, gate decision and claim is one comment on its Pipeline Step: a line a person reads and a YAML block the engine reads. A child run's call and its parent's rejections are comments on its Pipeline Run.
- **Close reasons end it.** A step closes as completed once it is done. A run closes as completed, with a summary of its steps, once it is done. The engine closes one as not planned when it finds it was opened twice; a person closes a run that failed or was abandoned as not planned.

A root run's id is its Pipeline Run's number. Every factory of a product shares the runs repository, so that number is unique across all of them. A child run carries its parent's Run ID, so one piece of work has one id in every factory, in every issue and in every branch name. See [run ids](pipelines.md#run-ids).

## How it relates to the tracker

A run starts from an item, and its Pipeline Run is a sub-issue of that item. So the item shows its runs, and a run shows where it came from. Once the run is closed, the item can start another.

The tracker's own work items stay for people. A `foreach` may create a Task sub-issue for each element of its list (`tracker.child.sync`), so the team sees the tasks on its board and can order them with blocked-by relations. Those Tasks are items; the units that work on them each have a Pipeline Step too. The engine reads an item's sub-issues as dependencies, and leaves the run tracker's issues out of them, so a Pipeline Run under a Story never holds that Story's run back.

A child run has no item: a call opens only its Pipeline Run, under the parent's, and the child factory's inbox finds it there by its Factory field. Factories that call each other must share the run tracker; they need not share the tracker.

## What people see where they work

| Where | What it shows |
|---|---|
| The item, such as a Story | Its Pipeline Run as a sub-issue, its Task sub-issues, its labels, and the run's pull requests, which close it when merged |
| The Pipeline Run | The run's steps as sub-issues, its Stage, its Pipeline and Factory, its child runs, and a summary when it closes |
| A Pipeline Step | Its Stage, who holds it, its Revision, its Output (the pull request, then the commit it was accepted at) and a comment for each attempt, gate decision and claim |
| A pull request | The unit's work, for review, and questions and escalations posted on it |
| The board | Each item's state in the signal field, when the project names one |
| The run session | Decisions to confirm at the prompt |
| `/fab0:inbox` | Every open run, and what waits on whom |

See [follow a run](../how-to/follow-a-run.md).

## What fab0 reads from the tracker

| Fact | Used for |
|---|---|
| An item's type and labels | Which pipeline a run belongs to, and `when` conditions |
| An item's body, title, comments or a board field | Inputs, as `issue` artifacts, and `when` conditions |
| Sub-issues | Each `foreach` element's item; other sub-issues, besides the run tracker's own, hold back the run's end |
| Blocked-by relations | Dependencies. See [dependencies and blocking](dependencies.md#dependencies-in-the-tracker) |
| Pull requests: their state, reviews, diff and required checks | Definitions of done, gates, inputs as `pr` artifacts, and merges |
| Labels on the run's item | Human gates decided by a label |
| The logged-in user | The actor of each fact, and the claim on a unit |

## What fab0 writes

Every write is an [action](../reference/actions.md), or part of `record`'s and `apply`'s work:

- on the tracker: labels, assignees, comments, board fields, and closing an item: the run's, or the item it is a sub-issue of;
- a Task sub-issue per `foreach` element, with blocked-by relations from the elements' `after`, and closing them at the end;
- a sub-issue per element of a list, under the run's item or the item it is part of (`tracker.items`);
- the run's pull request in each repository whose run branch has work, and each unit's pull request, in the runs repository too; their draft state; and comments with questions and escalations, on the run's item when a unit has no pull request;
- the signal field on the board, when the project names one;
- on the run tracker: the Pipeline Runs and Pipeline Steps, their fields, assignees and comments, and closing them.

Each write checks first, so `apply` can run as often as you like. A person's own changes stand: a pull request someone marked ready isn't turned back into a draft, and a blocked-by someone removed isn't put back. The run tracker's issues are the engine's: people read them, and decide on them only where a gate says so, such as setting a Pipeline Step `Done` for a gate `via: issue`.

## People and roles

`fab0.yaml` maps roles to GitHub users, for example `product-owner: {github: [po-user]}`. A step, a gate or a repository names the role whose turn it is, and `tracker.assign` assigns an item to a role. Roles keep the factory independent of who fills them.

## One account for people and agents

The person running fab0 and the agents use the same GitHub login. So GitHub sees every pull request as the person's own, and lets them leave only a Comment review on it. fab0 counts Comment reviews as feedback, and a person's conversation comments on the pull request too. The comments fab0 itself posts don't count. To approve a pull request they opened, the person comments `/approve`. See [gates](gates.md#human-gates). A separate identity for agents is **Planned**.

## The board

A GitHub Project is optional. With `tracker.project` and a text field in `tracker.fields.signal`, `apply` shows each item's state there. Other `tracker.fields` map purposes to field names, for `tracker.field` actions and `when` conditions. fab0 never writes the board's Status: the board's own workflows own it.
