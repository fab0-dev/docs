# Start and continue a run

This guide starts a run from a tracker item, takes your decisions where the run asks for them, and continues it until it is done. For what a run id is and why, see [pipelines and steps](../explanation/pipelines.md).

You need a factory that [validates](build-your-first-factory.md), with `tracking` set and the run tracker [set up](github-setup.md#3-the-run-tracker), a pipeline whose trigger is an `issue`, and an open item it matches: for example an issue of type Story, `acme/shop#52`.

## 1. Start the run

In Claude Code, in the home checkout, on the base branch, run:

```text
/fab0:run #52
```

The `#` says it is an item. The run's Pipeline Run opens in the runs repository, as a sub-issue of the item, and its number is the run id:

```text
acme/shop#52 starts as run 12 (story), tracked in acme/shop-runs#12
```

The session then runs the pipeline as far as it can go, and stops when it needs a person, is blocked, or is done. It ends with the run's position, the line that says where it is:

```text
run 12 · story · acme/shop#52 · pass 1 · at spec (gate human)
```

`/fab0:run #52` again never starts a second run while the first is open: it goes on with run 12.

Nothing moves a run on between sessions: a run goes on only when someone runs `/fab0:run`. To see where it stands meanwhile, [follow it on its issues](follow-a-run.md).

## 2. Decide where the run asks you

A step's gate says who decides, and how. The session's report, and `/fab0:inbox`, say what waits on you.

| The gate | Where you decide | How |
|---|---|---|
| `human` via `pr`, `done: {pr: {state: approved}}` | The step's pull request, in the repository the step writes, the runs repository too | Approve with an approving review. GitHub doesn't let you approve a pull request you opened, and fab0 opened it with the login of whoever ran the session: comment `/approve` instead. Ask for changes with any other review, a Comment review too. The next `/fab0:run` merges what you approved: don't merge it yourself |
| `human` via `pr`, `done: {pr: {state: merged}}` | The step's pull request | Merge it to accept it, or leave a review to ask for changes |
| `human` via `prompt` | The run session | Answer the session's question, below |
| `human` via `issue` | The step's Pipeline Step, in the runs repository | Set its `Stage` to `Done` |
| `human` via `label` | The run's item | Add the gate's label |

Only someone in the gate's owner role decides. An approval counts for the commit the pull request holds when it is given: a later attempt needs a new one. An agent's questions are on the step's pull request, or on the run's item when the step has none: answer them there.

### Confirm at the prompt

A step under `human: {owner: …, via: prompt}` has no pull request. When the session reaches it, it shows what the step produced, its summary and its Output, and asks you whether to accept it:

- **Yes:** the session runs `fab0-resolve confirm 12 plan`, and the run goes on.
- **No:** it asks what should change, and runs `fab0-resolve confirm 12 plan --reject '<what should change>'`. The step's agent reworks it with your words.

`confirm` writes your decision on the step's Pipeline Step, with your login. If the session's login isn't in the gate's owner role, `confirm` refuses and names the role, and the step waits for someone in it: they run `/fab0:run` in their own session. You can also run `fab0-resolve confirm` yourself, in any terminal in the home checkout.

## 3. Continue it

After you have decided, continue the run:

```text
/fab0:run
```

With no argument, the session goes on with the only run in this checkout that has work to do. When several have, it asks which, the one interrupted first, then the ones with work for an agent, then the ones with actions only. When none has, it says what each run waits on, and on whom, and stops. A bare `/fab0:run` never starts a run from an item: that takes `#<n>`.

`/fab0:run 12` continues run 12 by its id, whatever else is open.

The run ends by itself when its last step is done: `onEnd` runs, its Pipeline Run closes with a summary of every step, and, with `pr.merge` at the end, each run pull request merges into `main` once its required checks pass. With `pr.ready` instead, the run pull requests are marked ready and wait for a person to merge them.

## A child run

A run that another factory's call started has no item of its own, only its Pipeline Run, a sub-issue of the caller's, and it has the caller's run id. In your factory's checkout, `/fab0:inbox` lists it under that id, as called by the other factory. Run it with `/fab0:run`, or `/fab0:run 12` when you have several runs open. See [connect a factory](connect-a-factory.md).

## A run from before 0.10

A run started with fab0 0.9 has no Pipeline Run, and 0.10 doesn't carry it over. Finish it with 0.9.1 before you upgrade, or close it. See [upgrade from 0.9](upgrade-from-0.9.md).
