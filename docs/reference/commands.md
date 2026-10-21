# Commands

The `fab0` plugin adds the engine, `fab0-resolve`, to the Bash `PATH` of every Claude Code session, and two slash commands. It needs [`uv`](https://docs.astral.sh/uv/), and an authenticated [`gh`](https://cli.github.com/).

## Slash commands

| Command | What it does |
|---|---|
| `/fab0:run [#<item> \| <run>] [--pipeline P] [--profile P] [--unit U]` | Runs the pipeline for one run until it needs a person, is blocked or is done: `next --apply`, the hand-outs, `record`, the confirmations at the prompt, and again. `#<item>` starts a run from an item of the home repository, or goes on with the run it has; `<run>` names a run by its id; with neither, it goes on with the only run that has work here, and asks which when several have (`pick`). It first runs `start '<argument>' --session`, which counts the session as one more pass over the run, and it ends with the run's position. It shows the start and end lines, the agents' activity, what `apply` did and each unit's duration as it goes, and, once at the start of the first round, the `log --follow` command that follows the run from another terminal. A unit whose gate is `human` with `via: prompt` is put to the person in the session, and their answer goes to `confirm`. See [running a pipeline](../explanation/execution.md) |
| `/fab0:inbox [--as USER]` | Shows every open run, where it is, what waits on you, what anyone can run, and what is blocked, and beside each run its latest event, when it has one on this machine. An item no run has started shows with `/fab0:run #<n>`. Read-only |

The plugin also has a `fab0:github` skill, which checks and prepares GitHub for a factory, the run tracker's issue types and fields among it. See [set up GitHub](../how-to/github-setup.md).

## `fab0-resolve`

Every command prints one JSON object, except `log`, which prints text when it succeeds. Its errors are the usual JSON object. Every command but `log` and `--version` reads the [run tracker](tracker.md) again when it starts, and keeps nothing between commands.

| Command | What it does |
|---|---|
| `fab0-resolve validate` | Checks the project's `.fab0/` wiring, schema 3. A `fab0.yaml` with `schema: 2` is refused, with a pointer to the [upgrade notes](../how-to/upgrade-from-0.9.md). It checks the run tracker's issue types, fields and Stage values (see [run tracker](tracker.md#configuration)), and with `factories`, reads each connected factory's wiring at its base branch and checks the connection. Prints the `pipelines`, `steps`, `artifacts`, the `factory` name, `tracking` (its repository and issue types), the `workspace` (each repository's local `path`, and whether it is `present`) and, with `factories`, each one with `checked`, or `why` it couldn't be checked and a warning. A tracker it can't read here is a warning, not an error |
| `fab0-resolve start <#item \| run>` | What `/fab0:run` is asked to run, as given. `#<n>` finds the open Pipeline Run of item `n` of the home repository, or opens one under the item: the run's id is that issue's number. Two starts at once open one run: the first one opened stands. A closed item is refused (exit 4), and an item whose pipeline starts by hand is a usage error. Anything else is a run id, which `start` only checks. Prints `run`, `item`, `pipeline`, `started` (whether a run started now), `tracker` (the Pipeline Run, for `#<n>`) and `line`. With `--session`, it counts one more pass of a session over the run, in the run's event log, and adds `pass` |
| `fab0-resolve status <run>` | Every unit of the run and its state, its `position`, one line that says where the run is (`run 57 · story · acme/product#412 · pass 3 · at implement 1/2 (running)`), and each unit's total duration (`duration` in seconds, and `took`, such as `8m 17s`): the sum over its recorded attempts and gate decisions. A unit with none recorded, or with entries without times, has no duration. With `--tree`, it adds `tree`: the run's position and, for each call, the child run it started, with its `factory`, `pipeline`, `item` (its Pipeline Run), `run`, `call`, `kind` and `position`, evaluated from the connected factory's checkout, or `why` it can't be. Read-only |
| `fab0-resolve next <run> [--apply]` | The same, and a hand-out for every unit that is ready or running, every auto gate that is due, and every call whose child run is done and whose `auto` gate is due. Before each hand-out it claims the attempt: it assigns the unit's Pipeline Step to the session's login, sets it `In Progress` and writes the claim on it (see [claims](tracker.md#claim)), then creates the unit's branch at its parent's head, with no commit. An attempt another login or machine claimed isn't handed out: the unit is `running`, with `claimed: elsewhere`. Each hand-out but an action's carries `line`, its start line, and records when it was handed out. With `--apply` it first performs what is due, as `apply` does, then hands out from the last read of the tracker `apply` made: see [`next --apply`](#next---apply) |
| `fab0-resolve record <run> <unit>` | Checks a handed-out unit's result, its outputs and its writes, then commits the unit's work on its branch and pushes the branch once it has commits. It writes the attempt on the unit's Pipeline Step and sets its Revision and Output. A refused record commits nothing, and an attempt recorded already is refused. A push that fails is said, not fatal: `unpushed_branches`, which `apply` pushes later. The result carries `entry` (the Pipeline Step), `verified`, `failed`, `recorded` (the attempt), `started`, `ended`, `duration` and `took`, `line` (the end line), and `outside`, files that appeared beside the repositories while the unit ran. In a run that a call started, it also checks each output the caller takes against the format the call accepts, from the run's `call` block. `record --gate` records the unit's auto gate, or a call's gate on what its child run handed back |
| `fab0-resolve apply <run>` | Performs what is due: actions, merges, pull requests, comments, signals. It merges a unit's branch into its parent where the unit's gate and definition of done let `apply` merge; under an auto gate, once its pull request's required checks pass. It opens a pull request for a unit a person looks at, and sets the step's Output to it. A unit with no pull request gets its questions or escalation on the run's item. It starts a call's child run, sends a call's rejection to its child run, and records a person's acceptance of a call's result on its Pipeline Step. It closes the Pipeline Step of each unit that is done, and the Pipeline Run once the run is (`tracked`). Writes to git, the item tracker and the run tracker. The result carries `applied`, what it did, and `follow`, the command that follows the run with `log --follow` |
| `fab0-resolve confirm <run> <unit>` | A person's decision in the run session, for a unit whose gate is `human` with `via: prompt`: it approves the unit, or for a call, what its child run handed back. With `--reject TEXT` it asks for changes in those words, and the unit reworks with them. It writes the decision as the attempt's gate decision on the unit's Pipeline Step, and `apply` then merges what it approved. Refused (exit 4) when the unit isn't waiting for a confirmation, when the login doesn't own the gate, or when the attempt is decided already. An unknown unit is a usage error. Prints `unit`, `attempt`, `decision` and `line` |
| `fab0-resolve inbox` | Every open run of the factory, and what it needs from whom. It finds runs among the factory's open Pipeline Runs, a child run among them, in run branches with unmerged work, and in item tracker items that match a trigger. Each run carries its `position`, its `item`, its `command`, and its `rank`, what a session here would do in it now: `interrupted`, `agent` or `actions`. An item no run has started carries `start`, and its command is `/fab0:run #<n>`. A child run carries `called`, the factory (`by`) and the `call` that started it. A unit another login or machine claimed waits on it, with no owner. A call waiting on its child run carries `child`, the child's Pipeline Run, `command`, the `/fab0:run` to run there with the run's own id, which the child run shares, and `in`, the connected factory's checkout. Each run that has events on this machine carries `latest`, the `time` and `line` of its last event. Runs that belong to no pipeline are listed under `skipped`, with why. Read-only |
| `fab0-resolve pick` | The run a bare `/fab0:run` goes on with: `pick`, the only open run with a `rank`, else none. `runs` lists every run that has one, ranked: `interrupted` first, then `agent`, then `actions`. With none, `waiting` says what waits on whom, and `start` lists the items to start. It never picks an item no run has started. Read-only |
| `fab0-resolve log <run>` | Prints the run's [event log](#the-event-log): one line for each event, oldest first, its time (UTC) and its line. With `--follow`, keeps printing new events. Reads only the home checkout's git directory: no wiring, tracker or `gh`, and no version check. Read-only |
| `fab0-resolve --version` | The fab0 release of the engine |

`tick` is gone since 0.9.1: a person continues a run with `/fab0:run`.

### `next --apply`

`fab0-resolve next <run> --apply` is one command for a round: it runs `apply`, then hands out from the evaluation `apply` ended with, so `next`'s own read of the tracker is saved. When `apply` changes nothing, the round is one pass over the tracker; when `apply` changes something, such as a merge, it reads the tracker again to see the effect, and the hand-outs come from that last read.

Its result holds what `apply` gives (`applied`, `tracked`, `kind`, and `follow`) and what `next` gives (`handouts` and `units`). The `handouts` and `units` are those `next` would give if it ran right after `apply`.

- **`--unit UNIT`** limits the hand-outs only. `apply` performs what is due for every unit, that unit's or not. When the unit isn't ready, the command exits with 4, and its result still lists `applied`.
- **A run that is finished.** When the run's `kind` is `done`, or `waiting` for the merge of its pull request, nothing is handed out.
- **When `apply` fails**, for example on a merge conflict with the base, the command exits with `apply`'s code and error, and hands out and claims nothing.

`next` and `apply` without `--apply` behave as before, so they can still be run one after the other.

### Options

| Option | Commands | Meaning |
|---|---|---|
| `--project DIR` | all | The home repo. Default: found from the current directory; from inside a worktree, its main checkout |
| `--profile NAME` | all but `log` | A profile from `fab0.yaml` to apply |
| `--pipeline NAME` | `start`, `status`, `next`, `record`, `apply`, `confirm` | The pipeline. Default: the one the run's Pipeline Run names, else the project's only pipeline, else the one whose trigger the run matches. A pipeline other than the one the Pipeline Run names is a usage error |
| `--as USER` | all but `validate` and `log` | Who is running. Default: the tracker login, else `git config user.name` |
| `--apply` | `next` | Perform what is due first, as `apply` does, then hand out |
| `--unit UNIT` | `next`, `apply` | Only this unit. With `next --apply` it limits the hand-outs only: `apply` still performs what is due for every unit |
| `--return FILE` | `record` | The agent's or tool's JSON reply |
| `--exit CODE` | `record` | A command's exit code |
| `--gate` | `record` | Record the unit's auto gate, or a call's gate: its verdict, or `--exit` for a command gate |
| `--output FILE` | `record` | A command gate's output, kept as the finding when it fails |
| `--reject TEXT` | `confirm` | Ask for changes, in these words, instead of approving |
| `--session` | `start` | Count a session taking the run up: one more `pass` event in the run's event log |
| `--tree` | `status` | Also where each child run of the run's calls is |
| `--follow` | `log` | After the events already logged, keep printing each new one, checking about once a second, until interrupted. Ctrl-C ends it with exit 0 |

### The event log

`next`, `record`, `apply` and `start --session` append each event of a run to `fab0/events/<run>.jsonl` in the home repo's git common directory: one JSON object per line, with `time` (UTC, to the second), `kind` (`handout`, `record`, `gate`, `apply`, `waiting`, `blocked`, or `pass` for a session taking the run up), `line`, and when they apply `unit`, `attempt`, `reason` and `pass`, the pass's number. The schema is `plugins/fab0/schemas/event.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core).

The log is local to the machine, and never committed, pushed or written to the run tracker: the tracker holds the run's state and facts, and the log only what this machine's commands did, for following a run as it goes. `validate`, `status`, `inbox`, `pick`, `confirm` and `log` never write it. A write that fails never changes a command's result or exit code: the result carries a warning that the event couldn't be logged, and why. See [following a run from outside its session](../explanation/execution.md#following-a-run-from-outside-its-session).

`log` prints one line for each event, and follows the run from any terminal with `--follow`:

```text
$ fab0-resolve log 57 --follow
2026-10-16T10:04:12Z  spec, attempt 1: spec-author on opus, branch fab0/57/spec
2026-10-16T10:12:40Z  spec, attempt 1: verified, 8m 28s
2026-10-16T10:12:41Z  waiting: spec (gate human)
```

A run with no events on this machine prints `run 77 has no events here yet`, and exits 0. A line that isn't a valid event prints as `event N can't be read`. With a run id that has characters other than letters, digits, `.`, `_` and `-`, or with no `.fab0/fab0.yaml` in the current directory or above it and no `--project`, `log` prints the usual `"ok": false` object and exits 2.

### Older engine

Every command that reads the project (`validate`, `start`, `status`, `next`, `record`, `apply`, `confirm`, `inbox`, `pick`; not `log`) first compares the engine's release with the plugin release Claude Code has installed for the project, read from the install record under `CLAUDE_CONFIG_DIR`. A local record for the project takes precedence over a project one, and a project one over a user one.

When the engine is older, the command exits 1 and writes nothing: no claim, fact, git or tracker change. It prints `"ok": false`, an `error` naming both releases and their paths, and a `fix` list: each orphaned cached version directory to remove, then to start a new Claude Code session. `/fab0:run` and `/fab0:inbox` show the `error` and every `fix` line, and stop. See [update the plugin](../how-to/use-an-example.md#update-the-plugin).

An engine of the same or a newer release runs as before. With no install record for the project, it also runs as before. With an unreadable record or release, the commands run and add a warning that the release couldn't be checked. `fab0-resolve --version` is never refused.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Done |
| 1 | An error, for example a failing `git` or `gh` call, or an engine older than the installed plugin |
| 2 | A usage error, for example an unknown pipeline, unit or item, or a malformed run id |
| 3 | The wiring is invalid; `errors` lists each problem with its file. A run tracker that lacks a type, field or Stage value, and a project without `tracking` that starts or writes a run, are invalid wiring |
| 4 | Refused, for example a reply that doesn't match its schema, a unit that wasn't handed out or isn't ready, a fact written already, a closed item, or a confirmation by someone who doesn't own the gate |

### Environment

| Variable | Meaning |
|---|---|
| `CLAUDE_CONFIG_DIR` | Claude Code's configuration directory. The engine reads the plugin install record, `plugins/installed_plugins.json`, and the plugin cache under it. Default: `~/.claude` |
| `FAB0_GH_FAKE` | A JSON file to read and write the item tracker and the run tracker in, instead of GitHub. For tests |
