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
| `git.run-branch`, `git.sync-base`, `git.remove-run-artifacts`, `pr.open-run`, `pr.ready`, `pr.merge` | The pipeline's `onStart` or `onEnd`: they act on the whole run |
| `tracker.child.sync` | A `foreach`'s `onStart` |
| `tracker.child.close` | A `foreach`'s `onEnd` |
| Every other action | Anywhere: `onStart`, `onEnd`, or as a step |

`git.*` and `pr.*` actions do nothing under `branching: flat`, which has no run branch. `tracker.*` actions need a tracker in `fab0.yaml`.

## git

| Action | Arguments | Done when |
|---|---|---|
| `git.run-branch` | none | The run branch exists in every repository the run writes. `apply` creates it from the base branch and pushes it |
| `git.sync-base` | none | The run branch contains the latest base branch, in every repository where it has work. `apply` merges the base in; a conflict stops `apply` and names the files |
| `git.remove-run-artifacts` | none | No `keep: run` file artifact is left on the run branch, except per-element ones (a path with `{unit}`, or the element's repository), which stay. `apply` commits their removal |

## pr

| Action | Arguments | Done when |
|---|---|---|
| `pr.open-run` | `draft`: `true` to open it as a draft | The run's pull request into the base branch exists in the home repo. Its body closes the run's item. A pull request a person marked ready isn't turned back into a draft |
| `pr.ready` | none | Every repository whose run branch has work has a run pull request, and none is a draft |
| `pr.merge` | none | The run branch is merged into the base branch everywhere. Allowed only when `git.auto_merge` has `into: [base]` and `allow_base: true`; otherwise a person merges the run's pull request |
| `pr.comment` | `body` | The run's pull request has a comment containing `body` |

## tracker

| Action | Arguments | Done when |
|---|---|---|
| `tracker.label` | `add`, `remove`: lists of labels | The run's item has every label in `add` and none in `remove` |
| `tracker.assign` | `role`: a role from `people` | The run's item is assigned to one of the role's users |
| `tracker.comment` | `body` | The run's item has a comment containing `body` |
| `tracker.field` | `{<purpose>: <value>}`, one or more | The run's item has those values on the board. A purpose is looked up in `tracker.fields`, else used as the field's name |
| `tracker.close` | none | The run's item is closed |
| `tracker.child.sync` | `type`: an issue type; `title`: a template, default `{unit.title}` | Every element of the `foreach` has a sub-issue of the run's item with that title and type. `apply` creates the missing ones, and adds every `after` that involves a new item as a blocked-by relation. Relations between items that already existed are left as people set them |
| `tracker.child.close` | `type` and `title`, as for `tracker.child.sync` | Every element's item is closed |
