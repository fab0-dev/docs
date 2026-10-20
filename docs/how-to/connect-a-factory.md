# Connect a factory

This guide connects a factory in one repository, the parent, to a factory in another, so that a step of the parent runs a pipeline of the other as a child run. For how calls work, see [connected factories](../explanation/connected-factories.md). The [`feature`](https://github.com/fab0-dev/fab0-examples/tree/main/feature) and [`delivery`](https://github.com/fab0-dev/fab0-examples/tree/main/delivery) examples are a complete pair to start from.

## 1. Give the child pipeline an interface

In the connected factory, declare what a caller may bind and what the pipeline can hand back:

```yaml
pipeline: delivery
trigger: {issue: {label: delivery}}
inputs:
  spec: {default: request}
  upstream: {optional: true}
outputs: [contract, feedback]
```

- Each input is a `store` artifact that the pipeline's steps read and none writes. Give it a `default`, such as the run's own item, so the pipeline still runs on its own, or make it `optional`.
- Each output is an artifact a step writes, of kind `file` or `store`.
- A step that reads an input another team provides waits for it. Leave it out of steps that can work without it, such as planning, so they go ahead.

Use the same tracker owner and the same runs repository as the parent, under the default `store.project`, or one of its own. Commit the wiring to the base branch: the parent reads it there.

## 2. Name the connected factory in the parent

In the parent's `.fab0/fab0.yaml`, add it under `factories`, with its checkout beside this one:

```yaml
factories:
  service: {github: acme/service, path: ../service, owner: service-developer}
people:
  service-developer: {github: [be-user]}
```

`owner` is the role whose turn it is while the child run works: the inbox shows it the run.

## 3. Call it

Add a `call` to the parent's pipeline. Bind each input to an artifact of the parent, and map each output you take to a `store` artifact of the parent, which is the format you accept:

```yaml
- call: {factory: service, pipeline: delivery}
  id: service
  inputs: {spec: spec}
  outputs: {contract: contract, feedback: service-feedback}
  gate: {auto: {agent: acceptor}}
```

- Give the receiving artifacts the format you need: a `schema` for YAML or JSON, `sections` for Markdown. The child checks against them before it hands anything back, and its briefs say what they are.
- Choose the acknowledgement: no gate accepts what is in your format; `auto` with an agent judges each output; `human` has a person review each one in a pull request of the runs repository, which needs `store.github`.
- Mark an output `optional` (`{artifact: <name>, optional: true}`) when the parent's next step shouldn't wait for it.

To call several factories at once, put the calls in a `parallel` block. To feed one child's output to another, bind it: `inputs: {upstream: contract}` in the second call.

## 4. Check the connection

Run `fab0-resolve validate` in the parent. It reads each connected factory's wiring at its base branch and lists it under `factories`, with `checked: true`. When it can't read a factory, it warns and says why; when a call doesn't fit, it refuses with the reason.

## 5. Set up GitHub

- The label or issue type the child pipeline's trigger names, in the connected factory's repository: a call files its item with it.
- The runs repository, shared by both factories, with write access for both teams. See [set up GitHub](github-setup.md).

## 6. Run it

Run `/fab0:run #<item>` in the parent. The run takes its id, for example `12`. When it reaches the call, it files the child run's item and stops. The child run has the parent's id: in the connected factory's checkout, its people find run 12 with `/fab0:inbox`, and run it with `/fab0:run`, or `/fab0:run 12` when they have several. Run `/fab0:run` in the parent again to acknowledge what comes back and go on.

`fab0-resolve status 12 --tree` in the parent shows the parent and each child where they are.
