# Use an example

This guide sets up a project with a factory from [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples). Each example's README has its own details; this page gives the steps they share. For what the examples are, see [examples](../explanation/examples.md).

## 1. Choose an example

| Example | Use it for |
|---|---|
| `story` | Delivering a Story: a spec the product owner approves in a pull request of the runs repository, a task list they confirm at the prompt, then parallel tasks that agents implement, review and merge into the run branch, and the run merged into `main` once its checks pass |
| `feature` with `delivery` | A Feature's Stories built by several teams, each in its own repository with its own factory: `feature` in the product repository, a copy of `delivery` in each code repository. See [connect a factory](connect-a-factory.md) |
| `triage` | Work done in the tracker only, such as classifying bug reports |

## 2. Copy it

Check out `fab0-examples` beside your project. From your project's root, copy what the example's README lists, for example for `story`:

```bash
cp -R ../fab0-examples/story/.fab0 .fab0
```

```bash
mkdir -p .claude/agents .claude/skills .claude/hooks && cp ../fab0-examples/story/agents/*.md .claude/agents/ && cp -R ../fab0-examples/story/skills/spec-format .claude/skills/ && cp ../fab0-examples/story/hooks/merge-guard.py .claude/hooks/
```

Merge the example's `claude-settings.json` into `.claude/settings.json`, or copy it there in a new project. It declares the `fab0` marketplace, enables the plugin, denies merges and force pushes to the model, and installs the merge guard.

Keep the line in each copied file that names the example and its release, such as `# from fab0-dev/fab0-examples story--v0.5.0`, so you can compare with a later release.

## 3. Make it yours

The example's `.fab0/` names your organisation `OWNER` and your repository `REPO`, and `feature` and `delivery` name the shared runs repository `PRODUCT-runs`. Replace them everywhere in `.fab0/` with the one line the example's README gives, for example for `story` in `acme/shop`:

```bash
perl -pi -e 's/OWNER/acme/g; s/REPO/shop/g' $(grep -rlE 'OWNER|REPO' .fab0)
```

`REPO` is also the factory's name on the run tracker, and it keeps this factory's files apart from other factories' in the runs repository.

Then edit `.fab0/fab0.yaml` where it says `EDIT`:

- `repos`: this repository as `home`, and every sibling repository the factory may change, each with its GitHub name and the role that owns it;
- `repos.runs` and `tracking`: the runs repository, a sibling checkout too. It holds the run tracker's issues of every run, and working files such as the `story` example's spec and task list. If your product already has one for another factory, name the same repository;
- `people`: the GitHub users in each role;
- `tracker`: the organisation that owns the issues, and a GitHub Project if you want a board.

Change anything else you like: the agents, the formats, the gates and their `done`. The files are yours.

The `story` example keeps its spec in the runs repository, and reviews it in a pull request there. To keep it in your repository instead, follow [keep the specs in your repository](https://github.com/fab0-dev/fab0-examples/tree/main/story#keep-the-specs-in-your-repository) in the example's README.

## 4. Set up GitHub

Create the issue types and labels the example uses, the run tracker's issue types and fields, the runs repository if the product has none, and the rulesets on `main`. See [set up GitHub](github-setup.md).

## 5. Set up Claude Code

1. Install [`uv`](https://docs.astral.sh/uv/).
2. Open Claude Code in the project and trust the folder. Claude Code applies a project's marketplaces only in a trusted folder.
3. Install the plugin for this project, once per clone:

   ```bash
   claude plugin install fab0@fab0 --scope project
   ```

4. Check the wiring:

   ```bash
   fab0-resolve validate
   ```

   It must print `"ok": true`. It also checks the run tracker's issue types and fields.

Commit `.fab0/` and `.claude/`, and push them to the base branch.

### Update the plugin

To move to a newer fab0 release, update the plugin, then start a new Claude Code session:

```bash
claude plugin update fab0@fab0 --scope project
```

A release that changes the wiring says what to change: from 0.9, see [upgrade from 0.9](upgrade-from-0.9.md).

A session that was open during the update, or a new one that still has an older cached version first on the `PATH`, runs the older engine. The engine compares its release with the plugin release Claude Code has installed for the project. When it is older, it stops before it does any work. `/fab0:run` and `/fab0:inbox` show the refusal and stop: nothing is fetched, applied, handed out or shown. The message says:

- the engine's release and path, and the installed release and path;
- a `fix` list: for each orphaned cached version directory, a line like `remove the cached version <dir>, which no install uses` (a version directory beside the installed one that no install record uses), then `start a new Claude Code session, so that it puts the installed version's engine first on the PATH`.

To fix it, remove the directories the message names, and start a new Claude Code session. The engine never removes them itself. If the message names no directory, only start a new session. Then run the command again.

An engine newer than the installed plugin, for example one run from a development checkout, runs as usual. If Claude Code's install record can't be read as JSON, or the installed or engine release isn't a dotted number such as `0.10.0`, the command runs and carries a warning that the engine's release couldn't be checked, and why.

## 6. Run it

Open an item the pipeline's trigger matches, for example an issue of type Story, and run `/fab0:run #<issue number>`. The run's Pipeline Run opens in the runs repository, under the item, and its number is the run id; after that, `/fab0:run` alone goes on with it. See [start and continue a run](start-and-continue-a-run.md). The example's README describes what happens and where you take part.

With `story`, you take part twice:

- **The spec**, in its pull request in the runs repository. Ask for changes with a Comment review, or approve it with an approving review. The pull request was opened with the login of whoever ran the session, and GitHub doesn't let you approve your own: comment `/approve` instead. Only an approval by someone in `product-owner` approves the spec, and the next `/fab0:run` merges it: don't merge it yourself.
- **The task list**, at the prompt: the session asks you to confirm it, or to say what to change.

Everything else is agents and `apply`, the merge into `main` included. Follow the run on its issues; see [follow a run](follow-a-run.md).
