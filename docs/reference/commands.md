# Commands

The `fab0` plugin adds the engine, `fab0-resolve`, to the Bash `PATH` of every Claude Code session, and two slash commands. It needs [`uv`](https://docs.astral.sh/uv/), and an authenticated [`gh`](https://cli.github.com/).

## Slash commands

| Command | What it does |
|---|---|
| `/fab0:run <run> [--pipeline P] [--profile P] [--unit U]` | Runs the pipeline for one run until it needs a person, is blocked or is done: `apply`, `next`, the hand-outs, `record`, and again. See [running a pipeline](../explanation/execution.md) |
| `/fab0:inbox [--as USER]` | Shows every open run, what waits on you, what anyone can run, and what is blocked. Read-only |

The plugin also has a `fab0:github` skill, which checks and prepares GitHub for a factory. See [set up GitHub](../how-to/github-setup.md).

## `fab0-resolve`

Every command prints one JSON object.

| Command | What it does |
|---|---|
| `fab0-resolve validate` | Checks the project's `.fab0/` wiring. Prints the pipelines, steps, artifacts, and the workspace: each repository's local path and whether it is there |
| `fab0-resolve status <run>` | Every unit of the run and its state. Read-only |
| `fab0-resolve next <run>` | The same, and a hand-out for every unit that is ready or running and every auto gate that is due. Claims each unit it hands out |
| `fab0-resolve record <run> <unit>` | Checks a handed-out unit's result and writes its ledger entry in the unit's checkout |
| `fab0-resolve apply <run>` | Performs what is due: actions, merges, pull requests, comments, signals. Writes to git and the tracker |
| `fab0-resolve inbox` | Every open run of the project, and what it needs from whom. Read-only |
| `fab0-resolve --version` | The fab0 release of the engine |

### Options

| Option | Commands | Meaning |
|---|---|---|
| `--project DIR` | all | The home repo. Default: found from the current directory; from inside a worktree, its main checkout |
| `--profile NAME` | all | A profile from `fab0.yaml` to apply |
| `--pipeline NAME` | `status`, `next`, `record`, `apply` | The pipeline. Default: the project's only pipeline, else the one whose trigger the run matches |
| `--as USER` | all but `validate` | Who is running. Default: the tracker login |
| `--unit UNIT` | `next`, `apply` | Only this unit |
| `--return FILE` | `record` | The agent's or tool's JSON reply |
| `--exit CODE` | `record` | A command's exit code |
| `--gate` | `record` | Record the unit's auto gate: its verdict, or `--exit` for a command gate |
| `--output FILE` | `record` | A command gate's output, kept as the finding when it fails |

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Done |
| 1 | An error, for example a failing `git` or `gh` call |
| 2 | A usage error, for example an unknown pipeline |
| 3 | The wiring is invalid; `errors` lists each problem with its file |
| 4 | Refused, for example a reply that doesn't match its schema, or a unit that wasn't handed out |

### Environment

| Variable | Meaning |
|---|---|
| `FAB0_GH_FAKE` | A JSON file to read and write tracker facts in, instead of GitHub. For tests |
