# Set up GitHub for fab0

fab0 keeps human decisions on GitHub and shows progress on a GitHub Projects board (P3). This page lists what to set up, then what fab0 reads and writes there.

## Checklist

1. **Issue types** (organisation settings → Planning → Issue types): `Story` and `Task` for the `story` recipe. An organisation owner adds them. The `plan` action stops if a type is missing rather than create an untyped issue.
2. **A Project** with three custom fields. fab0 writes these and never Status:

   ```bash
   gh project field-create <number> --owner <owner> --name Stage --data-type SINGLE_SELECT --single-select-options "spec,plan,implement,deliver,done"
   ```

   ```bash
   gh project field-create <number> --owner <owner> --name Run --data-type TEXT
   ```

   ```bash
   gh project field-create <number> --owner <owner> --name "Waiting on" --data-type TEXT
   ```

   The Stage options are the stage names of your pipelines plus `done`. fab0 doesn't create missing options; it reports them.
3. **Built-in workflows** on the Project: item added → Todo, item closed → Done. Auto-add from your repositories is optional, because the orchestrator adds the items it works on.
4. **Views:**
   - My turn: assignee is `@me`, not done, grouped by Stage.
   - Board: open items grouped by Stage.
   - Waiting: `Waiting on` is set.
   - Hierarchy: Stories with sub-issue progress.
   - By repository.
5. **Branch protection** on the base branch of every repository in `fab0.yaml`: pull requests required, your linters and tests as required checks, and reviews as your team chooses.
6. **Access:** everyone who runs fab0 has `gh` logged in with the `project` scope. Runs use the person's own login; there is no GitHub App.
7. **`tracker:`** in `fab0.yaml` names the Project's owner and number, and the three fields.

## Where each fact lives

| Fact | Home | Written by | Read by the resolver |
|---|---|---|---|
| Intent | issue body | people | yes |
| Kind of item | issue type | people, actions | yes |
| Hierarchy and order | sub-issues, blocked-by | people, actions | yes |
| Artifacts and ledger | stage branch, then the base branch after the merge | stages, resolver | yes |
| Human approval and done | merge of the stage pull request | people | yes |
| Requested changes | pull request reviews | people | yes, as an input of the next attempt |
| Who has claimed a task | assignee | actions, `--take` | yes |
| Stage, run id, waiting reason | Project fields | orchestrator | no |
| Status | Project field | Project built-in workflows | no |
| Narrative for people | issue and pull request comments | orchestrator, people | no |

Who may run a stage comes from the roles in `fab0.yaml`, not from GitHub permissions.

## Issue types

A pipeline names the type it runs for (`item: {issue_type: Story}`), so the names are the project's choice. Each pipeline in a project needs a different type.

| Type | Runs | Created by | Parent |
|---|---|---|---|
| Story | the `story` pipeline | people | none, or a grouping issue |
| Task | nothing of its own: one element of `foreach: tasks` | the `plan` action | its Story |

Other types (Bug, Spike, …) are added when a run needs them (P8). A type that needs a spec runs its own pipeline, for example a copy of `story` with `item: {issue_type: Bug}`.

## Relations

| Relation | Between | Created by | Meaning to the resolver |
|---|---|---|---|
| Sub-issue | Story → Task | `plan` | hierarchy, and where `plan` looks for what it already created |
| Blocked-by | Task → Task, from `depends_on` in `tasks.yaml`; any pair set by people | `plan`, people | a blocked task isn't offered until its blockers are done |
| Pull request closes issue | task pull request → Task, deliver pull request → Story | orchestrator, `Closes` in the body | the merge is what counts; the close follows |
| Pull request refers to issue | any other stage pull request → its item | orchestrator, `Refs` in the body | none; a link for people |

An issue has at most one parent. Sub-issues can span repositories in one organisation, so progress bars work across repositories. fab0 uses no labels.

## Naming

| Thing | Form | Example |
|---|---|---|
| Story title | free | `Booking extension` |
| Task issue title | `[run task] title` | `[412 T1] Booking API extension` |
| Stage branch | `{stage}/{run}-{slug}` | `spec/412-booking-extension` |
| Task branch | `{stage}/{run}-{task}-{slug}` | `implement/412-T1-booking-api-extension` |
| Stage pull request title | `<Stage> #<run>: <item title>` | `Spec #412: Booking extension` |
| Task pull request title | `<Stage> <run> <task>: <task title>` | `Implement 412 T1: Booking API extension` |
| Deliver pull request title | `Deliver #<run>: <item title>` | `Deliver #412: Booking extension` |

The bracketed prefix of a task title is how `plan` finds its own issues, so don't edit it. A run id is the issue number and needs no prefix.

## Pull requests and notifications

- The orchestrator requests reviews from the users of the stage's owner role, so people get GitHub's usual e-mail and mobile notifications. fab0 adds no channel of its own.
- Clarification questions go in one comment on the stage pull request. Answers come as edits or as a review, never as comments read back.
- Each time a stage pull request opens or updates, the orchestrator posts one handoff comment on the item. It gives the stage, who ran it, the model, the verification results and the link.
- fab0 never merges. The project's `.claude/settings.json` denies `gh pr merge`, force pushes and pushes to `main`.
