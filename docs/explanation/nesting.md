# Nesting pipelines

**Status: Planned (roadmap step B.4).** The resolver refuses `call`, and pipeline `inputs` and `outputs`, as "not supported yet". Until B.4 passes, the flat `story` pipeline is the way to work across repositories. This page describes the design that B.4 will test.

## When to nest

For a single-repo product, or a Story whose repositories follow the same process, the flat `story` pipeline is simpler. Nesting is for repositories that really work differently, for example a backend with contract-first design and migrations next to a frontend with design review.

It costs more issues (a Story, one Delivery per repository, then Tasks) and one more gate per repository. GitHub sub-issues can span repositories in one organisation, so the hierarchy and its progress bars still show on the board.

## `call`

`call` runs another pipeline for a child item, possibly in another repository. It works like a function call: the called pipeline declares its inputs and outputs, and the caller passes artifacts in. Each repository owns how it plans and builds. The Story in the home repo owns only what is shared: the spec, the fan-out to repositories, and delivery.

Every repository that owns a pipeline has its own `.fab0/` with its stages, artifact types and pipelines. `fab0.yaml` exists only in the home repo.

The parent, in the home repo. The spec stage also writes `scope.yaml`, because `foreach` reads only structured artifacts:

```yaml
pipeline: story
item: {issue_type: Story}
stages:
  - spec                    # spec.md + scope.yaml (repos: [backend, web])
  - foreach: scope.repos    # decided by the approved spec
    call: {pipeline: delivery, repo: "{each}"}
    inputs: {spec: spec}
  - deliver                 # after every child run is done
```

The children, each in its own repository and owned by its team:

```yaml
# backend/.fab0/pipelines/delivery.yaml
pipeline: delivery
item: {issue_type: Delivery}
inputs:  {spec: spec}
outputs: {contract: openapi}
stages:
  - breakdown   # this repository's tasks.yaml from the spec; gate: human
  - contract    # openapi.yaml; gate: human
  - plan
  - foreach: tasks
    item: {issue_type: Task}
    stages: [implement]
    gate: human
```

```yaml
# web/.fab0/pipelines/delivery.yaml
pipeline: delivery
item: {issue_type: Delivery}
inputs: {spec: spec, contract: {type: openapi, from: backend}}
stages:
  - breakdown   # needs only the spec, so it starts when the spec is merged
  - plan
  - foreach: tasks
    item: {issue_type: Task}
    stages: [implement]   # implement reads the contract, so it waits for it
    gate: human
```

## Child run ids

- **Form.** A child run adds a key and its own number: `{parent}-{key}-{n}`, for example `412-BE-1`. Each repository declares its key in `fab0.yaml` (two or three capital letters).
- **Numbering.** The number counts child runs of that key under the same parent. A new number is used only when a cancelled child is replaced (`412-BE-2`).
- **Deeper nesting** appends the same pattern: `412-BE-1-DB-1`. The id shows the path from the root.
- **No padding.** Numbers are not zero-padded, and ids sort numerically.

| Place | Form | Example |
|---|---|---|
| Command | run id | `/fab0:run 412-BE-1` |
| Child issue title | `[run id] title` | `[412-BE-1] Booking extension: backend` |
| Board | `Run` field | `412-BE-1` |
| Stage branch | `{stage}/{run}-{slug}` | `contract/412-BE-1-booking-extension` |
| Ledger | `work/{run}/ledger/` where the stage ran | `work/412-BE-1/ledger/contract-1.yaml` |

**Allocation.** `call` is an action: a check plus an apply step.

1. The check lists the parent's sub-issues and reads the run ids from their titles.
2. For each repository in the fan-out that has no open child, the apply step creates one, numbered after the highest already used for that key.

Two people starting the same fan-out at once can still create a duplicate. The resolver reports duplicate ids, and a person closes one. Like task claims, this is a social guarantee, not an atomic one.

## How it runs

1. The product owner merges the spec pull request. The next `/fab0:run 412`, by anyone, runs the fan-out and creates `412-BE-1` and `412-FE-1`: a Delivery issue in each repository, a sub-issue of the Story, assigned to the repository's owner.
2. Both developers run `breakdown` in parallel, each in their own repository, from the same spec. Each child's ledger records the spec's hash.
3. The backend's contract pull request is merged. The web child's `contract` input is now on the backend's base branch, so its implement stages become runnable.
4. When both children are done, the Story's `deliver` collects their outputs, and its pull request closes the Story.

## The join

- **A child is done** when its last human-gated pull request is merged. Nothing is written to mark it. The next `/fab0:run` that sees a done child closes its Delivery issue as a projection.
- **The parent's next step** is runnable when every child it created is done. The resolver evaluates children before their parent, so whoever moves first sees the join.
- **Closed children.**
  - A child closed by hand while its run isn't done is reported, not counted.
  - A child closed as not planned leaves the parent `blocked`. A person then replaces it, or removes the repository from `scope.yaml`.

## Siblings are ordered by artifacts, not by issues

An input with `from:` names a sibling's output. The resolver doesn't run a stage that reads it until that artifact is merged. This is finer than GitHub's blocked-by, which would hold the whole web delivery until the backend is done, although web can start its breakdown at once. The board's `Waiting on` field shows the reason, for example `backend: contract`.

## Staleness crosses levels with no new rule

If the spec changes after the children started, their recorded spec hash no longer matches. They go stale and run their stages again under the same run id: `breakdown` first, then the `plan` check reconciles their tasks. If the backend contract changes after web implemented against it, web's affected tasks go stale.

## Validation across repositories

The resolver will read a child pipeline from that repository's base branch and check, before anything runs:

- every `call` names a pipeline that exists in the named repository;
- the caller's inputs match the called pipeline's declared input types, and every `from:` names an output a sibling declares;
- no pipeline calls itself, directly or indirectly;
- nesting is at most three levels deep.

Types are checked; meaning is not. A change to a pipeline's declared outputs is reviewed like any interface change.

## Considered and not used

- **One hub pipeline with per-repository branches.** It would make the home repo own every team's process.
- **Independent repository pipelines with no parent.** They lose the join and the place to collect delivery results.
