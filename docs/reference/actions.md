# Actions

The catalogue of fab0's built-in actions. An action is a step, or an entry in a pipeline's or block's `onStart` or `onEnd`. `apply` performs it; nothing else does. Each action has a read-only check: when the check passes, the action is done, so it writes no ledger entry and performing it twice changes nothing.

```yaml
onStart:
  - git.run-branch
  - tracker.label: {add: [triaging], remove: [needs-triage]}
```

Arguments may use the [step placeholders](step.md#placeholders), such as `{run.title}` or `{classify.severity}`.

## Where an action may go

| Actions | Where |
|---|---|
| `git.run-branch`, `git.sync-base`, `pr.open-run`, `pr.ready`, `pr.merge` | The pipeline's `onStart` or `onEnd`: they act on the whole run |
| `tracker.child.sync` | A `foreach`'s `onStart` |
| `tracker.child.close` | A `foreach`'s `onEnd` |
| Every other action | Anywhere: `onStart`, `onEnd`, or as a step |

A [`call`](pipeline.md#call) and a called pipeline have actions of their own, which no wiring names: `call.start`, which files the child run's item and records the call, and `call.bind`, which a called run starts with. `apply` performs them like any other.

`git.*` and `pr.*` actions do nothing under `branching: flat`, which has no run branch. `tracker.*` actions need a tracker in `fab0.yaml`.

fab0 0.6's `git.remove-run-artifacts` is gone, and `validate` refuses it with a hint: a working file is a `store` artifact, which never reaches a product repository, so nothing is left to remove.

## git

| Action | Arguments | Done when |
|---|---|---|
| `git.run-branch` | none | The run branch exists in every repository the run writes. `apply` creates it at the base branch's head, with no commit, and pushes it |
| `git.sync-base` | none | The run branch contains the latest base branch, in every repository where it has work. `apply` merges the base in; a conflict stops `apply` and names the files |

## pr

| Action | Arguments | Done when |
|---|---|---|
| `pr.open-run` | `draft`: `true` to open it as a draft | Every repository whose run branch has work the base branch lacks has had a run pull request into the base branch. A repository the run hasn't changed gets none, since GitHub opens no pull request without a change. A run branch usually gets work after the run starts, so `apply` checks this action again after its last round and opens the pull request then. One a person closed stays closed, and one a person marked ready isn't turned back into a draft |
| `pr.ready` | none | Every repository whose run branch has work has an open run pull request, and none is a draft. `apply` opens the missing ones, a closed one included, and marks drafts ready |
| `pr.merge` | none | The run branch is merged into the base branch everywhere. Allowed only when `git.auto_merge` has `into: [base]` and `allow_base: true`; otherwise a person merges the run's pull request |
| `pr.comment` | `body` | The run's pull request in the home repo has a comment containing `body` |

Every run pull request's body closes the run's item, `Closes <owner>/<repo>#<run>`, in whichever repository it is.

## tracker

`tracker.label`, `tracker.assign`, `tracker.comment`, `tracker.field` and `tracker.close` act on the run's item, or with `item: parent`, on the item it is a sub-issue of.

| Action | Arguments | Done when |
|---|---|---|
| `tracker.label` | `add`, `remove`: lists of labels | The run's item has every label in `add` and none in `remove` |
| `tracker.assign` | `role`: a role from `people` | The run's item is assigned to one of the role's users |
| `tracker.comment` | `body` | The run's item has a comment containing `body` |
| `tracker.field` | `{<purpose>: <value>}`, one or more | The run's item has those values on the board. A purpose is looked up in `tracker.fields`, else used as the field's name |
| `tracker.close` | none | The run's item is closed |
| `tracker.child.sync` | `type`: an issue type; `title`: a template, default `{unit.title}` | Every element of the `foreach` has a sub-issue of the run's item with that title and type. `apply` creates the missing ones, and adds every `after` that involves a new item as a blocked-by relation. Relations between items that already existed are left as people set them |
| `tracker.child.close` | `type` and `title`, as for `tracker.child.sync` | Every element's item is closed |
| `tracker.items` | `from`: a list artifact, read as a `foreach` reads it; `of`: `run` (default) or `parent`; `type`, `label`; `title` (default `{unit.title}`) and `body`, templates on each element | Every element of the list has a sub-issue, with that title (and type), of the run's item or of its parent. `apply` creates the missing ones. Until the list is there, the action waits on it |
