# Set up GitHub

This guide prepares GitHub for a factory: the login, the issue types and labels its pipelines use, an optional board, the base branch, and the runs repository. Claude Code can check all of it for you: ask it to set up GitHub for fab0, and the `fab0:github` skill goes through these steps.

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

Protect the base branch with a ruleset that requires a pull request, with your tests as required checks. A run then reaches the base branch only through its run pull request, which a person merges, or `apply` when the factory's merge policy allows the base branch; see [who merges](../explanation/gates.md#who-merges). A ruleset that asks for a person's review refuses `apply`'s merge, so a factory that lets `apply` merge into the base branch keeps the ruleset to required checks.

Leave `fab0/**` branches unprotected: `apply` merges approved units into run branches by pushing a merge commit, which a protected branch would refuse. If your CI runs on pull requests into any branch, unit pull requests show their checks, and agents and people can read them. `apply` waits only for checks GitHub reports as required, so on unprotected run branches it doesn't wait. The base branch's required checks still gate the run's pull request.

## 6. The runs repository

The runs repository holds what runs produce for themselves: each run's ledger, its working files, and the review pull requests of units whose outputs are all in the run store. `store.github` in `fab0.yaml` names it. Your product repositories then receive only product changes.

One runs repository serves every factory of a product. Each factory keeps its runs under its own `store.project`, which defaults to the home repository's name, so their run numbers don't collide. If the product has one already, only name it in `fab0.yaml` and check it: steps 4 and 5 below.

1. Create it:

   ```bash
   gh repo create acme/product-runs --private --description "fab0 run store"
   ```

   An empty repository is fine: the first record starts `main`. GitHub allows the ruleset of the next step on a private repository only on a paid plan. On a free plan, make the runs repository public (`--public`) to keep the ruleset. A public one holds nothing your public product repositories don't. Keep it private without a ruleset only if the runs must stay private, since then nothing stops a person's force push.

2. Add a ruleset that blocks force pushes to `main` and its deletion, so the store's history stays append-only. Write it to `ruleset.json`:

   ```json
   {"name": "fab0 run store", "target": "branch", "enforcement": "active",
    "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
    "rules": [{"type": "deletion"}, {"type": "non_fast_forward"}]}
   ```

   ```bash
   gh api repos/acme/product-runs/rulesets -X POST --input ruleset.json
   ```

   Don't require pull requests or checks on it: the engine pushes to `main` directly.

3. Give write access to everyone in `people`, one login or a team at a time:

   ```bash
   gh api -X PUT repos/acme/product-runs/collaborators/po-user -f permission=push
   ```

   Everyone who runs fab0 pushes there with their own `gh` login, so each record names who made it. The owner of a human gate approves its review pull requests there with an approving review, or with a comment `/approve` on one they opened, and only an approval by someone in that role approves the unit. fab0 then records the decision and merges the pull request, so nobody merges or pushes there by hand, and the ruleset on its `main` needs no required review.

4. Name it in `fab0.yaml`:

   ```yaml
   store: {github: acme/product-runs}
   ```

5. Check that it can be reached:

   ```bash
   fab0-resolve validate
   ```

   `validate` reads the runs repository with `git ls-remote`, and refuses the wiring when it can't.

The `fab0:github` skill checks all of this, and creates the runs repository when you ask.

## 7. Sub-issues and relations

Sub-issues and blocked-by relations need nothing beyond issues being enabled. fab0 reads them on every call; see [dependencies and blocking](../explanation/dependencies.md#dependencies-in-the-tracker).
