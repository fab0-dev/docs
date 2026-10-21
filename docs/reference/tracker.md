# Run tracker

The run tracker holds every run: one issue for the run, a **Pipeline Run**, and one sub-issue for each of its units that does work or calls (an agent, command or tool step, or a call), a **Pipeline Step**. An action step has none: its check is its record. The issues' fields carry the run's state between steps, sessions and factories. Their assignees are claims, their comments are the run's log and its facts, and their close reasons end it. Every command reads the tracker again when it starts and keeps nothing between commands, so what the issues say is the run.

The run tracker is not the item tracker. The item tracker (`tracker` in `fab0.yaml`) holds the work items people file, such as a Story, its Task sub-issues, their labels and their board fields. The run tracker (`tracking`) holds the runs that work on them. A run started from an item is a sub-issue of that item.

The engine reaches the run tracker only through the `Tracking` class in `plugins/fab0/lib/fab0_engine/tracking.py`, so another kind of tracker can stand behind the same methods. `github` is the first kind. The facts on its comments are checked against `plugins/fab0/schemas/ledger-entry.json`, `claim.json`, `call.json` and `rejection.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). For how to read a run on its issues, see [follow a run](../how-to/follow-a-run.md).

## Configuration

`tracking` in `fab0.yaml` names the repository that holds the issues, and can rename the issue types, the fields and the Stage values. Its fields are in the [project reference](project.md#tracking).

```yaml
tracking:
  kind: github
  github: acme/product-runs
```

Every factory of a product names the same repository, the runs repository. A run started from an item has its Pipeline Run's number as its id, so one repository gives every run of every factory a distinct id, and a child run finds its parent's issue there.

`validate` reads the organization's issue types and fields. A missing or disabled type, a missing field, a field of another data type, or a Stage value the field has no option for is invalid wiring, exit 3. A field not pinned to a type that carries it is a warning, since GitHub then shows it only on demand. When `validate` can't read the tracker, for example with no `gh` login, it warns that the tracker isn't checked. `start`, and a run's first write, are refused without `tracking`, with a hint to add it. To create the types and fields, see [set up GitHub](../how-to/github-setup.md).

## Issue types

| Type | Default name | One for | Parent | Holds |
|---|---|---|---|---|
| `run` | Pipeline Run | each run | the work item that started it; the parent run's Pipeline Run, for a child run; none, for a run started by hand | the run's id, pipeline, factory and Stage; for a child run, the `call` block and any `rejected-<n>` blocks |
| `step` | Pipeline Step | each unit that does work or calls: a step, a foreach element's step, or a call; not an action step | the run's Pipeline Run | the unit's Stage, Revision and Output; who claimed it; its attempts, gate decisions and claims as comments |

`tracking.types` renames them. Both are organization issue types, so an admin creates them once for every repository of the organization.

| Issue | Title | Body |
|---|---|---|
| Pipeline Run, started from an item | the item's title | `Started from acme/product#412.`, then the factory and the pipeline |
| Pipeline Run, a child run | `<pipeline> of <factory> for <parent pipeline> run <id> (<call>)` | `Called by run 57, acme/product-runs#57.`, then the factory and the pipeline |
| Pipeline Run, started by hand | `<pipeline> run <id>` | `Started by hand.`, then the factory and the pipeline |
| Pipeline Step | the unit's id, such as `implement-T2` | `A step of run 57, acme/product-runs#57.` |

## Issue fields

The fields are organization issue fields. `tracking.fields` renames them by their key.

| Issue field | Key | Data type | On | Holds |
|---|---|---|---|---|
| Run ID | `run_id` | text | run, step | The run's id. A run started from an item has its Pipeline Run's number; a manual run, the id given; a child run, its parent's |
| Stage | `status` | single select | run, step | Where the issue is in its life: `Todo`, `In Progress` or `Done`. GitHub reserves the name Status |
| Pipeline | `pipeline` | text | run | The pipeline the run runs. The engine reads a run's pipeline from here |
| Factory | `factory` | text | run | The factory whose run it is: its home repository's name, such as `product` for `acme/product`, lowercased, with any character other than a letter, digit or `-` made `-` |
| Step | `step` | text | run, step | On a step, its unit's id. On a run, the units under way: running, waiting, or to rework. Cleared when the run closes |
| Waiting on | `waiting` | text | run, step | On a step that waits on a person (a human gate, questions, an escalation), its owner role's logins, such as `@po-user`, or the role when it has no logins. On a run, everyone it waits on. Cleared when nobody is waited on |
| Revision | `revision` | number | step | The unit's attempt: 1 when it is first claimed, then the number of each attempt `record` writes. A rework raises it |
| Output | `output` | text | step | Where the unit's result is: its pull request while it is in review, then the commit it was accepted at, as a link |

A run finds its Pipeline Run by its id and its Factory. An id of digits names a root run's issue by number, which counts when the issue is a Pipeline Run of this factory whose Run ID is that number. Any other id, and a child run's, is found by Run ID and Factory: the open run, else the newest closed one, leaving out one closed as not planned.

## Stage

| Value | Key | Meaning |
|---|---|---|
| `Todo` | `todo` | Opened, or opened again, and not taken yet |
| `In Progress` | `in_progress` | A session took the step: the step is assigned to its login |
| `Done` | `done` | The run or step is done, and closed as completed. A person who sets a Pipeline Step `Done` decides its gate, where the gate is `human` with `via: issue` |

`tracking.status` renames the values by their key and may add more, such as `blocked`. The engine sets only these three. A Pipeline Run goes `In Progress` once one of its units has started. A call's definition of done, `done: {issue: {status, run: child}}`, names a Stage value as the tracker shows it, such as `Done`, and the call waits until its child run's Pipeline Run has it. See [pipeline](pipeline.md#call).

## Lifecycle

Each event is a write of one command. The comment is the line a person reads; where the event writes a fact, a YAML block follows the line (see [facts](#facts)).

| Event | Command | Issue | Stage | Other changes | Comment |
|---|---|---|---|---|---|
| A run starts from an item | `start #<n>` | a new Pipeline Run, under the item | `Todo` | Run ID: its own number; Pipeline; Factory | `run 57 · story · from acme/product#412` |
| A run started by hand writes first | `next` | a new Pipeline Run, on its own | `Todo` | Run ID: the id given; Pipeline; Factory | `run nightly-3 · triage · started by hand` |
| A call starts its child run | `apply` (`call.start`) | a new Pipeline Run, under the parent's | `Todo` | Run ID: the parent's; the child's Pipeline and Factory | on the child: `run 57 · delivery · called by acme/product-runs#57`, and `called by contract of run 57, acme/product-runs#57`, then the [`call` block](#call); on the parent: `api · child run acme/product-runs#63`; on the call's Pipeline Step: `started acme/product-runs#63, delivery of api` |
| The engine first writes for a unit: its claim, or a call's start | `next`, `apply` | a new Pipeline Step, under the run | `Todo` | Run ID; Step: the unit's id | — |
| An attempt is handed out | `next` | the Pipeline Step, opened again if it was closed | `In Progress` | assigned to the session's login; Revision 1, when it has none | `handed out, attempt 1`, then the [claim](#claim) |
| An attempt is recorded | `record` | the Pipeline Step | — | Revision: the attempt; Output: the commit, when the attempt committed | `attempt 1 recorded: <summary>`, then the [attempt](#attempts-and-gate-decisions) |
| An auto gate decides | `record --gate` | the Pipeline Step | — | — | `gate approve: <reasons>`; for a call, `accepted: <reasons>` or `rejected: <reasons>`; then the gate decision |
| A person decides at the prompt | `confirm` | the Pipeline Step | — | — | `confirmed by @po-user at the prompt`, or `asked for changes by @po-user at the prompt: <text>`, then the gate decision. On a call: `accepted: accepted by @po-user`, or `rejected: <text>` |
| A unit's pull request opens for review | `apply` | the Pipeline Step | — | Output: the pull request | — |
| A unit waits on a person, or no longer does | `apply` | the Pipeline Step | — | Waiting on: set or cleared | — |
| Where the run stands changes | `apply` | the Pipeline Run | `In Progress` once a unit has started | Step: the units under way; Waiting on: everyone the run waits on | — |
| A person accepts a call's result on its issue | `apply` | the call's Pipeline Step, which the person set `Done` | — | — | `accepted: set Done on <step>`, then the gate decision |
| A call's gate rejects what its child handed back | `apply` | the child's Pipeline Run, opened again | `Todo` | — | `rejected by <call> of run 57: <reasons>`, then the [`rejected-<n>` block](#rejections) |
| A unit is done: its definition of done holds | `apply` | the Pipeline Step, closed as completed | `Done` | Output: the commit it was accepted at; Waiting on cleared | `done, revision 2` |
| The run is done | `apply` | the Pipeline Run, closed as completed | `Done` | Step and Waiting on cleared | `run 57 done: spec (revision 1), …` |
| Two sessions opened one issue at once | any that opens one | the later issue, closed as not planned | unchanged | — | `opened twice: acme/product-runs#57 is …` |

A rework needs no event of its own: the next attempt is claimed and recorded on the same Pipeline Step, and its Revision rises. A step reworks on a rejection, a request for changes, a failed check, a merge conflict, failing required checks, or a missing output, never because another step made a newer version of an input.

## Assignees

A claim assigns the Pipeline Step to the session's login and sets it `In Progress`, before the attempt is handed out. A step `In Progress` and assigned to another login isn't handed out here: the unit shows as `running`, with `claimed: elsewhere`. Two sessions that claim at once both see the other's assignment and give way, and the next round decides. The [claim](#claim) comment names the machine as well, so two checkouts of one login don't run the same attempt either.

## Close reasons

| Reason | Set by | Means |
|---|---|---|
| completed | `apply` | The run or step is done. Its Stage is `Done` |
| not planned | the engine, on a duplicate | Two sessions opened one Pipeline Run or Pipeline Step at once. The first one opened stands, and the other is closed as not planned. Readers leave a not-planned issue out: its facts don't count, and a run search skips it. A child run closed as not planned blocks its call |

A closed Pipeline Step opens again when it is claimed for a new attempt, as when a caller rejects what the step made. A closed child run opens again when its caller rejects what it handed back. Once an item's Pipeline Run is closed, `start #<n>` on that item starts a new run.

## Facts

A fact is one comment: a line for people, a blank line, then a fenced YAML block whose first line is `# fab0 <name>`. The engine writes it and checks it against its schema, chosen by its name.

````markdown
attempt 1 recorded: Added the pricing rules with tests; all tests pass.

```yaml
# fab0 implement-T2-1
step: implement
unit: T2
attempt: 1
...
```
````

| Name | On | Schema | Written by |
|---|---|---|---|
| `<unit>-<attempt>` | the unit's Pipeline Step | `ledger-entry.json` | `record` |
| `<unit>-<attempt>-gate` | the unit's Pipeline Step | `ledger-entry.json` | `record --gate`, `confirm`, or `apply` for a person's acceptance of a call's result on its issue |
| `<unit>-<attempt>-claim` | the unit's Pipeline Step | `claim.json` | `next` |
| `call` | the child run's Pipeline Run | `call.json` | the parent's `apply` |
| `rejected-<n>` | the child run's Pipeline Run | `rejection.json` | the parent's `apply` |

- **Written once.** The first comment of a name stands, and a later one of the same name is ignored. `record` refuses an attempt whose fact is there already.
- **Only members count.** A comment counts only when its author is the repository's owner, a member or a collaborator, since anyone can comment on a public runs repository.
- **The engine's alone.** Neither people nor agents write facts. A person decides by approving a pull request, setting a label, setting a Pipeline Step `Done` or answering at the prompt, and the engine writes what follows.

A unit's id is its step's name, with `-<element id>` for a foreach element, so `implement-T2-1` is attempt 1 of the `implement` step for element `T2`.

### Attempts and gate decisions

```yaml
step: implement
unit: T2
attempt: 1
executor: agent
actor: be-user
model: sonnet
branch: fab0/57/implement-T2
base: {branch: fab0/57/base, sha: 4c80e8a0a1b2c3d4e5f60718293a4b5c6d7e8f90}
claims: ["backend:src/pricing.py", "backend:tests/test_pricing.py"]
heads: {backend: 9f1c2d3e4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d}
gate: {type: auto}
started: '2026-10-15T10:00:00Z'
ended: '2026-10-15T10:04:12Z'
summary: Added the pricing rules with tests; all tests pass.
```

| Field | Required | Meaning |
|---|---|---|
| `step` | yes | The step, or the call for a call's gate decision |
| `unit` | no | The `foreach` element's id |
| `attempt` | yes | The attempt's number, from 1 |
| `executor` | yes | What made it: `agent`, `action`, `command` or `tool`; `person` for a person's decision at the prompt or on an issue |
| `actor` | yes | The tracker user who ran it |
| `model` | no | The model the agent ran on |
| `branch` | no | The branch the attempt was made on. A call's gate decision has none |
| `heads` | no | Per repository, the commit the attempt left its branch at, when the branch has commits its parent lacked at the hand-out. The unit is done once these commits are in the branch it merges into. An attempt without `heads` changed nothing, so its gate is the decision |
| `base` | no | The parent branch (`branch`) and the commit (`sha`) the inputs were read at. A call's gate decision has none |
| `started` | no | When the attempt or the gate decision was handed out, as a UTC time to the second, such as `2026-10-15T10:00:00Z`. A hand-out given again starts again |
| `ended` | no | When it was recorded, in the same form. Written with `started` |
| `inputs` | no | The hash of each input, by name, as `sha256:<hex>`. Only a change in an input people write, a `pr` or an `issue` artifact, reworks the unit: that is how a request for changes or an answer arrives |
| `outputs` | no | The hash of each output the attempt wrote, by name |
| `claims` | no | The paths the unit claimed, as `<repo>:<glob>` |
| `verify` | no | The checks of each output, by its name: `pass`, or the list of errors. Writes outside the claims add `claims:<repo>` with the files |
| `gate` | yes | The gate: `type` (`none`, `human` or `auto`). An auto gate's decision adds the `agent` or `command`, the `decision` (`approve`, `reject` or `escalate`), who merges after an approval (`merge`: `auto`, or `human` when the unit's definition of done is its own pull request merged), and the branch it merges `into`. A person's decision adds `decision` and `via`: `prompt` for `confirm`, `issue` for a call's Pipeline Step set `Done` |
| `summary` | no | The return's summary, a gate's reasons, or a command's exit |
| `questions` | no | The return's questions |
| `verdict` | no | A gate's verdict: the agent's, as returned, or one made from a command's exit or a person's words |
| `data` | no | The return's `data`, which later steps read as `{<step>.<field>}` |
| `exit` | no | A command step's exit code |
| `rework` | no | Why this attempt was made, when it isn't the first: `stale` (an input people write changed), `missing` (an output is gone), `verify` (a check failed), `rejected`, `conflict` (the branch conflicts with its parent) or `checks` (required checks fail) |

A duration isn't kept: it is `ended` minus `started`, never below 0. `fab0-resolve status` adds up the durations of a unit's attempts and gate decisions. A command gate's decision keeps its command with `{attempt}`, not the path the command ran with, because the path is one machine's and the facts are everyone's.

### Claim

Before `next` hands an attempt out, it assigns the step and writes the claim. The first claim of a name stands: a machine whose claim lost doesn't hand the attempt out.

```yaml
actor: po-user
machine: 3f2a9c0d4b5e6f708192a3b4c5d6e7f8
at: '2026-10-15T10:00:00Z'
```

| Field | Required | Meaning |
|---|---|---|
| `actor` | yes | The tracker user who took it |
| `machine` | yes | The checkout that took it: an id kept in the home repo's git directory, so a checkout knows its own claim |
| `at` | yes | When, as a UTC time to the second |

### `call`

A [call](pipeline.md#call) starts a child run in a connected factory. The parent's `apply` opens the child's Pipeline Run under its own and writes this block on it. The child reads it there to find its parent, its inputs and what its caller accepts. No item is made in the child factory's repository. For how calls work, see [connected factories](../explanation/connected-factories.md).

| Field | Required | Meaning |
|---|---|---|
| `factory` | yes | The connected factory, as the parent's `factories` names it |
| `pipeline` | yes | The child pipeline |
| `unit` | yes | The call's unit in the parent run |
| `element` | no | Inside a `foreach`, the element the call is for |
| `parent` | yes | The calling run: its `factory` on the tracker, its `run` id, its Pipeline Run (`issue`, as `owner/repo#n`), and its work `item`, when it has one |
| `bindings` | yes | Per child input, the parent's artifact bound to it |
| `sources` | yes | Per child input, where the file bound to it is read: see [sources](#sources) |
| `formats` | yes | Per output the parent takes, its accepted format: see [formats](#formats) |
| `acknowledge` | no | How the call accepts what the child hands back, by its gate: `none` accepts it once the child run reaches the Stage the call's `done` names; `auto` and `human` wait for the call's gate to approve its latest look |
| `actor` | yes | The tracker user whose command wrote it |
| `at` | yes | When, as a UTC time to the second |

#### Sources

A file is read across factories at the commit of its producer's latest attempt, in a checkout of the repository that holds it, which both factories list.

| Field | Required | Meaning |
|---|---|---|
| `sources.<input>.factory` | yes | The factory that produces the file |
| `sources.<input>.artifact` | yes | The producer's artifact |
| `sources.<input>.repo` | yes | The producer's key of the repository in its `repos` |
| `sources.<input>.github` | yes | That repository, as `owner/name` |
| `sources.<input>.path` | yes | The file's path in it |
| `sources.<input>.call` | no | For a file another call of the caller receives, that call. It counts once the caller accepted it |
| `sources.<input>.caller` | no | The factory that made that call |

#### Formats

| Field | Required | Meaning |
|---|---|---|
| `formats.<output>.artifact` | yes | The parent's artifact that receives the output |
| `formats.<output>.schema` | no | The JSON Schema the output must be valid against, carried whole, so the child checks it at the source |
| `formats.<output>.sections` | no | The Markdown sections the output must have, from the parent artifact's checks |
| `formats.<output>.optional` | no | `true` when the parent doesn't need the output |

### Rejections

When a call's gate rejects what its child run handed back, the parent's `apply` writes a `rejected-<n>` block on the child's Pipeline Run and opens it again, `Todo`. `<n>` is the call's attempt that rejected it. The child's units it names rework, with its reasons and findings.

| Field | Required | Meaning |
|---|---|---|
| `call` | yes | The call's unit in the parent run |
| `attempt` | yes | The call's attempt that rejected: its n-th look at what the child handed back |
| `by` | yes | The parent's Pipeline Run, as `owner/repo#n` |
| `rejects` | yes | Per output the call takes, the child's `unit` and `attempt` that produced the version rejected |
| `reasons` | yes | The gate's reasons |
| `findings` | no | The gate's findings |
| `actor` | yes | The tracker user whose command wrote it |
| `at` | yes | When, as a UTC time to the second |

## The interface

`Tracking` is everything the engine asks of a run tracker. A new kind implements the same methods.

| Method | Does |
|---|---|
| `check` | What `validate` reports: the errors and warnings about types, fields and Stage values |
| `get` | An issue, with its sub-issues and comments |
| `runs` | The open Pipeline Runs, of one factory and at one Stage when given |
| `runs_of`, `find_run` | A factory's runs with one Run ID; the open one, else the newest closed one |
| `run_of_item` | The open run of a factory that an item started |
| `find_issue` | The issue of a type whose fields hold given values, for a definition of done |
| `steps` | A run's Pipeline Steps, read again |
| `open_run`, `open_step` | Open a Pipeline Run or a Pipeline Step, with its fields and its first comment |
| `claim` | Assign a step to a login and set it `In Progress`, or say that another login holds it |
| `set` | Set fields by their key; an empty value clears one |
| `log` | Write a comment |
| `close`, `reopen` | Close as completed or not planned; open again, `Todo` |
| `first_of` | Of issues opened twice at once, keep the first and close the others as not planned |

The event log, which `fab0-resolve log` prints, is not on the tracker: it is a local file of each machine. See [the event log](commands.md#the-event-log).
