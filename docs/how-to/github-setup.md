# Set up GitHub

This guide prepares GitHub for a factory: the login, the issue types and labels its pipelines use, an optional board, and the base branch. Claude Code can check all of it for you: ask it to set up GitHub for fab0, and the `fab0:github` skill goes through these steps.

## 1. Log in

Everyone who runs fab0 needs `gh` logged in:

```bash
gh auth status
```

A board needs the `project` scope:

```bash
gh auth refresh -s project
```

## 2. Issue types

Triggers such as `{issue: {type: Story}}`, and `tracker.child.sync` with `type: Task`, name issue types. Issue types belong to the organisation, and only an organisation owner creates them, in the organisation's settings under issue types. `apply` doesn't create an item without its type.

## 3. Labels

List the labels your factory uses: in triggers, `tracker.label` actions, and human gates with `via: label`. Create the missing ones:

```bash
gh label list --repo acme/product
```

```bash
gh label create needs-triage --repo acme/product
```

A label made from data, such as `severity-{classify.severity}`, needs one label per value.

## 4. A board (optional)

To see each item's state on a GitHub Project:

1. Add a text field to the project, for example `fab0`.
2. Name it in `fab0.yaml`:

   ```yaml
   tracker: {kind: github, owner: acme, project: 7, fields: {signal: fab0}}
   ```

Every field named in `tracker.fields` must exist on the project. A single-select field needs an option for every value an action sets: `apply` doesn't create options. fab0 never writes Status, which the project's own workflows own.

## 5. The base branch

Protect the base branch with a ruleset that requires a pull request, with your tests as required checks. A run then reaches the base branch only through its run pull request, which a person merges.

Leave `fab0/**` branches unprotected: `apply` merges approved units into run branches by pushing a merge commit, which a protected branch would refuse. If your CI runs on pull requests into any branch, unit pull requests show their checks, and agents and people can read them. `apply` waits only for checks GitHub reports as required, so on unprotected run branches it doesn't wait. The base branch's required checks still gate the run's pull request.

## 6. Sub-issues and relations

Sub-issues and blocked-by relations need nothing beyond issues being enabled. fab0 reads them on every call; see [dependencies and blocking](../explanation/dependencies.md#dependencies-in-the-tracker).
