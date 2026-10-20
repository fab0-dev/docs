# Running a pipeline

fab0 runs inside Claude Code. The work is split between a deterministic engine and the session that carries out what it hands out. This page explains the split, and the loop that `/fab0:run` follows. The [commands reference](../reference/commands.md) lists every command and option.

## The engine and the session

**The engine**, `fab0-resolve`, is a program in the `fab0` plugin. It decides; it never improvises:

- it reads `.fab0/`, git, the run store and the tracker, and works out every unit's state;
- it hands out what is due, with a brief for each agent;
- it checks what comes back, commits the unit's work, and records the attempt in the run store;
- it performs every write that can be done exactly: actions, merges, pull requests, comments, relations.

**The session** runs `/fab0:run`. It executes; it never decides:

- it prepares the branches and worktrees a hand-out names;
- it runs each agent as a subagent with its brief, runs commands, and calls tools;
- it passes the replies back to the engine. It never commits or pushes: `record` does.

The model doesn't route, because a deterministic program is repeatable, and can be tested and reviewed. The engine doesn't call models or tools, because the session already can.

## The run store

What a run produces for itself, its ledger and its `store` artifacts, lives in the **run store**: a runs repository beside the product's repositories, named in `store.github`. The product repositories receive only product changes. The engine keeps its own clone of the runs repository, in the home repo's git directory unless `store.path` names one. `status`, `next`, `apply` and `inbox` pull it first, so what another machine recorded counts. Offline, they read the local copy and say so in a warning. See [artifacts and the ledger](artifacts-and-ledger.md).

## The loop

`/fab0:run` first finds its run. `#<item>` starts a run from an item, or goes on with the one it has; a run id names a run; with neither, `fab0-resolve pick` names the only run that has work here, and the session asks which when several have. Then `fab0-resolve start` checks what it was given, and counts the session as one more pass over the run. See [run ids](pipelines.md#run-ids).

It then repeats these steps until nothing more is handed out:

1. **`next --apply`** first performs what is due, as `apply` does: every action whose check fails, every merge a gate allows, every pull request a person or a gate needs, and every question or escalation to post. Each write checks first, so running it twice changes nothing. Then it hands out every unit that is ready, and every auto gate that is due, from the same read of the tracker. Before it hands out an attempt, it claims it: it writes a claim fact to the run store and pushes it, and creates the unit's branch from its parent's head, with no commit. The hand-outs reuse the last read of the tracker that `apply` made, so `next` doesn't read it again. When `apply` changes nothing, the whole round is one pass over the tracker; when it changes something, such as a merge, `apply` reads the tracker afresh to see the effect, and the hand-outs come from that last read. `--unit` limits the hand-outs only.
2. **The session** prepares the checkouts of every hand-out of the round in one turn. In the next it runs the agents of the round in parallel, each in its own worktree, runs commands in their worktree, and calls tools.
3. **The session records.** For each hand-out, in one Bash call, it writes the reply and runs `record` (a gate's verdict is recorded the same way). The round's calls go in one message, so one refusal doesn't stop the others.

`record` does, in order:

1. it checks the reply against its schema, and each output against its format, schema and checks. An output of kind `store` is read from the unit's outbox;
2. it checks that the unit wrote only inside its claims, and nothing in a repository it may not write;
3. it commits the unit's changes in each worktree it wrote;
4. it puts each `store` output into the run store, appends the attempt to the ledger with `heads`, the commit each repository's branch is at, and pushes the run store;
5. it pushes the unit's branch once it has commits. A branch with no work stays on the machine.

A refused record commits nothing. A push that fails is said in the result, not fatal: the next `apply` pushes the run store, and pushes a unit's branch before it merges it or opens its pull request.

A round of three agents is four turns: `next --apply`, the checkouts, the agents, and the records. The session still shows what `apply` did, and a start line and an end line for each hand-out.

Then it reports what ran and how long each unit took, what `apply` did, and what the run is waiting for, and on whom.

`apply` and `next` still work on their own, so a session or a person can run them one after the other: `next --apply` is the same work without `next`'s own read of the tracker.

Besides actions and merges, `apply`:

- opens a unit's pull request when a person must look at it. A unit whose outputs are all in the run store gets a review pull request in the runs repository instead, and `apply` puts each new attempt's outputs on its branch. Once the gate's owner approves it, `apply` records the approval and merges it. See [gates](gates.md);
- records a person's edit of those outputs on the review branch as an attempt by that person;
- posts questions and escalations once: on the unit's pull request, or on the run's item when the unit has none, because its attempt changed nothing;
- opens a repository's run pull request once its run branch has work, if `onStart` has `pr.open-run`;
- pushes what a record couldn't push to the run store.

A run's state is `units` while work is left, `waiting` when only the merge of its pull request into the base branch is left, and `done` when that pull request is merged.

## What you see during a run

A run can take twenty minutes, so the session shows its progress as it goes. The engine writes the lines and works out the times; the session shows the lines exactly as they are.

- **A start line for each hand-out.** After `next --apply`, and before any agent starts, the session shows one line for each hand-out of the round: the unit, its attempt, the agent (or the command, or the tool's name), the model and the branch. For example: `implement-T2, attempt 2: implementer on opus, branch fab0/53/implement-T2`. A gate's line says it is the gate of the unit it judges. A command's line gives the command, and a tool's line gives the tool's name. An action gets no line: `apply` performs it.
- **The agents' activity.** The agents of a round start together, in the foreground, and Claude Code shows what each one does while it works, such as the tool calls it makes. Nothing is serialized to make this visible: the agents still run in parallel.
- **An end line for each record.** When a unit or a gate is recorded, the session shows its outcome and how long it took, from the hand-out to the record, checkout time included. For example: `implement-T2, attempt 2: verified, 4m 12s`. A unit that fails its checks reads `not verified`, with the names of the failed checks. A command adds its exit code, and a unit with questions says how many. A gate's line names the gate, as its start line does, and gives its decision (`approved`, `rejected` or `escalated`), as in `gate of implement-T2, attempt 1: rejected, 1m 5s`. For a command gate it gives the decision and the exit code. A unit or gate handed out by an older engine, or recorded without a start, says the time is unknown.
- **What `apply` did.** At the top of each round the session shows a short list, one line for each thing `next --apply` did, which is what `apply` does: a merge, a pull request with its link, a review branch updated in the runs repository, a person's edit recorded as an attempt, a sync, a signal, a push of the run store. When `apply` did nothing, it says so in one line.
- **The end report.** When the run stops, the report gives each unit's total duration: the sum over all its attempts and gate decisions. A unit that was never recorded, or whose ledger entries have no times, shows none.

The engine keeps the start and end of every attempt and every gate decision in the [ledger](../reference/ledger.md), in the run store, so `fab0-resolve status` gives each unit's duration at the end of the run or any time later. Times are UTC, to the second. A duration is never negative.

## Following a run from outside its session

Only the session that drives a run shows its progress. To see what a run has done, from another terminal or as the owner of an unattended run, read its **event log**.

The engine keeps one log for each run, with the time of each event. It holds:

- each hand-out, with the start line `next` returned (an action's hand-out adds none);
- each result `record` recorded, and each auto gate's decision, with the end line `record` returned;
- each thing `apply` did, one event for each entry of its `applied` list. A report `apply` repeats, such as a merge that waits for its pull request's required checks, is logged once;
- a unit starting to wait on a person (a human gate, questions, an escalation, or the run waiting for the merge of its own pull requests), and a unit becoming blocked by a signal, such as a tracker item outside the run. It is logged when the unit's state, reason or attempt changes, so a unit that keeps waiting adds no more events. A unit that only waits its turn adds none.

A person's decision on a human gate is not an event of its own: it shows as what follows it, `apply`'s merge or the reworked hand-out. Nor does the log hold what an agent does inside a unit. Only the engine's events are logged, and only what its lines and states already show: no brief, no returned data, no findings.

The log is a file on the machine that runs the engine: `fab0/events/<run>.jsonl` in the home repo's git directory (the common git directory, when the home repo has worktrees). Every checkout and process on the machine shares it. It is never committed, pushed or written to the tracker. It doesn't show a run that is driven on another machine: there, `fab0-resolve status`, the inbox and the tracker are the shared view, because they read the run store and the tracker that every machine writes. A run already under way when the log was added has events from its next command on.

`fab0-resolve log <run>` prints it, one line for each event, oldest first: its time (UTC, to the second) and its line.

```text
$ fab0-resolve log 54
2026-10-16T10:04:12Z  spec, attempt 1: implementer on opus, branch fab0/54/spec
2026-10-16T10:12:40Z  spec, attempt 1: verified, 8m 28s
2026-10-16T10:12:41Z  waiting: spec (gate human)
2026-10-16T10:31:07Z  apply: spec: merged into backend:fab0/54/base
```

With `--follow` it prints what is logged, then each new event within about two seconds of its being written, until you interrupt it with Ctrl-C, which ends it with exit 0. A run with no events yet is said so in one line; with `--follow` it then waits, and prints the events as the run starts. A line that can't be read is replaced by `event N can't be read`, and the others are printed.

`log` reads only the home checkout's git directory. It loads no wiring and calls neither `gh` nor the tracker, so it works with `gh` not authenticated and with `.fab0/` invalid, in any terminal with `uv`. Run it from the home checkout, or give `--project <home>` from anywhere.

You don't have to type the command: `/fab0:run` shows it once, at the start of the run's first round, to paste into another terminal. It gives the engine's absolute path, `log <run> --follow`, and `--project` with the home checkout's path. And `/fab0:inbox` shows each open run's latest event, its time and line, beside the run. A run with no events on this machine shows none.

## Hand-outs and briefs

A hand-out tells the session everything it needs for one unit: the branches to create and the worktree to work in, what the unit may change, its executor, and the JSON schema its reply must match. A unit with `store` outputs also gets an **outbox**: a folder under the home repo's git directory, outside every checkout, where its agent writes them.

An agent's hand-out carries a **brief**: the whole assignment, in plain text. It holds:

- the unit's inputs, inline;
- a rework section with the reasons, when it isn't the first attempt. A `store` output has no branch to build on, so the rework brief shows its latest version;
- where to write each output: a path in its worktree, or a file in its outbox;
- what it may change and read;
- the skills to load;
- the reply's schema.

So any Claude Code agent can be a step. It needs no knowledge of fab0, only of its craft.

A gate's brief adds the producer's summary and the command that shows the change, and asks for a verdict.

## Worktrees

Each unit works in its own git worktree, under the repository's git directory, so parallel units never share a checkout. A unit whose branch is already checked out somewhere uses that checkout. `/fab0:run` removes the worktrees of finished units. It never removes a checkout a person made.

The home checkout's `.fab0/` governs the run, even when the engine is called from inside a worktree. Keep the home checkout on the base branch while a run goes on: the engine warns when it isn't, and `/fab0:run` stops to ask.

## The inbox

`/fab0:inbox` shows every open run of the project, where it is, and what it needs. It finds runs from their traces: runs in the run store, run branches not yet in the base, and open items that match a trigger. An item no run has started yet shows as one to start, with `/fab0:run #<n>`; starting is a person's choice, so a bare `/fab0:run` never takes one. It sorts the runs' units into:

- what waits on your roles;
- what anyone can run now;
- what waits on others, including units another machine claimed and is running;
- what is blocked by a signal.

The run store keeps every run, so the inbox evaluates finished runs too, and leaves them out of what it shows.

A call waiting on its child run shows the child run's item, the `/fab0:run` to run, and the connected factory's checkout to run it in: the inbox there lists that run.

Beside each open run it shows the run's latest event from the [event log](#following-a-run-from-outside-its-session), when the run has one on this machine. It changes nothing.

## Who may run what

A session runs one run of its own factory. A call's child run belongs to the connected factory, whose people run it from their own checkout, with its own wiring, agents and gates, so `/fab0:run` never runs it, even when that checkout is beside its own.

Anyone with the project checked out may run any unit: claims keep two machines from running the same one. A claim is a fact in the run store, written once and pushed before the hand-out, so the first machine to push it takes the attempt. Another machine sees the unit as `running`, with the reason `claimed: elsewhere`, and doesn't hand it out. Each attempt is claimed, a rework included. The tracker login is the actor recorded in the ledger, and each person pushes to the run store with their own credentials. A human gate's `owner` says whose turn the decision is, and the inbox shows it to them.
