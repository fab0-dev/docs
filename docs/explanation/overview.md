# What fab0 is

fab0 runs software delivery as pipelines of Claude Code agents. A pipeline is wired in a few short YAML files in the project, and its progress is carried on GitHub.

This page gives the constraints fab0 is built under, the principles that follow from them, and the words the rest of the docs use.

## Constraints

- **Claude Code is the harness.** There are no containers, no fab0 command-line tool and no hosted runner. A pipeline runs inside a Claude Code session, interactive or headless (`claude -p`).
- **A factory is composed from stages declared in YAML.**
- **Stages exchange typed artifacts,** not only Markdown. Which artifact types exist is configuration.
- **GitHub and GitHub Projects show and carry the workflow.**
- **Verification uses what already exists** (schemas, linters, the project's tests, a review agent) before anything written for fab0.
- **Only Claude models for now,** but nothing in the YAML may depend on that.

fab0 relies on these Claude Code facts:

- The Agent tool takes a `model` per call, which overrides the agent file. A subagent starts with a fresh context and returns one message.
- Files in a plugin's `bin/` directory are on the Bash `PATH`. One plugin can't find another plugin's install directory.
- Plugin subagents ignore `permissionMode`, `hooks` and `mcpServers`. The project's `.claude/settings.json` permission rules also apply to subagents.
- Headless mode supports `--permission-mode dontAsk`, `--max-budget-usd`, `--output-format json` and `--add-dir`.

## Principles

Each principle has a reason. A principle without one would be a preference.

- **P1. Plugins carry behaviour; the project carries wiring.** Agents and skills come from ordinary Claude Code plugins, from any marketplace. Stages, pipelines and artifact types are short YAML files in the project's `.fab0/` that name those agents. *Reason:* any plugin can join a pipeline without knowing about fab0, and the wiring stays readable in one place.
- **P2. The model does not route.** A deterministic resolver picks the next stage from the pipeline, the ledger and GitHub. The orchestrating session executes and doesn't decide. *Reason:* when a model routes, routing costs tokens on every step, and it is where most failures concentrate.
- **P3. Git is the truth for content; GitHub is the truth for human decisions; the Projects board is a projection.** *Reason:* each fact has one home, so nothing has to be reconciled.
- **P4. Verify at the source, cheaply, with standard tools.** An agent's output is checked against a schema when it returns, and files are linted when they are written. Judgment goes to a review agent. *Reason:* free-form output has to be re-parsed by custom checks, which grow without limit.
- **P5. Prefer an artifact a tool can check over a section of prose.** Tasks are YAML, a verdict is JSON, scenarios are `.feature` files. *Reason:* a structured artifact needs a schema; a section of prose needs a parser.
- **P6. No compile step.** The YAML is read at run time and checked by the resolver before anything runs. *Reason:* Claude Code already loads plugins and settings, so a generated copy would duplicate it.
- **P7. Name capabilities, not vendors.** A stage asks for a model class, and the project maps classes to models. *Reason:* the YAML must not depend on one model provider.
- **P8. Add a rule only when a run has needed it.** *Reason:* rules written ahead of use guess at problems and then have to be maintained.

## Glossary

| Term | Meaning |
|---|---|
| Item | A GitHub issue that a pipeline runs for, typed by its issue type (Story, Task, …) |
| Run | One pipeline executing for one item, until it is done |
| Run id | The issue number of the run's item, for example `412`. Commands, branches, ledger paths and the board all use it |
| Stage | One step of a pipeline: an agent stage (one agent call) or an action stage |
| Action | A deterministic GitHub operation with no model and no owner, made of a check and an apply step. Both are safe to repeat |
| Task | One entry of a run's `tasks.yaml`. It has its own sub-issue, branch and pull request, but it is not a run. Commands address it as `--task T2` |
| Attempt | The n-th execution of an agent stage for the same run and task |
| Gate | What must pass before the pipeline moves on: `none`, an agent gate, or `human` |
| Stage PR | The pull request of a stage branch. Merging it is the human gate |
| Done | A task or run is done when its last human-gated pull request is merged. Issue state follows from that and is not the record |
| Ledger | The append-only record of agent-stage attempts, kept in git |
| Recipe | A complete set of `.fab0/` files for one way of working, copied into a project |
| Home repo | The repository that holds `.fab0/fab0.yaml`, the specs and the ledgers of stages run there |

## Where to go next

- How a run moves: [execution](execution.md).
- What stages pass to each other: [artifacts and the ledger](artifacts-and-ledger.md).
- How people take turns: [gates and handoff](gates-and-handoff.md).
- The file formats: [wiring reference](../reference/wiring.md).
