# Watch a run

This guide turns on the watch, `/fab0-watch`, so that a session follows this checkout's runs, tells you what changed and what waits on you, and goes on with a run by itself when a review or a child lets it. For how it works and why, see [the watch](../explanation/execution.md#the-watch); for its commands and options, see the [reference](../reference/commands.md#the-watch).

You need the `fab0` plugin enabled in the project, and a run started, for example with `/fab0:run #52`: see [start and continue a run](start-and-continue-a-run.md).

## 1. Turn it on

In Claude Code, in the home checkout, run:

```text
/fab0-watch
```

It watches every open run of the checkout. To watch one run only, give its id: `/fab0-watch 12`.

A band above the prompt then shows each run on one line, where it is and what it waits on:

```text
● run 12 · story · acme/shop#52 · at spec (gate human)
    waits: spec: product-owner (gate human), acme/shop-runs#4
fab0 watch [Check now] [Pause] [Stop]
```

The status line counts the runs and those that wait on a person. Each change shows as a dim line in the transcript, and a run that newly waits on a person, or that is done, also shows a toast and a notification.

## 2. Answer, and let it go on

Answer where the run waits: for example, approve the spec's review pull request on GitHub. Within a minute or so, the watch's next tick records your approval and merges the pull request, then goes on with the run:

```text
fab0 run 12: spec: waiting (gate human) → done: going on with /fab0:run 12
```

The session runs `/fab0:run 12` as if you had typed it, under the session's permission mode. When the run waits again, the watch tells you, and waits too.

The watch never decides for you: a human gate still waits for a person. It goes on with one run at a time, never twice on the same work, and pauses when it has started `/fab0:run` too often in an hour, or when you stop a turn it started. `/fab0-watch` takes it up again.

## 3. Follow it in the pane

```text
/fab0-watch pane
```

The pane shows each run's position, what it waits on with a link to each pull request, its child runs, and its last events on this machine. While a turn runs, it follows each unit as it is handed out and recorded. A run with work has a button that runs `/fab0:run` for it.

## 4. Leave it, and come back

You can close the session while the run waits, for example on a child run in another team's factory. The watch is kept for this checkout: the next session you open there takes it up, says what changed meanwhile, and goes on if there is work. Through a long wait, the watch ticks less often, down to once every ten minutes.

You can also clear the conversation at any wait: the run's state is the engine's, so nothing is lost. The `watch_fresh` option clears it before each run the watch starts.

## 5. Connected factories

Turn the watch on in each factory's checkout. A child's watch goes on with the run as soon as the parent's call starts it, and the parent's goes on as soon as a child hands something back. People only review.

## Options and controls

| To | Run |
|---|---|
| Only see the runs, never go on by itself | `/fab0-watch auto off` |
| Let it go on again | `/fab0-watch auto on` |
| Hold it for now | `/fab0-watch pause`, then `/fab0-watch` |
| Stop it, and forget it for the next session | `/fab0-watch stop` |

`watch_per_hour` (default 6) caps how often an hour it starts `/fab0:run`, and `watch_fresh` clears the session before each one. Set them under `/config`, with the `fab0` plugin's options.
