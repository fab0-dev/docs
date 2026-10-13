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

## Checks

They need only [`uv`](https://docs.astral.sh/uv/):

```bash
uvx pymarkdownlnt scan -r docs README.md CONTRIBUTING.md
```

```bash
uvx codespell
```

CI runs both on every pull request, and checks links with lychee: offline on every pull request, and the full check weekly.
