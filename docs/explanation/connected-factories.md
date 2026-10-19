# Connected factories

A product is often built in several repositories, each with its own people: a service, a web client, a mobile app. Each repository can have a factory of its own, with the agents and the process that fit its code. A factory **connects** other factories and calls their pipelines as a step of its own. The calling side is the **parent**, and the run it starts in the other factory is a **child run**.

This page says how that works and why. To set one up, see [connect a factory](../how-to/connect-a-factory.md). For the fields, see [`factories`](../reference/project.md#factories), [`call`](../reference/pipeline.md#call) and [link facts](../reference/ledger.md#link-facts).

## Why connect factories, not repositories

A factory can already write several repositories: its `repos` lists them, and a task names the one it changes. That keeps one process, one set of agents and one owner for all of them. When each team works its own way, with its own reviewers, its own task format and its own people deciding, one factory has to hold every team's process at once.

A connected factory stays complete on its own. Its wiring, agents and gates are its team's, it runs from its team's checkout, and it can run without any caller. The parent knows only what it needs to: the pipeline it calls, what it binds, and what it takes back. So each side changes without the other, as long as that interface holds.

## What passes between them

Only artifacts, and only through the call's interface:

- **Inputs.** A pipeline that may be called declares `inputs`: `store` artifacts its steps read. The call binds each one to an artifact of the parent, such as its spec. A child sees only what is bound to it. An input the call doesn't bind reads its `default`, such as the run's own item, or nothing, when it is `optional`.
- **Outputs.** The pipeline declares `outputs`, artifacts its steps write. The call maps each one it takes to an artifact of its own, and that artifact is the **accepted format**: its schema, and the sections its checks ask for.

Nothing else crosses: no shared files, no messages. A child that needs to know something asks for it as an input, and a parent that needs something declares it as an output it takes.

## A call's life

1. **Start.** When the call's turn comes, `apply` files the item the child pipeline's trigger expects (its issue type or label) in the connected factory's home repository, as a sub-issue of the parent run's item. It records the call as `call@<call>` in the parent's folder of the runs repository, with the child run's id, which is the parent run's own: run 12 calls, and the child is run 12 too, in its own factory's folder (`runs/<child project>/12/`) and on its own branches (`fab0/12/…`), though its item has a number of its own. The call then waits on the child run, and it is the connected factory's owner's turn. The parent's session stops there.
2. **Bind.** The child's people find the run in their own inbox, under the parent's id, and run it in their own checkout: `/fab0:run`, with no argument, goes on with it when it is the only run with work there, and `/fab0-watch` keeps it going. Its first action, `call.bind`, finds the call by the run's id, the `call@*` fact in another project's folder of that id that names this factory, and copies what the call binds and accepts into `bound@parent`, in the child's own folder.
3. **Check at the source.** When a child step writes an output the parent takes, `record` checks it against the accepted format as well as against the child's own checks. A mismatch fails the attempt there, where it can be fixed, rather than in the parent later. The child's brief says what that format is.
4. **Export.** Once the unit that wrote it is done, by the child's own gate, `apply` hands the output back as `export@<unit>-<attempt>+<output>`.
5. **Acknowledge.** The call's gate answers each export. With `none`, an export in the accepted format is accepted at once. With an `auto` gate, an agent judges it. With a `human` gate, a person reviews it in a pull request of the runs repository: an approving review accepts, and `apply` merges; a review that asks for changes rejects. Each answer is an `ack@*` fact in the parent's folder. Until it comes, the child unit waits. A rejection is a rework, with the parent's findings in its brief, under the child's own `retry` and `then`.
6. **Receive and join.** An accepted export becomes the latest version of the parent artifact it maps to. The call is done when every output it takes, except the optional ones, has an accepted version, and only then does the parent's next step start.

Each project writes facts only in its own folder of the runs repository, and reads the other's. Every fact is create-only, so two machines never overwrite each other, and nothing needs a lock across factories.

## Children work in parallel, and wait only for what they read

Calls in a `parallel` block run side by side. When one child needs what another hands back, the parent binds it: the web client's call binds `upstream` to the contract the service's call receives. The web client's run starts at once and plans from the spec. Only its steps that read the contract wait, as `data`, until the parent accepts the service's contract. Then they read the version the parent accepted, and the ledger keeps it as what they were built against.

A newer accepted version makes those steps stale, as any changed input does, so a contract reworked after a rejection reaches the web client too.

## Who judges what

A child judges only its own area: its own gates review its own work, and what it reports is about what it built. The parent judges the whole. It decides what it accepts from each child, and its own next steps, such as a wrap-up, decide what the parent's work needs next.

This is a choice of the factories, not a rule of fab0: core gives it a footing. A child sees only its bindings, hands back only its declared outputs, and is checked against the parent's format before anything goes back.

## What a session runs

`/fab0:run` runs one run of its own factory. It never runs a child run, even when the connected factory's checkout is beside it: the child run is that factory's, with its own wiring, agents and gates, and its people run it. The parent's session says where each call waits and what to run there, and `/fab0:inbox` in the connected factory lists the run. With `/fab0-watch` on in each checkout, nobody has to type it: each factory's watch goes on with its own run when the engine says so, and the parent's goes on once a child hands something back. `fab0-resolve status <run> --tree`, and the watch's pane, show the parent and each child where they are.

A child run's pull requests merge into its own base branch when its people decide. The parent doesn't wait for them: its join is on what it accepted, not on a merge. So the child items, which close when their runs merge, don't hold back the parent's end.

## Limits

These wait until a run needs them:

- A called pipeline doesn't call another factory itself: one level.
- A pipeline calls a given factory once, and not inside a `foreach`: a child run has its parent's id, so two child runs of one factory for one parent would share it.
- A child pipeline is started by an issue trigger. A manual trigger can't be called yet.
- A call's `auto` gate is an agent. A person acknowledges in a review pull request, not by a label.
- A child run shows as failed on its call only when its item is closed as not planned. What blocks it inside its own factory shows there.
- Starting a call reads the connected factory's wiring from its checkout, so the parent's machine needs that checkout.

## An example

The [`feature`](https://github.com/fab0-dev/fab0-examples/tree/main/feature) example is a parent. Each Story of a Feature is one run: it writes a spec, calls a service and its web client side by side (each a copy of the [`delivery`](https://github.com/fab0-dev/fab0-examples/tree/main/delivery) example), and wraps up from their reports. The wrap-up files follow-up Stories under the Feature, or closes it. See [examples](examples.md).
