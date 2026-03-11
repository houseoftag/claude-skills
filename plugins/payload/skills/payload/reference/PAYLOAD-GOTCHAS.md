# Payload CMS Gotchas & Best Practices

Hard-won lessons from production Payload CMS 3 + Next.js 15 projects. Follow these exactly.

---

## CSS Isolation: Frontend vs Payload Admin

### The Problem
Global CSS imported in the frontend route group (`src/app/(frontend)/layout.tsx`) bleeds into the Payload admin panel in production. The admin panel becomes completely unusable — broken layout, wrong colors, missing spacing.

### Why It Happens
Next.js production builds merge CSS from all route groups. Even though `(frontend)` and `(payload)` are separate route groups, their CSS is NOT isolated.

### The Fix
Scope ALL frontend CSS under a wrapper class:

1. Add `className="your-site"` to the frontend `<body>` tag
2. Move `:root` custom properties to `.your-site`
3. Scope all base element styles with `:where()` for zero specificity:
   ```css
   /* WRONG — overrides Payload's heading styles */
   .your-site h1 { color: var(--color-text); }

   /* CORRECT — zero specificity, component rules win */
   .your-site :where(h1, h2, h3) { color: var(--color-text); }
   ```
4. Scope the universal reset: `*, *::before, *::after` becomes `.your-site *, .your-site *::before, .your-site *::after`
5. Add `margin: 0; padding: 0;` directly to `.your-site` (otherwise browser default body margin leaks through)

### Why `:where()` Matters
Without it, `.your-site h1` has specificity `0-1-1`, beating component-level rules like `.hero-headline { color: white }` (specificity `0-1-0`). The `:where()` wrapper zeroes out the element selector's contribution.

---

## Payload CSS Build Stripping Bug

### The Problem
Next.js build pipeline strips Payload's `:root` CSS variable definitions AND layout rules (`.template-minimal`, `.template-default`) from the production bundle. The admin panel renders with no variables and broken layout.

### Why It Happens
Next.js tree-shakes CSS it considers "unused." Payload's variables and layout classes get removed during build optimization.

### The Fix
1. Copy Payload's full CSS to `public/payload-styles.css`:
   ```bash
   cp node_modules/@payloadcms/next/dist/prod/styles.css public/payload-styles.css
   ```
2. Create a provider component that loads it via `<link>`:
   ```tsx
   // src/components/AdminTheme.tsx
   export default function AdminTheme({ children }: { children: React.ReactNode }) {
     return (
       <>
         <link rel="stylesheet" href="/payload-styles.css" />
         {children}
       </>
     )
   }
   ```
3. Register as a `providers` component (NOT `afterNav`):
   ```ts
   // payload.config.ts
   admin: {
     components: {
       providers: ['@/components/AdminTheme'],
     },
   }
   ```

### Critical: Use `providers`, Not `afterNav`
`afterNav` only renders on authenticated pages (after the sidebar nav). The login page uses `template-minimal` which has no nav, so the CSS never loads on login. `providers` wraps the entire admin app including login.

### Maintenance
When upgrading Payload, re-copy `payload-styles.css` from the new version's `node_modules`.

---

## Tailwind CSS v4 Does NOT Work with Next.js + Payload

### The Problem
Tailwind CSS v4 utility classes are never generated when used in a Payload CMS + Next.js project. The `@theme` block and `@source` directives appear as raw unprocessed CSS in the browser. The page renders completely unstyled — no backgrounds, no spacing, no colors.

### Why It Happens
Tailwind v4 uses `@import "tailwindcss"` which gets resolved by Next.js's webpack CSS pipeline. Webpack splits CSS imports into separate modules and processes each independently through PostCSS. The sequence:

1. Webpack sees `@import "tailwindcss"` in your `styles.css`
2. It resolves this to `node_modules/tailwindcss/index.css` and extracts it as a **separate CSS chunk**
3. `@tailwindcss/postcss` processes that chunk — generating the theme layer, base resets, and preflight
4. Your remaining CSS (with `@theme`, `@source`, and utility class references) is processed as a **second chunk**
5. Since the second chunk doesn't contain `@import "tailwindcss"`, `@tailwindcss/postcss` doesn't activate for it
6. Result: theme variables are defined (from chunk 1) but **zero utility classes are generated** because the scanner never ran against your source files

The `source()` parameter (`@import "tailwindcss" source("../../")`) doesn't help — webpack still splits the import before PostCSS can process it as a unit. The `@source` directive also doesn't help for the same reason.

### The Fix: Use Tailwind CSS v3
Tailwind v3 uses `@tailwind base; @tailwind components; @tailwind utilities;` directives which webpack does NOT split. They remain in the CSS file and are processed by the `tailwindcss` PostCSS plugin in-place.

```bash
# Remove v4
pnpm remove tailwindcss @tailwindcss/postcss

# Install v3
pnpm add -D tailwindcss@3 postcss autoprefixer
```

**postcss.config.mjs:**
```js
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
export default config
```

**tailwind.config.ts:**
```ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/app/(frontend)/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      // your custom colors, fonts, etc.
    },
  },
  plugins: [],
}
export default config
```

**styles.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Your custom CSS here */
```

### How to Diagnose
If you suspect this issue, check the compiled CSS in the browser:
```bash
# Get the CSS URL from the page source
curl -s http://localhost:3000 | grep -o 'href="[^"]*\.css[^"]*"'

# Check if utility classes exist
curl -s "<css-url>" | grep "\.bg-" | head -5
```

If you see theme variables defined but zero utility classes (no `.bg-*`, `.text-*`, `.flex`, etc.), this is the webpack splitting issue. Switch to Tailwind v3.

### When This Might Be Fixed
This is fundamentally a webpack issue. If Next.js switches to a different CSS bundling approach (or if `@tailwindcss/postcss` adds a mode that doesn't depend on `@import` detection), v4 may work in the future. Until then, **always use Tailwind v3 with Payload + Next.js projects**.

---

## Reserved Field Names with Drafts Enabled

### The Problem
When `versions: { drafts: true }` is enabled on a collection, Payload reserves the field name `status` internally (mapped to `_status` in the database with enum values `draft`/`published`). If you create your own field named `status`, the database enum gets created with Payload's values instead of yours, causing query failures.

### Example Error
```
Failed query: select count(*) from "events" where "events"."status" = $1 params: upcoming
```

### The Fix
Never name a field `status` on collections with drafts enabled. Use a more specific name:
```ts
// WRONG — conflicts with Payload's internal _status field
{ name: 'status', type: 'select', options: ['upcoming', 'past', 'cancelled'] }

// CORRECT — no conflict
{ name: 'eventStatus', type: 'select', options: ['upcoming', 'past', 'cancelled'] }
```

---

## Database Migration Safety

### NEVER Use `migrate:fresh`
`migrate:fresh` drops ALL tables and recreates from scratch. **All data is permanently lost.** There is no confirmation prompt that clearly warns about this.

### Safe Migration Workflow
```bash
# 1. Back up first — ALWAYS
npm run backup:db

# 2. Create migration
npx payload migrate:create <name>

# 3. Run migration (NOT migrate:fresh)
npx payload migrate

# 4. If migration fails due to "dev mode" warning, answer 'y'
#    but understand this may cause issues if schema drifted
```

### Dev Mode vs Migrations
When running `npm run dev`, Payload auto-pushes schema changes without creating migrations. The DB schema and migration history get out of sync. When you later try to run migrations, Payload warns about this and may try to recreate existing tables.

**Best practice:** Use migrations from the start if you plan to deploy. Or at minimum, always back up before any migration operation.

---

## Bulk Media Import: Never Use Payload's Upload API

### The Problem
Using `payload.create({ collection: 'media', filePath: '...' })` to register existing files triggers Payload's upload processor, which:
- Re-processes the image through Sharp
- Creates new resized variants with deduplicated filenames (`-2.jpg`, `-3.jpg`)
- Stores the NEW filenames in the database, not the originals

This can double your file count.

### The Fix
Write directly to the database (SQLite example), bypassing Payload's upload processor entirely:
```python
import sqlite3, uuid

conn = sqlite3.connect('your-database.db')
cursor = conn.cursor()

# Insert into media table (id is autoincrement integer)
cursor.execute("""INSERT INTO media (
    alt, url, thumbnail_u_r_l, filename, mime_type, filesize,
    width, height, focal_x, focal_y, ...sizes...
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 50, 50, ...)""", values)

# For array tables (e.g., photo_galleries_photos, race_results_race_meet_files):
# - id column is TEXT (UUID), must be generated
# - _parent_id is FK to parent table
# - _order is 1-based position
cursor.execute("""INSERT INTO photo_galleries_photos (
    id, photo_id, caption, _parent_id, _order
) VALUES (?, ?, ?, ?, ?)""", (str(uuid.uuid4()), media_id, caption, gallery_id, order))
```

### Key Schema Details
- `media` table: `id` is autoincrement integer
- Array tables: `id` is TEXT (UUID), must be generated with `uuid.uuid4()`
- Array tables have `_parent_id` (FK to parent) and `_order` (1-based position)
- Upload fields store `file_id` as FK to `media.id`

---

## Folders Feature (Payload v3 Experimental)

Enables grid/thumbnail toggle for upload collections in admin.

```ts
// payload.config.ts — root level
folders: {},

// Collection level
export const Media: CollectionConfig = {
  slug: 'media',
  folders: true,
  // ...
}
```

Adds a `payload-folders` system collection and `folder_id` columns. Requires a migration.

---

## Disaster Recovery

If the database and all uploaded media need to be restored:

```bash
# 1. Restore DB from git backup
npm run restore:db

# 2. Re-register media files and link to galleries/collections
npm run import:media

# 3. Re-create admin user
npm run dev  # visit /admin to create first user

# 4. Back up the restored DB
npm run backup:db
```

Prerequisite: You need a backup workflow set up with `backup:db` and `restore:db` npm scripts, and a `reimport-media` script that does direct database inserts (see "Bulk Media Import" section above).
