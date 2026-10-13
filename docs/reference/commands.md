# Commands reference

fab0 has two commands for people, both skills of the core plugin, and one script that they call.

## `/fab0:run <run> [--task T] [--take] [--profile P]`

Runs a pipeline for one item until it needs a person, is done, or is blocked. You type it in a Claude Code session, or pass it to `claude -p`. A model never invokes it on its own.

| Argument | Meaning |
|---|---|
| `<run>` | The run id: the item's issue number in the home repo |
| `--task T` | Work only on task `T`, for example `T2` |
| `--take` | Claim task `T` if someone else is assigned. It reassigns the task issue to you first |
| `--profile P` | Apply profile `P` from `fab0.yaml` |

Without `--task`, it works through the tasks you may run, one after another.

**What it does on GitHub:**

- pushes stage branches;
- opens and updates stage pull requests;
- posts question and handoff comments;
- creates and edits task sub-issues;
- updates the board fields.

**What it never does:** merge, push to the base branch, or force-push.

**At the end it reports:**

- each stage, task, attempt and model, and whether the attempt was verified;
- what it opened or updated on GitHub;
- what the run waits for, and on whom.

Commits on a stage branch have the subject `<stage>[ <task>] attempt <n> (fab0 <version>): <summary>`, so a pull request's commits show which release ran each attempt.

## `/fab0:inbox [--as USER]`

Read-only. For every open item of every pipeline in the project it shows:

- **Ready for you:** the exact `/fab0:run` command for each stage or task you may run.
- **Pending actions:** actions anyone may run.
- **Waiting on others,** with the reason.
- **Blocked,** with the reason.
- **Done, issue still open.**

It never runs what it suggests. `--as` shows another user's view.

## `fab0-resolve`

The resolver, on the `PATH` through the plugin's `bin/`. Each command prints one JSON object. You normally call only `validate`; the skills call the rest.

| Command | Does |
|---|---|
| `fab0-resolve --version` | Prints the fab0 release |
| `fab0-resolve validate [--profile P]` | Checks `.fab0/`. Prints `"ok": true`, or the errors by file |
| `fab0-resolve next <run> [--task T] [--profile P] [--as USER]` | What the run needs next: `stage`, `gate`, `action`, `tasks`, `wait`, `done` or `blocked`, with the brief, model and branch for an agent call |
| `fab0-resolve record <run> <stage> [--task T] [--gate] --return <file>` | Records the result of what `next` handed out. Validates the return, verifies outputs, checks write scope, writes the ledger entry |
| `fab0-resolve inbox [--as USER] [--profile P]` | The data behind `/fab0:inbox` |

Every command takes `--project <path>` to name the home repo. By default the home repo is found from the current directory.

| Exit code | Meaning |
|---|---|
| 0 | OK |
| 1 | Error |
| 2 | Usage |
| 3 | Invalid wiring |
| 4 | Refused, for example a write outside the stage's scope |

`FAB0_GH_FAKE=<file.json>` makes the resolver read GitHub facts from a file instead of `gh`. The tests use it.
