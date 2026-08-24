# State cases and coverage

A full-page screenshot of a closed page proves nothing about a menu that opens, a form that
validates, a slider that moves, or a header that sticks. State cases cover that gap.

## How the mechanism works

1. `capture` opens the **reference** page, replays the reference-side actions, and freezes the
   result — a cropped screenshot, or a computed value.
2. Later, `states` opens the **candidate** page, replays the candidate-side actions, and compares
   against the frozen result.

The live reference is never the release oracle. Only the frozen, hashed result is.

## Anatomy

```js
states: [
  {
    name: "mobile-menu-open",           // unique, stable — it names the artifact directory
    route: "/",
    breakpoint: "mobile",               // defaults to the first breakpoint
    covers: ["surface:/:mobile:menus:fcd533c5ed81:0"],
    settleMs: 200,                      // optional pause after the actions
    actions: [
      { action: "click",
        referenceSelector: ".legacy-toggle",
        candidateSelector: "button[aria-label='Open menu']" },
      { action: "wait", ms: 200 }
    ],
    comparisons: [
      { type: "screenshot",
        referenceSelector: ".legacy-panel",
        candidateSelector: "nav[aria-label='Mobile navigation']",
        threshold: 97 },
      { type: "computedStyle",
        referenceSelector: ".legacy-panel",
        candidateSelector: "nav[aria-label='Mobile navigation']",
        properties: ["position", "backgroundColor", "fontSize", "lineHeight"] },
      { type: "geometry",
        referenceSelector: ".legacy-panel",
        candidateSelector: "nav[aria-label='Mobile navigation']",
        tolerance: 1 }
    ]
  }
]
```

Selector rules: use `selector` when both sides share a selector, or **both**
`referenceSelector` and `candidateSelector` when the DOMs differ. One of the pair alone is a
configuration error (exit 2).

Actions: `click`, `hover`, `press` (needs `key`), `fill` (`value`), `check` (`checked`), `scroll`
(`x`, `y`), `wait` (`ms`).

Comparisons: `screenshot` (omit the selector for a full page), `computedStyle` (needs `properties`),
`geometry` (`tolerance` defaults to 1px), `text` (whitespace-normalized), `attribute` (needs
`attribute`), `visible`.

Comparisons are matched **by index** against the frozen manifest. Reordering or inserting one
invalidates the frozen state references and forces a refresh — append when you can.

## Which fields force a refresh

Reference-side only: `name`, `route`, `breakpoint`, `settleMs`, the actions minus their
`candidateSelector`, and the comparisons minus `candidateSelector`, `threshold`, and `tolerance`.

So you can retune candidate selectors, thresholds, and tolerances freely. Changing what the
reference does or measures needs `capture --refresh`.

## Coverage mapping — the part people skip

`capture` also freezes `reports/reference-inventory.json`: every rendered form, menu, dialog,
control, media element, and interactive element on every route and breakpoint, each with a stable
`surface:<route>:<breakpoint>:<kind>:<digest>:<n>` ID.

`states` fails until every surface ID is either:

- listed in some state's `covers` array, or
- listed in `stateCoverage.exclusions` with a real reason:

```js
stateCoverage: {
  exclusions: [
    { id: "surface:/about/:mobile:media:abc123:0", reason: "Static map embed; no controls." }
  ]
}
```

Workflow: read the frozen inventory, group the surfaces, write one state case per genuine
interaction, and exclude the rest with reasons a reviewer would accept. "Not important" is not a
reason. Report `unknown` means an ID you mapped no longer exists — the surface changed.

The `id` digest hashes the surface's rendered detail, so a copy change on the reference produces a
new ID and forces you to re-map. That is deliberate: a changed control deserves a fresh look.

## Safety

Defaults, and they should stay:

- Non-`GET`/`HEAD`/`OPTIONS` requests are aborted.
- Navigation requests are aborted, `submit` is prevented, clicks on `a[href]` are prevented, and
  `window.open` is neutered. A state that navigates fails with an explicit error.
- Every WebSocket is closed while side effects are disallowed.

`stateSafety: { allowSideEffects: true, allowNavigation: true }` is only for an isolated test
service that can absorb real submissions. Never point it at production, and never enable it to make
a state case pass. Testing real form delivery is a separate, separately authorized job.

## Practical cases worth writing

Mobile menu open, dropdown or mega-menu hover, accordion or `<details>` expanded, modal or cookie
dialog open, tab switch, carousel after one advance, form empty-submit validation message, focus
ring on the primary input, sticky header after a scroll, and any hover state that changes more than
a color.
