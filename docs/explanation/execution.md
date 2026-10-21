# Running a pipeline

fab0 runs inside Claude Code. The work is split between a deterministic engine and the session that carries out what it hands out. This page explains the split, and the loop that `/fab0:run` follows. The [commands reference](../reference/commands.md) lists every command and option, and [follow a run](../how-to/follow-a-run.md) shows where to watch one.

## The engine and the session

**The engine**, `fab0-resolve`, is a program in the `fab0` plugin. It decides; it never improvises:

- it reads `.fab0/`, git, the tracker and the run tracker, and works out every unit's state;
- it hands out what is due, with a brief for each agent;
- it checks what comes back, commits the unit's work, and writes the attempt on the unit's Pipeline Step;
- it performs every write that can be done exactly: actions, merges, pull requests, comments, relations, and the run tracker's issues and fields.

**The session** runs `/fab0:run`. It executes; it never decides:

- it prepares the branches and worktrees a hand-out names;
- it runs each agent as a subagent with its brief, runs commands, and calls tools;
- it asks a person to confirm where a gate waits at the prompt;
- it passes the replies back to the engine. It never commits, pushes or writes the run tracker: `record` and `apply` do.

The model doesn't route, because a deterministic program is repeatable, and can be tested and reviewed. The engine doesn't call models or tools, because the session already can.

## The run's state is on its issues

A run's state isn't kept in the session or on the machine. It is on the [run tracker](tracker.md): the run's Pipeline Run, a Pipeline Step for each unit, their fields, and the facts on their comments. The engine decides from those issues, the pipeline's definitions of done and its gates, and nothing else. It reads the tracker again on every command and keeps nothing between commands.

So a run can stop at any point and go on later, in another session or on another machine, and a person can see where it is without a session at all. Before 0.10 this state was a ledger in a run store that only the engine read; see [artifacts](artifacts.md#why-there-is-no-ledger) for why it went.

## The loop

`/fab0:run` first checks the wiring with `validate`, then finds its run:

- `#<item>` starts a run from that item: `start` opens the item's Pipeline Run in the runs repository, as a sub-issue of the item, and its number is the run id. When the item already has an open run, `start` finds it instead. A factory without `tracking` can't start a run from an item.
- A run id names a run.
- With neither, `fab0-resolve pick` names the only run that has work here, and the session asks which when several have. It never starts an item nobody named, because starting is a person's choice.

See [run ids](pipelines.md#run-ids). The session then repeats these steps until nothing more is handed out:

1. **`next --apply`** first performs what is due, as `apply` does (below). Each write checks first, so running it twice changes nothing. Then it hands out every unit that is ready, and every auto gate that is due, from the same read of the tracker. Before it hands out an attempt, it claims it: it assigns the unit's Pipeline Step to the session's login, sets it `In Progress`, and writes a claim fact that names this machine. `--unit` limits the hand-outs only.
2. **The session** prepares the checkouts of every hand-out of the round in one turn: each unit's branch, cut from its parent's head, and its worktree. In the next turn it runs the agents of the round in parallel, each in its own worktree, runs commands in their worktree, and calls tools.
3. **The session records.** For each hand-out, in one Bash call, it writes the reply and runs `record` (a gate's verdict is recorded the same way). The round's calls go in one message, so one refusal doesn't stop the others.
4. **The session asks.** For each unit waiting on a gate `human` with `via: prompt`, it shows what the unit produced and asks the person whether to accept it, then runs `fab0-resolve confirm <run> <unit>`, or `--reject` with what should change. Only the gate's owner may confirm. See [gates](gates.md#human-gates).

`record` does, in order:

1. it checks the reply against its schema, and each output against its format, schema and checks;
2. it checks that the unit wrote only inside its claims, and nothing in a repository it may not write;
3. it commits the unit's changes in each worktree it wrote;
4. it pushes the unit's branch once it has commits. A branch with no work stays on the machine;
5. it writes the attempt as a fact on the unit's Pipeline Step, with `heads`, the commit each repository's branch is at, and sets the step's Revision and its Output, the commit.

A refused record commits nothing. A push that fails is said in the result, not fatal: `apply` pushes a unit's branch before it merges it or opens its pull request.

A round of three agents is four turns: `next --apply`, the checkouts, the agents, and the records. When the loop stops, the session reports what ran and how long each unit took, what `apply` did, and what the run is waiting for, and on whom.

## What `apply` does

`apply` performs every write the state calls for, and nothing a model would have to judge:

- every action whose check fails: a lifecycle action, an action step, or the start of a call's child run;
- every merge a unit's gate and `done` leave to it. See [who merges](gates.md#who-merges);
- a pull request for each unit a person or a gate must look at, in whichever repository the unit writes, the runs repository too. It is a draft until the unit's gate approves, and it is the unit's Output while it is open;
- questions and escalations, posted once: on the unit's pull request, or on the run's item when the unit has none, because its attempt changed nothing;
- a repository's run pull request, once its run branch has work, if `onStart` has `pr.open-run`;
- for a call, a rejection sent to its child run, which opens that run again, and a person's acceptance on the call's Pipeline Step recorded as its gate decision;
- the Pipeline Step of each unit that is done, set `Done` and closed, with the commit it was accepted at as its Output, and the Pipeline Run, closed as completed with a summary once the run is done.

`apply` and `next` also work on their own, so a session or a person can run them one after the other: `next --apply` is the same work without `next`'s own read of the tracker.

A run's state is `units` while work is left, `waiting` when only the merge of its pull request into the base branch is left, and `done` when it is merged. A pipeline that ends with `pr.merge` never waits there: `apply` merges the run's pull requests once their required checks pass.

## What you see during a run

A run can take twenty minutes, so the session shows its progress as it goes. The engine writes the lines and works out the times; the session shows the lines exactly as they are.

- **A start line for each hand-out**, before any agent starts: the unit, its attempt, the agent (or the command, or the tool's name), the model and the branch. For example: `implement-T2, attempt 2: implementer on opus, branch fab0/53/implement-T2`. A gate's line says it is the gate of the unit it judges. An action gets no line: `apply` performs it.
- **The agents' activity.** The agents of a round start together, in the foreground, and Claude Code shows what each one does while it works. Nothing is serialized to make this visible.
- **An end line for each record**: the outcome and how long it took, from the hand-out to the record. For example: `implement-T2, attempt 2: verified, 4m 12s`, or `gate of implement-T2, attempt 1: rejected, 1m 5s`. A unit that fails its checks reads `not verified`, with the names of the failed checks.
- **What `apply` did**, at the top of each round: one line for each merge, pull request, action, rejection sent back or acceptance recorded. When it did nothing, it says so in one line.
- **The end report**, with each unit's total duration over all its attempts and gate decisions.

Each fact keeps the start and end of its attempt or gate decision, so `fab0-resolve status` gives each unit's duration at the end of the run or any time later. Times are UTC, to the second.

## Following a run from outside its session

Only the session that drives a run shows its lines. Anyone else follows the run on its issues: the Pipeline Run lists the run's steps as sub-issues, and each Pipeline Step shows its stage, who holds it, its Revision, its Output and a comment for each attempt. They are the shared view, written by every machine that works on the run. See [follow a run](../how-to/follow-a-run.md).

On the machine that drives a run, the engine also keeps an **event log**: each hand-out, record, thing `apply` did, and unit starting to wait on a person or becoming blocked by a signal, with its time. It is a file under the home repo's git directory, never committed or pushed, so it shows only this machine's work. `fab0-resolve log <run> --follow` prints it as it grows; `/fab0:run` shows that command once, at the start of the run's first round, to paste into another terminal, and `/fab0:inbox` shows each open run's latest event. The [commands reference](../reference/commands.md) describes the log.

## Hand-outs and briefs

A hand-out tells the session everything it needs for one unit: the branches to create and the worktree to work in, what the unit may change, its executor, and the JSON schema its reply must match.

An agent's hand-out carries a **brief**: the whole assignment, in plain text. It holds:

- the unit's inputs, inline;
- a rework section with the reasons, when it isn't the first attempt;
- where to write each output: a path in its worktree;
- what it may change and read;
- the skills to load;
- the reply's schema.

So any Claude Code agent can be a step. It needs no knowledge of fab0, only of its craft.

The brief is also a file, under the home checkout's git directory (`.git/fab0/briefs/`), and its last line is `<!-- end of brief -->`. The hand-out's `prompt` is one sentence that names the file, and the session passes it to the agent as it is. A brief can run to tens of kilobytes, and copying it into the agent's prompt costs the session minutes per hand-out. A copy cut off midway would leave the agent half its assignment; with the last line to check for, the agent can tell.

A gate's brief adds the producer's summary and the command that shows the change, and asks for a verdict. A call's gate gets what the child run handed back and what the call asked for.

## Worktrees

Each unit works in its own git worktree, under the repository's git directory, so parallel units never share a checkout. Factories that share a repository, such as the runs repository, keep their worktrees under their own names, since a child run has its parent's id. A unit whose branch is already checked out somewhere uses that checkout. `/fab0:run` removes the worktrees of finished units. It never removes a checkout a person made.

The home checkout's `.fab0/` governs the run, even when the engine is called from inside a worktree. Keep the home checkout on the base branch while a run goes on: the engine warns when it isn't, and `/fab0:run` stops to ask.

## The inbox

`/fab0:inbox` shows every open run of the factory, where it is, and what it needs. It finds runs among the factory's open Pipeline Runs, by their Factory field, in run branches not yet in the base, and in open items that match a trigger. An item no run has started yet shows as one to start, with `/fab0:run #<n>`. A child run shows with the factory and call that started it, and has no item of its own, only its Pipeline Run. The inbox sorts the runs' units into:

- what waits on your roles;
- what anyone can run now;
- what waits on others, including units another machine claimed and is running;
- what is blocked by a signal.

A call waiting on its child run shows the child's Pipeline Run, the `/fab0:run` to run, and the connected factory's checkout to run it in: the inbox there lists that run. The inbox changes nothing.

## Who may run what

A session runs one run of its own factory. A call's child run belongs to the connected factory, whose people run it from their own checkout, with its own wiring, agents and gates, so `/fab0:run` never runs it, even when that checkout is beside its own.

Anyone with the project checked out may run any unit: claims keep two machines from running the same attempt. A claim assigns the unit's Pipeline Step to the session's login and names the machine. The first claim stands. Another machine sees the unit as `running`, with the reason `claimed: elsewhere`, and doesn't hand it out. Each attempt is claimed, a rework included. The tracker login is the actor of each fact, and each person writes with their own credentials. A human gate's `owner` says whose turn the decision is, and the inbox shows it to them.
