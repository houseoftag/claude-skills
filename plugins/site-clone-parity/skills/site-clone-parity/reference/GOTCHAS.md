# Gotchas

Verified against clone-parity 0.1.0 (`houseoftag/clone-parity`, first release, 2026-08-24).

## Tool bugs to route around

- **`elements.enabled: false` crashes `control` and `certify`.** `control` unconditionally runs the
  element gate and then reads `report.summary`, which the skipped path never sets:
  `TypeError: Cannot convert undefined or null to object`. Leave `elements.enabled` at `true`. If
  you truly need it off, set `certification.requireControl: false` as well — and say so in the
  project docs.
- **`boundaries` does not normalize or validate routes.** Every other command normalizes `--route`
  and rejects unknown ones. `boundaries` passes the raw string to the browser, so
  `--route about` or a `boundaries.routes` entry without a trailing slash can 404 with a confusing
  error instead of "No configured routes match". Always write boundary routes as `/about/`.
- **`capture` reports `status: "captured"` for every freshly written image.** The `"missing"` branch
  is unreachable. Do not treat its absence as proof that nothing failed; read the `hash` field.

## Behaviour that surprises people

- **A one-pixel height difference near the top reddens every tile below it.** Tiles are fixed
  1500px slices of the full-page image, so any vertical shift misaligns everything after it. Fix
  the topmost difference first and treat the rest as noise until it is clean.
- **Query strings are dropped from routes.** `/search/?q=x` normalizes to `/search/`. Paginated or
  filtered views need real paths.
- **`elements` anchors are keyed on rendered text.** Changed copy shows up as a high-severity
  `missing` plus an `unexpected`, not as a "text changed" finding. Read the pair together.
- **Duplicate content on one page collapses.** Anchors de-duplicate by `region|kind|key`, so two
  identical buttons in `main` count once. Cover the second one with a state case if it matters.
- **`region` is only `header`, `footer`, or `main`** (nearest `<header>`/`<footer>` ancestor). A
  visually distinct sidebar is `main`.
- **`tileMatchThreshold` defaults to 95, which is loose.** Tighten it as the candidate converges.
- **Artifacts grow fast.** Each gate writes the full-page reference, candidate, and diff PNGs *plus*
  three PNGs per tile, and `certify` does two visual runs plus a control, each under
  `.clone-parity/artifacts/runs/<run-id>/`. Nothing prunes old runs. On a large site expect
  gigabytes; delete stale `runs/` directories between sessions, and keep `.clone-parity/` gitignored
  (`init` does this).
- **`elements`, `states`, `inventory`, and `boundaries` run serially.** Only `gate` and `capture`
  use `capture.concurrency`. On a 60-route site the element gate is 240 sequential page loads —
  budget the wall-clock, and use `--route` while iterating.
- **`certify` refuses `--route`.** It always uses the complete inventory. That is the point.
- **`certify` fingerprints the Git worktree before and after the run** and fails if it changed. A
  build that writes into the tree (generated files, lockfile churn) fails certification. Commit
  first, or move the build output outside the repo.
- **`checks` run before the browser gates but nothing restarts the candidate server.** If the check
  rebuilds, the server must pick the new output up on its own, or the gates judge the old build.
  Use a wrapper script that builds and restarts.
- **Link checks use `HEAD`.** Servers that answer 405 to `HEAD` look like broken links until you set
  `integrity.allowLinkGet: true`.
- **`freezeAnimations` cannot stop a video or a canvas render loop.** Use `capture.hideSelectors`.
- **`enforceLocal` blocks fonts.** A candidate loading Google Fonts while the reference mirror ships
  them locally fails on origins *and* on `fontFamily` element findings. Localize the font.

## Capture pitfalls by source type

- **WordPress** — analytics, chat widgets, ad slots, and lazy-load plugins make live captures
  nondeterministic. Mirror the site first, then serve the mirror.
- **Anything behind Cloudflare** — a challenge page can be captured as the reference without any
  error. Check the first frozen PNG by eye once, before trusting the set.
- **Shopify** — cart drawers and app embeds inject markup on load. Expect state cases, and expect
  the inventory to list app surfaces you must exclude with reasons.
- **Hot-reload dev servers** — never the candidate. HMR clients, error overlays, and injected
  scripts change pixels and console output. Use a production build.

## Never do these

- Refresh references because the candidate failed.
- Lower a threshold to clear a visible defect.
- Hand-edit anything under `.clone-parity/`, including `lock.json`.
- Enable `stateSafety` against production.
- Report parity from a screenshot instead of the report.
