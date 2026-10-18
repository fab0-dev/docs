# Dependencies and blocking

Units run in parallel as far as their dependencies allow, and the engine respects dependencies wherever they are declared. On every call, it works out each unit's state before it hands anything out. `fab0-resolve status` and `/fab0:inbox` show the states.

## Unit states

| State | Meaning |
|---|---|
| `ready` | It can start now. `next` hands it out |
| `running` | It was handed out, and nothing is recorded yet. `next` hands it out again, to the same checkout. With the reason `claimed: elsewhere`, another machine claimed the attempt, and it isn't handed out here |
| `waiting` | It is recorded and waits on its gate: `merge` (for `apply`), `gate` (an auto gate is due), `human`, `questions` (a person answers), or `escalated` |
| `blocked` | It can't start, and a reason says why. See below |
| `done` | The commits its latest attempt recorded (`heads`) are in the branch it merges into, or GitHub reports its pull request merged at those commits, as after a squash merge. An attempt that committed nothing is done when its gate passes; for one reviewed in the runs repository, when its owner merges the review pull request. For an action, its check passes |

A gated block is `open` while its units are under way.

## Why a unit is blocked

| Reason | What it waits for |
|---|---|
| `order` | Steps that come first: the previous node, an element's `after`, a block's `onStart` |
| `data` | An input that doesn't exist yet. Data dependencies follow from inputs and outputs, so nothing needs declaring |
| `claim` | An earlier unit whose claimed paths overlap. Units with disjoint claims run in parallel; overlapping ones run one after another |
| `limit` | A free slot: `parallel.max` for the run, or a `foreach`'s `max` |
| `tracker` | Items the tracker says come first, while they are open |
| `cross-run` | Another open run that claims overlapping paths, when the project's policy is `block` |
| `invalid-dependency` | A person, because the dependencies can't be right. See below |
| `condition` | A tracker item a `when` asks about, on a run that has none |
| `failed` | A changed input, after a command failed, after checks failed more times in a row than the gate's `retry`, or after an auto gate's retries ran out with `then: fail`. On a call: its child run's item was closed as not planned |
| `factory` | A call's connected factory, whose wiring the call can't read, so it can't start the child run |

A unit that is merely waiting its turn (`order`, `data`, `claim`, `limit`) needs nobody. The others are signals a person may need to act on.

## Calls

A call waits on its child run (`child`), which another factory's people run. In the child, a unit whose outputs the parent takes waits for the parent's answer (`ack`) once its own gate has passed, and in the parent, a call with an `auto` or `human` gate waits to give that answer. A child's step that reads what another call hands back waits with `data` until the parent accepts it: the dependency between two factories is an input, like any other. See [connected factories](connected-factories.md).

## Dependencies in the tracker

The tracker's own relations are dependencies too. GitHub's blocked-by and sub-issue relations are read on every call:

- **A `foreach` element's item** is the sub-issue that `tracker.child.sync` made for it. When the engine creates the items, it adds the elements' `after` as blocked-by relations.
- **From then on, the tracker is the truth.** A person who adds or removes a blocked-by on the board changes what the engine hands out next. A relation a person removed is never put back.
- **A blocker inside the run** makes the element wait until the blocking element's work is merged. **A blocker outside the run**, such as another Story or a plain issue, holds it as `tracker` until that item closes.
- **Blocked-by on the run's own item** holds back the whole run.
- **Other sub-issues of the run's item**, besides its elements' items, hold back the run's end until they close.

Elements without a tracker item use their `after` only.

## Invalid dependencies

Some dependencies can't be satisfied, and the engine reports them instead of guessing:

- a cycle;
- an `after` that names no element;
- an item blocked by its own run's item;
- a blocker closed as not planned;
- a blocker inside the run whose item a person closed while its work isn't merged.

## Other runs

Two open runs may want the same files. The engine reads other runs' claims from the run store: the claimed paths of each unit's latest attempt, recorded in the ledger. A unit's claims hold until its commits reach the base branch. When a ready unit's claims overlap another open run's, it carries a warning, or with `parallel.cross_run: block` it waits.

## Signals on the board

Blocking signals are projected, not stored twice. `status` and `next` print them. With `tracker.fields.signal` set, `apply` writes each item's state into that board field: `done`, or its first unfinished unit and why, for example `blocked: implement-T2 (order T1)`. The engine never reads the field back.
