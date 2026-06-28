# 04 — Live preview & drafts

> Reference: `src/utilities/generatePreviewPath.ts` (incl. `collectionLivePreview()`),
> `src/app/(frontend)/next/preview/route.ts` + `next/exit-preview/route.ts`,
> `src/components/LivePreviewListener.tsx`, the detail routes under `app/(frontend)/*/[slug]`.

## Goal

Every collection that renders a public page gets a **side-by-side live preview that updates
as the editor types**, plus a **draft → publish** safety net. Live preview is configured
**per collection** — there is no global switch — so it's easy to wire one collection (Pages)
and forget the rest.

## The four pieces

1. **`admin.livePreview` + `admin.preview`** on each collection (the preview pane + button).
2. **`generatePreviewPath()`** — builds the `/next/preview?...` URL with the secret.
3. **`/next/preview` + `/next/exit-preview` routes** — validate the secret, toggle draft
   mode, redirect. Collection-agnostic; write once.
4. **The frontend route renders in draft mode** + mounts `<LivePreviewListener/>`.

## Pattern: a shared per-collection config helper

Don't copy the `livePreview` block into every collection — factor it:

```ts
// generatePreviewPath.ts
const collectionPrefixMap = { pages: '', programs: '/program', news: '/news',
  events: '/events', locations: '/locations', galleries: '/photos' }

export const collectionLivePreview = (
  collection: keyof typeof collectionPrefixMap,
): Pick<NonNullable<CollectionConfig['admin']>, 'livePreview' | 'preview'> => ({
  livePreview: {
    url: ({ data, req }) =>
      `${process.env.NEXT_PUBLIC_SERVER_URL}${generatePreviewPath({ slug: data?.slug as string, collection, req }) ?? ''}`,
    breakpoints: [
      { label: 'Mobile', name: 'mobile', width: 375, height: 667 },
      { label: 'Tablet', name: 'tablet', width: 768, height: 1024 },
      { label: 'Desktop', name: 'desktop', width: 1440, height: 900 },
    ],
  },
  preview: (data, { req }) => generatePreviewPath({ slug: data?.slug as string, collection, req }),
})
```

```ts
// any page-rendering collection
admin: { ...collectionLivePreview('programs'), useAsTitle: 'name' }
```

Typing the return as `Pick<…admin…, 'livePreview' | 'preview'>` keeps the `url`/`preview`
callbacks correctly typed without per-call annotations.

## Pattern: the frontend route renders in draft mode

```tsx
import { draftMode } from 'next/headers'
import { LivePreviewListener } from '@/components/LivePreviewListener'

export default async function ProgramPage({ params }) {
  const { slug } = await params
  const { isEnabled: draft } = await draftMode()
  const result = await payload.find({
    collection: 'programs', where: { slug: { equals: slug } }, limit: 1,
    draft, overrideAccess: draft,           // show the working draft when previewing
  })
  return (<div>{draft && <LivePreviewListener />}{/* … */}</div>)
}
```

`LivePreviewListener` is just `RefreshRouteOnSave` from `@payloadcms/live-preview-react`
calling `router.refresh()`. If a route filters by status (`_status: { equals: 'published' }`),
**relax it in draft mode** so drafts preview: `...(draft ? {} : { _status: { equals: 'published' } })`.

## Make it update *as you type*: autosave

The single most common complaint: "*the preview only updates when I save (cmd+S / click
out).*" That's because, without **autosave**, the live-preview iframe only refreshes when the
document *saves*. Enable draft autosave with a short interval:

```ts
versions: {
  drafts: {
    autosave: { interval: 100 },   // push updates to the iframe as the editor types
  },
}
```

- `drafts: true` (no autosave) → refresh **on save**. `drafts: { autosave }` → refresh
  **as you type**. (`autosave` is admin/version behavior — **no migration**.)
- A collection with **no drafts at all** still gets live preview, but only refresh-on-save.
  Give it `versions.drafts` to unlock autosave (that *is* a migration — see below).
- Editors must **reload an already-open admin tab** to pick up a changed `autosave` config.

## Drafts on collections that render pages

Enable `versions.drafts` on every collection with a public page so editors can stage changes
and publish deliberately (and get autosave). Enabling drafts on a collection that **already
has data** is a migration that adds `_status` — back-fill existing rows to `'published'` or
they vanish from the site. See [PAYLOAD-GOTCHAS.md (migrations)](PAYLOAD-GOTCHAS.md).

## Which collections get this

Only the ones that render a **distinct public page** (Pages, Programs, News, Events,
Locations, Galleries). Collections with no standalone URL (Media, Users, form submissions,
team members rendered only in a grid, job postings in a list) **don't** — there's nothing to
preview.

## Env + security

- `PREVIEW_SECRET` and `NEXT_PUBLIC_SERVER_URL` must be set.
- The `/next/preview` route validates `previewSecret === PREVIEW_SECRET` **and** that the
  request is authenticated before enabling draft mode (returns 403 otherwise). Don't loosen
  this.

## Checklist

- [ ] `/next/preview` + `/next/exit-preview` routes; `PREVIEW_SECRET` + `NEXT_PUBLIC_SERVER_URL` set.
- [ ] `generatePreviewPath` prefix map covers every page-rendering collection.
- [ ] `...collectionLivePreview(slug)` in each such collection's `admin`.
- [ ] Each detail route: `draftMode()` → `draft`/`overrideAccess` on the fetch + `<LivePreviewListener/>`.
- [ ] `versions.drafts.autosave.interval` for update-as-you-type.
- [ ] Backfill `_status='published'` when enabling drafts on existing data.
