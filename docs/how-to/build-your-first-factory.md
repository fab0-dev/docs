# Build your first factory

This guide builds a small factory from scratch: an issue labelled `release-notes` gets release notes written by an agent, which a maintainer reviews and merges. It uses every building block once. To start from a complete factory instead, see [use an example](use-an-example.md).

You need:

- a GitHub repository you can push to, checked out locally, for example `acme/product`;
- a runs repository for fab0's own records, for example `acme/product-runs`. See [the runs repository](github-setup.md#6-the-runs-repository);
- [Claude Code](https://code.claude.com/) with the `fab0` plugin, `gh` logged in, and [`uv`](https://docs.astral.sh/uv/). See [set up GitHub](github-setup.md).

## 1. Describe the project

Create `.fab0/fab0.yaml` in the repository:

```yaml
schema: 2
repos:
  home: {path: ., github: acme/product, owner: maintainer}
people:
  maintainer: {github: [po-user]}
tracker: {kind: github, owner: acme}
store: {github: acme/product-runs}
models:
  claude-code: {deep: opus, balanced: sonnet, fast: haiku}
pipelines: [release-notes]
```

- `repos` names the repositories the factory works in. `home` is this one, and `owner` is the role whose turn its human gates are.
- `people` maps each role to GitHub users. Put your own login in place of `po-user`.
- `store` names the runs repository. Each run's ledger, the record of every attempt and gate decision, goes there, so this repository receives only the notes.
- `models` maps model classes to models, so steps ask for `balanced`, not a model name.

## 2. Describe the artifacts

Steps read and write artifacts. This factory has three: the request, which is the issue's body; the notes file the agent writes; and the reviews on the notes' pull request, so the agent sees what the maintainer asks for.

`.fab0/artifacts/request.yaml`:

```yaml
artifact: request
kind: issue
issue: {part: body}
```

`.fab0/artifacts/notes.yaml`:

```yaml
artifact: notes
kind: file
file: {repo: home, path: "docs/releases/{run}.md", format: markdown}
verify:
  - sections: [Highlights, Changes, Upgrade notes]
```

`verify` makes the engine check that the agent wrote those three sections before the work goes to review.

`.fab0/artifacts/reviews.yaml`:

```yaml
artifact: reviews
kind: pr
pr: {of: unit, part: reviews}
```

## 3. Write the agent

An agent is a plain Claude Code agent. It describes its craft; fab0's brief tells it what to read, where to write and how to reply. Create `.claude/agents/notes-writer.md`:

```markdown
---
name: notes-writer
description: Writes release notes for one release from a request that names the release and what it contains.
tools: Read, Grep, Glob, Write, Edit
---

You write the release notes for one release.

Read the request, then the commits and pull requests it points to. Write the notes in three sections, Highlights, Changes and Upgrade notes, for the people who use the product, not for its developers.

Change only the file your brief tells you to write. If something can't be decided from what you can read, ask in `questions`.

Reply exactly as your brief's Reply section says.
```

## 4. Describe the step

`.fab0/steps/draft.yaml`:

```yaml
step: draft
agent: notes-writer
model: balanced
inputs: [request, reviews]
outputs: [notes]
repos: {write: [home], read: [home]}
paths: ["docs/releases/{run}.md"]
return: {questions: optional}
```

`paths` is the step's claim: the agent may change that file and nothing else. `reviews` as an input sends the step back to its agent when the maintainer leaves a review. `return` lets the agent ask questions instead of guessing.

## 5. Describe the pipeline

`.fab0/pipelines/release-notes.yaml`:

```yaml
pipeline: release-notes
trigger: {issue: {label: release-notes}}
onStart:
  - git.run-branch
  - pr.open-run: {draft: true}
steps:
  - step: draft
    gate: {human: {owner: maintainer}}
onEnd:
  - git.sync-base
  - pr.ready
```

- The trigger makes every issue labelled `release-notes` a run, with the issue's number as its id.
- `onStart` creates the run branch. `pr.open-run` opens the run's pull request into `main`, as a draft, once the run branch has work: GitHub opens no pull request without a change.
- The `draft` step's gate is human: the maintainer reviews the notes' pull request into the run branch, and merging it accepts them.
- `onEnd` brings `main` into the run branch and makes sure the run's pull request is open and ready, for the maintainer to merge.

## 6. Validate

From the repository's root:

```bash
fab0-resolve validate
```

It prints `"ok": true`, or every problem with its file. It also checks that the runs repository can be reached. Fix them, then commit `.fab0/` and `.claude/` and push them to `main`.

## 7. Run it

1. Open an issue that says what the release contains, and label it `release-notes`, for example `#7`.
2. In Claude Code, run `/fab0:run #7`. The run takes its id from the runs repository, for example `1`, and says it on the issue. The run's branch, `fab0/1/base`, is created, the agent writes the notes, and their pull request opens against the run branch. The run then waits for you.
3. Review the notes' pull request. To ask for changes, leave a review and run `/fab0:run` again; with only this run open, it needs no argument, and the agent revises the notes from your review. Merge the pull request to accept them.
4. Run `/fab0:run` once more. The run branch now has the notes, so the run's pull request opens, and `onEnd` marks it ready. Merge it into `main`.

`fab0-resolve status 1` shows every unit's state, and where the run is, at any point, and `/fab0:inbox` shows what waits on whom. With [the watch](watch-a-run.md) on, you don't type `/fab0:run` again: the session goes on after your review by itself.

## Next steps

- Add a reviewer agent as an [auto gate](../explanation/gates.md#auto-gates), so notes reach you already reviewed.
- Split larger work with [`foreach`](../explanation/pipelines.md#operators), as the `story` example does.
- Look up any field in the [reference](../index.md#reference).
