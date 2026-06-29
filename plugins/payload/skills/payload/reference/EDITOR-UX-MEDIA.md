# 01 — Media & uploads

> Reference: `src/collections/Media.ts`, `src/collections/Galleries.ts`,
> `src/collections/Programs.ts` (the `gallery` field).

## Goal

A media library a non-technical editor can actually use: human-readable titles,
thumbnails, search, and categories — and a **"Choose from existing" picker that works**.
Plus: every image field is a real upload, and galleries are filled by bulk-selecting many
photos at once.

## Pattern: the Media collection

```ts
export const Media: CollectionConfig = {
  slug: 'media',
  admin: {
    useAsTitle: 'alt',                                   // editors see alt text, not filenames
    defaultColumns: ['alt', 'category', 'filename', 'updatedAt'],
    listSearchableFields: ['alt', 'filename'],           // search matches both
    pagination: { defaultLimit: 24 },                    // more thumbnails per page (default is 10)
  },
  upload: {
    staticDir,                                           // volume-backed dir, NEVER the container fs
    mimeTypes: ['image/*', 'application/pdf'],
    adminThumbnail: 'thumbnail',                         // the square crop used everywhere in admin
    focalPoint: true,                                    // editor sets the subject; auto-crops keep it
    imageSizes: [
      { name: 'thumbnail', width: 300, height: 300, position: 'centre' },
      { name: 'card', width: 768 },
      { name: 'feature', width: 1600 },
    ],
  },
  fields: [
    { name: 'alt', type: 'text', required: true,         // required → useAsTitle always populated
      admin: { description: 'Describe the image for screen readers and SEO.' } },
    { name: 'category', type: 'select', admin: { position: 'sidebar' }, options: [/* … */] },
    { name: 'caption', type: 'text', label: 'Caption' }, // single source of truth for captions
  ],
}
```

### Why these choices

- **`useAsTitle: 'alt'` + `required` alt** — every media doc shows a readable title in the
  picker drawer and relationship cells, and your images get alt text for free.
- **`imageSizes` + `adminThumbnail`** — Payload renders the small square crop in the list,
  the picker, and relationship cells. Without it editors scan raw filenames.
- **`category` (sidebar select) + `listSearchableFields`** — filter + search make a library
  of hundreds of assets navigable.
- **`focalPoint: true`** — auto-crops (thumbnail/card) keep the subject framed.

## Pattern: a universal thumbnail-grid media picker

It's tempting to make the media list a thumbnail grid via
`admin.components.views.list.Component`. The trap: in Payload 3.x that same component *also*
renders inside the **"Choose from existing" picker drawer** (the drawer's `render-list`
server function uses `collectionConfig.admin.components.views.list.Component`). A **server**
component of `<a href>` cards then **navigates away instead of selecting** — breaking the
picker and discarding the editor's unsaved page. That's why a naive grid is wrong.

**The fix is a `'use client'` component that is *mode-aware*.** Wire it once and it becomes
the grid in all three surfaces: the full-page library, every single-select picker (incl. the
Lexical rich-text upload picker), and the `hasMany` multi-select picker. Verified on Payload
**3.85.1** (twincedars `src/components/admin/MediaGridView.tsx`).

```tsx
'use client'
import { useConfig, useListDrawerContext, useListQuery, useModal } from '@payloadcms/ui'

export function MediaGridView(props: { enableRowSelections?: boolean; newDocumentURL?: string }) {
  // data + search/filter/pagination — works in BOTH modes (this component is wrapped by
  // ListQueryProvider either way). refineListData updates the URL on the full page and
  // notifies the drawer (onQueryChange → refetch) inside it; new docs flow back into `data`.
  const { data, query, handlePageChange, refineListData } = useListQuery()
  // drawer context: {} (all undefined) on the full page, populated inside a picker drawer.
  const { isInDrawer, onSelect, onBulkSelect, allowCreate, createNewDrawerSlug } = useListDrawerContext()
  const { openModal } = useModal()

  const multi  = isInDrawer && Boolean(props.enableRowSelections)   // hasMany picker
  const single = isInDrawer && !multi && typeof onSelect === 'function'
  // card click:
  //   !isInDrawer → <a href={editURL}>            (navigate; the classic library)
  //   single      → onSelect({ collectionSlug, doc, docID: String(doc.id) })   (Upload field closes the drawer)
  //   multi       → toggle a LOCAL Set<id>; a "Select N" button → onBulkSelect(new Map([...ids].map(id => [id, true])))
  // "Upload new":  full page → <a href={props.newDocumentURL}>;  drawer → openModal(createNewDrawerSlug)  (NEVER <a href>)
}
```

### The non-obvious parts (each cost a debugging cycle)

- **Overriding `views.list.Component` replaces the *whole* list body**, not a slot. The
  default view's `SelectionProvider` + "Select N" toolbar live *inside* the view you replace,
  so `useSelection()` is **not** guaranteed around you. **Manage multi-select with local
  state** (a `Set<id>`, keyed by id so it survives pagination) and build the `Map<id,true>`
  for `onBulkSelect` yourself. Don't rely on the framework's selection provider/button.
- **Detect mode with `useListDrawerContext()`** — `ListDrawerContext` defaults to `{}`, so on
  the full page `isInDrawer`/`onSelect` are simply `undefined` (safe to destructure). `onSelect`
  = single-select; `enableRowSelections` (a clientProp, true only for `hasMany`) = multi-select.
- **Don't re-fetch.** Read `useListQuery().data.docs`; drive search/category/pagination through
  `refineListData()` / `handlePageChange()`. `mergeQuery` **replaces** `where` wholesale (pass
  `where: {}` to clear a filter) and auto-resets to page 1 on search/where changes.
- **In-drawer "create new"** = `openModal(createNewDrawerSlug)` (or the context's
  `DocumentDrawerToggler`) — a stacked drawer that preserves unsaved work. Never navigate.
- **Lexical's upload picker uses the same `ListDrawer`** (single-select), so it's covered for
  free — no separate component.
- **`@payloadcms/ui` must be a runtime `dependency`**, not a devDependency — a client component
  imports it at runtime.

> Prefer the stock table picker if a grid isn't worth the coupling: it already works (row-click
> → `onSelect`, thumbnail in the filename cell, your `defaultColumns` + search + category filter).
> The grid couples to `@payloadcms/ui` client internals, so a Payload major may need a touch-up.

## Pattern: every image field is an `upload`, never a text URL

```ts
// ✅ editor gets the visual picker + alt/focal point + responsive sizes
{ name: 'backgroundImage', type: 'upload', relationTo: 'media' }

// ❌ a text field they must paste a URL into — no picker, no alt, no resizing
{ name: 'imageUrl', type: 'text' }
```

Audit your block/collection fields for any `type: 'text'` field that holds an image URL and
convert it.

## Pattern: galleries = `upload` with `hasMany`, not an array

An `array` of `{ image, caption }` forces editors to add **one photo at a time**. An
`upload` field with `hasMany: true` gives the bulk multi-select drawer (checkboxes, pick
20 at once) and drag-to-reorder.

```ts
// ✅ bulk multi-select
{
  name: 'images',
  type: 'upload',
  relationTo: 'media',
  hasMany: true,
  admin: { description: 'Select multiple photos at once via "Choose from existing".' },
}

// ❌ one row at a time
{ name: 'images', type: 'array', fields: [
    { name: 'image', type: 'upload', relationTo: 'media', required: true },
    { name: 'caption', type: 'text' },
] }
```

**Captions live on the Media doc** (its own `caption`/`alt`), not per-gallery-row — that's
why the Media collection has a `caption` field. Reusable, and one source of truth. (On
twincedars, 0 of 223 gallery rows ever used a per-row caption, confirming this.)

Rendering (Layer 1 gets populated Media docs at `depth >= 1`):

```tsx
const images = (gallery.images ?? [])
  .map(asMedia)                                  // number | Media -> Media | null
  .filter((m): m is Media => Boolean(m?.url))
// …images.map((media) => <figure><img src={media.url} alt={media.alt} />…</figure>)
```

> Switching an existing array field to `hasMany` is a schema change — see
> [PAYLOAD-GOTCHAS.md (migrations)](PAYLOAD-GOTCHAS.md) (the array table is dropped; data moves to
> the `_rels` table). Update any seed scripts to push bare media IDs (`[id1, id2]`), not
> `[{ image: id }]`.

## Storage discipline (deploy hygiene)

- Upload `staticDir` → a **persistent volume** (e.g. Railway `/data/media`), never the
  ephemeral container filesystem.
- **Never commit content images to git or `/public`.** `/public` is for optimized,
  code-referenced UI assets only.

## Checklist

- [ ] `useAsTitle` set to a required human field (alt/title).
- [ ] `imageSizes` (incl. a square `thumbnail`) + `adminThumbnail` + `focalPoint`.
- [ ] `listSearchableFields` + a sidebar `category` select + `pagination.defaultLimit`.
- [ ] A `caption` field on Media (single source for gallery captions).
- [ ] Media list view: either the default table picker (zero-maintenance) **or** a mode-aware
      `'use client'` grid (see "universal thumbnail-grid media picker") — never a *server*-component grid.
- [ ] Every image field is `type: 'upload'`.
- [ ] Galleries are `upload hasMany`, not arrays.
- [ ] `staticDir` on a persistent volume; no content images in git/`/public`.
