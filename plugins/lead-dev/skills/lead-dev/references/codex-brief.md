# Writing a Codex brief

How to turn one of your decided specs into a hand-off that Codex implements
faithfully on the first try. This is the implementer-facing half of the `lead-dev`
workflow.

The blocks below use the same XML-tag vocabulary as the Codex plugin's internal
`gpt-5-4-prompting` skill, so your briefs and the plugin's own prompt handling
speak the same language.

---

## The one principle: prompt lean

Codex (the GPT-5-class model your `~/.codex/config.toml` points at) is
reinforcement-trained to gather context, plan, implement, test, and refine on its
own. So:

- **Do** spend words on what can be *verified*: the outcome, the contract, the
  acceptance criteria, the verify command, the scope fence.
- **Don't** add upfront-plan requests, preambles, status-update demands, or
  "think harder / be thorough / don't stop early." Those measurably make Codex
  worse — it can stop early or drift.
- **Better contract > more reasoning.** Tighten the brief before you reach for
  `--effort high`.
- **One job per run.** Split unrelated asks into separate `/codex:rescue` calls.

A brief is not a long document. *Minimal does not mean short* — include every
detail Codex can't infer, and nothing it can.

---

## Brief template

Drop unused blocks. `<task>` and `<action_safety>` belong in essentially every
write task; add the rest as the job needs them.

```xml
<task>
[The concrete job and the end state. Where in the repo it lives. Point to a
concrete example file to mirror: "Follow the pattern in src/widgets/Card.tsx."]
</task>

<contract>
[Interfaces/signatures Codex must match, with example I/O.
e.g. validateEmail(input: string): boolean
     "a@b.com" -> true,  "a@.com" -> false]
</contract>

<acceptance_criteria>
[Done means, verifiably:
 1. ...
 2. `npm run build` passes with no type errors
 3. `npm test -- path/to/test` is green]
</acceptance_criteria>

<verify>
[Exact commands, with flags, Codex must run before finishing.
 e.g. `pnpm test src/auth --run` and `pnpm tsc --noEmit`]
</verify>

<action_safety>
Keep changes tightly scoped to the task above.
No unrelated refactors, renames, or cleanup.
Use only dependencies already in the repo; do not add packages.
Do not edit or delete tests to make checks pass.
Implement the minimal solution that satisfies the criteria.
</action_safety>

<verification_loop>
Before finishing, run the verify commands and confirm the result against the
acceptance criteria. If a check fails, fix it rather than reporting a draft.
Show the verify command output as evidence.
</verification_loop>

<structured_output_contract>
Return: 1) summary of the change  2) touched files  3) verification performed
(command + result)  4) residual risks / follow-ups.
</structured_output_contract>
```

### Optional blocks (pull from the plugin's vocabulary as needed)
- `<completeness_contract>` — for multi-step work that must not stop at the first
  plausible result.
- `<default_follow_through_policy>` — "default to the most reasonable low-risk
  interpretation and keep going; only stop on a detail that changes correctness."
- `<missing_context_gating>` — "do not guess missing repo facts; retrieve them or
  state what's unknown." Use when a wrong guess would be costly.
- `<grounding_rules>` / `<dig_deeper_nudge>` — for diagnosis/review briefs.

---

## How to invoke

Implementation, fixes, refactors, tests go through `/codex:rescue` — invoke the
`Skill` tool with skill `codex:rescue`, and pass the brief plus any flags as the
argument. Note the example is a **non-visual** task — the data layer behind a UI
*you* are building yourself. Example argument string:

```
--fresh --background
<task>
Implement getUsageSummary() in src/billing/usage.ts: given an accountId and a
date range, return per-day usage rolled up from the events table. Mirror the
query and error-handling pattern in src/billing/invoices.ts.
</task>

<contract>
getUsageSummary(accountId: string, range: { from: string; to: string }):
  Promise<UsageDay[]>
UsageDay and the db client are already defined in src/billing/types.ts and
src/db.ts — import them. An empty range returns [].
</contract>

<acceptance_criteria>
1. One entry per calendar day in range, ascending; days with no events return 0s.
2. Invalid range (from > to) throws RangeError, matching invoices.ts.
3. `pnpm tsc --noEmit` clean; `pnpm test src/billing --run` green.
</acceptance_criteria>

<verify>
pnpm tsc --noEmit && pnpm test src/billing --run
</verify>

<action_safety>
Only add getUsageSummary and its test. No schema changes, no new dependencies, do
not edit other tests.
</action_safety>
```

Notes:
- No `--model` flag: the run inherits the SOTA model set at the Codex level
  (`~/.codex/config.toml`). Add `--model` only for a deliberate one-off.
- `--fresh` for a new task / `--resume` for a follow-up on the same Codex thread.
- `--background` for large or long jobs (then point the user at `/codex:status`);
  omit it for small, bounded ones.
- For an independent review pass of local changes use `/codex:review`; for a
  harder, custom-focus pass use `/codex:adversarial-review`. After a review,
  present findings and **stop** — don't auto-apply fixes; ask first.

---

## Worked examples

### A) Bug fix (foreground, scoped)
```xml
<task>
Diagnose and fix: POST /api/reports/export occasionally writes two rows to the
exports table for a single request. The handler is in src/api/reports/export.ts.
Preserve all other behavior.
</task>

<acceptance_criteria>
1. One request produces exactly one exports row (no duplicate on retry/race).
2. Existing export tests still pass.
</acceptance_criteria>

<verify>
pnpm test src/api/reports --run
</verify>

<completeness_contract>
Apply the fix; don't stop at diagnosis. Check whether the same double-write path
exists in the adjacent archive handler only if it shares the same writer.
</completeness_contract>

<action_safety>
Smallest safe fix on the failing path. No refactors. Do not touch or delete tests.
</action_safety>
```

### B) Tests to a contract (implementation assumed complete)
```xml
<task>
Write unit tests for the already-implemented parseDateRange() in
src/lib/dates.ts. Assume the implementation is correct and complete — your job is
coverage, not changing it.
</task>

<acceptance_criteria>
Cover: valid ranges, reversed start/end, single-day, invalid input, timezone
boundary. All tests pass.
</acceptance_criteria>

<verify>
pnpm test src/lib/dates --run
</verify>

<action_safety>
Only add a test file next to dates.ts. Do not modify dates.ts. Do not add deps.
</action_safety>
```

### C) Refactor to a defined target
```xml
<task>
Refactor src/api/client.ts so every request goes through a single request()
helper that injects auth headers and handles 401 refresh. The four existing
exported functions must keep identical signatures and behavior.
</task>

<acceptance_criteria>
1. All four functions delegate to request(); no duplicated header/refresh logic.
2. Public signatures unchanged.
3. `pnpm tsc --noEmit` clean; `pnpm test src/api --run` green.
</acceptance_criteria>

<verify>
pnpm tsc --noEmit && pnpm test src/api --run
</verify>

<action_safety>
Confine changes to src/api/client.ts. No new dependencies. Do not weaken or delete
tests; if a test must change, explain why in the summary.
</action_safety>
```

---

## Anti-patterns (don't ship these to Codex)

| Don't | Do |
| --- | --- |
| "Take a look and improve this." | A `<task>` with a concrete job and end state. |
| "Investigate and report back." | A `<structured_output_contract>` with the exact shape. |
| "Think harder, be very thorough." | A `<verification_loop>` tied to the acceptance criteria. |
| Bundling review + fix + docs + roadmap in one run. | One job per run; sequence separate `/codex:rescue` calls. |
| Delegating any UI/frontend implementation to Codex. | You build the presentation layer yourself; delegate only the non-visual logic behind it, behind a contract. |
| Handing over an unresolved product/architecture question. | Decide it first; delegate the decided spec. |
| "Make the tests pass." (invites deleting tests) | "Fix the code so the existing tests pass; do not edit tests." |
| "Add retry, caching, and a plugin system while you're in there." | Scope fence in `<action_safety>`: minimal solution, this path only. |
