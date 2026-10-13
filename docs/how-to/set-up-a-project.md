# Set up a project

This page takes a project from nothing to its first `/fab0:run`. The step-by-step commands live in the recipe's README, which is versioned with the recipe. This page explains what each step is for.

## Before you start

- [`uv`](https://docs.astral.sh/uv/): the resolver runs on it.
- [`gh`](https://cli.github.com/), logged in with the `project` scope: `gh auth refresh -s project`.
- Claude Code.
- The project's repositories, checked out side by side under one parent directory.

## 1. Choose a recipe and copy it

A recipe is a complete, working set of `.fab0/` files for one way of working. Recipes live in [`fab0-dev/fab0-recipes`](https://github.com/fab0-dev/fab0-recipes). Today there is one, [`story`](https://github.com/fab0-dev/fab0-recipes/tree/main/story): one spec drives tasks in one or more repositories.

Copy the recipe into the home repo and edit `fab0.yaml` for your repositories, people and board. The [`story` README](https://github.com/fab0-dev/fab0-recipes/blob/main/story/README.md) gives the exact commands. Every field is in the [wiring reference](../reference/wiring.md).

**Recipes are copied in full, not referenced.**

- From then on the files are the project's own. The behaviour they point at (agents, skills, the resolver) moves with the plugin release.
- A recipe update reaches a project only when someone copies it again, so a plugin release can't change a project's pipeline without a commit in that project.
- The first line of each copied file names its source and release, for example `# from fab0-dev/fab0-recipes story--v0.1.0`, so a later comparison is easy.

## 2. Set up GitHub

Issue types, a Projects board with three fields, and branch protection. See [GitHub setup](github-setup.md).

## 3. Set up Claude Code

1. Merge the recipe's `claude-settings.json` into `.claude/settings.json`. It declares the `fab0` marketplace, enables the plugin, and denies merging, force pushes, pushes to `main` and edits under `.github/`.
2. Open Claude Code in the home repo and **trust the folder**. Claude Code applies a project's marketplaces only in a trusted folder, and ignores them silently otherwise.
3. Install the plugin for the repository once per clone: `claude plugin install fab0@fab0 --scope project`. Some clients, such as the desktop app, don't load a plugin that is enabled but not installed.
4. Restart open sessions; plugins load when a session starts.

## 4. Check the wiring

```bash
fab0-resolve validate
```

It must print `"ok": true`. The resolver refuses to run on invalid wiring. It checks the schemas, that every name resolves, that inputs come before the stages that read them, and that every agent is either `plugin:name` or a file in `.claude/agents/`.

What the resolver can't see is in the recipe README's checklist: the folder is trusted, the plugins are installed, the GitHub setup is done, and any linter commands your verifiers use are installed. If an agent is still missing at run time, the Agent tool call fails, and the orchestrator stops and names the stage.

## 5. First run

Open an issue of the pipeline's type (Story) with the intent in its body, then:

```text
/fab0:run <issue number>
```

What happens next is in [gates and handoff](../explanation/gates-and-handoff.md#a-story-from-start-to-done).
