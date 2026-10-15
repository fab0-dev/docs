"""Check that the reference pages match fab0's schema files, both ways:

- every property a schema file defines appears on its page, in code format;
- every field a page lists in a table whose first column is "Field" is a property of one of its schema files.

The schemas are read from a fab0-core checkout: $FAB0_CORE, else `../fab0-core` beside this repository.
Standard library only.

    python3 scripts/check-reference.py
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = Path(os.environ.get("FAB0_CORE", ROOT.parent / "fab0-core"))
SCHEMAS = CORE / "plugins" / "fab0" / "schemas"
PAGES = {
    "project.md": ["project.json"],
    "pipeline.md": ["pipeline.json"],
    "step.md": ["step.json"],
    "artifact.md": ["artifact.json"],
    "returns-and-verdicts.md": ["return.json", "verdict.json"],
    "ledger.md": ["ledger-entry.json"],
}


def properties(node) -> set[str]:
    """Every property name defined anywhere in a schema."""
    found = set()
    if isinstance(node, dict):
        for key, value in node.items():
            # `extensions` in return.json holds properties the engine adds when a step asks for them
            if key in ("properties", "extensions") and isinstance(value, dict):
                found |= set(value)
            found |= properties(value)
    elif isinstance(node, list):
        for item in node:
            found |= properties(item)
    return found


def code_words(text: str) -> set[str]:
    """Every word inside a code span: `git.auto_merge.into` gives git, auto_merge, into."""
    words = set()
    for span in re.findall(r"`([^`\n]+)`", text):
        words |= set(re.findall(r"[A-Za-z_$][A-Za-z0-9_-]*", span))
    return words


def table_fields(text: str) -> list[str]:
    """The first-column fields of every table whose header's first cell is Field."""
    fields, in_table = [], False
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else None
        if cells is None:
            in_table = False
            continue
        if cells[0] == "Field":
            in_table = True
            continue
        if in_table and not set(cells[0]) <= set("-: "):
            span = re.match(r"`([^`]+)`", cells[0])
            if span:
                fields.append(span.group(1))
    return fields


def main() -> int:
    if not SCHEMAS.is_dir():
        sys.exit(f"no schemas at {SCHEMAS}: check out fab0-core beside this repository, or set FAB0_CORE")
    problems = []
    for page, schema_files in PAGES.items():
        path = ROOT / "docs" / "reference" / page
        text = path.read_text()
        defined = set()
        for name in schema_files:
            defined |= properties(json.loads((SCHEMAS / name).read_text()))
        missing = sorted(defined - code_words(text))
        if missing:
            problems.append(f"{page}: not documented: {', '.join(missing)}")
        for field in table_fields(text):
            last = re.split(r"[.\s]", field.replace("[]", ""))[-1].strip("`")
            if last and last not in defined:
                problems.append(f"{page}: `{field}` is no field of {', '.join(schema_files)}")
    for p in problems:
        print(p)
    print(f"{len(problems)} problems" if problems else f"every field of {len(PAGES)} pages matches its schema")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
