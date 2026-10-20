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
- **Reference** (`docs/reference/`): the file formats, actions and commands, field by field. The JSON Schemas and the engine in [`fab0-core`](https://github.com/fab0-dev/fab0-core) are the source of truth; when they disagree with a page, the page is wrong. `scripts/check-reference.py` checks every field both ways.
- **Tutorials** (`docs/tutorials/`, not yet created): a guided first experience.

Write one kind of page per file. Link to the other kinds instead of mixing them.

## Style

- Plain, short sentences. Active voice. Present tense for what fab0 does.
- Say what is built. Mark what isn't as **Planned**, and say what exists today.
- Use fab0's terms as the [glossary](docs/explanation/overview.md#glossary) defines them.
- Give a reason for every rule and principle.
- No counts or sizes that go stale.
- Write the examples with made-up names (`acme/product`, `po-user`).

## Running a Docs issue

A Docs issue runs this repository's own fab0 factory (`.fab0/`) on its own branch, `fab0/<issue>/base`:

| Step | Who | What | Gate |
|---|---|---|---|
| start | `apply` | the run branch; its draft pull request into `main`, which closes the issue, opens once the first page is merged into it | — |
| `brief` | `docs-planner` | compares the docs with fab0's sources and writes the brief (findings, outline, acceptance checks) and its task list, which fab0 keeps in the run store, [`fab0-dev/fab0-runs`](https://github.com/fab0-dev/fab0-runs), under `runs/docs/<run>/` | **human**: the docs owner approves the brief's review pull request in `fab0-dev/fab0-runs`, and fab0 merges it |
| tasks | `apply` | one Task sub-issue per page or section | — |
| `write`, per task | `docs-writer` | writes the page, in parallel with tasks whose files don't overlap | **auto**: `docs-reviewer`, on a different model; on approval `apply` merges the page into the run branch |
| end | `apply` | closes the Task sub-issues, brings `main` in, marks the run's pull request ready | **human**: the docs owner merges it into `main` |

The agents are in `.claude/agents/`. They share the project skill `.claude/skills/docs-style/`, which defines the page kinds, the style, the brief format and the review checklist. The planner also uses Anthropic's `doc-coauthoring` skill. Ask for changes to a brief or a page with a review on its pull request; a Comment review is enough. You can also edit the brief on its review branch; your edit counts as your own version of it.

Findings that need a code change are filed as Stories in [`fab0-dev/fab0`](https://github.com/fab0-dev/fab0).

**Setup,** once per clone:

1. Check out [`fab0`](https://github.com/fab0-dev/fab0), [`fab0-core`](https://github.com/fab0-dev/fab0-core) and [`fab0-examples`](https://github.com/fab0-dev/fab0-examples) beside this repository. The planner reads them as sources, and `scripts/check-reference.py` reads the schemas from `fab0-core`.
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

**Run:** open an issue of type Docs with the intent in its body, then `/fab0:run #<issue number>`; after that, `/fab0:run` goes on with it. `/fab0:inbox` shows what is waiting for you. Each item's state shows in the `Waiting on` field of the [fab0 docs board](https://github.com/orgs/fab0-dev/projects/2).

## Checks

They need [`uv`](https://docs.astral.sh/uv/), and a `fab0-core` checkout beside this repository for the field check:

```bash
uvx pymarkdownlnt scan -r docs README.md CONTRIBUTING.md
```

```bash
uvx codespell
```

```bash
python3 scripts/check-reference.py
```

CI runs them on every pull request, and checks links with lychee: offline on every pull request, and the full check weekly.
