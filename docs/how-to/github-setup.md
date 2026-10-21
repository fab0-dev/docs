# Set up GitHub

This guide prepares GitHub for a factory: the login, the issue types and labels its pipelines use, the run tracker, the runs repository, the rulesets on your branches, and an optional board. Claude Code can check all of it for you: ask it to set up GitHub for fab0, and the `fab0:github` skill goes through these steps. It creates the runs repository when you ask, and says what an organisation owner still has to do.

## 1. Log in

Everyone who runs fab0 needs `gh` logged in:

```bash
gh auth status
```

A board needs the `project` scope:

```bash
gh auth refresh -s project
```

## 2. Issue types and labels for your items

Triggers such as `{issue: {type: Story}}`, and `tracker.child.sync` with `type: Task`, name issue types. Issue types belong to the organisation, and only an organisation owner creates them, in the organisation's settings under issue types. `apply` doesn't create an item without its type.

List the labels your factory uses: in triggers, `tracker.label` actions, and human gates with `via: label`. Create the missing ones:

```bash
gh label list --repo acme/shop
```

```bash
gh label create needs-triage --repo acme/shop
```

A label made from data, such as `severity-{classify.severity}`, needs one label per value.

## 3. The run tracker

Each run is an issue of type `Pipeline Run`, with an issue of type `Pipeline Step` under it for each of its steps, in the runs repository. Their fields carry the run's state from step to step, and between factories. See [the run tracker](../reference/tracker.md).

Issue types and issue fields belong to an organisation, so the runs repository must be owned by one. An organisation owner sets them up once, in the organisation's settings, for every factory of the organisation:

1. Add two issue types: `Pipeline Run` and `Pipeline Step`.
2. Add eight issue fields, with these data types:

   | Field | Data type | Enable it on |
   |---|---|---|
   | `Run ID` | text | `Pipeline Run`, `Pipeline Step` |
   | `Stage` | single select, with the options `Todo`, `In Progress` and `Done` | `Pipeline Run`, `Pipeline Step` |
   | `Pipeline` | text | `Pipeline Run` |
   | `Factory` | text | `Pipeline Run` |
   | `Step` | text | `Pipeline Run`, `Pipeline Step` |
   | `Waiting on` | text | `Pipeline Run`, `Pipeline Step` |
   | `Revision` | number | `Pipeline Step` |
   | `Output` | text | `Pipeline Step` |

   The lifecycle field is called `Stage` because GitHub reserves the name Status.
3. Enable (pin) each field on the issue types the table names. GitHub shows a field that isn't pinned to a type only on demand, so `validate` warns about it.

These names are the defaults. If your organisation needs others, name them in `tracking.types`, `tracking.fields` and `tracking.status` in `fab0.yaml`; see the [project reference](../reference/project.md). `Stage` may have more options than these three.

`validate` reads the organisation's settings. It refuses the wiring while a type or a field is missing, a field has another data type, or `Stage` lacks an option, for example:

```text
tracking: no issue type 'Pipeline Run' in acme (tracking.types.run)
tracking: the issue field 'Revision' is text, and tracking.fields.revision needs number
```

When it can't read the organisation, because `gh` isn't logged in or there is no network, it warns that the tracker isn't checked, and goes on.

## 4. The runs repository

The runs repository holds the run tracker's issues of every run, and the files runs produce for themselves, such as the `story` example's specs and task lists. Your product repositories then receive only product changes. Every factory of a product shares one runs repository: a root run's id is its Pipeline Run's number, which is unique in that repository, and a call's child run is a sub-issue of its parent's run. If the product has one already, only name it in `fab0.yaml` and check it: items 4 and 5 below.

1. Create it:

   ```bash
   gh repo create acme/shop-runs --private --description "fab0 runs"
   ```

   Private keeps the runs' specs and records to the project's people. GitHub allows the rulesets of [the next section](#5-rulesets) on a private repository only on a paid plan; on a free plan, make it public (`--public`) to keep them.

2. Give write access to everyone in `people`, one login or a team at a time:

   ```bash
   gh api -X PUT repos/acme/shop-runs/collaborators/po-user -f permission=push
   ```

   Everyone who runs fab0 writes there with their own `gh` login: issues, comments, branches and pull requests. fab0 reads a step's facts only from comments by the repository's owner, its members and its collaborators, since anyone may comment on a public repository. The owner of a human gate also reviews its pull requests there.

3. Check it out beside your home checkout, as you do every other repository the factory writes:

   ```bash
   gh repo clone acme/shop-runs ../shop-runs
   ```

4. Name it in `fab0.yaml` twice: as an entry of `repos`, where the factory keeps files, and in `tracking`, where the run tracker's issues are:

   ```yaml
   repos:
     home: {path: ., github: acme/shop, owner: product-owner}
     runs: {path: ../shop-runs, github: acme/shop-runs}
   tracking: {kind: github, github: acme/shop-runs}
   ```

   A factory that keeps no files there, such as the `triage` example, names it only in `tracking`. Factories that keep files there and share a run id, a parent and its children, name their branches apart; see [connect a factory](connect-a-factory.md).

5. Check the wiring:

   ```bash
   fab0-resolve validate
   ```

   It prints `"ok": true`, with the run tracker's repository and types under `tracking`, or every problem with its file.

## 5. Rulesets

Add a ruleset to `main` in each repository a run writes, the runs repository too, that requires a pull request and blocks force pushes and deletion. In your product repositories, add your tests as required checks. Write it to `ruleset.json`:

```json
{"name": "main", "target": "branch", "enforcement": "active",
 "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
 "rules": [{"type": "deletion"}, {"type": "non_fast_forward"},
           {"type": "pull_request", "parameters": {
             "required_approving_review_count": 0, "dismiss_stale_reviews_on_push": false,
             "require_code_owner_review": false, "require_last_push_approval": false,
             "required_review_thread_resolution": false}}]}
```

```bash
gh api repos/acme/shop-runs/rulesets -X POST --input ruleset.json
```

- **`main` requires a pull request.** A run reaches `main` only through its run pull request. A pipeline that ends with `pr.merge` merges each run pull request through GitHub once its required checks pass, so the ruleset and its checks apply to fab0's merge as to a person's. `pr.merge` merges with a merge commit, so allow merge commits. A ruleset that also asks for an approving review refuses that merge until someone approves.
- **Run branches stay unprotected:** `fab0/**`, or the names your `git.branches` gives them. `apply` merges accepted units into the run branch by pushing a merge commit, which a pull request rule would refuse.
- **Checks on run branches.** If your CI runs on pull requests into any branch, unit pull requests show their checks, and agents and people can read them. Under an `auto` gate, `apply` waits for a unit's required checks before it merges; on unprotected run branches no check is required, so it doesn't wait. The base branch's required checks still gate the run's pull request.

A pipeline with `branching: flat` has no run branch: `apply` pushes its merges into `main`, which this ruleset refuses. See [choose how a pipeline uses git](choose-git-workflow.md).

## 6. A board (optional)

To see each item's state on a GitHub Project:

1. Add a text field to the project, for example `fab0`.
2. Name it in `fab0.yaml`:

   ```yaml
   tracker: {kind: github, owner: acme, project: 7, fields: {signal: fab0}}
   ```

Every field named in `tracker.fields` must exist on the project. A single-select field needs an option for every value an action sets: `apply` doesn't create options. fab0 never writes the project's Status, which the project's own workflows own.

## 7. Sub-issues and relations

Sub-issues and blocked-by relations need nothing beyond issues being enabled. fab0 reads them on every call; see [dependencies and blocking](../explanation/dependencies.md).
