# fab0 documentation

fab0 is a toolkit for building and operating software factories: pipelines of agents, commands and tools, written as short YAML files, with a gate on every transition, run on their own git branches, and tracked on GitHub.

These pages describe the latest release of the `fab0` plugin.

## Status markers

| Marker | Meaning |
|---|---|
| (none) | Built |
| **Planned** | Designed and accepted by `validate` where it says so, but not built. The page says what exists today |

## Explanation: how fab0 works and why

- [What fab0 is](explanation/overview.md): building blocks, principles, glossary
- [Pipelines and steps](explanation/pipelines.md): triggers, executors, operators, units, lifecycle actions
- [Gates](explanation/gates.md): `none`, `auto` and `human`, questions, and who merges
- [Branches and merges](explanation/branching.md): run branches, claims, conflicts
- [Dependencies and blocking](explanation/dependencies.md): unit states, and the tracker's relations
- [Artifacts and the ledger](explanation/artifacts-and-ledger.md): kinds, staleness, checks, the record
- [Running a pipeline](explanation/execution.md): the engine, the session, and the loop
- [The tracker](explanation/tracker.md): what fab0 reads from GitHub, and what it writes
- [Examples](explanation/examples.md): ready-made factories, and how to take one

## How-to guides

- [Build your first factory](how-to/build-your-first-factory.md)
- [Use an example](how-to/use-an-example.md)
- [Set up GitHub](how-to/github-setup.md)
- [Choose how a pipeline uses git](how-to/choose-git-workflow.md)

## Reference

- [Project file](reference/project.md): `.fab0/fab0.yaml`
- [Pipeline](reference/pipeline.md): `.fab0/pipelines/<name>.yaml`, operators, gates, conditions
- [Step](reference/step.md): `.fab0/steps/<name>.yaml`
- [Artifact](reference/artifact.md): `.fab0/artifacts/<name>.yaml`
- [Returns and verdicts](reference/returns-and-verdicts.md): what agents reply
- [Ledger entry](reference/ledger.md)
- [Actions](reference/actions.md): the catalogue
- [Commands](reference/commands.md): `/fab0:run`, `/fab0:inbox`, `fab0-resolve`

## Repositories

| Repository | Contents |
|---|---|
| [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0) | The product's home repo: its rules, roadmap and principles |
| [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) | The `fab0` marketplace and plugin: the engine, the schemas, `/fab0:run` and `/fab0:inbox` |
| [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) | Example factories to copy, with their agents and skills |
| [`fab0-dev/docs`](https://github.com/fab0-dev/docs) | These docs, and the factory that maintains them |
