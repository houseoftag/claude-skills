# 03 — Block layout builder

> Reference: `src/collections/Pages.ts` (the `layout` field + `LAYOUT_BLOCKS`),
> `src/components/admin/BlockRowLabel.tsx`, `src/blocks/*/config.ts` (the `imageURL`),
> `src/components/RenderBlocks.tsx`.

## Goal

Editors compose a page from pre-designed sections (a `blocks` field), and the builder reads
as a **scannable list of named sections** — not a wall of identical "Block" rows — with a
**visual "Add section" picker**.

## Pattern: block = config + presentational component + renderer entry

Each design section is three things (the two-layer split — see the
[README](EDITOR-UX.md#principles)):

1. **Block config** (Layer 2 wiring): `src/blocks/Hero/config.ts` — fields + admin.
2. **Presentational component** (Layer 1): `src/components/blocks/Hero.tsx` — props only.
3. **Renderer entry**: a `blockType → component` map in `RenderBlocks.tsx`.

```ts
// Pages.ts
{
  name: 'layout',
  type: 'blocks',
  admin: { initCollapsed: true },         // a tidy stack of named sections, expand one at a time
  blocks: LAYOUT_BLOCKS,
}
```

## ⚠️ Gotcha: row labels are **per-block**, not field-level

To make a collapsed row say `01. Hero — Empowering children…` instead of `Block`, you need
a custom row label. The trap:

- `admin.components.RowLabel` on the **field** works for **`array`** fields only. On a
  **`blocks`** field it is a **type error and silently ignored at runtime** (confirmed in
  `@payloadcms/ui` `renderField.js`: the `'blocks'` case reads `blockConfig.admin.components.Label`,
  the `'array'` case reads the field's `RowLabel`).
- The correct slot is **each block's** `admin.components.Label`.

Inject it once across all blocks rather than editing every config:

```ts
// Pages.ts
const withRowLabel = (block: Block): Block => ({
  ...block,
  admin: { ...block.admin, components: { ...block.admin?.components, Label: '/components/admin/BlockRowLabel#BlockRowLabel' } },
})
const LAYOUT_BLOCKS: Block[] = [HeroBlock, /* … */].map(withRowLabel)
```

The label component gets the row's data via `useRowLabel()` (the `RowLabelProvider` derives
it from the form path — so a per-block `Label` *does* see the block's fields):

```tsx
'use client'
import { useRowLabel } from '@payloadcms/ui'

export function BlockRowLabel() {
  const { data, rowNumber } = useRowLabel<Record<string, unknown>>()
  const typeLabel = TYPE_LABELS[data?.blockType as string] ?? 'Section'
  const snippet = (data?.heading ?? data?.title ?? data?.eyebrow ?? '') as string
  return <span><strong>{typeLabel}</strong>{snippet && ` — ${snippet.slice(0, 60)}`}</span>
}
```

> Importing from `@payloadcms/ui` in a custom admin component? **Declare it as a
> dependency** (`pnpm add @payloadcms/ui@<payload version>`) — it's only a transitive dep
> otherwise, so `tsc`/`next build` fails to resolve it.

## Pattern: a visual "Add section" picker (block thumbnails)

A Payload block takes `imageURL` (+ `imageAltText`), shown in the "Add block" drawer:

```ts
export const HeroBlock: Block = {
  slug: 'hero',
  imageURL: '/block-thumbs/hero.webp',
  imageAltText: 'Hero section preview',
  labels: { singular: 'Hero', plural: 'Heroes' },
  fields: [/* … */],
}
```

### ⚠️ Gotcha: the picker thumbnail is **3:2 / `object-fit: cover`**

The block-picker thumbnail container is `aspect-ratio: 3 / 2` with `object-fit: cover`
(see `@payloadcms/ui` `ItemsDrawer`/`BlockSelector` scss). Any other source ratio is
**center-cropped** — wide blocks lose their sides, tall blocks lose top/bottom. Author every
thumbnail at **3:2** (e.g. 600×400). If you screenshot live blocks (which have wildly
different heights), **letterbox onto a uniform 3:2 white canvas** so nothing crops:

```js
sharp(input).resize(600, 400, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 1 } })
  .flatten({ background: { r: 255, g: 255, b: 255, alpha: 1 } }).webp({ quality: 82 })
```

Schematic SVGs or real screenshots both work — keep them small and in `/public` (they ship
with the admin; they're optimized UI assets, not content).

## Editor-readability extras (low effort, high payoff)

- `initCollapsed: true` on the blocks field.
- Plain-language `label`/`admin.description` on fields.
- Group a CTA's label + link in a `type: 'row'`; tuck rarely-touched fields into a collapsed
  group. Avoid fully custom field components / swapping the editor at this stage — high cost,
  ~90% of the feel comes from the above.

## Checklist

- [ ] `blocks` field with `initCollapsed: true`.
- [ ] Per-block `admin.components.Label` (NOT field-level `RowLabel`), injected via a map.
- [ ] `@payloadcms/ui` declared if the label/admin components import it.
- [ ] `imageURL` + `imageAltText` on every block, authored at **3:2**.
- [ ] Block thumbnails in `/public`, small, letterboxed if screenshotted.
