---
name: framer
description: >
  Use when working with a Framer site programmatically — connecting to a Framer
  project, reading or writing Framer CMS collections, syncing external data into
  Framer, publishing or deploying a Framer site, or editing the Framer canvas
  from a script. Triggers on: "Framer", "framer-api", "Framer CMS",
  "Framer Server API", "publish the Framer site", "FRAMER_API_KEY".
---

# Framer Server API

Framer projects are edited through the **Server API** — the `framer-api` npm package, which opens a
stateful WebSocket to a headless Framer instance. Same method surface as the in-app Plugin API, plus
publishing and deployment, with no browser and no open Framer window.

**Verified against `framer-api@0.1.29`, 2026-08-17.** Open beta: free today, per-use pricing later.

There is no REST endpoint and no official MCP server. JS/TS is the only client language.

## Setup

Two values are needed, and **only a human can produce the key** — it is created in the Framer app:

1. **API key** — in Framer: `Cmd+K` → "open settings" → **API Keys** → create and copy. The key is
   scoped to that one project. Store it in a `0600` file or `.env`; refer to the path, never print it.
2. **Project URL** — the browser address bar of the open project:
   `https://framer.com/projects/<Name>--<id>`. `connect()` also takes the bare id.

Set `FRAMER_API_KEY` in the environment and `connect()` picks it up with no second argument.

## Connect

`connect()` opens a connection that must be closed, or the script hangs. Three ways to close it —
pick by runtime:

```ts
import { withConnection } from "framer-api"

// Works on every runtime. Closes on resolve and on throw.
await withConnection(projectUrl, async (framer) => {
    const info = await framer.getProjectInfo()
    console.log(info.name)
})
```

```ts
// Node 24+ / Bun 1.3+ only — `using` is a SyntaxError on Node 22.
using framer = await connect(projectUrl)
```

```ts
// Manual: needs try/finally, or a thrown error leaks the connection.
const framer = await connect(projectUrl, apiKey)
try { /* ... */ } finally { await framer.disconnect() }
```

Runtimes: Node 22+, Bun 1.1+, Deno 1.4+, Cloudflare Workers. `getProjectInfo()` is the cheapest
liveness check — it returns `{ name, id }` and proves the key and URL are both right.

## Publish and deploy

Two distinct steps. `publish()` builds a **preview** deployment; `deploy(id)` promotes it to
production and any custom domains.

```ts
const changes = await framer.getUnpublishedPageChanges()
const { deployment } = await framer.publish()
const hostnames = await framer.deploy(deployment.id)   // production — authorize first
```

`deploy()` is a production release. Get explicit per-deploy authorization, publish the preview first,
and read `getDeploymentIssues(deployment.id)` before promoting.

## Reference

- **CMS collections** — fields, items, upsert-by-slug, field-data shapes, syncing an external source:
  [`reference/cms.md`](reference/cms.md)
- **Canvas editing** — the `framer.agent` namespace, its command DSL, `readProject`, branches:
  [`reference/agent-api.md`](reference/agent-api.md)

## Gotchas

- **`fieldData` keys are field IDs, not field names.** Build a `name → id` map from
  `collection.getFields()` every run; a script keyed by name writes nothing and reports success.
- **An item without an `id` is a new item.** Upserting means looking up the existing item id by slug
  first. Skip that and each run duplicates the whole collection.
- **Nothing is transactional.** A script that dies mid-run leaves a half-written collection. Make
  every sync idempotent and re-runnable rather than adding rollback.
- **The first call costs 1–2s** while the sandbox cold-starts; later calls are fast, and the instance
  stays warm for a while. Batch work into one connection instead of reconnecting per item.
- **Retry on transport errors** with the exported `isRetryableError(error)` guard.
- The API key belongs to one project. A second Framer site needs its own key.
