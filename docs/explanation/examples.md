# Examples

fab0 ships no factory, but it shows how to build one. [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) holds complete, working factories, each with its wiring, its agents and skills, and the settings it needs. They are examples of good practice, not a standard: copy one, then make it yours.

## The examples

| Example | What it shows |
|---|---|
| `story` | Delivery. A `spec-author` agent writes the spec, which the product owner approves in its pull request in the runs repository, and `apply` merges. A `planner` agent writes the task list from it, which the product owner confirms at the prompt. Agents implement the tasks in parallel on sub-branches, a reviewer agent judges each one, and `apply` merges it into the run branch. The run merges into `main` with `pr.merge` once its checks pass |
| `feature` | A composition of [connected factories](connected-factories.md). Each Story of a Feature is one run: requirements the product owner approves in a pull request, then a service and its web client built side by side by two calls, each done when its child run is, and accepted by an `acceptor` agent. A wrap-up, approved like the requirements, files follow-up Stories under the Feature, or closes it. Its own files are in the runs repository, on a run branch there |
| `delivery` | The connected factory each code repository copies for `feature`. It plans, which its developer confirms at the prompt, writes a contract when other teams build against it, implements each task under a reviewer agent, and reports on its own area. It names its branches after itself, since it shares the runs repository with its caller. It also runs on its own |
| `triage` | Work that isn't code. An agent classifies a bug report, a command checks the classification, and actions label it, escalate it when it is severe, and comment, all in the tracker, with no pull requests |

Each example names its run tracker in `tracking`, keeps its working files (specs, task lists, contracts, reports) in the runs repository under `runs/<factory>/<run>/`, and gives every step and call its `done`. A person reviews only what needs a person: the spec, or the requirements and wrap-up, in a pull request, and a plan at the prompt. Everything else is agents and `apply`, the merge into `main` included.

Each example's README says what it does, what to copy where, and how to set up GitHub and Claude Code for it. The organization, the repository's name and the runs repository are placeholders in the copied files, which the README replaces in one step.

## Copy or install

**Copy** (recommended). The files become yours:

- they are versioned with your project, and changed only by a commit;
- you can edit them freely;
- every copied file names its source and release: the wiring and scripts in their first comment line, agents and skills just after their front matter, and JSON schemas in a `$comment`. So a diff against a newer release shows what changed.

**Install** the example's agents, skills and hooks as a plugin from the examples marketplace, if you want updates without owning those files. The wiring in `.fab0/` is always copied. Plugin agents and skills are named with the plugin's prefix, for example `agent: story:spec-author`.

Either way, the `fab0` plugin, which holds the engine and `/fab0:run`, is installed from the `fab0` marketplace and updates itself.

## The merge guard

Every example's settings deny the model `gh pr merge`, pushes to the base branch and force pushes. `story`, `feature` and `delivery` add a hook, the merge guard, that blocks the same commands however they are written. So every merge goes through `apply`, as each step's gate and `done` say, or through a person. `apply` merges through its own calls, which neither blocks. See [who merges](gates.md#who-merges).

## Why examples, not a built-in factory

A factory encodes a team's process: what a spec looks like, how work splits, who reviews. These differ between teams, and change over time. Keeping them in the project, as files the team owns, lets each team change its process with a commit. The examples keep good defaults one copy away.
