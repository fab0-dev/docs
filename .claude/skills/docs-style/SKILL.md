---
name: docs-style
description: How the fab0 docs are structured, written and reviewed — the four Diátaxis page kinds, the writing style, fab0's vocabulary and status markers, the brief format of a Docs run, and the review checklist. Use when planning, writing or reviewing any page under docs/, or the brief of a Docs run.
---

# fab0 docs style

The fab0 docs describe fab0 as it is built, and say plainly what is not built yet. A reader should be able to trust every sentence without opening the code.

## Sources of truth

- **Behaviour and formats:** the `core` repository: `plugins/fab0/schemas/*.json`, the engine in `plugins/fab0/lib/fab0_engine/`, and the skills in `plugins/fab0/skills/`.
- **Examples:** the `examples` repository: each example's `.fab0/`, agents, skills and README.
- **Principles, decisions and what is planned:** the `product` repository: `CLAUDE.md`, `ROADMAP.md` and `DECISIONS.md`.

When a page and a source disagree, the page is wrong. Never describe behaviour you haven't found in a source. `scripts/check-reference.py` also checks the reference pages field by field against the schemas, both ways.

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
- A reference page's field tables have `Field` as the first column, one field per row in code format, so the field check can read them.

## Writing

- **Plain and short.** One idea per sentence. Cut words that carry nothing ("simply", "just", "in order to", "it should be noted").
- **Active voice, present tense** for what fab0 does: "`record` writes the attempt on its Pipeline Step", not "the attempt will be written".
- **Second person** in how-to and tutorial steps: "Run `fab0-resolve validate`."
- **Headings** in sentence case. No heading that only repeats the page title.
- **Lists** for three or more parallel items, steps as numbered lists, tables for anything with two or more attributes per item.
- **Code formatting** for commands, file names, paths, field names, values and issue types used as values: `fab0.yaml`, `gate: human`, `--unit`.
- **Link text** says where it goes: "see [gates](…)", never "click here".
- **Examples** use made-up names: `acme/product`, `po-user`, `be-user`, Story `#412`.
- **A reason for every rule.** A rule or principle without its reason is a preference.
- **No counts or sizes that go stale** (line counts, numbers of tests, "currently 3 agents").
- Style follows the Google developer documentation style guide (developers.google.com/style, CC BY 4.0) where this skill says nothing.

## fab0's vocabulary

Use the glossary in `docs/explanation/overview.md` exactly. In particular:

- **factory**, **run**, **run id**, **step**, **unit**, **attempt**, **gate**, **artifact**, **action**, **hand-out**, **brief**, **run tracker**, **Pipeline Run**, **Pipeline Step**, **claim**, **example**, **home repo**: as defined there.
- **pull request** in prose (not "PR"); "the run's pull request" and "a unit's pull request".
- **repository** in prose; "repo" only in fixed terms (home repo) and in field names.
- **merge**: `apply` merges what a step's gate and `done` leave to it, and a person merges where they leave it to a person. Nothing else merges.
- Say **Story**, **Task**, **Docs** with a capital when they name an issue type.

## Status markers

| Marker | Use |
|---|---|
| none | built |
| **Planned** | designed, not built. Say what exists today, if anything, and what `validate` does with it |

Anything the engine or `validate` refuses as not built yet is Planned.

## The brief of a Docs run

The `brief` step writes the brief, `brief.md` where its hand-out says (a file of the runs repository, reviewed in its pull request there), with exactly these sections, in this order:

1. **Intent**: what the issue asks for, in two or three sentences of your own.
2. **Readers**: who reads the result, what they already know, and what they are trying to do.
3. **Sources**: the files that are the truth for this work, each as `repo:path@<short sha>`.
4. **Findings**: what you found when you compared the docs with the sources. One numbered finding each (`F1`, `F2`, …): what the page says, what the source says, `path:line@sha` for both, and whether a docs task fixes it or it needs a code change (`code`). Write "None" for a run that adds new material only.
5. **Outline**: the pages to add or change, each with its Diátaxis kind and the headings it will have.
6. **Acceptance**: numbered checks (`A1`, `A2`, …), each a question a reader must be able to answer from the changed pages alone, or a fact that must hold ("every field in `step.json` appears in reference/step.md"). Tasks list the ids they meet.
7. **Open questions**: decisions only the docs owner can make. Write "None" when there are none.

The task list (`tasks.yaml`, kept beside the brief) splits the outline into tasks of one page or one section each, as `.fab0/schemas/tasks.json` says: `id`, `title`, `repo: home`, the `files` the task changes, `depends_on` where one page must exist before another links to it, and `acceptance`, the ids it meets. Tasks that may run in parallel touch disjoint files. Every acceptance id is met by at least one task.

## Review checklist

A reviewer of a docs change checks, in order:

1. **Truth.** Every claim matches its source at the pinned commit. Open the source; don't trust the writer's summary. An unverifiable claim is a finding.
2. **Acceptance.** Each acceptance id the task lists is met. A reader test: with only the changed pages, can you answer each acceptance question? Put the ids that aren't met in the verdict's `details.unmet`.
3. **Kind.** The page is one Diátaxis kind and passes that kind's test.
4. **Status.** Planned things are marked, built things aren't.
5. **Scope.** Only the task's files changed (`git diff --name-only`).
6. **Style and vocabulary** as above. Report only what a reader would notice; leave out matters of taste.
7. **Checks.** `uvx pymarkdownlnt scan -r docs README.md CONTRIBUTING.md`, `uvx codespell` and `python3 scripts/check-reference.py` pass, and every relative link resolves.
