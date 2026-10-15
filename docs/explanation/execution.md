# Running a pipeline

fab0 runs inside Claude Code. The work is split between a deterministic engine and the session that carries out what it hands out. This page explains the split, and the loop that `/fab0:run` follows. The [commands reference](../reference/commands.md) lists every command and option.

## The engine and the session

**The engine**, `fab0-resolve`, is a program in the `fab0` plugin. It decides; it never improvises:

- it reads `.fab0/`, git and the tracker, and works out every unit's state;
- it hands out what is due, with a brief for each agent;
- it checks and records what comes back;
- it performs every write that can be done exactly: actions, merges, pull requests, comments, relations.

**The session** runs `/fab0:run`. It executes; it never decides:

- it prepares the branches and worktrees a hand-out names;
- it runs each agent as a subagent with its brief, runs commands, and calls tools;
- it passes the replies back to the engine, and commits what was recorded.

The model doesn't route, because a deterministic program is repeatable, and can be tested and reviewed. The engine doesn't call models or tools, because the session already can.

## The loop

`/fab0:run <run>` repeats these steps until nothing more is handed out:

1. **`apply`** performs what is due: every action whose check fails, every merge a gate allows, every pull request a person or a gate needs, and every question or escalation to post. Each write checks first, so running it twice changes nothing.
2. **`next`** hands out every unit that is ready, and every auto gate that is due. It claims each unit by creating its branch on `origin`.
3. **The session** prepares each hand-out's checkout, and runs the agents of the round in parallel, each in its own worktree. It runs commands in their worktree, and calls tools.
4. **`record`** checks each reply and output, and writes the ledger entry. A gate's verdict is recorded the same way.
5. **The session commits** what was recorded, with the work, on the unit's branch.

Then it reports what ran, what `apply` did, and what the run is waiting for, and on whom.

A run's state is `units` while work is left, `waiting` when only the merge of its pull request into the base branch is left, and `done` when that pull request is merged.

## Hand-outs and briefs

A hand-out tells the session everything it needs for one unit: the branches to create and the worktree to work in, what the unit may change, its executor, and the JSON schema its reply must match.

An agent's hand-out carries a **brief**: the whole assignment, in plain text. It holds:

- the unit's inputs, inline;
- a rework section with the reasons, when it isn't the first attempt;
- where to write each output;
- what it may change and read;
- the skills to load;
- the reply's schema.

So any Claude Code agent can be a step. It needs no knowledge of fab0, only of its craft.

A gate's brief adds the producer's summary and the command that shows the change, and asks for a verdict.

## Worktrees

Each unit works in its own git worktree, under the repository's git directory, so parallel units never share a checkout. A unit whose branch is already checked out somewhere uses that checkout. `/fab0:run` removes the worktrees of finished units. It never removes a checkout a person made.

The home checkout's `.fab0/` governs the run, even when the engine is called from inside a worktree. Keep the home checkout on the base branch while a run goes on: the engine warns when it isn't, and `/fab0:run` stops to ask.

## The inbox

`/fab0:inbox` shows every open run of the project and what it needs. It finds runs from their traces: run branches not yet in the base, run folders on a ledger branch, and open items that match a trigger. It sorts their units into:

- what waits on your roles;
- what anyone can run now;
- what waits on others;
- what is blocked by a signal.

It changes nothing.

## Who may run what

Anyone with the project checked out may run any unit: claims keep two machines from running the same one. The tracker login is the actor recorded in the ledger. A human gate's `owner` says whose turn the decision is, and the inbox shows it to them.
