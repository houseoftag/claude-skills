# 02 — Reusable link field

> Reference: `src/fields/link.ts`, `src/components/RenderBlocks.tsx` (the
> `resolveLinks()` call), the CTA blocks under `src/blocks/*`.

## Goal

One field editors use for **every** link — a CTA button, a nav item, a breadcrumb. They
pick an internal page/post from a type-to-complete search box (no hand-typed paths that
break when a slug changes), *or* type a custom URL, and optionally open it in a new tab.
Layer-1 components keep receiving a plain `href` string, so the design stays re-pull-safe.

## Pattern: `linkField()`

A factory returning the field array, spread into any group/array/collection:

```ts
// src/fields/link.ts
export const LINKABLE_COLLECTIONS = ['pages', 'news', 'events', 'programs', 'locations', 'galleries'] as const

export const linkField = (): Field[] => [
  {
    name: 'linkType', type: 'radio', defaultValue: 'internal',
    options: [
      { label: 'Page on this site', value: 'internal' },
      { label: 'Custom URL', value: 'custom' },
    ],
    admin: { layout: 'horizontal' },
  },
  {
    name: 'linkTo', type: 'relationship', relationTo: [...LINKABLE_COLLECTIONS], // POLYMORPHIC
    admin: {
      // tolerate legacy rows (no linkType) that already picked a doc
      condition: (_d, s) => s?.linkType !== 'custom' && (s?.linkType === 'internal' || !s?.linkType || !!s?.linkTo),
    },
  },
  {
    name: 'href', type: 'text', label: 'Custom URL',
    admin: { condition: (_d, s) => s?.linkType === 'custom' || (!s?.linkType && !!s?.href) },
  },
  { name: 'newTab', type: 'checkbox', label: 'Open in a new tab', defaultValue: false },
]
```

**Polymorphic `relationTo`** is the key move — the picker can target *any* routable
collection (Pages, News, Events, Programs, Locations, Galleries), each rendered as its own
type-to-complete search box. This is what the editor actually wanted when they said "the
link picker is missing the other content types."

## Pattern: `resolveLinks()` — the Layer-2 normalizer

The picked doc is a Payload relationship (`{ relationTo, value }`). Layer-1 components must
never see that. `resolveLinks()` walks the (cloned) data tree and rewrites each link object
to a plain `href` **before** render, mapping each collection to its public path:

```ts
const COLLECTION_PREFIX: Record<string, string> = {
  pages: '', news: '/news', events: '/events',
  programs: '/program',      // NB singular route, plural collection
  locations: '/locations', galleries: '/photos',  // NB galleries live at /photos
}

const docHref = (relationTo: string, doc: unknown): string | undefined => {
  const slug = (doc as { slug?: string })?.slug
  if (typeof slug !== 'string' || !slug) return undefined
  if (relationTo === 'pages') return slug === 'home' ? '/' : `/${slug}/`
  const prefix = COLLECTION_PREFIX[relationTo]
  return prefix === undefined ? undefined : `${prefix}/${slug}/`
}

export const resolveLinks = <T>(node: T): T => {
  if (Array.isArray(node)) { node.forEach(resolveLinks); return node }
  if (node && typeof node === 'object') {
    const obj = node as Record<string, unknown>
    if ('linkTo' in obj) {
      const lt = obj.linkTo as { relationTo?: string; value?: unknown }
      const href = lt?.relationTo ? docHref(lt.relationTo, lt.value) : docHref('pages', lt)
      if (href) obj.href = href            // picked doc wins; else the typed href stays
    }
    for (const k of Object.keys(obj)) { if (k !== 'linkTo') resolveLinks(obj[k]) } // don't recurse into the populated doc
  }
  return node
}
```

Call it once at the render boundary, on a clone so you never mutate Payload's cached doc:

```tsx
// RenderBlocks.tsx (Layer 2)
const resolved = resolveLinks(structuredClone(block))
return <Component {...resolved} />   // Layer 1 sees a plain href + newTab
```

## ⚠️ Gotchas

- **Populate the relationship.** `resolveLinks` needs `linkTo.value` to be the *doc* (with
  its `slug`), so the page fetch must use sufficient `depth` (e.g. `depth: 3` for a
  block-layout page). At `depth: 0` you get a bare ID and no href.
- **Match your route prefixes exactly.** Singular/plural mismatches bite: a `programs` doc
  is served at `/program/<slug>/`; `galleries` at `/photos/<slug>/`. Verify each against the
  actual `app/(frontend)` route, not the collection slug.
- **Trailing slashes** must match the rest of the site (seed data, nav). Pick one
  convention and make `docHref` honor it.
- **`newTab` rendering touches Layer 1.** Resolving the href is Layer 2, but applying
  `target="_blank" rel="noopener noreferrer"` happens in the component's `<a>`. Keep it a
  one-liner: `{...(cta.newTab ? { target: '_blank', rel: 'noopener noreferrer' } : {})}`.
- **Don't forget the globals.** A site's highest-value internal links are usually the
  Header/Footer **nav** — wire `linkField()` there too, and run `resolveLinks()` (or resolve
  inline) in `SiteHeader`/`SiteFooter`, which fetch globals directly and won't call
  `RenderBlocks`.

## Checklist

- [ ] `linkField()` factory with radio + polymorphic `linkTo` + `href` + `newTab`.
- [ ] `relationTo` lists every collection that has a public detail page.
- [ ] `resolveLinks()` maps every linkable collection to its real route prefix.
- [ ] Called on a `structuredClone` at the render boundary.
- [ ] Page fetches use enough `depth` to populate `linkTo`.
- [ ] Swapped into all CTA fields **and** Header/Footer nav globals.
