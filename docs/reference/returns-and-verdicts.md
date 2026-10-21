# Returns and verdicts

What agents reply with. A step's agent (or a tool step's session) replies with a **return**; an agent in an auto gate replies with a **verdict**. Each is one JSON object, and `record` checks it against its schema before anything is written. `record` then writes it, as the attempt's or the gate decision's comment on the unit's Pipeline Step: see [the run tracker](tracker.md). The schemas are `plugins/fab0/schemas/return.json` and `verdict.json` in [`fab0-core`](https://github.com/fab0-dev/fab0-core). The brief gives the agent the exact schema it must match.

## Return

```json
{
  "summary": "Added Hotel.extend with tests for S1 to S5; all tests pass.",
  "questions": []
}
```

| Field | Required | Meaning |
|---|---|---|
| `summary` | yes | What the agent did, in a few sentences. It goes in the attempt's comment and at the top of the unit's pull request, and its first line in the commit message |
| `questions` | when the step's `return.questions` is `required` | What a person must answer before the unit can go on. Allowed when the step's `return.questions` is `optional`. Leaving it out, or an empty list, means none. Never `null` |
| `data` | when the step's `return.schema` is set | Structured output, checked against that schema. Later steps read it as `{<step>.<field>}` |

No other field is allowed.

## Verdict

```json
{
  "decision": "reject",
  "reasons": ["S3 isn't implemented."],
  "findings": [
    {"check": "scenarios", "message": "Extending into a taken night isn't refused.", "location": "hotel/booking.py:42"}
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `decision` | yes | `approve` passes the gate. `reject` sends the work back to its step with the findings, up to the gate's `retry`. `escalate` hands the gate to a person |
| `reasons` | yes | Why, in sentences. For `escalate`, what a person has to decide |
| `findings` | no | Specific problems, each with a `message` (one sentence), and optionally the `check` it fails and a `location` as `path:line` |
| `details` | no | Anything the factory's own review conventions add, such as unmet acceptance criteria. fab0 records it and doesn't read it |

A call's `auto` gate, the acceptor, replies with a verdict too, once the child run is done: `approve` accepts what the child handed back, and `reject` sends it back to the child run with the reasons and findings, where the units that wrote it rework. See [`call`](pipeline.md#call).

A command gate has no verdict: its exit code decides, 0 for `approve` and anything else for `reject`, with its output as the finding. A person's decision at the prompt, `fab0-resolve confirm`, is recorded as a gate decision; a rejection, `--reject <text>`, carries a verdict `reject` with that text as its reason.
