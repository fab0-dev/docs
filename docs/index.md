# fab0 documentation

> **Being rewritten.** These pages describe fab0 0.5, a delivery factory. fab0 is being rebuilt as a toolkit for building factories, and the pages are rewritten in the refactor's step R7. The plan and the target model are in [REFACTOR.md](https://github.com/fab0-dev/fab0/blob/main/REFACTOR.md).

fab0 runs software delivery as pipelines of Claude Code agents, wired in a few short YAML files and carried on GitHub.

These pages describe fab0 as it is in the latest release of the core plugin. What is designed but not built yet is marked.

## Status markers

| Marker | Meaning |
|---|---|
| (none) | Built and in the latest release |
| **Planned (step X)** | Designed, not built. The step is in the [roadmap](https://github.com/fab0-dev/fab0/blob/main/ROADMAP.md) |
| **Since 0.x** | Added in that release, for features newer than the first public one |

## Explanation: how fab0 works and why

- [What fab0 is](explanation/overview.md): constraints, principles, glossary
- [How a run executes](explanation/execution.md): the orchestrator, the resolver, the next-stage rule
- [Artifacts and the ledger](explanation/artifacts-and-ledger.md)
- [Verification](explanation/verification.md): the verification ladder and write scope
- [Gates and handoff](explanation/gates-and-handoff.md): how people take turns, and a Story from start to done
- [Several repositories and models](explanation/multi-repo.md)
- [Nesting pipelines](explanation/nesting.md) (Planned)
- [Decisions](explanation/decisions.md): open questions and rejected alternatives

## How-to guides

- [Set up a project](how-to/set-up-a-project.md)
- [Set up GitHub](how-to/github-setup.md)

## Reference

- [Wiring](reference/wiring.md): `fab0.yaml`, artifact types, stages, pipelines
- [Commands](reference/commands.md): `/fab0:run`, `/fab0:inbox`, `fab0-resolve`
- [Ledger](reference/ledger.md)

## Repositories

| Repository | Contents |
|---|---|
| [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0) | The product's home repo: rules, roadmap, fab0's own wiring and specs |
| [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) | The `fab0` marketplace and core plugin: resolver, schemas, agents, skills |
| [`fab0-dev/fab0-recipes`](https://github.com/fab0-dev/fab0-recipes) | Ready-made `.fab0/` setups to copy into a project |
| [`fab0-dev/docs`](https://github.com/fab0-dev/docs) | These docs |
