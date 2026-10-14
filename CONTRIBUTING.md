# Contributing to the fab0 docs

## Where a change starts

| You want to | Start with |
|---|---|
| Change how fab0 behaves | A Story in [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0). Its tasks include the docs change in this repository, so code and docs merge together |
| Fix or improve the docs on their own (an audit, a new guide, a restructure) | An issue of type **Docs** in this repository |
| Fix a typo | A pull request |

Every change reaches `main` through a reviewed pull request.

## What goes where

- **Explanation** (`docs/explanation/`): how fab0 works and why. Principles, design, trade-offs.
- **How-to** (`docs/how-to/`): steps for one task, for a reader who knows what they want.
- **Reference** (`docs/reference/`): the file formats and commands, field by field. The JSON Schemas and the resolver in [`fab0-core`](https://github.com/fab0-dev/fab0-core) are the source of truth; when they disagree with a page, the page is wrong.
- **Tutorials** (`docs/tutorials/`, not yet created): a guided first experience.

Write one kind of page per file. Link to the other kinds instead of mixing them.

## Style

- Plain, short sentences. Active voice. Present tense for what fab0 does.
- Say what is built. Mark what isn't: **Planned (step X)**, with the step from the [roadmap](https://github.com/fab0-dev/fab0/blob/main/ROADMAP.md).
- Use fab0's terms as the [glossary](docs/explanation/overview.md#glossary) defines them.
- Give a reason for every rule and principle.
- No counts or sizes that go stale.
- Write the examples with made-up names (`acme/product`, `po-user`).

## Running a Docs issue

> **Suspended.** This repository's fab0 pipeline is archived during the refactor and rebuilt on the new core in step R7 of [REFACTOR.md](https://github.com/fab0-dev/fab0/blob/main/REFACTOR.md). Until then, docs changes are ordinary pull requests. The rest of this section describes the 0.5 pipeline.

A Docs issue runs this repository's own fab0 pipeline (`.fab0/`):

| Stage | Who | What | Gate |
|---|---|---|---|
| `brief` | docs owner | `docs-planner` compares the docs with fab0's sources and writes `briefs/<run>.md` (findings, outline, acceptance checks) and `work/<run>/tasks.yaml` | merging the brief pull request |
| `plan` | anyone (action) | one Task sub-issue per page or section | — |
| `write` (per task) | docs owner | `docs-writer` writes the page | `docs-reviewer` on a different model, then merging the task pull request |
| `deliver` | anyone (action) | appends the delivered tasks to the brief, in a pull request that closes the issue | merging it |

The agents are in `.claude/agents/`. They share the project skill `.claude/skills/docs-style/`, which defines the page kinds, the style, the brief format and the review checklist. The planner also uses Anthropic's `doc-coauthoring` skill.

Findings that need a code change are filed as Stories in [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0).

**Setup,** once per clone:

1. Check out [`fab0`](https://github.com/fab0-dev/fab0), [`fab0-core`](https://github.com/fab0-dev/fab0-core) and [`fab0-recipes`](https://github.com/fab0-dev/fab0-recipes) beside this repository. The planner reads them as sources.
2. Open Claude Code here and trust the folder.
3. Install the two plugins this repository enables:

   ```bash
   claude plugin install fab0@fab0 --scope project
   ```

   ```bash
   claude plugin install example-skills@anthropic-agent-skills --scope project
   ```

   Keep the committed settings with `git checkout -- .claude/settings.json`.
4. Check the wiring:

   ```bash
   fab0-resolve validate
   ```

**Run:** open an issue of type Docs with the intent in its body, then `/fab0:run <issue number>`. `/fab0:inbox` shows what is waiting for you. Progress shows on the [fab0 docs board](https://github.com/orgs/fab0-dev/projects/2).

## Checks

They need only [`uv`](https://docs.astral.sh/uv/):

```bash
uvx pymarkdownlnt scan -r docs README.md CONTRIBUTING.md
```

```bash
uvx codespell
```

CI runs both on every pull request, and checks links with lychee: offline on every pull request, and the full check weekly.
