# Choose how a pipeline uses git

This guide gets you the `git` and `ledger` settings for one pipeline: where its accepted work lands, whether it needs a ledger branch, and what `git.auto_merge` must allow. It needs fab0 0.6.2 or later, where every merge into the base branch obeys `git.auto_merge`, whatever the gate. For how branches and merges work, see [branches and merges](../explanation/branching.md); for the fields, see the [project reference](../reference/project.md#git) and its [`ledger`](../reference/project.md#ledger) section.

## 1. Decide where accepted work lands

`branching` is `run` by default. A pipeline may set its own in its `git` block.

| | `run` | `flat` |
|---|---|---|
| Gives | One pull request into the base branch that shows the whole run. Each unit reads what was merged before it. `apply` merges accepted units into the run branch under the default policy. The base branch can require pull requests | Each accepted unit is on the base branch at once, and the next unit reads it |
| Costs | Work reaches the base branch only when the run's pull request merges. The pipeline needs `git.run-branch` in `onStart`, and usually `pr.open-run`, `git.sync-base` and `pr.ready` | No run-wide review. Every unit's pull request targets the base branch, so by default a person merges each one. `git.*` and `pr.*` actions do nothing. If `apply` merges, it pushes to the base branch, and a ruleset that requires pull requests there refuses it |
| Suits | Delivery factories, such as the `story` example | Pipelines whose units are independent, and pipelines that write no files, such as the `triage` example |

## 2. Check whether the pipeline writes files

If no step of the pipeline writes a repository or an artifact of kind `file`, the run opens no pull request. It needs a ledger branch:

1. In `fab0.yaml`, set `ledger.branch` to a branch nothing else uses, for example `fab0/ledger`. It is project-wide: a pipeline's own `git` block can't hold `ledger`.
2. Use `branching: flat` for the pipeline, as the `triage` example does. Under `run` the pipeline would still need `git.run-branch`, and so a run branch that never gets a pull request.

Without `ledger.branch`, `validate` refuses the pipeline: "no step writes files, so the run opens no pull request: set ledger.branch in fab0.yaml".

On the ledger branch nothing merges. An auto gate's approval, or a human gate's label, is the decision, and `apply` pushes the branch. So `git.auto_merge` doesn't apply to such a pipeline.

## 3. Decide what `apply` may merge

`git.auto_merge` has `into`, a list of `run` and `base`. Merging into the base branch also needs `allow_base: true`; the schema refuses `into: [base]` without it.

- **`run`:** `apply` merges units with gate `none` and label-decided human gates into the run branch. A gate with `merge: auto` passes `validate` only if `into` holds `run`, which is the default.
- **`flat`:** a unit with gate `none`, a label-decided human gate or `merge: auto` has the base branch as its parent. Unless `git.auto_merge` has `into: [base]` and `allow_base: true`, it waits, and a person merges its pull request. With both, `apply` merges it by pushing to the base branch. `validate` refuses `merge: auto` unless `into` holds `base`. A ruleset that requires pull requests on the base branch must let the fab0 login bypass it, or `apply`'s merges fail; see [set up GitHub](github-setup.md). Units inside a gated block merge into the block's branch either way, so this doesn't hold them, and `validate` checks a `merge: auto` gate there against `run`, not `base`.
- **A ledger branch:** leave `merge: auto` off, since the gate already decides. `validate` still checks the target of a `merge: auto` gate.
- **`pr.merge`:** merges the run branch into the base branch, so it only acts under `run`; under `flat` it does nothing. In either case `validate` refuses it unless `into` holds `base` and `allow_base` is `true`. It pushes to the base branch too, so the same ruleset rule applies.

## 4. Write the settings

These are fragments of `.fab0/fab0.yaml`, with the same keys the `story` and `triage` examples use.

A `run` pipeline, with the defaults spelled out. A person merges the run's pull request:

```yaml
git:
  base: main
  branching: run
  auto_merge: {into: [run]}
```

A `run` pipeline whose run `apply` merges into the base branch with `pr.merge` in `onEnd`:

```yaml
git:
  branching: run
  auto_merge: {into: [run, base], allow_base: true}
```

A `flat` pipeline where a person merges each unit's pull request:

```yaml
git:
  branching: flat
```

A `flat` pipeline where `apply` merges units with gate `none`, a label-decided gate or `merge: auto` into the base branch:

```yaml
git:
  branching: flat
  auto_merge: {into: [base], allow_base: true}
```

A pipeline that writes no files, `flat` with a ledger branch:

```yaml
git:
  branching: flat
ledger:
  branch: fab0/ledger
```

A pipeline that differs from the project, such as a triage pipeline next to a delivery one. The project keeps `run`, and the pipeline file, `.fab0/pipelines/triage.yaml`, overrides it:

```yaml
git:
  branching: flat
```

A pipeline's `git` holds only `branching` and `auto_merge`, and it is merged over the project's as a JSON Merge Patch: a key you leave out keeps the project's value. `base`, `branches` and `ledger` stay project-wide. The project also needs `ledger.branch` if this pipeline writes no files.

## 5. Validate

```bash
fab0-resolve validate
```

| `validate` says | Change |
|---|---|
| `run branching needs git.run-branch, which creates the run branch` | Add `git.run-branch` to the pipeline's `onStart`, or use `branching: flat` |
| `no step writes files, so the run opens no pull request: set ledger.branch in fab0.yaml` | Set `ledger.branch` (step 2) |
| `merge auto would merge into the run branch` or `the base branch, which git.auto_merge.into doesn't allow` | Add `run` (under `run`) or `base` (under `flat`) to `git.auto_merge.into`, or drop `merge: auto` |
| `pr.merge merges into the base branch, which git.auto_merge doesn't allow` | Set `into: [base]` with `allow_base: true`, or remove `pr.merge` |
| `git.auto_merge` error naming `allow_base` | Add `allow_base: true` beside `into: [base]` |

## Next steps

- [Gates](../explanation/gates.md): who merges for each gate
- [Pipeline reference](../reference/pipeline.md)
- [Actions reference](../reference/actions.md)
- [Set up GitHub](github-setup.md): the base branch ruleset
- [Use an example](use-an-example.md)
