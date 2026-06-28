# Payload Editor-UX Playbook

A reusable set of patterns and gotchas for building **editor-friendly, maintainable
Payload CMS 3 + Next.js 15 sites** — the quality-of-life layer Payload doesn't give you by
default. This is the **canonical, cross-project home** (it lives in the `payload` skill, so
it travels to every machine via the marketplace); proven on real deployments and meant to
be applied to every Payload site we build.

> **How to use this on a project.** Read the relevant topic doc below *before* you
> implement, follow (or improve) its pattern, then record which version of this skill the
> project was built against — see the **"Contributing QoL improvements back"** workflow in
> the skill's `SKILL.md`. Code paths in examples (`src/fields/link.ts`,
> `src/components/admin/*`, …) are from a reference implementation; copy the helpers and
> adapt. **Found a better way? Update these docs and push** — the workflow explains how
> (you're pre-authorized to commit playbook improvements without asking).

## Why this exists

Payload gives you a CMS; it does **not** give you a *good editor experience* by default.
A non-technical editor opening a stock Payload install hits: a table of cryptic filenames
for media, free-text URL fields they have to hand-type, a "layout" that's a wall of
identical "Block" rows, no preview, and no draft safety net. Each of these has a clean,
standard fix. This playbook is the collected set.

## Principles

1. **Two-layer architecture — keep design re-pulls safe.**
   - *Layer 1 (presentational):* pure components, props only, **no Payload imports**.
     A mirror of the design system. Safe to refresh/re-pull.
   - *Layer 2 (wiring):* field configs, `RenderBlocks`, and the server components in
     `app/(frontend)/` that fetch Payload data and feed Layer 1.
   - **Keep Layer-1 prop contracts stable** (a plain `href` string, a `newTab` boolean —
     never a Payload relationship object). Layer 2 normalizes Payload shapes *before*
     render (see [reusable-link-field](EDITOR-UX-LINK-FIELD.md)).

2. **Editor-first.** Every field a non-technical editor touches should be visual and
   guided: image *pickers* (not filenames), page *pickers* (not typed URLs), live
   preview, scannable collapsed layouts, draft → publish.

3. **Conventions over per-site reinvention.** Shared helpers (`linkField()`,
   `collectionLivePreview()`) and a fixed Media model mean a new site is *configuration*,
   not re-implementation.

4. **The build must stay green.** Custom admin components are real TypeScript that
   `next build` typechecks — keep `tsc --noEmit` at zero errors, and declare
   `@payloadcms/ui` as a dependency if you import from it.

## The patterns

| Doc | What it standardizes |
|-----|----------------------|
| [01 — Media & uploads](EDITOR-UX-MEDIA.md) | A scannable media library + working "Choose from existing" picker; image fields that are real uploads; bulk-select galleries. |
| [02 — Reusable link field](EDITOR-UX-LINK-FIELD.md) | One `linkField()`: internal page/post picker (polymorphic) vs custom URL, open-in-new-tab, resolved to a plain `href` in Layer 2. |
| [03 — Block layout builder](EDITOR-UX-LAYOUT-BUILDER.md) | Block-based pages that read as a scannable list of named sections, with a visual "Add section" picker. |
| [04 — Live preview & drafts](EDITOR-UX-LIVE-PREVIEW.md) | Side-by-side live preview that updates *as you type*, per collection, with a draft → publish workflow. |
| [05 — SQLite migrations](PAYLOAD-GOTCHAS.md) | A reliable forward-only migration workflow + the drizzle/SQLite gotchas (and their fixes) we hit. |

## Stack assumptions

- **Payload CMS 3.x** + **Next.js 15** (App Router), custom frontend (not the canned
  Payload frontend).
- **`@payloadcms/db-sqlite`** with **migrations** (not dev-push). Most gotchas in
  [05](PAYLOAD-GOTCHAS.md) are SQLite/drizzle-specific; Postgres avoids some.
- **Tailwind v3** for the frontend, scoped with `:where()` so it doesn't leak into the
  admin panel.
- Per-collection `versions.drafts` for anything with a public page.

## Quick-start checklist for a new Payload site

- [ ] Media collection per [01](EDITOR-UX-MEDIA.md) (useAsTitle, imageSizes,
      adminThumbnail, listSearchableFields, categories). Do **not** override the media
      list view with a custom grid component (it breaks the picker drawer — see 01).
- [ ] Copy `src/fields/link.ts`; wire `relationTo` to your routable collections and the
      URL prefix map; swap `linkField()` into every CTA/nav field ([02](EDITOR-UX-LINK-FIELD.md)).
- [ ] Block layout builder with per-block `admin.components.Label` row labels +
      `imageURL` thumbnails at 3:2 ([03](EDITOR-UX-LAYOUT-BUILDER.md)).
- [ ] Copy `src/utilities/generatePreviewPath.ts` + the `/next/preview` routes; add
      `collectionLivePreview()` + `versions.drafts.autosave` to every page-rendering
      collection ([04](EDITOR-UX-LIVE-PREVIEW.md)).
- [ ] Galleries as `upload hasMany`, not arrays ([01](EDITOR-UX-MEDIA.md)).
- [ ] Drive `migrate:create` headlessly and watch for the recreate `INSERT…SELECT` bug
      ([05](PAYLOAD-GOTCHAS.md)).
