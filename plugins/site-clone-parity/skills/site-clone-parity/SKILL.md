---
name: site-clone-parity
description: >
  Deterministic release gate for website clones. Use when rebuilding, migrating, or re-platforming
  an existing site and the new build must match the old one — pixel parity, computed styles, hidden
  interaction states, internal links, and CSS breakpoints — judged by the `clone-parity` CLI instead
  of by eye. Triggers on: clone a site, site clone, rebuild an existing site, re-platform, WordPress
  to Next.js, pixel parity, visual parity, visual regression against a reference site, clone-parity,
  certify the clone, "does my rebuild match the original".
  Do not use for ordinary frontend testing when there is no reference site.
---

# Site clone parity

`clone-parity` is the acceptance authority for a site clone. You propose candidate changes. The
command decides pass or fail. Never declare parity from a screenshot you looked at.

Source: `github.com/houseoftag/clone-parity` (private). Deeper docs live in that repo:
`docs/protocol.md` and `docs/configuration.md`.

## The three roles

| Role | Meaning |
| --- | --- |
| Reference | The site being copied. Read-only. Its captured bytes are frozen evidence. |
| Candidate | The rebuild you are changing. The only thing you edit. |
| Frozen references | Images, state results, element baselines, and the interaction inventory under `.clone-parity/`, sealed by `references/lock.json`. |

## Hard rules

1. Change the candidate only. Never edit files under `.clone-parity/`.
2. `capture --refresh` needs explicit user intent to adopt a changed source site. A failing
   candidate is never a reason to refresh. Breaking this rule destroys the method: a refreshed
   reference makes any candidate pass.
3. Never lower `tileMatchThreshold`, a state `threshold`, or a `certification.*` requirement to make
   a failure go away. Fix the candidate, or record a deliberate deviation in project docs.
4. Read the JSON report and the full-resolution diff tile before you diagnose. Do not guess from
   source HTML or a regex.
5. Run `certify` before you recommend release. `ok: true` in the certificate is the only "done".

## Exit codes

`0` pass · `1` a gate failed — read the report · `2` operator or configuration error (bad config,
stale lock, missing reference, crash). A `2` is your mistake, not the candidate's.

## Setup

If `clone-parity` is not on PATH:

```bash
npm install -g github:houseoftag/clone-parity
npx playwright install chromium
```

Then, in the candidate repository:

```bash
clone-parity init          # writes clone-parity.config.mjs, gitignores .clone-parity/
```

Point `reference.baseUrl` at the source site and `candidate.baseUrl` at the rebuild. Both must be
browser-reachable and must serve the build you want judged. Read
[reference/SETUP.md](reference/SETUP.md) for config recipes, route discovery, breakpoint choice, and
how to turn a live source site into a stable local reference.

## Command map

| Command | Use it for |
| --- | --- |
| `discover` | Freeze the route list from a sitemap index. |
| `capture` | Freeze visual, state, element, and inventory references. Never overwrites without `--refresh`. |
| `gate` | Full-page tiled pixel comparison at native resolution. |
| `elements` | Semantic anchors: typography, color, geometry, image identity. |
| `states` | Declarative interaction cases against frozen state results. |
| `inventory` | Advisory live listing of interactive surfaces. |
| `boundaries` | Prove the breakpoint set covers both sides of every CSS pixel edge. |
| `control` | Reference against itself. Must be 100%. Proves the checker, not the clone. |
| `integrity` | Route status, internal links, browser errors, outside origins. |
| `inspect` | Print the worst findings and verify report freshness and evidence hashes. |
| `certify` | The full release contract over the complete route inventory. |

Useful flags: `--config <file>`, `--route <path>` (repeatable), `--breakpoint <name>`
(`inventory`, `integrity`), `--refresh` (capture only), `--enforce-local`, `--json`,
`--report <file>` and `--limit <n>` (inspect), `--sitemap <url>` (discover).

## Operating loop

1. Freeze the routes — `discover`, or list them in `routes`.
2. `capture`. Review what got frozen; a bad reference poisons everything downstream.
3. `control` **before you trust any failure**. Reference against itself must be 100%. If it is not,
   repair the capture environment — the clone is not the problem.
4. `boundaries`. Add every missing width to `breakpoints`, then `capture --refresh`. That refresh is
   legitimate: the reference definition changed, not the source site.
5. Read `.clone-parity/reports/reference-inventory.json`. Every surface ID must appear in some
   state's `covers` array or in `stateCoverage.exclusions` with a reason. `states` keeps failing
   until each one is mapped.
6. Loop on one route at a time: focused `gate` / `elements` / `states` → inspect the worst tile →
   change the candidate → rerun the same focused command.
7. Make the candidate server serve the output of the configured build check.
8. `certify` over the whole inventory. Review the certificate and its evidence.

```bash
clone-parity capture
clone-parity control
clone-parity gate --route /about/
clone-parity inspect --report gate.json
clone-parity certify
```

## Reading a failure

Cheapest to most expensive:

1. Freshness. `inspect` reports a `freshness` array. A stale report proves nothing.
2. Did `control` pass in this session? If not, stop — the harness is broken.
3. `inspect --report gate.json` → worst tile → open
   `.clone-parity/artifacts/visual/<route-slug>/<breakpoint>/diff/NN.png` at full size.
4. `elements.json` findings name the anchor, the CSS property, and both values. Act on these before
   pixels; they are far faster to read.
5. `states.json` for anything a closed page cannot show.
6. Many unrelated routes failing together means a shared asset, font, or stale reference — not a
   component. Check that before editing components.

The full triage table, including "everything below one point is red":
[reference/TRIAGE.md](reference/TRIAGE.md).

## Hidden states

A closed-page screenshot certifies nothing about menus, dialogs, accordions, sliders, hover, focus,
form validation, or sticky headers. Each needs a state case with declarative actions and
comparisons. Navigation and non-read requests stay blocked by default; enable `stateSafety` options
only against an isolated test service, never production.

Authoring recipes and the coverage-mapping workflow: [reference/STATES.md](reference/STATES.md).

## Before you touch anything

Read [reference/GOTCHAS.md](reference/GOTCHAS.md). It carries the traps that cost real time:
`elements.enabled: false` crashes `control` and `certify`, route trailing slashes, artifact disk
growth, why a one-pixel height shift reddens every tile below it, and the capture pitfalls specific
to WordPress and proxied sources.

## Reporting to the user

Quote the report, not your impression: the `matchPct`, the failing tile path, or the element
finding. If you fixed something, name the gate that now passes and its threshold. If a gate still
fails, say so plainly with the number.
