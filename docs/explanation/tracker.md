# The tracker

Git carries the work; the tracker carries what people decide. fab0 reads the tracker on every call, and writes to it only through `apply`. GitHub is the one tracker so far: `tracker: {kind: github}`.

## What fab0 reads

| Fact | Used for |
|---|---|
| An item's type and labels | Which pipeline a run belongs to, and `when` conditions |
| An item's body, title, comments or a board field | Inputs, as `issue` artifacts, and `when` conditions |
| Sub-issues | Each `foreach` element's item; other sub-issues hold back the run's end |
| Blocked-by relations | Dependencies. See [dependencies and blocking](dependencies.md#dependencies-in-the-tracker) |
| Pull requests: their state, who merged them, reviews, diff and required checks | Gates, inputs as `pr` artifacts, and merges. Who merged a review pull request decides whether its gate passes |
| Labels on the run's item | Human gates decided by a label |
| The logged-in user | The actor in the ledger, and the claim on a unit |

## What fab0 writes

Every write is an [action](../reference/actions.md), or part of `apply`'s merges and pull requests:

- labels, assignees, comments, board fields, and closing an item;
- a sub-issue per `foreach` element, with blocked-by relations from the elements' `after`, and closing them at the end;
- the run's pull request in each repository whose run branch has work, each unit's pull request, and a unit's review pull request in the runs repository; their draft state; and comments with questions and escalations, on the run's item when a unit has no pull request, and when someone outside a gate's owner role merged a review pull request;
- the signal field on the board, when the project names one.

Each write checks first, so `apply` can run as often as you like. A person's own changes stand: a pull request someone marked ready isn't turned back into a draft, and a blocked-by someone removed isn't put back.

## People and roles

`fab0.yaml` maps roles to tracker users, for example `product-owner: {github: [po-user]}`. A step, a gate or a repository names the role whose turn it is, and `tracker.assign` assigns an item to a role. Roles keep the factory independent of who fills them.

## One account for people and agents

The person running fab0 and the agents use the same GitHub login. So GitHub sees every pull request as the person's own, and lets them leave only a Comment review on it. fab0 counts Comment reviews as feedback, and a person's conversation comments on the pull request too. The comments fab0 itself posts don't count. Once the unit's pull request is merged, its comments stop counting, as its reviews do. A separate identity for agents isn't built.

## The board

A GitHub Project is optional. With `tracker.project` and a text field in `tracker.fields.signal`, `apply` shows each item's state there. Other `tracker.fields` map purposes to field names, for `tracker.field` actions and `when` conditions. fab0 never writes Status: the board's own workflows own it. See [set up GitHub](../how-to/github-setup.md).
