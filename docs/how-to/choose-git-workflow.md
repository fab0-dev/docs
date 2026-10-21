# Choose how a pipeline uses git

This guide gets you the `git` settings for one pipeline: where its accepted work lands, who merges each unit, and how the run reaches the base branch. Since fab0 0.10, no setting above the gates says who merges: each step's gate and `done` say it. For how branches and merges work, see [branches and merges](../explanation/branching.md); for the fields, see the [project reference](../reference/project.md) and the [pipeline reference](../reference/pipeline.md).

## 1. Decide where accepted work lands

`branching` is `run` by default. A pipeline may set its own in its `git` block.

| | `run` | `flat` |
|---|---|---|
| Gives | One pull request into the base branch per repository, which shows the whole run. Each unit's pull request targets the run branch, and each unit reads what was merged before it. The base branch can require pull requests | Each accepted unit is on the base branch at once, and the next unit reads it |
| Costs | Work reaches the base branch only when the run's pull request merges. The pipeline needs `git.run-branch` in `onStart`, and usually `pr.open-run`, `git.sync-base`, and `pr.merge` or `pr.ready`. A repository gets its run pull request only once its run branch has work | No run-wide review. Every unit's pull request targets the base branch. `git.*` and `pr.*` actions do nothing. When `apply` merges a unit, it pushes a merge commit to the base branch, which a ruleset that requires pull requests refuses |
| Suits | Delivery factories, such as the `story` example, and any pipeline that writes files into a protected base branch | Pipelines that write no files, such as the `triage` example |

## 2. Check whether the pipeline writes files

If no step of the pipeline writes a repository or an artifact of kind `file`, the run changes nothing in your repositories: its state is on its Pipeline Run and Pipeline Steps, so nothing is committed and no pull request opens. Use `branching: flat` for such a pipeline, as the `triage` example does. Under `run` it would need `git.run-branch`, which creates run branches that never get work. Nothing merges for a unit that changed nothing: its gate decides, and its `done` is its Pipeline Step, `done: {issue: {status: Done}}`.

A pipeline that writes files only in the runs repository writes a repository too. If that repository's `main` requires pull requests, give the pipeline a run branch: the `feature` example does, because under `flat` `apply` would push each step's merge into the runs repository's `main`.

## 3. Decide who merges each unit

A unit merges into its parent: the run branch under `run`, the base branch under `flat`, or the branch of a gated block it is in. Its gate and its `done` say who merges it:

| The unit's gate and `done` | Who merges |
|---|---|
| Any gate, with `done: {pr: {state: merged}}` | A person merges the unit's pull request. That is the only way a unit reaches a protected base branch under `flat` |
| `none` | `apply`, once the work is recorded |
| `auto` | `apply`, once the agent or command approves and the pull request's required checks pass |
| `human` via `label`, `issue` or `prompt` | `apply`, once the owner has decided |
| `human` via `pr`, with `done: {pr: {state: approved}}` | `apply`, once the owner approved the pull request's head |

`apply` merges by pushing a merge commit to the parent branch. That is why run branches stay unprotected; see [set up GitHub](github-setup.md#5-rulesets).

## 4. Decide how the run reaches the base

Under `run`, end the pipeline's `onEnd` with one of these:

- **`pr.merge`:** `apply` opens any run pull request a repository lacks, and merges each one through GitHub once its required checks pass. The base branch's ruleset applies to it as to a person's merge. Use it when the gates before it are the review you want.
- **`pr.ready`:** `apply` marks the run pull requests ready, and a person merges them. The run is done once they are merged. Use it to keep a person on the merge into the base.

Under `flat`, both do nothing: there is no run pull request.

## 5. Write the settings

These are fragments of `.fab0/fab0.yaml` and of a pipeline file, with the same keys the examples use.

A `run` pipeline, with the defaults spelled out:

```yaml
git:
  base: main
  branching: run
```

Its pipeline starts the run branch and ends with the run's merge:

```yaml
onStart:
  - git.run-branch
  - pr.open-run: {draft: true}
onEnd:
  - git.sync-base
  - pr.merge
```

Put `pr.ready` in place of `pr.merge` to leave the merge to a person.

A `flat` pipeline:

```yaml
git:
  branching: flat
```

A pipeline that differs from the project, such as a triage pipeline next to a delivery one. The project keeps `run`, and the pipeline file, `.fab0/pipelines/triage.yaml`, overrides it:

```yaml
git:
  branching: flat
```

A pipeline's `git` holds only `branching`. `base` and `branches` stay project-wide. Name the branches yourself with `git.branches` when factories that share a run id write one repository, as a parent and its children do in the runs repository:

```yaml
git:
  base: main
  branching: run
  branches: {run: "service/{run}/base", unit: "service/{run}/{unit}"}
```

## 6. Validate

```bash
fab0-resolve validate
```

| `validate` says | Change |
|---|---|
| `onStart: run branching needs git.run-branch, which creates the run branch` | Add `git.run-branch` to the pipeline's `onStart`, or use `branching: flat` |
| `git.auto_merge is gone in fab0 0.10: …` | Remove `git.auto_merge`, from `fab0.yaml` or the pipeline's `git`. See [upgrade from 0.9](upgrade-from-0.9.md) |
| `steps[0].gate.merge is gone in fab0 0.10: …` | Remove `merge` from the gate |
| ``steps[0]: 'draft' has no `done` (D109): …`` | Add a `done` to the step, beside its gate |

## Next steps

- [Gates](../explanation/gates.md): definitions of done, and who merges for each gate
- [Pipeline reference](../reference/pipeline.md)
- [Actions reference](../reference/actions.md)
- [Set up GitHub](github-setup.md#5-rulesets): the rulesets on `main` and on run branches
- [Use an example](use-an-example.md)
