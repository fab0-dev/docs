# Branches and merges

A run works on its own branch. Each unit works on a sub-branch of it, in its own worktree, so units run in parallel without touching each other. Under the default, run branching, only the finished run reaches the base branch. This page explains how. The [project reference](../reference/project.md#git) lists the settings, and [choose how a pipeline uses git](../how-to/choose-git-workflow.md) helps you pick them.

## Run branching (default)

- `onStart` creates the **run branch**, `fab0/<run>/base`, in every repository the run may write, at the base branch's head and with no commit.
- Each unit works on `fab0/<run>/<unit>`, cut from its parent's head: the run branch, or the branch of a gated block around it. Its pull request targets that parent.
- A unit's inputs are read at its parent's head, and its ledger entry records that commit. So a unit sees exactly what was merged before it.
- A repository gets the run's pull request into the base branch, usually as a draft, once its run branch has work the base branch lacks. Each run pull request closes the run's tracker item.
- When a unit is accepted, its branch merges into its parent: by `apply` for gate `none`, for `merge: auto`, and for a human gate decided by a label; by a person merging its pull request otherwise.
- At the end, the run's pull requests carry everything into the base branch. A person merges them.

```text
main
└── fab0/412/base                 the run; its pull request into main is the result
    ├── fab0/412/implement-T1     a unit; its pull request targets fab0/412/base
    └── fab0/412/implement-T2
```

## Flat branching

With `branching: flat`, there is no run branch: each unit's pull request targets the base branch. A factory uses it when its units are independent and each should be on `main` as soon as it is accepted, with no run-wide review to wait for.

A person merges each unit into the base branch, unless `git.auto_merge` allows the base branch (`into: [base]` with `allow_base: true`). Then `apply` merges gate `none`, label-decided and `merge: auto` units itself. The default holds back because the base branch is the project's, and fab0 doesn't push to it unless the project says it may. Units inside a gated block merge into the block's branch, not the base branch, so this doesn't hold them. To choose, see [choose how a pipeline uses git](../how-to/choose-git-workflow.md).

## No empty commits, no empty pull requests

A product repository receives only product changes. Branches are created with no commit, and a unit's branch gets one only when `record` commits what the unit changed. `record` pushes the branch then, and `apply` pushes it before it merges it or opens its pull request. A branch with no work stays on the machine that made it.

So a repository the run only reads gets no commit and no pull request, and a step that writes no repository, such as one that works only in the tracker, leaves nothing in any product repository. Its record is in the run store, like every other unit's. It still works on a branch of the home repository, which never gets a commit, because it reads its parent's state there.

This holds because GitHub opens no pull request without a change, and a commit that changes nothing only adds noise to a product's history.

## Several repositories

A run may write several repositories, each a sibling checkout named in `fab0.yaml`. Each gets the same run branch name, and its own run pull request once its run branch has work. The run is done when every run branch with work is merged.

## No force pushes, ever

Branches move forward only. A unit's branch is brought up to date by merging its parent into it, never by a rebase. `apply` changes branches through git plumbing, or in the branch's own checkout only when that checkout is clean, so nobody's work moves under them.

## When GitHub's branch is ahead

A person who merges a unit's pull request on GitHub moves that branch on GitHub past the local copy. When `apply` pushes a branch, run or unit, and GitHub's copy already contains every commit of the local one, it doesn't push. It brings the local branch forward to GitHub's commit and goes on, so the run doesn't stop for a branch nobody has to move. It compares with the `origin/<branch>` ref the session's fetch left, so a branch that moves on GitHub after that fetch isn't seen. If the branch is checked out with uncommitted changes, the checkout stays as it is, the local branch stays behind, and `apply` goes on: it reads the fresher of the local and GitHub's copy anyway.

A branch that has diverged, where each side has a commit the other lacks, still stops the run. `apply` fails with an error that names the repository and the branch, and moves neither side. Someone must bring the two together by hand.

## Claiming a unit

Two machines must never run the same attempt of a unit. When `next` hands an attempt out, it first writes a claim for it in the run store, a create-only fact naming who took it and from which checkout, and pushes it. The first claim pushed stands. A machine whose claim lost the race, or that finds another checkout's claim, doesn't hand the unit out: the unit shows as `running` with `claimed: elsewhere`. Every attempt is claimed, so two machines can't take the same rework either. Assignment in the tracker still says whose turn a human gate is.

The claim is a fact rather than a branch. Two machines that push the same new branch at the same commit both succeed, so a branch could only be a claim with a commit of its own, and that commit would be an empty one in the product's history.

## Conflicts and failing checks

Before a unit merges, `apply` tests whether its branch merges cleanly into its parent, and whether its pull request's required checks pass.

- If not, the unit goes back to its agent once, with the conflicting files or the failing checks in its brief. When the merge would be clean, `apply` first brings the branch up to date with its parent; otherwise the agent resolves the conflict markers.
- If the attempt made to fix it has the same trouble, a person decides.

## The final merge

The run's pull requests are the last gate, and it is human. `onEnd` brings the base branch into each run branch with work, so each pull request shows the result as it will land, opens the pull request of a repository that has none yet, and marks each one ready. Merging them ends the run.
