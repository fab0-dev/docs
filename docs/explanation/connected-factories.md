# Connected factories

A product is often built in several repositories, each with its own people: a service, a web client, a mobile app. Each repository can have a factory of its own, with the agents and the process that fit its code. A factory **connects** other factories and calls their pipelines as a step of its own. The calling side is the **parent**, and the run it starts in the other factory is a **child run**.

This page says how that works and why. To set one up, see [connect a factory](../how-to/connect-a-factory.md). For the fields, see [`factories`](../reference/project.md#factories) and [`call`](../reference/pipeline.md#call); for the issues and comments a call writes, see the [run tracker reference](../reference/tracker.md).

## Why connect factories, not repositories

A factory can already write several repositories: its `repos` lists them, and a task names the one it changes. That keeps one process, one set of agents and one owner for all of them. When each team works its own way, with its own reviewers, its own task format and its own people deciding, one factory has to hold every team's process at once.

A connected factory stays complete on its own. Its wiring, agents and gates are its team's, it runs from its team's checkout, and it can run without any caller. The parent knows only what it needs to: the pipeline it calls, what it binds, and what it takes back. So each side changes without the other, as long as that interface holds.

## What passes between them

Only files, and only through the call's interface:

- **Inputs.** A pipeline that may be called declares `inputs`: files its steps read. The call binds each one to a file of the parent, such as its spec. A child sees only what is bound to it. An input the call doesn't bind reads its `default`, such as the run's own item, or nothing, when it is `optional`.
- **Outputs.** The pipeline declares `outputs`, files its steps write. The call maps each one it takes to an artifact of its own, and that artifact is the **accepted format**: its schema, and the sections its checks ask for.

Nothing else crosses: no messages, and no copies. A child that needs to know something asks for it as an input, and a parent that needs something declares it as an output it takes.

## Files across factories

A file one factory writes and another reads stays where its producer wrote it. On the reading side, its artifact names only its `format` (`file: {format: yaml}`), with no repository and no path: the call says whose file it is. The reader reads it at the commit of its producer's latest attempt, in its own checkout of the repository the file is in.

So both factories must list that repository in `repos`. It is the runs repository, which every factory of a product shares: the examples write specs, contracts and reports there, under `runs/<factory>/<run>/`. Git holds the content and its history, and the producer's fact names the commit, so nothing is copied between factories and nothing links them but the run tracker.

## A call's life

1. **Start.** When the call's turn comes, `apply` opens the child's **Pipeline Run** in the runs repository, as a sub-issue of the parent's, with the parent's Run ID and the child's own Factory and Pipeline. A comment on it, the `call` block, holds what the call binds, where each bound file is read, and the formats the call accepts. The call makes no item in the connected factory's repository: the child's Pipeline Run is its only issue. The call then waits on the child run, and it is the connected factory's owner's turn. The parent's session stops there.
2. **Take it up.** The child's people find the run in their own inbox, which finds it on the run tracker by its Factory field, and run it in their own checkout with `/fab0:run`, under the parent's run id. The child reads its call from its own Pipeline Run.
3. **Check at the source.** When a child step writes an output the parent takes, `record` checks it against the accepted format as well as against the child's own checks. A mismatch fails the attempt there, where it can be fixed, rather than in the parent later. The child's brief says what that format is.
4. **The child's run is done.** The child works through its own pipeline, under its own gates, to its own end. Its Pipeline Run then reaches `Done` and closes. The call waits until the child's Pipeline Run reaches the status its `done` names, `issue: {run: child, status: Done}`.
5. **Accept or reject.** The call's gate decides what came back. With `none`, it is accepted. With an `auto` gate, an agent judges each output against what the call asked for. With a `human` gate, the owner sets the call's Pipeline Step `Done` (`via: issue`) or confirms at the prompt (`via: prompt`). Each decision is a fact on the call's own Pipeline Step. See [accepting what a child hands back](gates.md#accepting-what-a-child-hands-back).
6. **Rework on a rejection.** A rejection is a `rejected-<n>` comment on the child's Pipeline Run, which names the child unit and attempt behind each rejected output. `apply` opens the child run again, at `Todo`. The child's people run it again, and those units rework with the parent's findings in their brief, under their own `retry` and `then`. When the child's run is done again, the call looks again.
7. **Join.** Once the call accepts, the files it receives count, and the parent's next step starts.

Every write is a sub-issue, a field or a comment on the run tracker, which every factory of the product shares. So the parent and the child see one tree of issues for one piece of work, and nothing needs a lock or a store of its own across factories.

## Children work in parallel, and wait only for what they read

Calls in a `parallel` block run side by side. When one child needs what another hands back, the parent binds it: the web client's call binds `upstream` to the contract the service's call receives. The web client's run starts at once and plans from the spec. Only its steps that read the contract wait, as `data`, until the parent accepts the service's run. Then they read the contract at the commit the service's run produced it.

## Who judges what

A child judges only its own area: its own gates review its own work, and what it reports is about what it built. The parent judges the whole. It decides what it accepts from each child, and its own next steps, such as a wrap-up, decide what the parent's work needs next.

This is a choice of the factories, not a rule of fab0: core gives it a footing. A child sees only its bindings, hands back only its declared outputs, and is checked against the parent's format before anything goes back.

## What a session runs

`/fab0:run` runs one run of its own factory. It never runs a child run, even when the connected factory's checkout is beside it: the child run is that factory's, with its own wiring, agents and gates, and its people run it. The parent's session says where each call waits and what to run there, and `/fab0:inbox` in the connected factory lists the run. `fab0-resolve status <run> --tree` shows the parent and each child where they are.

A child run is done as its own pipeline says. The `delivery` example ends with `pr.merge`, so its run is done once its run pull requests are merged into its own base branch, and only then does the parent's call look at what it handed back.

## What `validate` checks

`validate` reads each connected factory's `.fab0/` at its base branch, from its checkout, as that factory's own engine would. It refuses a connection where:

- the two factories have the same name: a factory's name is its home repository's name, and the run tracker tells runs apart by it;
- the child doesn't share the parent's run tracker, since its Pipeline Run is a sub-issue of the parent's. They need not share the tracker of work items;
- they share a repository and name their branches alike, since a child run has its parent's run id. The same holds between two children of one parent;
- an exchanged file is in a repository one of them lacks in `repos`;
- the called pipeline is missing, calls another factory itself, lacks an input or output the call names, leaves a required input unbound, or hands back a format other than the one the call accepts;
- the child's own wiring is invalid.

Without a checkout of the connected factory, the connection isn't checked, and `validate` says so.

## Limits

These wait until a run needs them:

- A called pipeline doesn't call another factory itself: one level.
- A pipeline calls a given factory once, and not inside a `foreach`: a child run has its parent's id, so two child runs of one factory for one parent would share it.
- A call's `auto` gate is an agent. A person accepts via issue or prompt, since a call has no pull request of its own.
- A child run shows as failed on its call only when its Pipeline Run is closed as not planned. What blocks it inside its own factory shows there.
- Starting a call reads the connected factory's wiring from its checkout, so the parent's machine needs that checkout.

## An example

The [`feature`](https://github.com/fab0-dev/fab0-examples/tree/main/feature) example is a parent. Each Story of a Feature is one run: the product owner approves its requirements, then a service and its web client are built side by side by two calls (each a copy of the [`delivery`](https://github.com/fab0-dev/fab0-examples/tree/main/delivery) example), and an `acceptor` agent accepts what each one hands back. A wrap-up, reviewed like the requirements, files follow-up Stories under the Feature, or closes it. See [examples](examples.md).
