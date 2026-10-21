# Connect a factory

This guide connects a factory in one repository, the parent, to a factory in another, so that a step of the parent runs a pipeline of the other as a child run. For how calls work, see [connected factories](../explanation/connected-factories.md). The [`feature`](https://github.com/fab0-dev/fab0-examples/tree/main/feature) and [`delivery`](https://github.com/fab0-dev/fab0-examples/tree/main/delivery) examples are a complete pair to start from.

The two factories share one run tracker and one runs repository: the child's Pipeline Run is a sub-issue of the parent's, and the files they exchange are in the runs repository, which both list in `repos`.

## 1. Wire the child for its caller

In the connected factory's `.fab0/fab0.yaml`, name the same runs repository and run tracker as the parent, and give its branches names of its own:

```yaml
repos:
  home: {path: ., github: acme/service, owner: developer}
  runs: {path: ../shop-runs, github: acme/shop-runs}
git:
  base: main
  branching: run
  branches: {run: "service/{run}/base", unit: "service/{run}/{unit}"}
tracking: {kind: github, github: acme/shop-runs}
```

A child run has its parent's run id. Both factories write the runs repository, so with the default names, `fab0/{run}/…`, the parent's run and the child's would share branches there. Naming them after the factory keeps them apart.

## 2. Give the child pipeline an interface

Declare what a caller may bind and what the pipeline can hand back:

```yaml
pipeline: delivery
trigger: {issue: {label: delivery}}
inputs:
  spec: {default: request}
  upstream: {optional: true}
outputs: [contract, feedback]
```

- Each input is a file that the pipeline's steps read and none writes, named only by its format: its content is wherever the caller's step wrote it. Give it a `default`, such as the run's own item, so the pipeline still runs on its own, or make it `optional`.

  ```yaml
  artifact: spec
  kind: file
  file: {format: markdown}
  ```

- Each output is a file a step writes, at a path in the runs repository, where the parent can read it:

  ```yaml
  artifact: contract
  kind: file
  file: {repo: runs, path: "runs/service/{run}/contract.yaml", format: yaml}
  ```

- A step that reads an input another team provides waits for it. Leave it out of steps that can work without it, such as planning, so they go ahead.

Commit the wiring to the base branch: the parent reads it there.

## 3. Name the connected factory in the parent

In the parent's `.fab0/fab0.yaml`, add it under `factories`, with its checkout beside this one, and list the runs repository in `repos`, with the same `tracking`:

```yaml
repos:
  home: {path: ., github: acme/shop, owner: product-owner}
  runs: {path: ../shop-runs, github: acme/shop-runs}
factories:
  service: {github: acme/service, path: ../service, owner: service-developer}
people:
  product-owner: {github: [po-user]}
  service-developer: {github: [be-user]}
tracking: {kind: github, github: acme/shop-runs}
```

`owner` is the role whose turn it is while the child run works: the inbox shows it the run. A factory's name on the run tracker is its home repository's name, so the two home repositories need different names.

## 4. Call it

Add a `call` to the parent's pipeline. Bind each input to an artifact of the parent, and map each output you take to a file of the parent, named only by the format you accept:

```yaml
- call: {factory: service, pipeline: delivery}
  id: service
  inputs: {spec: spec}
  outputs: {contract: contract, feedback: service-feedback}
  gate: {auto: {agent: acceptor, model: deep}}
  done: {issue: {run: child, status: Done}}
```

```yaml
artifact: contract
kind: file
file: {format: yaml}
schema: .fab0/schemas/contract.json
```

- `done: {issue: {run: child, status: Done}}` makes the call done when the child's run is. `validate` refuses a call with any other `done`.
- Give the receiving files the format you need: a `schema` for YAML or JSON, `sections` in `verify` for Markdown. The child checks against them before it hands anything back, and its briefs say what they are.
- Choose who accepts what comes back, in the call's `gate`. Gate `none` accepts what is in your format. `auto` with an agent judges it against what you asked for. `human` has a person decide, `via: issue`, by setting the call's Pipeline Step `Done`, or `via: prompt`, in the run session. A rejection opens the child's run again, and the child's units that made the rejected outputs rework them.
- Mark an output `optional` (`{artifact: <name>, optional: true}`) when the parent's next step shouldn't wait for it.

To call several factories at once, put the calls in a `parallel` block, as the `feature` example does. To feed one child's output to another, bind it: `inputs: {upstream: contract}` in the second call. Children that write one repository name their branches apart from each other too.

## 5. Check the connection

Run `fab0-resolve validate` in the parent. It reads each connected factory's wiring at its base branch, and lists it under `factories`, with `checked: true`. When it can't read a factory, it warns and says why. When the factories don't fit, it refuses with the reason, for example:

- `its run tracker isn't this factory's: a child's Pipeline Run is a sub-issue of the parent's`;
- `it names its branches as this factory does, and both have acme/shop-runs, …: give it git.branches of its own`;
- `outputs.contract: it is in acme/service, which this factory lacks in its repos`: an exchanged file must be in a repository both factories list;
- `input 'spec' is required, with no default: bind it`.

## 6. Set up GitHub

- The run tracker's issue types and fields, in the organisation both factories' repositories belong to. See [set up GitHub](github-setup.md#3-the-run-tracker).
- The runs repository, shared by both factories, with write access for both teams.

A call opens no item in the connected factory's repository: the child run's only issue is its Pipeline Run. The child's trigger label or issue type is needed only for runs started there.

## 7. Run it

Run `/fab0:run #<item>` in the parent. The run takes its id, for example `12`. When it reaches the call, `apply` opens the child's Pipeline Run as a sub-issue of the parent's, with the call's bindings and accepted formats in a comment, and the session stops there: it never runs the child.

The child run has the parent's id. In the connected factory's checkout, its people find run 12 with `/fab0:inbox`, and run it with `/fab0:run`, or `/fab0:run 12` when they have several. When the child run is done, run `/fab0:run` in the parent again: the call's gate judges what came back, and the run goes on.

`fab0-resolve status 12 --tree` in the parent shows the parent and each child where they are. See [follow a run](follow-a-run.md).
