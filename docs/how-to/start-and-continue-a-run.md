# Start and continue a run

This guide starts a run from a tracker item, and continues it until it is done. For what a run id is and why, see [run ids](../explanation/pipelines.md#run-ids).

You need a factory that [validates](build-your-first-factory.md), with a pipeline whose trigger is an `issue`, and an open item it matches: for example an issue of type Story, `acme/shop#52`.

## 1. Start the run

In Claude Code, in the home checkout, run:

```text
/fab0:run #52
```

The `#` says it is an item. The run takes its id from the runs repository, the next free number, for example `12`, and the item gets a comment that says so. The session then runs the pipeline as far as it can go, and stops when it needs a person, is blocked, or is done. It ends with the run's position, the line that says where it is:

```text
run 12 · story · acme/shop#52 · pass 1 · at spec (gate human)
```

`/fab0:run #52` again never starts a second run while the first isn't done: it goes on with run 12.

## 2. Continue it

When the run waits on you, answer where it says: approve or comment on its review pull request (a comment `/approve` approves one you opened yourself, which GitHub doesn't let you approve), answer its questions, or merge its pull request. Then continue it:

```text
/fab0:run
```

With no argument, the session goes on with the only run in this checkout that has work to do. When several have, it asks which, the one interrupted first, then the ones with work for an agent, then the ones with actions only. When none has, it says what each run waits on, and on whom, and stops. A bare `/fab0:run` never starts a run from an item: that takes `#<n>`.

`/fab0:run 12` continues run 12 by its id, whatever else is open.

## 3. See where it is

- `/fab0:inbox` lists every open run with its position, what waits on you, and the command for each. An item no run has started shows with `/fab0:run #<n>`.
- `fab0-resolve status 12` gives every unit's state, and the run's position. With `--tree`, it shows each child run the run's calls started, where it is.
- `fab0-resolve log 12 --follow` follows the run's events from any terminal on this machine.

## 4. Let it continue by itself

Instead of typing `/fab0:run` after each review, turn on the watch: it goes on with the run in the session when the engine says it has work. See [watch a run](watch-a-run.md).

## A child run

A run that another factory's call started has the caller's id. In your factory's checkout, `/fab0:inbox` lists it under that id, as called by the other factory. Run it with `/fab0:run`, or `/fab0:run 12` when you have several runs open, or let `/fab0-watch` take it. See [connect a factory](connect-a-factory.md).

## A run from before 0.9

A run started before 0.9 keeps its item's number as its id: `/fab0:run 52` continues it, and `/fab0:run #52` finds it too.
