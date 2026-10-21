# Follow a run

This guide finds a run on the run tracker and reads where it stands: from its issues on GitHub, which anyone with access to the runs repository can read, and from a checkout of the factory with `/fab0:inbox` and `fab0-resolve`. Reading changes nothing. For what each field and comment holds, see [the run tracker](../reference/tracker.md).

## 1. Find its Pipeline Run

A run's Pipeline Run is an issue in the runs repository, the repository `tracking.github` names. For a run started from an item, its number is the run id: run `12` is `acme/shop-runs#12`. A manual run's Pipeline Run carries the id it was given in its Run ID. Find it from any of these:

- **The item that started it.** The Pipeline Run is a sub-issue of the item, for example of Story `acme/shop#52`.
- **The session.** `/fab0:run` says where the run is tracked when it starts it: `acme/shop#52 starts as run 12 (story), tracked in acme/shop-runs#12`.
- **The runs repository.** List its issues of type `Pipeline Run`. Every factory of the product keeps its runs there, and each one's `Factory` and `Run ID` fields say whose run it is.

A child run, which another factory's call started, is a sub-issue of its caller's Pipeline Run. It carries the caller's `Run ID`, and its `Factory` names the factory that runs it. A child run has no item of its own.

## 2. Read its fields

The Pipeline Run's fields say what the run is, and where it stands:

| Field | Holds |
|---|---|
| `Run ID` | The run id: the Pipeline Run's own number for a root run, the caller's for a child run |
| `Pipeline` | The pipeline it runs |
| `Factory` | The factory whose run it is: its home repository's name, such as `shop` |
| `Stage` | `Todo` until a step has started, `In Progress` while the run goes on, `Done` once it is done |
| `Step` | The steps under way: running, waiting on their gate, or to be reworked |
| `Waiting on` | Everyone the run waits on, such as `@po-user`: the people its steps wait on, and whoever merges its run pull requests when only that is left |

Each step of the run that does work, and each call, is a Pipeline Step, a sub-issue of the Pipeline Run, titled with its unit, such as `spec` or `implement-T2`. Its fields say where that step stands:

| Field | Holds |
|---|---|
| `Step` | The unit |
| `Stage` | `Todo` until a session takes the step, `In Progress` while it is worked on or waits on its gate, `Done` once its `done` holds |
| `Waiting on` | The people in the role the step waits on, such as `@po-user`: for a human gate, an agent's questions, or an escalation |
| `Revision` | The attempt: 1, then one more for each rework after a rejection, a request for changes or a failed check |
| `Output` | The step's pull request while it is in review, then the commit it was accepted at |

`apply` updates the fields each time it runs, so they show where the run stood after the last `/fab0:run`. A Pipeline Step's assignee is the login of the session that took it: its claim. A step that is done is closed as completed, and the Pipeline Run closes as completed once the run is done, with a summary of every step and its revision. A step closed as not planned was opened twice at once, and the other one stands.

## 3. Read the comments

The comments are the run's log. On each Pipeline Step, each attempt, gate decision and claim is one comment: a line for people, then a YAML block that fab0 reads, headed `# fab0 <name>`, for example:

- `handed out, attempt 1`, with the block `# fab0 spec-1-claim`: a session took the step;
- `attempt 1 recorded: …`, with `# fab0 spec-1`: what the attempt produced, its summary, and its commits;
- a gate's decision, with `# fab0 spec-1-gate`: an agent's verdict and findings, a command's result, or a person's confirmation at the prompt, such as `confirmed by @po-user at the prompt`;
- `done, revision 1`, when the step closes.

The Pipeline Run's comments say where the run came from (`run 12 · story · from acme/shop#52`), which child runs its calls opened, and, at the end, the summary. A child run's Pipeline Run also holds its `call` block, what its caller bound and accepts, and a `rejected-<n>` block each time the caller rejected what it handed back.

Don't edit these comments, and don't add blocks of your own: fab0 reads the first comment of each name, and only comments by the runs repository's owner, members and collaborators count.

## 4. See what waits on whom

In a checkout of the factory, run:

```text
/fab0:inbox
```

It reads the factory's open Pipeline Runs and lists:

- what waits on you: a human gate, questions, an escalation, or a run pull request to merge;
- what anyone can run now, with its command;
- what waits on someone else, a child run in another factory included, with the command and the checkout to run it in;
- what is blocked, and why.

Under them, it lists every open run with its position, and items no run has started yet with `/fab0:run #<n>`. It runs nothing.

## 5. Look at one run in detail

From the home checkout:

```bash
fab0-resolve status 12 --tree
```

It gives every unit's state and why, and the run's position, the one line that says where it is. `--tree` adds each child run the run's calls started, with its own position, read from that factory's checkout beside this one; a child it can't read says why.

To follow the run's events as a session records them, from any terminal on the machine that runs it:

```bash
fab0-resolve log 12 --follow
```

The event log is kept in the home checkout's git directory, so it shows only what sessions on this machine did. `/fab0:run` prints this command in its first round. Without `--follow`, it prints the events so far and stops.
