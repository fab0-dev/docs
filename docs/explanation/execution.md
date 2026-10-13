# How a run executes

Two parts run a pipeline: the **orchestrator**, a skill running in a Claude Code session, and the **resolver**, a script that decides. The orchestrator never chooses what to do next (P2).

## The orchestrator

The orchestrator is the `/fab0:run <run>` skill of the core plugin. Its procedure is fixed:

1. Run `fab0-resolve validate`, and stop if the wiring is invalid. Fetch every repository in the workspace.
2. Run `fab0-resolve next <run>`. It prints one JSON object: a stage to run, an agent gate to run, an action to apply, the runnable tasks, `wait`, `done` or `blocked`.
3. For an agent stage or gate, call that agent through the Agent tool with the brief and the model from the result, verbatim. For an action, apply its operations with the core `fab0:github` skill.
4. After an agent call, run `fab0-resolve record <run> <stage> --return <file>`. The resolver validates the agent's JSON, hashes and verifies the outputs, checks the write scope and writes the ledger entry.
5. Commit the ledger entry and the artifacts on the stage branch, and update the board.
6. Repeat until `wait`, `done` or `blocked`. At a human gate, push the branch, open or update its pull request and post a handoff comment on the item.

An interactive run is the skill typed in a session, where the person can watch and answer questions. A headless run is the same skill under `claude -p`:

```bash
claude -p "/fab0:run 412" --permission-mode dontAsk --max-budget-usd 5 --output-format json
```

Both run on the person's own machine. Full options are in the [commands reference](../reference/commands.md).

## The resolver

The resolver is one script, `fab0-resolve`, in the core plugin's `bin/` directory, so it is on the `PATH` with no separate install. It is Python with inline dependencies, run through [`uv`](https://docs.astral.sh/uv/), so `uv` is its one prerequisite.

It:

- validates `.fab0/` before computing anything;
- computes the next step of a run;
- validates returns and artifacts, hashes outputs, runs verifiers, checks the write scope and writes ledger entries;
- reads ledgers from the base branch and from the branches of open stage pull requests in every repository, and reads merges, sub-issues and assignees from GitHub through `gh`;
- computes which tasks can run independently (lanes);
- answers `inbox`: for every open item of a pipeline's issue type, what `next` would give one person.

The resolver reads GitHub and never writes to it. It writes only ledger entries and its own pending hand-outs under the home repo's git directory.

### The brief

The resolver builds each agent's prompt, the brief, from what is on GitHub and in git. A text input of up to 64 KiB is put in the brief, so the agent needs no git to read it. A larger input, or a directory, is given as a `git show` (or `git ls-tree`) command at a pinned commit.

## The next-stage rule

Stages are evaluated in pipeline order. The first one that isn't satisfied is next.

- An **agent stage** is satisfied when its outputs exist, aren't stale, passed verification, and its gate passed:
  - with `gate: none`, a verified attempt is enough;
  - with an agent gate, the gate approved;
  - with `gate: human`, the attempt's ledger entry is on the base branch, which only a merged pull request can do.
- An **action stage** is satisfied when its check passes, meaning its result is already on GitHub. For `plan`, the Task sub-issues match `tasks.yaml`.
- An unsatisfied stage whose inputs are missing is `blocked`. One whose pull request is open and not merged is `wait`.

Consecutive agent stages work on one branch, named after the first of them, until a stage with `gate: human` ends the group. That stage's pull request carries all of their changes.

## Staleness

Staleness is based on hashes, as in `make`. An output is stale when the hash of any input it was built from has changed since. No revision counters or timestamps are needed.

A new attempt is also handed out when someone edited a stage's outputs, and when new requested-changes reviews arrived on its pull request. Reviews count as an implicit input.

## Headless and unattended runs

- **Built:** a headless run with `claude -p`.
- **Planned (step A.6):** reading the cost of each stage from Claude Code's OpenTelemetry metrics.
- **Not in scope while Claude Code on a person's machine is the only harness:** pending actions run by a GitHub Actions workflow on merge, or agent stages run by a hosted runner. A run is only artifacts and GitHub facts, so either could be added without changing this model.
