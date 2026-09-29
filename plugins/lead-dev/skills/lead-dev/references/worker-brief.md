# Writing a worker brief

How to turn one of your decided specs into a hand-off that a Sonnet 5.5 worker
implements faithfully on the first try. This is the implementer-facing half of the
`lead-dev` workflow.

The blocks below are XML tags. A worker starts with none of your context, so the
brief must stand alone.

---

## The one principle: prompt lean

A Sonnet 5.5 worker gathers context, implements, tests, and refines on its own. So:

- **Do** spend words on what can be *verified*: the goal, the files in scope, the
  contract, the acceptance check, the exact return format.
- **Don't** add "do not be lazy", "be very thorough", or tool-retry nudges. They
  are old workarounds and no longer help.
- **Never write "minimize tool calls" or "only use tools when strictly
  necessary".** Sonnet 5.5 follows them literally and skips reads and checks it
  needs.
- **At `low` effort, demand real evidence.** Sonnet 5.5 sometimes reports code done
  without a real check. A coding brief at `low` effort must require the actual
  test, typecheck, or build output in the return.
- **Better contract > more reasoning.** Tighten the brief, or raise effort one
  notch, before you escalate to an Opus worker.
- **One job per worker.** Split unrelated asks into separate workers.

A brief is not a long document. *Minimal does not mean short* — include every
detail the worker can't infer, and nothing it can.

---

## Brief template

Drop unused blocks. `<goal>`, `<scope>`, `<constraints>`, `<acceptance_check>`, and
`<return_format>` belong in essentially every write task.

```xml
<goal>
[The concrete job and the end state. Point to a concrete example file to mirror:
"Follow the pattern in src/widgets/Card.tsx."]
</goal>

<scope>
Files to change: [paths].
Files to read for context: [paths].
Out of scope: [what the worker must not touch].
</scope>

<contract>
[Interfaces/signatures the worker must match, with example I/O.
e.g. validateEmail(input: string): boolean
     "a@b.com" -> true,  "a@.com" -> false]
</contract>

<constraints>
Keep changes tightly scoped to the goal above.
No unrelated refactors, renames, or cleanup.
Use only dependencies already in the repo; do not add packages.
Do not edit or delete tests to make checks pass.
Do not run git write commands (commit, stash, checkout, reset).
Implement the minimal solution that satisfies the criteria.
</constraints>

<acceptance_check>
[Done means, verifiably:
 1. ...
 2. `pnpm tsc --noEmit` passes with no errors
 3. `pnpm test src/auth --run` is green
Run these commands before finishing. If a check fails, fix it rather than
reporting a draft.]
</acceptance_check>

<return_format>
Return exactly: 1) summary of the change (3 sentences max)  2) touched files
3) each verify command with its real, pasted output  4) residual risks or
follow-ups. Do not paste whole files.
</return_format>
```

### Optional blocks
- `<completeness_contract>` — for multi-step work that must not stop at the first
  plausible result.
- `<missing_context_gating>` — "do not guess missing repo facts; retrieve them or
  state what's unknown." Use when a wrong guess would be costly.
- `<read_only>` — for review and investigation workers: "You are read-only. Do not
  edit any file."

---

## How to invoke

Spawn the worker with the `Agent` tool: `model: 'sonnet'` and the brief as the
prompt. Always pass `model` — an omitted one inherits the coordinator's Opus. Notes:

- Effort: `medium` for routine implementation, `low` for mechanical edits, `high`
  only for the hardest work. The `Agent` tool takes no `effort` parameter. A
  `general-purpose` worker runs at `medium` (the claude-config override); for
  another level, set `effort` in a custom agent type's frontmatter, or in a
  Workflow stage's `agent()` options.
- Follow-up on the same task → `SendMessage` to that worker with the delta only.
- Several independent pieces → spawn all workers in one message. Workers that
  write to one tree run one at a time, or each in its own worktree.
- Large or long jobs → run in the background; the harness notifies on completion.
- Independent review → a fresh worker with `<read_only>`, Sonnet for routine
  changes, Opus for high-stakes or user-facing ones. Present findings and
  **stop** — don't auto-apply fixes; decide first.

Example prompt. Note the example is a **non-visual** task — the data layer behind
a UI *you* are designing:

```xml
<goal>
Implement getUsageSummary() in src/billing/usage.ts: given an accountId and a
date range, return per-day usage rolled up from the events table. Mirror the
query and error-handling pattern in src/billing/invoices.ts.
</goal>

<scope>
Files to change: src/billing/usage.ts, plus a test at src/billing/usage.test.ts.
Files to read: src/billing/invoices.ts, src/billing/types.ts, src/db.ts.
Out of scope: schema changes, other billing modules.
</scope>

<contract>
getUsageSummary(accountId: string, range: { from: string; to: string }):
  Promise<UsageDay[]>
UsageDay and the db client are already defined in src/billing/types.ts and
src/db.ts — import them. An empty range returns [].
</contract>

<constraints>
No new dependencies. Do not edit other tests. No git write commands.
</constraints>

<acceptance_check>
1. One entry per calendar day in range, ascending; days with no events return 0s.
2. Invalid range (from > to) throws RangeError, matching invoices.ts.
3. `pnpm tsc --noEmit && pnpm test src/billing --run` is clean and green.
</acceptance_check>

<return_format>
Summary, touched files, the verify command with its real output, residual risks.
</return_format>
```

---

## Worked examples

### A) Bug fix (scoped)
```xml
<goal>
Diagnose and fix: POST /api/reports/export occasionally writes two rows to the
exports table for a single request. The handler is in src/api/reports/export.ts.
Preserve all other behavior. Apply the fix; don't stop at diagnosis.
</goal>

<scope>
Change: src/api/reports/export.ts. Check the adjacent archive handler only if it
shares the same writer. Out of scope: everything else.
</scope>

<constraints>
Smallest safe fix on the failing path. No refactors. Do not touch or delete tests.
</constraints>

<acceptance_check>
1. One request produces exactly one exports row (no duplicate on retry/race).
2. `pnpm test src/api/reports --run` passes.
</acceptance_check>

<return_format>
Root cause in two sentences, the diff summary, the test output pasted.
</return_format>
```

### B) Tests to a contract (implementation assumed complete)
```xml
<goal>
Write unit tests for the already-implemented parseDateRange() in
src/lib/dates.ts. Assume the implementation is correct — your job is coverage,
not changing it.
</goal>

<scope>
Add one test file next to dates.ts. Do not modify dates.ts.
</scope>

<constraints>
Do not add dependencies.
</constraints>

<acceptance_check>
Cover: valid ranges, reversed start/end, single-day, invalid input, timezone
boundary. `pnpm test src/lib/dates --run` passes.
</acceptance_check>

<return_format>
Touched files and the pasted test output.
</return_format>
```

### C) Refactor to a defined target
```xml
<goal>
Refactor src/api/client.ts so every request goes through a single request()
helper that injects auth headers and handles 401 refresh. The four existing
exported functions must keep identical signatures and behavior.
</goal>

<scope>
Confine changes to src/api/client.ts.
</scope>

<constraints>
No new dependencies. Do not weaken or delete tests; if a test must change,
explain why in the return.
</constraints>

<acceptance_check>
1. All four functions delegate to request(); no duplicated header/refresh logic.
2. Public signatures unchanged.
3. `pnpm tsc --noEmit && pnpm test src/api --run` is clean and green.
</acceptance_check>

<return_format>
Summary, touched files, pasted verify output.
</return_format>
```

---

## Anti-patterns (don't ship these to a worker)

| Don't | Do |
| --- | --- |
| "Take a look and improve this." | A `<goal>` with a concrete job and end state. |
| "Investigate and report back." | A `<return_format>` with the exact shape. |
| "Be very thorough, don't be lazy." | An `<acceptance_check>` the worker must run and paste. |
| "Minimize tool calls" / "only use tools when strictly necessary". | Say nothing about tool use; the worker follows these literally. |
| Bundling review + fix + docs + roadmap in one worker. | One job per worker; spawn separate workers. |
| Handing over design-defining UI work. | You write the code that invents the look; delegate it once decided, with tokens, states, and a reference. |
| Handing over an unresolved product/architecture question. | Decide it first; delegate the decided spec. |
| "Make the tests pass." (invites deleting tests) | "Fix the code so the existing tests pass; do not edit tests." |
| "Add retry, caching, and a plugin system while you're in there." | Scope fence in `<constraints>`: minimal solution, this path only. |
| Omitting `model` on the spawn. | Always pass `model: 'sonnet'` (or `'opus'` on escalation). |
