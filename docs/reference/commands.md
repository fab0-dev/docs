# Commands

The `fab0` plugin adds the engine, `fab0-resolve`, to the Bash `PATH` of every Claude Code session, and two slash commands. It needs [`uv`](https://docs.astral.sh/uv/), and an authenticated [`gh`](https://cli.github.com/).

## Slash commands

| Command | What it does |
|---|---|
| `/fab0:run <run> [--pipeline P] [--profile P] [--unit U]` | Runs the pipeline for one run until it needs a person, is blocked or is done: `next --apply`, the hand-outs, `record`, and again. It shows the start and end lines, the agents' activity, what `apply` did and each unit's duration as it goes. See [running a pipeline](../explanation/execution.md) |
| `/fab0:inbox [--as USER]` | Shows every open run, what waits on you, what anyone can run, and what is blocked. Read-only |

The plugin also has a `fab0:github` skill, which checks and prepares GitHub for a factory. See [set up GitHub](../how-to/github-setup.md).

## `fab0-resolve`

Every command prints one JSON object.

| Command | What it does |
|---|---|
| `fab0-resolve validate` | Checks the project's `.fab0/` wiring. Prints the pipelines, steps, artifacts, and the workspace: each repository's local path and whether it is there |
| `fab0-resolve status <run>` | Every unit of the run and its state, and each unit's total duration (`duration` in seconds, and `took`, such as `8m 17s`): the sum over its recorded attempts and gate decisions. A unit that has none recorded, or an entry without times, has no duration. Read-only |
| `fab0-resolve next <run> [--apply]` | The same, and a hand-out for every unit that is ready or running and every auto gate that is due. Claims each unit it hands out. Each hand-out but an action's carries `line`, its start line, and records when it was handed out. With `--apply` it first performs what is due, as `apply` does, then hands out from the last read of the tracker `apply` made: see [`next --apply`](#next---apply) |
| `fab0-resolve record <run> <unit>` | Checks a handed-out unit's result and writes its ledger entry in the unit's checkout. The result carries `started`, `ended`, `duration` and `took`, and `line`, the end line. It reads the run's item from the tracker only when it must pick the pipeline: the unit and its context come from git and its saved hand-out, not from the tracker. The one exception is a unit that sits behind a `when` only the tracker can decide: it isn't in the run without the tracker, so `record` then reads the tracker as `status` does |
| `fab0-resolve apply <run>` | Performs what is due: actions, merges, pull requests, comments, signals. Writes to git and the tracker |
| `fab0-resolve inbox` | Every open run of the project, and what it needs from whom. Read-only |
| `fab0-resolve --version` | The fab0 release of the engine |

### `next --apply`

`fab0-resolve next <run> --apply` is one command for a round: it runs `apply`, then hands out from the evaluation `apply` ended with, so `next`'s own read of the tracker is saved. When `apply` changes nothing, the round is one pass over the tracker; when `apply` changes something, such as a merge, it reads the tracker again to see the effect, and the hand-outs come from that last read. Like every command, it reads the tracker's current state when it starts; nothing is kept between commands.

Its result holds what `apply` gives (`applied`, with what it did, and `kind`) and what `next` gives (`handouts` and `units`). The `handouts` and `units` are those `next` would give if it ran right after `apply`.

- **`--unit UNIT`** limits the hand-outs only. `apply` performs what is due for every unit, that unit's or not. When the unit isn't ready, the command exits with 4, and its result still lists `applied`.
- **A run that is finished.** When the run's `kind` is `done`, or `waiting` for the merge of its pull request, nothing is handed out.
- **When `apply` fails**, for example on a merge conflict with the base, the command exits with `apply`'s code and error, and hands out and claims nothing.

`next` and `apply` without `--apply` behave as before, so they can still be run one after the other.

### Options

| Option | Commands | Meaning |
|---|---|---|
| `--project DIR` | all | The home repo. Default: found from the current directory; from inside a worktree, its main checkout |
| `--profile NAME` | all | A profile from `fab0.yaml` to apply |
| `--pipeline NAME` | `status`, `next`, `record`, `apply` | The pipeline. Default: the project's only pipeline, else the one whose trigger the run matches |
| `--as USER` | all but `validate` | Who is running. Default: the tracker login |
| `--apply` | `next` | Perform what is due first, as `apply` does, then hand out |
| `--unit UNIT` | `next`, `apply` | Only this unit. With `next --apply` it limits the hand-outs only: `apply` still performs what is due for every unit |
| `--return FILE` | `record` | The agent's or tool's JSON reply |
| `--exit CODE` | `record` | A command's exit code |
| `--gate` | `record` | Record the unit's auto gate: its verdict, or `--exit` for a command gate |
| `--output FILE` | `record` | A command gate's output, kept as the finding when it fails |

### Older engine

Every command that reads the project (`validate`, `status`, `next`, `record`, `apply`, `inbox`) first compares the engine's release with the plugin release Claude Code has installed for the project, read from the install record under `CLAUDE_CONFIG_DIR`. A local record for the project takes precedence over a project one, and a project one over a user one.

When the engine is older, the command exits 1 and writes nothing: no claim, ledger entry, git or tracker change. It prints `"ok": false`, an `error` naming both releases and their paths, and a `fix` list: each orphaned cached version directory to remove, then to start a new Claude Code session. `/fab0:run` and `/fab0:inbox` show the `error` and every `fix` line, and stop. See [update the plugin](../how-to/use-an-example.md#update-the-plugin).

An engine of the same or a newer release runs as before. With no install record for the project, it also runs as before. With an unreadable record or release, `validate`, `inbox` and the run commands run and add a warning that the release couldn't be checked. `fab0-resolve --version` is never refused.

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
| `CLAUDE_CONFIG_DIR` | Claude Code's configuration directory. The engine reads the plugin install record, `plugins/installed_plugins.json`, and the plugin cache under it. Default: `~/.claude` |
| `FAB0_GH_FAKE` | A JSON file to read and write tracker facts in, instead of GitHub. For tests |
