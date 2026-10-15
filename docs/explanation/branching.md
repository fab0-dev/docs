# Branches and merges

A run works on its own branch. Each unit works on a sub-branch of it, in its own worktree, so units run in parallel without touching each other. Only the finished run reaches the base branch. This page explains how. The [project reference](../reference/project.md#git) lists the settings, and [choose how a pipeline uses git](../how-to/choose-git-workflow.md) helps you pick them.

## Run branching (default)

- `onStart` creates the **run branch**, `fab0/<run>/base`, in every repository the run writes, and opens the run's pull request into the base branch, usually as a draft.
- Each unit works on `fab0/<run>/<unit>`, cut from its parent: the run branch, or the branch of a gated block around it. Its pull request targets that parent.
- A unit's inputs are read at its parent's head, and its ledger entry records that commit. So a unit sees exactly what was merged before it.
- When a unit is accepted, its branch merges into its parent: by `apply` for gate `none`, for `merge: auto`, and for a human gate decided by a label; by a person merging its pull request otherwise.
- At the end, the run's pull request carries everything into the base branch. A person merges it.

```text
main
└── fab0/412/base                 the run; its pull request into main is the result
    ├── fab0/412/spec             a unit; its pull request targets fab0/412/base
    ├── fab0/412/implement-T1
    └── fab0/412/implement-T2
```

## Flat branching

With `branching: flat`, there is no run branch: each unit's pull request targets the base branch. A factory uses it when its units are independent and each should be on `main` as soon as it is accepted, with no run-wide review to wait for.

A person merges each unit into the base branch, unless `git.auto_merge` allows the base branch (`into: [base]` with `allow_base: true`). Then `apply` merges gate `none`, label-decided and `merge: auto` units itself. The default holds back because the base branch is the project's, and fab0 doesn't push to it unless the project says it may. Units inside a gated block merge into the block's branch, not the base branch, so this doesn't hold them. To choose, see [choose how a pipeline uses git](../how-to/choose-git-workflow.md).

## Runs that write no files

A pipeline whose steps write no files, such as one that works only in the tracker, opens no pull requests at all. Whatever its branching, it keeps its ledger on `ledger.branch`, which `apply` pushes and nothing merges, because the record must live in git and nothing may push to the base branch. The ledger branch belongs to this case, not to `flat`: under `run` branching such a pipeline still needs the run branch.

## Several repositories

A run may write several repositories, each a sibling checkout named in `fab0.yaml`. Each gets the same run branch name and its own run pull request. The run is done when every one of them is merged.

## No force pushes, ever

Branches move forward only. A unit's branch is brought up to date by merging its parent into it, never by a rebase. `apply` changes branches through git plumbing, or in the branch's own checkout only when that checkout is clean, so nobody's work moves under them.

## Claiming a unit

Two machines must never run the same unit. When `next` hands a unit out, it claims it by creating its branch on `origin`, create-only, with an empty commit that says who took it. If the push is refused, another machine has the unit, and it isn't handed out. Assignment in the tracker still says whose turn a human gate is.

## Conflicts and failing checks

Before a unit merges, `apply` tests whether its branch merges cleanly into its parent, and whether its pull request's required checks pass.

- If not, the unit goes back to its agent once, with the conflicting files or the failing checks in its brief. When the merge would be clean, `apply` first brings the branch up to date with its parent; otherwise the agent resolves the conflict markers.
- If the attempt made to fix it has the same trouble, a person decides.

## The final merge

The run's pull request is the last gate, and it is human. `onEnd` brings the base branch into the run branch, so the pull request shows the result as it will land, and marks it ready. Merging it ends the run.
