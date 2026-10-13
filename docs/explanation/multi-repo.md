# Several repositories and models

## Workspace

- **Sibling checkouts.** A product's repositories are checked out side by side under one parent directory. `fab0.yaml` declares each one's path, relative to the home repo.
- **Where the session starts.** The orchestrator session starts in the home repo, with `--add-dir` for the others, or with the parent directory as its working directory.
- **The home repo** holds `.fab0/fab0.yaml`. For a single-repo product it is that repository. For several repositories it is a dedicated orchestration repository, or whichever one owns the product's non-code truth.

## How a run spans repositories

- **Tasks.** `foreach: tasks` runs each task in the repository named by its `repo` field. Each task has its own branch and pull request there.
- **Ledgers.** Entries live in the repository where the stage ran.
- **Pinned reads.** Another repository is read at a pinned commit. The brief carries the commit, and the ledger records the hash as an input.
- **Several pull requests** (Planned). A stage that writes several repositories will open one pull request per repository, on branches with the same name, and its gate will pass when all of them are merged. Today the ledger and the pull request belong to the first repository in `repos.write`.
- **`keep: run` artifacts.** `deliver` changes only the home repo, so such artifacts in other repositories stay. Whether it should clean them up is an [open decision](decisions.md).

The default for several repositories is the flat `story` pipeline, with tasks in each repository. When repositories follow different processes, each can own a pipeline that the Story calls: see [nesting](nesting.md) (Planned).

**Planned:** `repo: each-touched`, an artifact kept once per repository a run touches. The name is reserved but not implemented.

## Models

- **Classes.** A stage names a model class (`deep`, `balanced`, `fast`). `fab0.yaml` maps each class to a model per harness under `models:`. The orchestrator passes the result as the Agent tool's `model`.
- **Profiles.** A profile changes the mapping for one run: `/fab0:run 412 --profile cheap`. It applies a JSON Merge Patch (RFC 7396) to `fab0.yaml`.
- **Review on a different model.** The core `story` pipeline reviews on a different model from the one that implemented: the reviewer gate uses `deep`, `implement` uses `balanced`. This is a default, not a rule, because its benefit hasn't been measured.

## Harness portability

Only Claude Code is supported. A second harness would have to replace this list:

- the orchestrator skill;
- the `fab0:github` skill's tool use;
- the agent files' frontmatter;
- the project's `.claude/settings.json`;
- any hooks.

Pipelines, stages, artifact types, the ledger, the resolver and every skill body stay harness-neutral by rule.

Not planned yet, but expected once a second harness exists:

- a `harness:` key on a stage;
- per-class fallback lists of models.
