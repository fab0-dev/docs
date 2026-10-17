# Choose how a pipeline uses git

This guide gets you the `git` settings for one pipeline: where its accepted work lands, and what `git.auto_merge` must allow. It describes fab0 0.7, where each run's ledger is in the run store, so no pipeline needs a branch of its own for it. For how branches and merges work, see [branches and merges](../explanation/branching.md); for the fields, see the [project reference](../reference/project.md#git) and its [`store`](../reference/project.md#store) section.

## 1. Decide where accepted work lands

`branching` is `run` by default. A pipeline may set its own in its `git` block.

| | `run` | `flat` |
|---|---|---|
| Gives | One pull request into the base branch that shows the whole run. Each unit reads what was merged before it. `apply` merges accepted units into the run branch under the default policy. The base branch can require pull requests | Each accepted unit is on the base branch at once, and the next unit reads it |
| Costs | Work reaches the base branch only when the run's pull request merges. The pipeline needs `git.run-branch` in `onStart`, and usually `pr.open-run`, `git.sync-base` and `pr.ready`. A repository gets its run pull request only once its run branch has work | No run-wide review. Every unit's pull request targets the base branch, so by default a person merges each one. `git.*` and `pr.*` actions do nothing. If `apply` merges, it pushes to the base branch, and a ruleset that requires pull requests there refuses it |
| Suits | Delivery factories, such as the `story` example | Pipelines whose units are independent, and pipelines that write no files, such as the `triage` example |

## 2. Check whether the pipeline writes files

If no step of the pipeline writes a repository or an artifact of kind `file`, the run changes nothing in your repositories. It needs no extra setting: like every run, it records its ledger in the run store, so nothing is committed and no pull request opens.

Use `branching: flat` for such a pipeline, as the `triage` example does. Under `run` it would need `git.run-branch`, which creates run branches that never get work.

Nothing merges for a unit that changed nothing. Its gate is the decision: an auto gate's approval, or a human gate's label.

## 3. Decide what `apply` may merge

`git.auto_merge` has `into`, a list of `run` and `base`. Merging into the base branch also needs `allow_base: true`; the schema refuses `into: [base]` without it.

- **`run`:** `apply` merges units with gate `none` and label-decided human gates into the run branch. A gate with `merge: auto` passes `validate` only if `into` holds `run`, which is the default.
- **`flat`:** a unit with gate `none`, a label-decided human gate or `merge: auto` has the base branch as its parent. Unless `git.auto_merge` has `into: [base]` and `allow_base: true`, it waits, and a person merges its pull request. With both, `apply` merges it by pushing to the base branch. `validate` refuses `merge: auto` unless `into` holds `base`. `apply` merges by pushing, so a ruleset that requires pull requests on the base branch refuses these merges. [Set up GitHub](github-setup.md#5-the-base-branch) tells you to require a pull request there, and describes no bypass for the fab0 login: choose `flat` with `allow_base` only if your base branch accepts `apply`'s pushes, otherwise leave `auto_merge` at its default and merge each unit's pull request yourself. Units inside a gated block merge into the block's branch either way, so this doesn't hold them, and `validate` checks a `merge: auto` gate there against `run`, not `base`.
- **A pipeline that writes no files:** leave `merge: auto` off, since the gate already decides. If a gate has it, `validate` still checks the target: under `flat`, `into` must hold `base` with `allow_base: true`; under `run`, it must hold `run`.
- **`pr.merge`:** merges the run branch into the base branch, so it only acts under `run`; under `flat` it does nothing. In either case `validate` refuses it unless `into` holds `base` and `allow_base` is `true`. It pushes to the base branch too, so a ruleset that requires pull requests there refuses it.

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

A pipeline that writes no files needs only `branching: flat`, as in the first `flat` fragment. Its ledger goes to the run store that `store` names, as every pipeline's does.

A pipeline that differs from the project, such as a triage pipeline next to a delivery one. The project keeps `run`, and the pipeline file, `.fab0/pipelines/triage.yaml`, overrides it:

```yaml
git:
  branching: flat
```

A pipeline's `git` holds only `branching` and `auto_merge`, and it is merged over the project's as a JSON Merge Patch: a key you leave out keeps the project's value. `base`, `branches` and `store` stay project-wide.

## 5. Validate

```bash
fab0-resolve validate
```

| `validate` says | Change |
|---|---|
| `run branching needs git.run-branch, which creates the run branch` | Add `git.run-branch` to the pipeline's `onStart`, or use `branching: flat` |
| `fab0 0.7 keeps the ledger in a run store, not in the product repositories: replace ledger with store: …` | Remove `ledger` from `fab0.yaml` and name the runs repository in `store`. See [set up GitHub](github-setup.md#6-the-runs-repository) |
| `merge auto would merge into the run branch, which git.auto_merge.into doesn't allow`, or the same message with `base branch` | Add `run` (under `run`) or `base` (under `flat`) to `git.auto_merge.into`, or drop `merge: auto` |
| `pr.merge merges into the base branch, which git.auto_merge doesn't allow` | Set `into: [base]` with `allow_base: true`, or remove `pr.merge` |
| `git.auto_merge` error naming `allow_base` | Add `allow_base: true` beside `into: [base]` |

## Next steps

- [Gates](../explanation/gates.md): who merges for each gate
- [Pipeline reference](../reference/pipeline.md)
- [Actions reference](../reference/actions.md)
- [Set up GitHub](github-setup.md#5-the-base-branch): the base branch ruleset
- [Use an example](use-an-example.md)
