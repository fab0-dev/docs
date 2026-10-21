# Branches and merges

A run works on its own branch. Each unit works on a sub-branch of it, in its own worktree, so units run in parallel without touching each other. Under the default, run branching, only the finished run reaches the base branch. This page explains how. The [project reference](../reference/project.md#git) lists the settings, and [choose how a pipeline uses git](../how-to/choose-git-workflow.md) helps you pick them.

## Run branching (default)

- `onStart` creates the **run branch**, `fab0/<run>/base`, in every repository the run may write, at the base branch's head and with no commit.
- Each unit works on `fab0/<run>/<unit>`, cut from its parent's head: the run branch, or the branch of a gated block around it. Its pull request targets that parent.
- A unit's inputs are read at its parent's head, and its fact records that commit. So a unit sees exactly what was accepted before it.
- A repository gets the run's pull request into the base branch, usually as a draft, once its run branch has work the base branch lacks. Each run pull request closes the run's item.
- When a unit is done, its branch merges into its parent: by `apply`, or by a person where the unit's `done` is `pr: merged`. See [who merges](gates.md#who-merges).
- At the end, the run's pull requests carry everything into the base branch, as the pipeline's `onEnd` says: `pr.merge` lets `apply` merge them once their required checks pass, and `pr.ready` leaves them to a person.

```text
main
└── fab0/412/base                 the run; its pull request into main is the result
    ├── fab0/412/spec             a unit; its pull request targets fab0/412/base
    ├── fab0/412/implement-T1
    └── fab0/412/implement-T2
```

## Flat branching

With `branching: flat`, there is no run branch: each unit's pull request targets the base branch. A factory uses it when its units are independent and each should be on `main` as soon as it is done, with no run-wide review to wait for, or when its steps write no repository at all, as the `triage` example's do.

Who merges follows each unit's gate and `done`, as under run branching, so `apply` merges what they leave to it straight into the base branch, with git. A ruleset that requires a pull request into the base refuses that push, and the unit stops. So a factory whose base is protected that way uses run branching: the `feature` example takes a run branch in the runs repository for that reason. Units inside a gated block merge into the block's branch, not the base branch. To choose, see [choose how a pipeline uses git](../how-to/choose-git-workflow.md).

## Branch names

`git.branches` sets the templates: `fab0/{run}/base` and `fab0/{run}/{unit}` by default. A child run has its parent's run id, so a parent and its children, or two children, that write the same repository would name their branches alike. Factories that share a repository, such as the runs repository, give their branches names of their own: the `delivery` example names them after its own factory. `validate` refuses connected factories that share a repository with the same branch names.

## No empty commits, no empty pull requests

A product repository receives only product changes. Branches are created with no commit. The run branch is pushed when `onStart` creates it, empty, in each repository the run may write. A unit's branch gets a commit only when `record` commits what the unit changed: `record` pushes it then, and `apply` pushes it before it merges it or opens its pull request. A unit's branch with no work stays on the machine that made it.

So a repository the run only reads gets no commit and no pull request, and a step that writes no repository, such as one that works only in the tracker, leaves nothing in any repository. Its record is on its Pipeline Step, like every other unit's. It still works on a branch of the home repository, which never gets a commit, because it reads its parent's state there.

This holds because GitHub opens no pull request without a change, and a commit that changes nothing only adds noise to a product's history.

## Several repositories

A run may write several repositories, each a sibling checkout named in `fab0.yaml`, the runs repository among them when a factory keeps files there. Each gets the same run branch name, and its own run pull request once its run branch has work. The run is done when every run branch with work is merged.

## No force pushes, ever

Branches move forward only. A unit's branch is brought up to date by merging its parent into it, never by a rebase. `apply` changes branches through git plumbing, or in the branch's own checkout only when that checkout is clean, so nobody's work moves under them.

## When GitHub's branch is ahead

A person who merges a unit's pull request on GitHub moves that branch on GitHub past the local copy. When `apply` pushes a branch, run or unit, and GitHub's copy already contains every commit of the local one, it doesn't push. It brings the local branch forward to GitHub's commit and goes on, so the run doesn't stop for a branch nobody has to move. It compares with the `origin/<branch>` ref the session's fetch left, so a branch that moves on GitHub after that fetch isn't seen. If the branch is checked out with uncommitted changes, the checkout stays as it is, the local branch stays behind, and `apply` goes on: it reads the fresher of the local and GitHub's copy anyway.

A branch that has diverged, where each side has a commit the other lacks, still stops the run. `apply` fails with an error that names the repository and the branch, and moves neither side. Someone must bring the two together by hand.

## Claiming a unit

Two machines must never run the same attempt of a unit. When `next` hands an attempt out, it first claims it on the run tracker: it assigns the unit's Pipeline Step to the session's login and writes a claim fact that names this machine. The first claim stands. A machine whose claim lost the race, or that finds another machine's claim, doesn't hand the unit out: the unit shows as `running` with `claimed: elsewhere`. Every attempt is claimed, so two machines can't take the same rework either.

The claim is on the run tracker rather than a branch. Two machines that push the same new branch at the same commit both succeed, so a branch could only be a claim with a commit of its own, and that commit would be an empty one in the product's history.

## Conflicts and failing checks

Before a unit merges, `apply` tests whether its branch merges cleanly into its parent, and, under an `auto` gate, whether its pull request's required checks pass.

- If not, the unit goes back to its agent once, with the conflicting files or the failing checks in its brief. When the merge would be clean, `apply` first brings the branch up to date with its parent; otherwise the agent resolves the conflict markers.
- If the attempt made to fix it has the same trouble, a person decides.

## The final merge

The run's pull requests carry its result into the base branch. `onEnd` typically brings the base branch into each run branch with work (`git.sync-base`), so each pull request shows the result as it will land. Then:

- **`pr.merge`** opens the pull request of any repository that has none yet, waits for each one's required checks, and merges each one through GitHub. Where the base branch requires no checks, it merges in the same pass. Where it does, the checks start only once the pull request is ready, so the pass that opens it waits, and a later `/fab0:run` merges. A ruleset on the base branch that requires a pull request applies, so the base stays protected while nobody has to merge by hand. Every example that writes a repository (`story`, `feature`, `delivery`) ends this way.
- **`pr.ready`** opens what is missing and marks each one ready, and a person merges them.

Merging them ends the run.
