# Use an example

This guide sets up a project with a factory from [`fab0-dev/fab0-examples`](https://github.com/fab0-dev/fab0-examples). Each example's README has its own details; this page gives the steps they share. For what the examples are, see [examples](../explanation/examples.md).

## 1. Choose an example

| Example | Use it for |
|---|---|
| `story` | Delivering a Story as a spec, then parallel tasks that agents implement, review and merge into the run branch |
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

Keep the line in each copied file that names the example and its release, such as `# from fab0-dev/fab0-examples story--v0.2.0`, so you can compare with a later release.

## 3. Make it yours

Edit `.fab0/fab0.yaml` where it says `EDIT`:

- `repos`: this repository as `home`, and every sibling repository the factory may change, each with its GitHub name and the role that owns it;
- `people`: the GitHub users in each role;
- `tracker`: the organisation or user that owns the issues, and a GitHub Project if you want a board.

Change anything else you like: the agents, the formats, the gates. The files are yours.

## 4. Set up GitHub

Create the issue types, labels and board fields the example uses, and protect the base branch. See [set up GitHub](github-setup.md).

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

   It must print `"ok": true`.

Commit `.fab0/` and `.claude/`, and push them to the base branch.

### Update the plugin

To move to a newer fab0 release, update the plugin, then start a new Claude Code session:

```bash
claude plugin update fab0@fab0 --scope project
```

A session that was open during the update, or a new one that still has an older cached version first on the `PATH`, runs the older engine. The engine compares its release with the plugin release Claude Code has installed for the project. When it is older, it stops before it does any work. `/fab0:run` and `/fab0:inbox` show the refusal and stop: nothing is fetched, applied, handed out or shown. The message says:

- the engine's release and path, and the installed release and path;
- a `fix` list: for each orphaned cached version directory, a line like `remove the cached version <dir>, which no install uses` (a version directory beside the installed one that no install record uses), then `start a new Claude Code session, so that it puts the installed version's engine first on the PATH`.

To fix it, remove the directories the message names, and start a new Claude Code session. The engine never removes them itself. If the message names no directory, only start a new session. Then run the command again.

An engine newer than the installed plugin, for example one run from a development checkout, runs as usual. If Claude Code's install record can't be read as JSON, or the installed or engine release isn't a dotted number such as `0.6.3`, the command runs and carries a warning that the engine's release couldn't be checked, and why.

## 6. Run it

Open an item the pipeline's trigger matches, for example an issue of type Story, and run `/fab0:run <issue number>`. The example's README describes what happens and where you take part.
