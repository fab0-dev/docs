# fab0 docs

The user documentation of [fab0](https://github.com/fab0-dev/fab0), a toolkit for building and operating software factories.

> These pages describe fab0 0.6, released at the end of the refactor in [REFACTOR.md](https://github.com/fab0-dev/fab0/blob/main/REFACTOR.md).

**Start reading at [docs/index.md](docs/index.md).**

The docs are plain Markdown, read on GitHub. They follow [Diátaxis](https://diataxis.fr/):

- `docs/explanation/`: how fab0 works and why;
- `docs/how-to/`: guides for a task;
- `docs/reference/`: the file formats, actions and commands, checked field by field against the schemas by `scripts/check-reference.py`.

Tutorials come when the first one is written.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

- A change to fab0's behaviour updates these docs in the same Story, as a task in this repository.
- This repository runs its own fab0 factory, in `.fab0/`, for Docs issues.
- Work that starts from the docs (an audit, a new guide, a restructure) is an issue of type **Docs** here.

## Licence

[CC BY 4.0](LICENSE).
