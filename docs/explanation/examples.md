# Examples

fab0 ships no factory, but it shows how to build one. [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples) holds complete, working factories, each with its wiring, its agents and skills, and the settings it needs. They are examples of good practice, not a standard: copy one, then make it yours.

## The examples

| Example | What it shows |
|---|---|
| `story` | Delivery. A product owner approves a spec and a task list, which are kept in the run store and reviewed in a pull request of the runs repository. Agents implement the tasks in parallel on sub-branches, and another agent reviews each one, which `apply` then merges into the run branch. A person merges the finished run into `main` |
| `feature` | A composition of [connected factories](connected-factories.md). Each Story of a Feature is one run: a spec reviewed by the product owner, then a service and its web client built side by side, each in its own repository with its own factory, and a wrap-up from what they hand back that files follow-up Stories under the Feature, or closes it |
| `delivery` | The connected factory each code repository copies for `feature`. It plans, writes a contract when other teams build against it, implements each task with a review, and reports on its own area. It also runs on its own |
| `triage` | Work that isn't code. An agent classifies a bug report, a command checks the classification, and actions label it, escalate it when it is severe, and comment, all in the tracker, with no pull requests |

Each example's README says what it does, what to copy where, and how to set up GitHub and Claude Code for it.

## Copy or install

**Copy** (recommended). The files become yours:

- they are versioned with your project, and changed only by a commit;
- you can edit them freely;
- every copied file names its source and release: the wiring and scripts in their first comment line, agents and skills just after their front matter, and JSON schemas in a `$comment`. So a diff against a newer release shows what changed.

**Install** the example's agents, skills and hooks as a plugin from the examples marketplace, if you want updates without owning those files. The wiring in `.fab0/` is always copied. Plugin agents and skills are named with the plugin's prefix, for example `agent: story:spec-author`.

Either way, the `fab0` plugin, which holds the engine and `/fab0:run`, is installed from the `fab0` marketplace and updates itself.

## Why examples, not a built-in factory

A factory encodes a team's process: what a spec looks like, how work splits, who reviews. These differ between teams, and change over time. Keeping them in the project, as files the team owns, lets each team change its process with a commit. The examples keep good defaults one copy away.
