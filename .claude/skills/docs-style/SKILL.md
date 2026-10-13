---
name: docs-style
description: How the fab0 docs are structured, written and reviewed — the four Diátaxis page kinds, the writing style, fab0's vocabulary and status markers, the brief format of a Docs run, and the review checklist. Use when planning, writing or reviewing any page under docs/ or a brief under briefs/.
---

# fab0 docs style

The fab0 docs describe fab0 **as it is in the latest release** of the core plugin, and say plainly what is not built yet. A reader should be able to trust every sentence without opening the code.

## Sources of truth

- **Behaviour and formats:** the core plugin in the `core` repository: `plugins/fab0/schemas/*.json`, `plugins/fab0/bin/fab0-resolve`, `plugins/fab0/skills/*/SKILL.md`, `plugins/fab0/agents/*.md`.
- **Recipes:** the `recipes` repository.
- **What is planned and why:** `ROADMAP.md` and `specs/` in the `product` repository.

When a page and a source disagree, the page is wrong. Never describe behaviour you haven't found in a source.

## Page kinds (Diátaxis)

Every page is exactly one kind. Decide the kind before writing, from what the reader is doing.

| Kind | Folder | The reader | The page | Test |
|---|---|---|---|---|
| Tutorial | `docs/tutorials/` | is learning, with no goal of their own yet | takes them through one complete, safe exercise that works | Could a newcomer follow it start to finish without choosing anything? |
| How-to | `docs/how-to/` | has a goal and knows the basics | gives the steps for that goal, nothing else | Does every paragraph move the reader toward the goal? |
| Reference | `docs/reference/` | is looking something up | describes the thing completely and neutrally, in the order of the thing itself | Could it be checked line by line against the schema or code? |
| Explanation | `docs/explanation/` | wants to understand | gives the reasons, trade-offs and connections | Does it answer "why", not "how do I"? |

- Don't mix kinds. Put the other kind on its own page and link to it.
- Grow the structure from content: don't create an empty folder or a page with no real content.
- `docs/index.md` lists every page under its kind. Add each new page there.

## Writing

- **Plain and short.** One idea per sentence. Cut words that carry nothing ("simply", "just", "in order to", "it should be noted").
- **Active voice, present tense** for what fab0 does: "The resolver writes the ledger entry", not "the ledger entry will be written".
- **Second person** in how-to and tutorial steps: "Run `fab0-resolve validate`."
- **Headings** in sentence case. No heading that only repeats the page title.
- **Lists** for three or more parallel items, steps as numbered lists, tables for anything with two or more attributes per item.
- **Code formatting** for commands, file names, paths, field names, values and issue types used as values: `fab0.yaml`, `gate: human`, `--task`.
- **Link text** says where it goes: "see [gates and handoff](…)", never "click here".
- **Examples** use made-up names: `acme/product`, `po-user`, `backend-dev`, Story `#412`.
- **A reason for every rule.** A rule or principle without its reason is a preference.
- **No counts or sizes that go stale** (line counts, numbers of tests, "currently 3 agents").
- Style follows the Google developer documentation style guide (developers.google.com/style, CC BY 4.0) where this skill says nothing.

## fab0's vocabulary

Use the glossary in `docs/explanation/overview.md` exactly. In particular:

- **run**, **run id**, **stage**, **action**, **task**, **attempt**, **gate**, **ledger**, **recipe**, **home repo**: as defined there.
- **pull request** in prose (not "PR"); "stage pull request" for the pull request of a stage branch.
- **repository** in prose; "repo" only in fixed terms (home repo) and in field names.
- **merge** means a person merging a pull request. fab0 never merges.
- Say **Story**, **Task**, **Docs** with a capital when they name an issue type.

## Status markers

| Marker | Use |
|---|---|
| none | built and in the latest release |
| **Planned (step X)** | designed, not built; X is the step in `ROADMAP.md`. Say what exists today, if anything |
| **Since 0.x** | a feature added after the first public release, on the line that introduces it |

Anything the resolver refuses as "not supported yet" is Planned.

## The brief of a Docs run

The `brief` stage writes `briefs/{run}.md` with exactly these sections, in this order:

1. **Intent**: what the issue asks for, in two or three sentences of your own.
2. **Readers**: who reads the result, what they already know, and what they are trying to do.
3. **Sources**: the files that are the truth for this work, each as `repo:path@<short sha>`.
4. **Findings**: what you found when you compared the docs with the sources. One numbered finding each (`F1`, `F2`, …): what the page says, what the source says, `path:line@sha` for both, and whether a docs task fixes it or it needs a code change (`code`). Write "None" for a run that adds new material only.
5. **Outline**: the pages to add or change, each with its Diátaxis kind and the headings it will have.
6. **Acceptance**: numbered checks (`A1`, `A2`, …), each a question a reader must be able to answer from the changed pages alone, or a fact that must hold ("every field in `stage.json` appears in reference/wiring.md"). Tasks trace to these ids.
7. **Open questions**: decisions only the docs owner can make. Write "None" when there are none.

The task list (`tasks.yaml`) splits the outline into tasks of one page or one section each: `repo: home`, the files the task changes, `depends_on` where one page must exist before another links to it, and `traces_to` the acceptance ids. Tasks that may run in parallel touch disjoint files.

## Review checklist

A reviewer of a docs change checks, in order:

1. **Truth.** Every claim matches its source at the pinned commit. Open the source; don't trust the writer's summary. An unverifiable claim is a finding.
2. **Acceptance.** Each acceptance id the task traces to is met. A reader test: with only the changed pages, can you answer each acceptance question? An unmet id goes in `unmet`.
3. **Kind.** The page is one Diátaxis kind and passes that kind's test.
4. **Status.** Planned things are marked, built things aren't.
5. **Scope.** Only the task's files changed (`git diff --name-only`).
6. **Style and vocabulary** as above. Report only what a reader would notice; leave out matters of taste.
7. **Checks.** `uvx pymarkdownlnt scan -r docs README.md CONTRIBUTING.md` and `uvx codespell` pass, and every relative link resolves.
