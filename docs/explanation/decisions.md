# Decisions

This page records the choices still open and the alternatives already rejected. Choices made where they apply (no loop construct, no approve command, actions outside the ledger, issue state not counted as done) are explained on their own pages.

## Open decisions

Each is settled after the [roadmap](https://github.com/fab0-dev/fab0/blob/main/ROADMAP.md) step named.

| Question | Settled after |
|---|---|
| Is one spec in the home repo enough, or does each repository need its own through `repo: each-touched`? | B.2 |
| Does write scope need interception during a stage, by a `PreToolUse` hook keyed on the agent, or is the check after the stage enough? | B.2 |
| Is finding sub-issues by the id in their title robust enough, or do actions need a hidden key? | B.1 |
| Should pending actions run from a small GitHub Actions workflow on merge, instead of waiting for someone to follow the `/fab0:inbox` hint? | B.3 |
| Is `uv` an acceptable prerequisite, or should the resolver be rewritten for a runtime Claude Code already guarantees? | A.6 |
| `deliver` changes only the home repo, so `keep: run` artifacts in other repositories stay. Should it open a clean-up pull request per repository? | B.2 |
| `when` and `call` are refused until a pipeline needs them, and schemas from plugins other than `fab0` don't resolve yet, because one plugin can't find another's directory. | B.4, C.2 |

## Rejected alternatives

- **The model reads the pipeline and routes.** Hashing for staleness and validating JSON need code anyway, and routing by the model is costly and fragile (P2).
- **A compile step that generates the runtime configuration.** It duplicates what Claude Code already loads (P6).
- **A cascade of configuration levels** (organisation, product, repository, pipeline, stage). Profiles plus a project's own YAML cover it.
- **A fab0 command-line tool in the first version** (`init`, `add`, `update`, `doctor`). Claude Code is the harness; recipes are copied by hand, and the doctor checks are a checklist in the recipe README. A tool is the natural next step once copying becomes a chore.
- **A fab0-specific plugin layout** (a `fab0/` directory and lookups inside plugins). Any plugin works as it is (P1).
- **A long-running cloud process that owns runs.** Most of a run's life is waiting for people, and such a process would become a second copy of the state.
- **A blob artifact store.** Git with LFS is enough.
- **Zero-padded ids.** A fixed width eventually overflows and has to be migrated. Ids and ledger names are unpadded and sorted numerically.
- **Mirroring order and status across files, board and comments.** Each fact has one home (P3); the board is a projection.
