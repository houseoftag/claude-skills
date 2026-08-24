# Setup and configuration

## Install

```bash
npm install -g github:houseoftag/clone-parity
npx playwright install chromium      # once per machine
clone-parity --help
```

Node.js 20 or newer. The repo also runs from a clone: `npm install && npm link`.

## Serving both sides

Both `baseUrl` values must be browser-reachable for the whole run.

| Source type | How to serve it as the reference |
| --- | --- |
| Live public site | Point `reference.baseUrl` at it, and set `network.enforceLocal: false` plus an explicit `allowedExternalOrigins` list. Slower and less stable — prefer a mirror. |
| Static mirror | `wget --mirror` or the `scrapling` skill, then `npx serve -l 4173 ./mirror`. Best option: deterministic bytes, no third-party requests. |
| WordPress on SiteGround | Mirror it first. A live WordPress reference brings analytics, chat widgets, and lazy-loaded ads that make captures nondeterministic. |
| Local rebuild | `next start` / `vite preview` on its own port. Never a hot-reload dev server — HMR overlays and injected scripts change pixels. |

The candidate must serve a **production build**. Put the build in `checks` so `certify` rebuilds it,
and make sure the server picks the new output up before the browser gates run (a wrapper script that
builds then restarts is the usual answer).

## Minimum configuration

```js
export default {
  schemaVersion: 1,
  reference: { baseUrl: "http://127.0.0.1:4173" },
  candidate: { baseUrl: "http://127.0.0.1:3000" },
  routes: ["/", "/about/"],
  breakpoints: [
    { name: "desktop",    width: 1728, height: 1000, isMobile: false },
    { name: "phone-max",  width: 767,  height: 900,  isMobile: true },
    { name: "tablet-min", width: 768,  height: 1024, isMobile: true },
    { name: "mobile",     width: 390,  height: 844,  isMobile: true }
  ],
  checks: [
    { name: "build", command: "npm", args: ["run", "build"] }
  ]
};
```

`checks` take an executable plus an argument array. There is no shell parsing — no pipes, no `&&`,
no globs. Wrap anything complex in a script file.

## Routes

Routes are normalized to a leading and trailing slash: `about` → `/about/`. **Query strings are
dropped.** A route that only differs by query string cannot be captured; give it a real path or
exclude it.

Sitemap discovery:

```js
discovery: { sitemapUrl: "https://example.com/sitemap_index.xml" },
routeFile: ".clone-parity/routes.json"
```

```bash
clone-parity discover      # follows nested sitemap indexes, keeps same-origin URLs only
```

Inline `routes` and `routeFile` entries are merged and de-duplicated. Put pages the pixel gate
cannot handle (search results, dated feeds, anything with rotating content) in
`excludeVisualRoutes` — they still get link and integrity checks.

## Breakpoints

Every breakpoint name becomes a directory and a report key, so keep them stable. Include:

- the real design widths you care about;
- **both sides of every CSS media-query edge** — 767 and 768 for a `max-width: 767px` rule.

`boundaries` computes the required widths from the actual stylesheets of both sides and fails until
each one is in `breakpoints` or in `boundaries.ignoreWidths`. Run it early; every added breakpoint
forces a `capture --refresh`.

`deviceScaleFactor` defaults to 1. Raising it multiplies capture time and disk use; the tiled
comparison already runs at native resolution.

## Settling and flake control

`capture` blocks until the page is stable: lazy images forced eager, `data-src` promoted,
background images preloaded, fonts ready, then N consecutive reads with an unchanged scroll height.

- `capture.settleDeadlineMs` (default 60000) — raise for heavy pages.
- `capture.stableReads` (default 3) — raise if a page keeps growing.
- `capture.allowUnsettled: false` — keep it false. True means "screenshot a half-loaded page".
- `capture.hideSelectors` — the correct tool for genuinely nondeterministic elements (a rotating
  testimonial, a live counter). It hides the selector on **both** sides with `visibility: hidden`,
  so the gate stops judging it. Prefer this over lowering a threshold.
- `capture.freezeAnimations: true` — zeroes transition and animation durations, hides scrollbars,
  hides the caret. Leave it on.

## Network policy

`network.enforceLocal: true` (default) aborts every request whose origin is not the side's own
origin or in `allowedExternalOrigins`, and fails the run when one is attempted. Service workers are
blocked. WebSockets follow the same allowlist.

This is deliberate: a clone that silently needs Google Fonts, a CDN, or an analytics beacon is not a
self-contained clone. When the source legitimately needs an origin, name it:

```js
network: { enforceLocal: true, allowedExternalOrigins: ["https://fonts.gstatic.com"] }
```

`--enforce-local` forces the strict mode for a single run even when the config relaxes it.

## Thresholds

- `capture.tileMatchThreshold` (default 95) — the percentage of matching pixels each 1500px tile
  must reach. **Every** tile must pass; a page average cannot hide a broken section. 95 is loose for
  a real clone — a 1728-wide tile can differ by ~130k pixels and still pass. Tighten toward 99.5
  once the candidate is close.
- `capture.pixelThreshold` (default 0.1) — per-pixel color tolerance passed to pixelmatch. Anti-
  aliased pixels are already excluded from tile counts.
- `certification.consecutiveVisualRuns` (default 2) — two clean passes catch nondeterminism.

## What the reference lock covers

`.clone-parity/references/lock.json` hashes every frozen image, the state manifest and its images,
the element baseline, and the reference inventory, plus a hash of the reference-defining config
(reference URL, routes, breakpoints, capture settling, network policy, reference-side state
definitions).

Consequences worth knowing before you edit the config:

- Changing any of those fields invalidates the lock and forces `capture --refresh`.
- Changing **candidate-only** fields — `candidate.baseUrl`, candidate selectors, thresholds,
  `covers` mappings, `checks`, `certification` — does not. That separation is intentional: tuning
  the candidate can never quietly re-baseline the reference.
- Hand-editing anything under `.clone-parity/` makes the next command exit 2.
