# Editing the Framer canvas

Two surfaces reach the canvas. Pick by how the change is expressed.

- **`framer.agent`** — the namespace Framer's own AI agent uses: a command DSL for layout and content,
  plus structured project queries. Best for "add a section", "change this copy", "restyle this block".
- **`framer.*` node methods** — typed, per-node primitives (`createFrameNode`, `setAttributes`,
  `cloneNode`, …). Best for narrow mechanical edits where you already hold a node id.

The `framer.agent` methods are marked internal in the package types. They work through `framer-api`
and are how Framer drives its own agent, but the shape can change between releases — pin the version.

## Read the DSL before writing any of it

`agent.getSystemPrompt()` returns the **only** documentation of the command syntax used by
`applyChanges()` and the query types used by `readProject()`. It is static, so fetch it once per
session and work from it. Guessing the syntax produces silently rejected commands.

```ts
const syntax = await framer.agent.getSystemPrompt()   // commands, design rules, query reference
const context = await framer.agent.getContext()       // this project: fonts, color tokens, text styles, icon sets
```

`getContext()` is project-specific and is what keeps generated layout on-brand — it carries the
project's real design tokens. Read both before composing changes.

## Read, then change

```ts
const { results } = await framer.agent.readProject([{ /* query */ }], { pagePath: "/about" })
const result = await framer.agent.applyChanges("cmd; cmd; cmd", { pagePath: "/about" })
```

`applyChanges` takes `;`-separated commands and returns the command status, any errors, and the
canonical ids of nodes it created — read the result rather than assuming it applied. `pagePath`
defaults to the active page, so pass it explicitly in a script.

For a pure copy edit, `agent.replaceText({ id, searchText, replaceText })` is the precise tool; it
returns `false` when nothing matched, which is the signal that the page moved under you.

## What is on the page

Node reads, all scoped by `pagePath`: `getNode`, `getNodes`, `getNodesOfTypes`,
`getDescendantsOfTypes`, `getDescendantReferencesOfTypes`, `getParentNode`, `getAncestors`,
`getScopeNode`, `getGroundNode`, `getRect`, `serialize`, `serializeNodes`.

Catalogs, for inserting things that already exist in the project: `listComponents()`,
`listIconSets()`, `readIcons({ iconSetName })`, `readComponentControls({ componentIds })`,
`readIconSetControls`, `readLayoutTemplateControls`, `readShaderControls`.

Prefer a project component over a hand-built frame — `listComponents()` first, build only what is
genuinely missing.

## Verify visually

```ts
const shot = await framer.screenshot(nodeId, { format: "png" })
const svg = await framer.exportSVG(nodeId)
```

`screenshot` is Server-API-only and is the way to check a canvas edit landed. Measure or look at the
result; do not report a visual change on the strength of a successful command alone.

## Branches keep a live site safe

Canvas edits apply to the active branch, and `main` is what publishing releases. Work on a branch:

```ts
const branch = await framer.agent.createBranch("cms-sync")
await framer.agent.switchBranch(branch.id)
// ...changes...
await framer.agent.getBranchChanges(branch.id)   // review before merging
await framer.agent.mergeBranch("main")
```

Also available: `getActiveBranch`, `getBranches`, `joinBranch`, `leaveBranch`, `renameBranch`,
`deleteBranch`.

## Publishing from the agent namespace

`agent.publish(input)` takes an action-discriminated input — preview, confirm publish, or deploy to
production — and returns status, URLs, warnings, and errors. The plain `framer.publish()` /
`framer.deploy(id)` pair in [`../SKILL.md`](../SKILL.md) is the simpler path for a script; production
promotion needs explicit authorization either way.

## Other useful agent calls

- `queryImages(input)` — find candidate images (source, query, count, orientation).
- `queryAnalytics({ query, from, to })` — Framer analytics rows, ISO date strings.
- `flattenComponentInstance({ id })` — detach an instance into editable layers.
- `makeExternalComponentLocal({ id })` — copy an external component into the project.
