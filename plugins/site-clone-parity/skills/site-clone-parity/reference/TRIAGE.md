# Failure triage

## Evidence order

1. **Freshness.** `clone-parity inspect --report <file>` returns a `freshness` array. Any entry
   means the report predates the current config, route list, or reference set. Rerun the gate; do
   not diagnose from it.
2. **Control.** `clone-parity control` compares the reference to itself at exact tolerance and must
   return 100%. A failing control means the capture environment is broken — browser version, fonts,
   nondeterministic source content, an unstable server. Fix that before reading any candidate
   failure. A checker that fails its own control is not evidence against the clone.
3. **Worst tile.** `inspect --report gate.json` sorts by worst tile. Open the full-resolution
   `diff/NN.png`; the matching `reference/NN.png` and `candidate/NN.png` sit beside it.
4. **Element findings.** `elements.json` names the anchor, property, and both values — usually the
   fastest path to a fix.
5. **State report** for anything a closed page cannot show.

## Symptom table

| Symptom | Most likely cause | Move |
| --- | --- | --- |
| Every tile below a certain Y is red, tiles above are clean | A height difference near the top shifted everything below. One real defect, not fifty. | Fix the topmost differing element, rerun. Judge only tile 0 until it is clean. |
| Many unrelated routes fail at once | Shared asset: font not loading, global CSS, header/footer component, or a stale reference. | Check `integrity.json` browser errors and `elements.json` `fontFamily` findings before touching components. |
| `gate` passes but `elements` reports high-severity `missing` | Text content differs, so the anchor ID changed. Anchors are keyed on rendered text. | Compare the reference and candidate copy. Text parity is part of clone parity. |
| Paired `missing` + `unexpected` for the same thing | Same element, changed text or region (header/main/footer). | Fix the text or the DOM placement. |
| `box-x` / `box-width` deltas above 4px | Container width, padding, or font metrics. | Check computed styles at that breakpoint, not the source CSS. |
| Everything fails right after a config edit | You changed a reference-defining field. | Revert it, or `capture --refresh` **only** if the user wants the new definition adopted. |
| Exit 2 "Frozen reference bytes changed outside capture --refresh" | Something wrote into `.clone-parity/`. | Restore from git or re-freeze deliberately. Never patch the lock. |
| Exit 2 "Page did not reach a stable loaded state" | Lazy content, an endless animation, or a slow image. | Raise `settleDeadlineMs`, or `hideSelectors` the offender. Do not set `allowUnsettled`. |
| `unexpectedOrigins` on a gate that otherwise matches | The page requests a third-party origin. | Localize the asset, or add the origin to `allowedExternalOrigins` with a reason. |
| `states` fails with coverage `missing` | New interactive surfaces appeared in the frozen inventory. | Add a state case or a `stateCoverage.exclusions` entry with a real reason. |
| `states` fails with coverage `unknown` | A `covers` or exclusion ID no longer exists in the inventory. | The surface changed; re-read `reference-inventory.json` and re-map. |
| `integrity` broken-link on a route that loads fine in a browser | The candidate does not answer `HEAD`. | Set `integrity.allowLinkGet: true` only when read requests are safe. |
| `boundaries` reports `unsupportedConditions` | A media query uses `em`/`rem` widths or a form the parser cannot read. | Convert to px, or list the equivalent px widths in `breakpoints` and set `boundaries.failOnUnsupportedConditions: false` with a note. |
| `certify` fails with "candidate Git state changed during certification" | A check or the dev server wrote into the working tree mid-run. | Make the build write outside the tree, or commit before certifying. |

## What each severity means in `elements.json`

- **high** — a missing anchor, an unexpected action (link or button), or a difference in
  `fontFamily`, `fontWeight`, `fontSize`, `color`, `textTransform`, `fontStyle`. High findings fail
  the gate.
- **medium** — other style properties, `x`/`width`/`height` deltas over 4px, unexpected non-action
  anchors. Reported, not fatal.
- **low** — `y` deltas over 8px. Usually the shadow of a real difference higher up the page.

## Discipline

- Fix one route and one breakpoint at a time with `--route`. A focused gate still validates against
  the complete reference lock, so it cannot pass by ignoring the rest.
- After each fix, rerun the same focused command before widening.
- Never conclude "close enough" from a diff image. The number in the report is the verdict.
