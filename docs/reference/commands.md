# Commands

The `fab0` plugin adds the engine, `fab0-resolve`, to the Bash `PATH` of every Claude Code session, and two slash commands. It needs [`uv`](https://docs.astral.sh/uv/), and an authenticated [`gh`](https://cli.github.com/).

## Slash commands

| Command | What it does |
|---|---|
| `/fab0:run <run> [--pipeline P] [--profile P] [--unit U]` | Runs the pipeline for one run until it needs a person, is blocked or is done: `apply`, `next`, the hand-outs, `record`, and again. It shows the start and end lines, the agents' activity, what `apply` did and each unit's duration as it goes, and, once at the start of the first round, the `log --follow` command that follows the run from another terminal. See [running a pipeline](../explanation/execution.md) |
| `/fab0:inbox [--as USER]` | Shows every open run, what waits on you, what anyone can run, and what is blocked, and beside each run its latest event, when it has one on this machine. Read-only |

The plugin also has a `fab0:github` skill, which checks and prepares GitHub for a factory. See [set up GitHub](../how-to/github-setup.md).

## `fab0-resolve`

Every command prints one JSON object, except `log`, which prints text when it succeeds. Its errors are the usual JSON object.

| Command | What it does |
|---|---|
| `fab0-resolve validate` | Checks the project's `.fab0/` wiring. Prints the pipelines, steps, artifacts, and the workspace: each repository's local path and whether it is there |
| `fab0-resolve status <run>` | Every unit of the run and its state, and each unit's total duration (`duration` in seconds, and `took`, such as `8m 17s`): the sum over its recorded attempts and gate decisions. A unit that has none recorded, or an entry without times, has no duration. Read-only |
| `fab0-resolve next <run>` | The same, and a hand-out for every unit that is ready or running and every auto gate that is due. Claims each unit it hands out. Each hand-out but an action's carries `line`, its start line, and records when it was handed out |
| `fab0-resolve record <run> <unit>` | Checks a handed-out unit's result and writes its ledger entry in the unit's checkout. The result carries `started`, `ended`, `duration` and `took`, and `line`, the end line |
| `fab0-resolve apply <run>` | Performs what is due: actions, merges, pull requests, comments, signals. Writes to git and the tracker. The result carries `follow`, the command that follows the run with `log --follow` |
| `fab0-resolve inbox` | Every open run of the project, and what it needs from whom. Each run that has events on this machine carries `latest`, the `time` and `line` of its last event. Read-only |
| `fab0-resolve log <run>` | Prints the run's [event log](#the-event-log): one line for each event, oldest first, its time (UTC) and its line. With `--follow`, keeps printing new events. Reads only the home checkout's git directory: no wiring, tracker or `gh`, and no version check. Read-only |
| `fab0-resolve --version` | The fab0 release of the engine |

### Options

| Option | Commands | Meaning |
|---|---|---|
| `--project DIR` | all | The home repo. Default: found from the current directory; from inside a worktree, its main checkout |
| `--profile NAME` | all but `log` | A profile from `fab0.yaml` to apply |
| `--pipeline NAME` | `status`, `next`, `record`, `apply` | The pipeline. Default: the project's only pipeline, else the one whose trigger the run matches |
| `--as USER` | all but `validate` and `log` | Who is running. Default: the tracker login |
| `--unit UNIT` | `next`, `apply` | Only this unit |
| `--return FILE` | `record` | The agent's or tool's JSON reply |
| `--exit CODE` | `record` | A command's exit code |
| `--gate` | `record` | Record the unit's auto gate: its verdict, or `--exit` for a command gate |
| `--output FILE` | `record` | A command gate's output, kept as the finding when it fails |
| `--follow` | `log` | After the events already logged, keep printing each new one, checking about once a second, until interrupted. Ctrl-C ends it with exit 0 |

### The event log

`next`, `record` and `apply` append each event of a run to `fab0/events/<run>.jsonl` in the home repo's git common directory: one JSON object per line, with `time` (UTC, to the second), `kind` (`handout`, `record`, `gate`, `apply`, `waiting` or `blocked`), `line`, and when they apply `unit`, `attempt` and `reason`. The log is local to the machine, and never committed, pushed or written to the tracker. `validate`, `status`, `inbox` and `log` never write it. A write that fails never changes a command's result or exit code: the result carries a warning that the event couldn't be logged, and why. See [following a run from outside its session](../explanation/execution.md#following-a-run-from-outside-its-session).

`log` prints one line for each event, and follows the run from any terminal with `--follow`:

```
$ fab0-resolve log 54 --follow
2026-10-16T10:04:12Z  spec, attempt 1: implementer on opus, branch fab0/54/spec
2026-10-16T10:12:40Z  spec, attempt 1: verified, 8m 28s
2026-10-16T10:12:41Z  waiting: spec (gate human)
```

A run with no events on this machine prints `run 77 has no events here yet`, and exits 0. A line that isn't a valid event prints as `event N can't be read`. With a run id that has characters other than letters, digits, `.`, `_` and `-`, or with no `.fab0/fab0.yaml` in the current directory or above it and no `--project`, `log` prints the usual `"ok": false` object and exits 2.

### Older engine

Every command that reads the project (`validate`, `status`, `next`, `record`, `apply`, `inbox`; not `log`) first compares the engine's release with the plugin release Claude Code has installed for the project, read from the install record under `CLAUDE_CONFIG_DIR`. A local record for the project takes precedence over a project one, and a project one over a user one.

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
