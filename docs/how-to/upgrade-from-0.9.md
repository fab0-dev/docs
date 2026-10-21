# Upgrade from 0.9

This guide moves a factory from fab0 0.9 to 0.10. In 0.10 a run's state is on a run tracker, an issue for the run and one for each of its steps, in place of the run store and its ledger; every step and call declares its `done` in configuration; and its gate alone says who makes it hold, with no merge settings above the gates. The wiring is schema 3, and 0.10 refuses schema 2.

Each step below fixes what `validate` refuses next, and quotes the refusal. To see a whole upgrade, compare an example's two releases in a checkout of [`fab0-examples`](https://github.com/fab0-dev/fab0-examples):

```bash
git diff story--v0.4.0 story--v0.5.0 -- story/.fab0
```

The other examples moved from `feature--v0.2.0`, `delivery--v0.2.0` and `triage--v0.2.0` to their `v0.3.0`.

## Before you start: finish or close your 0.9 runs

0.10 doesn't carry 0.9 runs over: it reads a run's state only from its Pipeline Run, which a 0.9 run doesn't have, and it doesn't read the run store. Finish every open run with 0.9.1 first. For a run you won't finish, close its run pull requests and delete its run branches (`fab0/<run>/base`): `/fab0:inbox` lists a run branch that isn't in the base as an open run.

The watch and `tick` went in 0.9.1, and 0.10 has nothing in their place: a run goes on when someone runs `/fab0:run`, and its issues show where it is. See [follow a run](follow-a-run.md).

## 1. Set up the run tracker on GitHub

An organisation owner adds the issue types `Pipeline Run` and `Pipeline Step` and their eight issue fields, once per organisation. The runs repository then needs rulesets: `main` requires a pull request, and run branches stay unprotected. See [set up GitHub](github-setup.md#3-the-run-tracker).

## 2. Update the plugin

```bash
claude plugin update fab0@fab0 --scope project
```

Start a new Claude Code session, then run `fab0-resolve validate`. On 0.9 wiring it refuses:

```text
this is schema 2, the fab0 0.6 to 0.9 wiring; this engine reads schema 3 (fab0 0.10), where every step and call declares its `done` and `tracking` names the run tracker. See the upgrade notes, or pin the plugin to fab0--v0.9.1
```

## 3. Say `schema: 3`

In `.fab0/fab0.yaml`:

```yaml
schema: 3
```

## 4. Replace `store` with the runs repository, and name the run tracker

```text
the run store is gone in fab0 0.10: a run's facts are on the run tracker (tracking), and what it produces for itself is files in the runs repository, an entry of repos (A6c). Drop store
```

Remove `store`. Name the runs repository as an entry of `repos`, with a checkout beside your home checkout, if the factory keeps files there, and name it in `tracking`. These are fragments of `fab0.yaml`. In 0.9:

```yaml
repos:
  home: {path: ., github: acme/shop, owner: product-owner}
store: {github: acme/shop-runs}
```

In 0.10:

```yaml
repos:
  home: {path: ., github: acme/shop, owner: product-owner}
  runs: {path: ../shop-runs, github: acme/shop-runs}
tracking: {kind: github, github: acme/shop-runs}
```

`store.project` has no successor: a factory's name on the run tracker is its home repository's name, here `shop`. The examples keep a run's files under `runs/<factory>/<run>/`, so factories that share the runs repository keep their files apart.

`validate` accepts wiring without `tracking`, but a run can't start without it, and `/fab0:run #52` refuses:

```text
a run starts on the run tracker: add `tracking` to fab0.yaml (see the fab0:github skill)
```

## 5. Remove the merge settings, and choose the run's end

```text
git.auto_merge is gone in fab0 0.10: who merges follows each step's gate and `done` (D110): `apply` merges what a gate `none` or `auto` lets through, and what a person approved for `done: {pr: {state: approved}}`; a person merges for `done: {pr: {state: merged}}`. Drop it
```

Remove `git.auto_merge`, with its `allow_base`, from `fab0.yaml` and from every pipeline's `git`, and `merge` from every gate. `validate` names each one it finds, such as `steps[1].steps[0].gate.merge is gone in fab0 0.10`. A pipeline's `git` now holds only `branching`.

Then choose how the run reaches `main`, at the end of each `run` pipeline's `onEnd`:

- **`pr.merge`:** `apply` merges each run pull request through GitHub once its required checks pass. It no longer needs any setting, and a ruleset that requires a pull request on `main` applies to it.
- **`pr.ready`:** the run pull requests are marked ready, and a person merges them.

See [choose how a pipeline uses git](choose-git-workflow.md).

## 6. Make store artifacts files

```text
kind: store is gone in fab0 0.10: make it kind: file at a path in a repository, the runs repository for a working file such as a task list. A file a call receives, or a caller binds, names only its format: file: {format: <format>}
```

A working file, such as a spec or a task list, becomes a file at a path in the runs repository. In 0.9, `.fab0/artifacts/spec.yaml`:

```yaml
artifact: spec
kind: store
store: {format: markdown}
```

In 0.10:

```yaml
artifact: spec
kind: file
file: {repo: runs, path: "runs/shop/{run}/spec.md", format: markdown}
```

Let the step that writes it write that repository, and claim the path, as the `story` example's `spec` step does:

```yaml
step: spec
agent: spec-author
model: deep
inputs: [intent, reviews]
outputs: [spec]
repos: {write: [runs], read: [all]}
paths: ["runs/shop/{run}/spec.md"]
return: {questions: optional}
owner: product-owner
```

A file that another factory writes, which a call receives or a caller binds, names only its format: it is read where its producer wrote it. Keep its `schema` or `verify`, which say what you accept:

```yaml
artifact: contract
kind: file
file: {format: yaml}
schema: .fab0/schemas/contract.json
```

A pipeline's `inputs` are such files too. A step can't write one: `validate` refuses `outputs: 'spec' has no location: a step writes a file at a repo and a path`.

A pipeline whose steps now write the runs repository, where 0.9 kept their outputs in the run store, may have been `flat`. Under `flat`, `apply` pushes each step's merge into `main`, which a ruleset that requires a pull request refuses: give it `branching: run` and a run branch, as the `feature` example does.

## 7. Add `done` to every step and call, and a `via` to every human gate

```text
steps[0]: 'spec' has no `done` (D109): add a pull request's state, as done: {pr: {state: merged}}, or an issue's, as {issue: {status: Done}}
```

Every step and call declares what makes it done, beside its gate. A step named by its name alone becomes a node: `- spec` is now `- {step: spec, done: …}`. A human gate's `via` says where its owner decides; it defaults to `pr`, but naming it says what the pipeline means. Choose by what the step did in 0.9:

| In 0.9 | In 0.10 |
|---|---|
| A human gate on a step whose outputs were in the run store, approved in a review pull request of the runs repository | Make the outputs files in the runs repository (step 6), then `gate: {human: {owner: product-owner, via: pr}}` and `done: {pr: {repo: runs, state: approved}}`. The owner approves, and `apply` merges |
| A human gate on a step that writes a repository, whose pull request a person merged | `via: pr` and `done: {pr: {state: merged}}`: the owner merges. With `state: approved`, the owner approves and `apply` merges |
| A human gate decided by a label | `via: label`, as before, and `done: {issue: {status: Done}}` |
| A decision that needs no review in a pull request, such as a task list | `via: prompt`, confirmed in the run session, and `done: {issue: {status: Done}}`, as the `story` example's `plan` step does. Or `via: issue`: the owner sets the step's Pipeline Step `Done` |
| An `auto` gate, or gate `none` | `done: {issue: {status: Done}}`: the step's Pipeline Step is `Done` once its work is in, and `apply` merges it |
| A `call` | `done: {issue: {run: child, status: Done}}`: the call is done when the child's run is |

The `story` example's pipeline after the upgrade:

```yaml
steps:
  - step: spec
    gate: {human: {owner: product-owner, via: pr}}
    done: {pr: {repo: runs, state: approved}}
  - step: plan
    gate: {human: {owner: product-owner, via: prompt}}
    done: {issue: {status: Done}}
  - foreach: tasks
    id: tasks
    onStart:
      - tracker.child.sync: {type: Task, title: "{unit.title}"}
    steps:
      - step: implement
        gate: {auto: {agent: reviewer, model: deep}, retry: 2, then: human}
        done: {issue: {status: Done}}
    onEnd:
      - tracker.child.close: {type: Task}
```

`validate` also refuses a `done` that doesn't fit its gate:

| `validate` says | Change |
|---|---|
| `` `approved` is a person's approval, which needs gate human via a pull request `` | Use `state: merged`, or a human gate `via: pr` |
| `via prompt decides with no pull request: done: {issue: {status: ...}}` | Use `done: {issue: {status: Done}}` with `via: prompt` or `via: issue` |
| `step 'label' has no pull request, since it writes no repository; use done: {issue: {status: ...}}` | Use `done: {issue: …}` for a step that writes no repository, such as an action |
| `via prompt needs the run tracker: set tracking in fab0.yaml` | Add `tracking` (step 4) |
| `'Finished' is no value of the tracker's status (Done, In Progress, Todo)` | Use a value of `tracking.status`, or `closed` for the issue's own state |

## 8. Connected factories

A factory that calls another, and the factory it calls, upgrade together, since `validate` in the parent checks the child's wiring at its base branch. Beside the steps above:

- **One run tracker.** Both name the same `tracking`: a child's Pipeline Run is a sub-issue of its parent's. Otherwise `validate` refuses `its run tracker isn't this factory's: a child's Pipeline Run is a sub-issue of the parent's`.
- **The runs repository in both.** Files the factories exchange are in a repository both list in `repos`, the runs repository. The receiving side names only the format (step 6). Otherwise: `outputs.contract: it is in acme/service, which this factory lacks in its repos`.
- **Branches apart.** A child run has its parent's run id, so a parent and its children, and children of one parent, that write one repository name their branches apart. The `delivery` example names them after its factory:

  ```yaml
  git:
    base: main
    branching: run
    branches: {run: "service/{run}/base", unit: "service/{run}/{unit}"}
  ```

  Otherwise `validate` refuses: `it names its branches as this factory does, and both have acme/shop-runs, where the parent's run id would name both runs' branches: give it git.branches of its own`.
- **Distinct names.** A factory's name is its home repository's name, so two connected factories need home repositories with different names.
- **Acceptance.** A call's `human` gate decides `via: issue` or `via: prompt`; the review pull request of 0.9 is gone: `a person accepts what a child run hands back via issue (the call's Pipeline Step set Done) or prompt, not via pr (D114)`. An `auto` acceptor and gate `none` stay as they were.
- **No item in the child's repository.** A call opens only the child's Pipeline Run, under the parent's. The child's trigger still starts runs of its own.

See [connect a factory](connect-a-factory.md).

## 9. Validate and run

```bash
fab0-resolve validate
```

It prints `"ok": true` once the wiring and the run tracker's setup are right. Commit `.fab0/` and push it to the base branch, then start a new run with `/fab0:run #<n>`. See [start and continue a run](start-and-continue-a-run.md).
