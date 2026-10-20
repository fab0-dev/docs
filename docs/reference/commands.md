# Commands

The `fab0` plugin adds the engine, `fab0-resolve`, to the Bash `PATH` of every Claude Code session, and two slash commands. It needs [`uv`](https://docs.astral.sh/uv/), and an authenticated [`gh`](https://cli.github.com/).

## Slash commands

| Command | What it does |
|---|---|
| `/fab0:run [#<item> \| <run>] [--pipeline P] [--profile P] [--unit U]` | Runs the pipeline for one run until it needs a person, is blocked or is done: `next --apply`, the hand-outs, `record`, and again. `#<item>` starts a run from an item of the home repository, or goes on with the run it has; `<run>` names a run by its id; with neither, it goes on with the only run that has work here, and asks which when several have (`pick`). It first runs `start '<argument>' --session`, which counts the session as one more pass over the run, and it ends with the run's position. It shows the start and end lines, the agents' activity, what `apply` did and each unit's duration as it goes, and, once at the start of the first round, the `log --follow` command that follows the run from another terminal. See [running a pipeline](../explanation/execution.md) |
| `/fab0:inbox [--as USER]` | Shows every open run, where it is, what waits on you, what anyone can run, and what is blocked, and beside each run its latest event, when it has one on this machine. An item no run has started shows with `/fab0:run #<n>`. Read-only |

The plugin also has a `fab0:github` skill, which checks and prepares GitHub for a factory. See [set up GitHub](../how-to/github-setup.md).

## `fab0-resolve`

Every command prints one JSON object, except `log`, which prints text when it succeeds. Its errors are the usual JSON object.

| Command | What it does |
|---|---|
| `fab0-resolve start <#item \| run>` | What `/fab0:run` is asked to run, as given. `#<n>` starts a run from item `n` of the home repository: the run takes its id from the runs repository's [register](ledger.md#the-register), and the item gets a comment that says it. An item that has a run not yet done, by register or a run of 0.8 by its number, or that a call made, gives that run instead. Anything else is a run id, which `start` only checks. Prints `run`, `item`, `pipeline`, `started` (whether a run started now) and `line`. With `--session`, it counts one more pass of a session over the run, in the run's event log, and adds `pass` |
| `fab0-resolve validate` | Checks the project's `.fab0/` wiring, and that the run store can be reached (`git ls-remote`, with no credential prompt). A store it can't reach is invalid wiring, exit 3. Prints the pipelines, steps, artifacts, the store (`runs`, the runs repository or its local path; `project`; `path`, its checkout) and the workspace: each repository's local path and whether it is there. With `factories`, it also reads each connected factory's wiring at its base branch, checks the connection, and lists it under `factories` with `checked`, or `why` it couldn't check and a warning |
| `fab0-resolve status <run>` | Pulls the run store, then gives every unit of the run and its state, its `position`, one line that says where the run is (`run 12 · story · acme/shop#52 · pass 3 · at implement 1/2 (running)`), and each unit's total duration (`duration` in seconds, and `took`, such as `8m 17s`): the sum over its recorded attempts and gate decisions. A unit that has none recorded, or an entry without times, has no duration. With `--tree`, it adds `tree`: the run's position and, for each call, the child run it started, with its `factory`, `item`, `run`, `kind` and `position`, evaluated from the connected factory's checkout, or `why` it can't be. Read-only |
| `fab0-resolve next <run> [--apply]` | The same, and a hand-out for every unit that is ready or running and every auto gate that is due. Claims each attempt it hands out with a claim fact in the run store, pushed before the hand-out, and creates the unit's branch at its parent's head, with no commit. An attempt another machine claimed isn't handed out: the unit is `running`, with `claimed: elsewhere`. A unit with store outputs gets an `outbox`, the folder to write them in. A call waiting for an agent's acknowledgement gets a hand-out with `ack`, the exports it answers, and no branch. Each hand-out but an action's carries `line`, its start line, and records when it was handed out. With `--apply` it first performs what is due, as `apply` does, then hands out from the last read of the tracker `apply` made: see [`next --apply`](#next---apply) |
| `fab0-resolve record <run> <unit>` | Checks a handed-out unit's result, its outputs and its writes, then commits the unit's work on its branch and pushes the branch once it has commits. It puts the outbox's files into the run store, writes the ledger entry there and pushes the store. A refused record commits nothing. A push that fails is said, not fatal: `unpushed` for the store, `unpushed_branches` for the branch; `apply` pushes both later. The result carries `started`, `ended`, `duration` and `took`, and `line`, the end line. It reads the run's item from the tracker only when it must pick the pipeline: the unit and its context come from git, the run store and its saved hand-out, not from the tracker. The one exception is a unit that sits behind a `when` only the tracker can decide: it isn't in the run without the tracker, so `record` then reads the tracker as `status` does. In a run that a call started, it also checks each output the caller takes against the format the call accepts, from the run's own `bound@parent` fact. `record --gate` records an agent's acknowledgement of what a child handed back as `ack@*` facts |
| `fab0-resolve apply <run>` | Performs what is due: actions, merges, pull requests, comments, signals. For a unit reviewed in the runs repository, it puts the latest outputs on its review branch, opens its review pull request, and records a person's edit on that branch as their attempt. Once the gate's owner approves the latest version, with a review or, on a pull request they opened, a comment `/approve`, it records the approval as the attempt's gate decision, then merges the review pull request at the commit approved. Nobody merges there by hand. A unit with no pull request gets its questions or escalation on the run's item. It also pushes what a record couldn't. It starts a call's child run and binds a called run to its call, hands back each output a caller takes once its unit is done, and opens the review pull request in which a person acknowledges what a child handed back, by an approving review that `apply` records and merges. Writes to git, the run store and the tracker. The result carries `follow`, the command that follows the run with `log --follow` |
| `fab0-resolve inbox` | Every open run of the project, and what it needs from whom. It finds runs in the run store, in run branches with unmerged work, and in tracker items that match a trigger. Each run carries its `position`, its `item`, its `command`, and its `rank`, what a session here would do in it now: `interrupted`, `agent` or `actions`. An item no run has started carries `start`, and its command is `/fab0:run #<n>`. A child run carries `called`, the factory (`by`) and the `call` that started it. A unit another machine claimed waits on it, with no owner. A call waiting on its child run carries `child`, its item, `command`, the `/fab0:run` to run there with the run's own id, which the child run shares, and `in`, the connected factory's checkout. Each run that has events on this machine carries `latest`, the `time` and `line` of its last event. Read-only |
| `fab0-resolve pick` | The run a bare `/fab0:run` goes on with: `pick`, the only open run with a `rank`, else none. `runs` lists every run that has one, ranked: `interrupted` first, then `agent`, then `actions`. With none, `waiting` says what waits on whom, and `start` lists the items to start. It never picks an item no run has started. Read-only |
| `fab0-resolve log <run>` | Prints the run's [event log](#the-event-log): one line for each event, oldest first, its time (UTC) and its line. With `--follow`, keeps printing new events. Reads only the home checkout's git directory: no wiring, tracker or `gh`, and no version check. Read-only |
| `fab0-resolve --version` | The fab0 release of the engine |

### `next --apply`

`fab0-resolve next <run> --apply` is one command for a round: it runs `apply`, then hands out from the evaluation `apply` ended with, so `next`'s own read of the tracker is saved. When `apply` changes nothing, the round is one pass over the tracker; when `apply` changes something, such as a merge, it reads the tracker again to see the effect, and the hand-outs come from that last read. Like every command, it reads the tracker's current state when it starts; nothing is kept between commands.

Its result holds what `apply` gives (`applied`, with what it did, `kind`, and `follow`, the command that follows the run with `log --follow`) and what `next` gives (`handouts` and `units`). The `handouts` and `units` are those `next` would give if it ran right after `apply`.

- **`--unit UNIT`** limits the hand-outs only. `apply` performs what is due for every unit, that unit's or not. When the unit isn't ready, the command exits with 4, and its result still lists `applied`.
- **A run that is finished.** When the run's `kind` is `done`, or `waiting` for the merge of its pull request, nothing is handed out.
- **When `apply` fails**, for example on a merge conflict with the base, the command exits with `apply`'s code and error, and hands out and claims nothing.

`next` and `apply` without `--apply` behave as before, so they can still be run one after the other.

### Options

| Option | Commands | Meaning |
|---|---|---|
| `--project DIR` | all | The home repo. Default: found from the current directory; from inside a worktree, its main checkout |
| `--profile NAME` | all but `log` | A profile from `fab0.yaml` to apply |
| `--pipeline NAME` | `start`, `status`, `next`, `record`, `apply` | The pipeline. Default: the one the run's register fact names, else the project's only pipeline, else the one whose trigger the run matches |
| `--as USER` | all but `validate` and `log` | Who is running. Default: the tracker login |
| `--apply` | `next` | Perform what is due first, as `apply` does, then hand out |
| `--unit UNIT` | `next`, `apply` | Only this unit. With `next --apply` it limits the hand-outs only: `apply` still performs what is due for every unit |
| `--return FILE` | `record` | The agent's or tool's JSON reply |
| `--exit CODE` | `record` | A command's exit code |
| `--gate` | `record` | Record the unit's auto gate: its verdict, or `--exit` for a command gate |
| `--output FILE` | `record` | A command gate's output, kept as the finding when it fails |
| `--session` | `start` | Count a session taking the run up: one more `pass` event in the run's event log |
| `--tree` | `status` | Also where each child run of the run's calls is |
| `--follow` | `log` | After the events already logged, keep printing each new one, checking about once a second, until interrupted. Ctrl-C ends it with exit 0 |

### The event log

`next`, `record`, `apply` and `start --session` append each event of a run to `fab0/events/<run>.jsonl` in the home repo's git common directory: one JSON object per line, with `time` (UTC, to the second), `kind` (`handout`, `record`, `gate`, `apply`, `waiting`, `blocked`, or `pass` for a session taking the run up), `line`, and when they apply `unit`, `attempt`, `reason` and `pass`, the pass's number. The log is local to the machine, and never committed, pushed or written to the tracker. `validate`, `status`, `inbox` and `log` never write it. A write that fails never changes a command's result or exit code: the result carries a warning that the event couldn't be logged, and why. See [following a run from outside its session](../explanation/execution.md#following-a-run-from-outside-its-session).

`log` prints one line for each event, and follows the run from any terminal with `--follow`:

```text
$ fab0-resolve log 54 --follow
2026-10-16T10:04:12Z  spec, attempt 1: implementer on opus, branch fab0/54/spec
2026-10-16T10:12:40Z  spec, attempt 1: verified, 8m 28s
2026-10-16T10:12:41Z  waiting: spec (gate human)
```

A run with no events on this machine prints `run 77 has no events here yet`, and exits 0. A line that isn't a valid event prints as `event N can't be read`. With a run id that has characters other than letters, digits, `.`, `_` and `-`, or with no `.fab0/fab0.yaml` in the current directory or above it and no `--project`, `log` prints the usual `"ok": false` object and exits 2.

### Older engine

Every command that reads the project (`validate`, `status`, `next`, `record`, `apply`, `inbox`; not `log`) first compares the engine's release with the plugin release Claude Code has installed for the project, read from the install record under `CLAUDE_CONFIG_DIR`. A local record for the project takes precedence over a project one, and a project one over a user one.

When the engine is older, the command exits 1 and writes nothing: no claim, ledger entry, git, run store or tracker change. It prints `"ok": false`, an `error` naming both releases and their paths, and a `fix` list: each orphaned cached version directory to remove, then to start a new Claude Code session. `/fab0:run` and `/fab0:inbox` show the `error` and every `fix` line, and stop. See [update the plugin](../how-to/use-an-example.md#update-the-plugin).

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
