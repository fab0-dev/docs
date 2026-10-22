# fab0 documentation

> **fab0 is being rebuilt.** These pages describe 0.10 and won't change until the rebuild's cutover, when they are rewritten against the new stack. The plan is [`REBUILD.md`](https://github.com/fab0-dev/fab0/blob/main/REBUILD.md) in the home repo.

fab0 is a toolkit for building and operating software factories: pipelines of agents, commands and tools, written as short YAML files, with a gate on every transition, run on their own git branches, and tracked on GitHub.

These pages describe the latest release of the `fab0` plugin, 0.10. Each run is an issue in a run tracker, with an issue for each of its steps, and those issues carry the run's state between steps and between factories. Every step defines its done in configuration, and its gate alone says who makes it hold: an agent, a command, or a person, in a pull request, on an issue or at the prompt. What runs produce for themselves are files in a runs repository, and the run store and its ledger are gone. 0.8 connects factories: a step of one factory runs a pipeline of another, in another repository. Coming from 0.9: see [Upgrade from 0.9](how-to/upgrade-from-0.9.md).

## Status markers

| Marker | Meaning |
|---|---|
| (none) | Built |
| **Planned** | Designed and accepted by `validate` where it says so, but not built. The page says what exists today |

## Explanation: how fab0 works and why

- [What fab0 is](explanation/overview.md): building blocks, principles, glossary
- [Pipelines and steps](explanation/pipelines.md): triggers, executors, operators, units, lifecycle actions
- [Gates](explanation/gates.md): definitions of done, `none`, `auto` and `human`, questions, and who merges
- [Branches and merges](explanation/branching.md): run branches, claims, conflicts
- [Dependencies and blocking](explanation/dependencies.md): unit states, and the tracker's relations
- [Connected factories](explanation/connected-factories.md): calling another repository's factory, what passes between them, and who judges what
- [Artifacts](explanation/artifacts.md): kinds, files in repositories, the runs repository, checks
- [Running a pipeline](explanation/execution.md): the engine, the session, and the loop
- [The tracker](explanation/tracker.md): the run's state on its issues, and what fab0 reads from GitHub and writes
- [Examples](explanation/examples.md): ready-made factories, and how to take one

## How-to guides

- [Build your first factory](how-to/build-your-first-factory.md)
- [Use an example](how-to/use-an-example.md)
- [Start and continue a run](how-to/start-and-continue-a-run.md)
- [Follow a run](how-to/follow-a-run.md) on its issues
- [Connect a factory](how-to/connect-a-factory.md)
- [Set up GitHub](how-to/github-setup.md), with the run tracker and the runs repository
- [Choose how a pipeline uses git](how-to/choose-git-workflow.md)
- [Upgrade from 0.9](how-to/upgrade-from-0.9.md)

## Reference

- [Project file](reference/project.md): `.fab0/fab0.yaml`, `tracking`, connected `factories`
- [Pipeline](reference/pipeline.md): `.fab0/pipelines/<name>.yaml`, `inputs` and `outputs`, operators and `call`, `done`, gates, conditions
- [Step](reference/step.md): `.fab0/steps/<name>.yaml`
- [Artifact](reference/artifact.md): `.fab0/artifacts/<name>.yaml`
- [Returns and verdicts](reference/returns-and-verdicts.md): what agents reply
- [Run tracker](reference/tracker.md): Pipeline Run and Pipeline Step issues, their fields, their lifecycle, and the facts on their comments
- [Actions](reference/actions.md): the catalogue
- [Commands](reference/commands.md): `/fab0:run`, `/fab0:inbox` and `fab0-resolve`

## Repositories

| Repository | Contents |
|---|---|
| [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0) | The product's home repo: its rules, roadmap and principles |
| [`fab0-dev/fab0-core`](https://github.com/fab0-dev/fab0-core) | The `fab0` marketplace and plugin: the engine, the schemas, `/fab0:run` and `/fab0:inbox` |
| [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) | Example factories to copy, with their agents and skills |
| [`fab0-dev/docs`](https://github.com/fab0-dev/docs) | These docs, and the factory that maintains them |
