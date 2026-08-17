# Framer CMS through the Server API

Everything here hangs off a connected `framer` instance. See [`../SKILL.md`](../SKILL.md) for connecting.

## Two kinds of collection

- **Collection** — created by a person in the Framer CMS. Editable in the app and through the API.
  `framer.getCollections()`, `framer.getCollection(id)`, `framer.createCollection(name)`.
- **ManagedCollection** — owned by a plugin or sync script, read-only inside the app.
  `framer.createManagedCollection(name)`, `framer.getManagedCollections()`. Use it when an external
  source is the source of truth and hand-edits in Framer would be lost anyway.

`collection.managedBy` tells you which you are holding: `"user"`, `"thisPlugin"`, or
`"anotherPlugin"`. A collection managed by *another* plugin rejects writes.

## Fields

```ts
const fields = await collection.getFields()        // [{ id, name, type, ... }]
await collection.addFields([{ type: "string", name: "Headline" }])
await collection.removeFields([fieldId])
await collection.setFieldOrder([id1, id2, id3])
```

`ManagedCollection` replaces the whole schema in one call instead: `setFields(fields)`, where each
field carries an `id` you choose. Stable ids matter — renaming a field keeps its canvas bindings only
if the id stays the same. Limit is 30 custom fields.

Field types: `boolean`, `color`, `number`, `string`, `formattedText`, `image`, `file`, `link`, `date`,
`enum`, `collectionReference`, `multiCollectionReference`, `array` (gallery), plus `divider`.
A field reported as `unsupported` is a newer Framer feature the API cannot read or write yet — skip
it rather than trying to map it.

## Items

```ts
const items = await collection.getItems()
// item: { id, slug, draft, fieldData, createdAt, updatedAt }

await collection.addItems([{ id, slug, fieldData }])   // id present → update
await collection.addItems([{ slug, fieldData }])       // id absent  → create
await collection.removeItems([itemId])
await collection.setItemOrder([id2, id1])
```

`addItems` is the write path for both create and update — there is no `updateItems`. `slug` is
required and unique per collection. `draft: true` keeps an item out of published output.

`ManagedCollection.addItems` requires an `id` on every item — supply the external system's id, so a
renamed title never orphans a record.

## Field data shapes

`fieldData` is `Record<fieldId, { type, value }>`, keyed by **field id**, never by name:

| type | `value` |
|---|---|
| `string`, `enum` | `string` |
| `formattedText` | `string` + optional `contentType: "auto" \| "markdown" \| "html"` (default `html`) |
| `number` | `number` |
| `boolean` | `boolean` |
| `date` | ISO string or epoch ms, or `null` |
| `color` | CSS color string or a color-style object, or `null` |
| `image` | URL string (or `null`) + optional `alt` |
| `file`, `link` | URL string, or `null` |
| `collectionReference` | item id string, or `null` |
| `multiCollectionReference` | array of item ids, or `null` |
| `array` | array of item inputs (gallery) |

Managed collections reference other items by **id**; unmanaged collections reference by **slug**.

Assets: upload local files first with `framer.uploadImage(s)` / `framer.uploadFile(s)` and write the
returned URL into the field.

## Idempotent upsert by slug

The pattern every sync script needs — from Framer's own `csv-importer` example:

```ts
const fields = await collection.getFields()
const fieldNameToId = new Map(fields.map((f) => [f.name.toLowerCase(), f.id]))

const existingItems = await collection.getItems()
const slugToExistingId = new Map(existingItems.map((item) => [item.slug, item.id]))

const items = rows.map((row) => ({
    id: slugToExistingId.get(row.slug),          // undefined → creates
    slug: row.slug,
    fieldData: {
        [fieldNameToId.get("headline")]: { type: "string", value: row.headline },
    },
}))

await collection.addItems(items)
```

Deletions are not implied: items no longer present in the source stay in Framer until
`removeItems()` is called with their ids. Diff the two id sets when the source is authoritative.

## Sync state

`setPluginData(key, value)` / `getPluginData(key)` store small strings on a collection or item — the
place for a last-synced timestamp, an external collection id, or a content hash. Both take and return
strings; serialize anything richer.

## Field values a person edits

A managed field marked `userEditable` can be changed in the app, and the script may **not** write it.
Use it for the copy a human owns on records the machine otherwise controls.

## Worked examples

`github.com/framer/server-api-examples` — `csv-importer` (create collection, add fields, upsert),
`notion-automations-sync` (external source on a schedule, Cloudflare Worker), `json-api` (read-only
HTTP layer over collections), `publish`.
