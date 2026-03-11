---
name: payload-railway-deploy
description: >
  Complete deployment playbook for Payload CMS 3 + Next.js 15 + SQLite sites on Railway.
  Use this skill whenever deploying a Payload CMS project to Railway, setting up Railway
  infrastructure for a Payload site, troubleshooting Railway deployment issues, or starting
  a new Payload project that will eventually deploy to Railway. Triggers on: "deploy to Railway",
  "Railway setup", "Payload deployment", "Railway volume", "Railway sqlite",
  "media upload Railway", "railway.toml".
---

# Payload CMS + Next.js + Railway: Deployment Playbook

This is a rigid reference skill. Follow the documented solutions exactly — they were discovered through painful trial and error and represent the only working approaches for each problem.

For Payload-specific gotchas (CSS isolation, migration safety, bulk media imports, folders feature, disaster recovery), see the Payload skill's `PAYLOAD-GOTCHAS.md` reference.

---

## 1. Railway Deployment — Step by Step

### Architecture
```
Railway Service
├── /app/                    <- Built app (ephemeral, rebuilt each deploy)
│   ├── .next/
│   ├── public/media -> /data/media  (symlink, created at startup)
│   └── backups/db-latest.sql       (committed to git)
└── /data/                   <- Persistent volume (survives deploys)
    ├── your-database.db
    └── media/               <- Uploaded image/PDF files
```

### Setup Steps (in order)

For Railway CLI syntax details, see the **railway** skill. The commands below are the Payload-specific sequence:

```bash
# 1. Install CLIs
brew install gh railway

# 2. Create GitHub repo (private)
gh auth login
gh repo create <name> --private --source=. --push

# 3. Create Railway project via dashboard
#    railway.app -> New Project -> Deploy from GitHub

# 4. Link locally
railway login
railway link

# 5. Create persistent volume (MUST use CLI or dashboard, NOT railway.toml)
railway volume add --mount-path /data

# 6. Set environment variables
railway variable set PAYLOAD_SECRET="$(openssl rand -hex 32)"
railway domain  # creates the domain, outputs the URL
railway variable set NEXT_PUBLIC_SERVER_URL="https://<your-domain>.up.railway.app"

# 7. Push code (triggers first deploy)
git push

# 8. Upload media files to volume (see "Media Upload" section below)
```

### Media Upload to Railway Volume
`railway ssh` stdin piping doesn't work (stdin redirected from `/dev/null`). Use GitHub releases as an intermediary:

```bash
# Create tarball
tar czf /tmp/media.tar.gz -C public/media .

# Upload as temporary GitHub release
gh release create media-upload /tmp/media.tar.gz \
  --repo <user>/<repo> --title "Media" --notes "temp"

# Download and extract inside Railway container
GH_TOKEN=$(gh auth token)
ASSET_ID=$(gh api repos/<user>/<repo>/releases/tags/media-upload \
  --jq '.assets[0].id')

railway ssh "curl -L \
  -H 'Authorization: token ${GH_TOKEN}' \
  -H 'Accept: application/octet-stream' \
  -o /tmp/media.tar.gz \
  'https://api.github.com/repos/<user>/<repo>/releases/assets/${ASSET_ID}' \
  && tar xzf /tmp/media.tar.gz -C /data/media/ \
  && rm /tmp/media.tar.gz"

# Clean up
gh release delete media-upload --repo <user>/<repo> --yes --cleanup-tag
rm /tmp/media.tar.gz
```

---

## 2. Railway Gotchas

### `payload-types.ts` Must Be Committed
Normally gitignored and auto-generated. But Railway builds don't have a database connection during `npm install`/`npm run build`, so `payload generate:types` can't run. The types file must be in the repo.

### No Database During Build Phase
Next.js pre-renders static pages during `npm run build`, which queries the database. On Railway, the persistent volume isn't mounted during build — only at runtime.

**Solution:** Restore a temp DB from the SQL dump during build:
```toml
# railway.toml
[build]
buildCommand = "mkdir -p public/media && node scripts/restore-build-db.mjs /tmp/build.db backups/db-latest.sql && DATABASE_URI=file:/tmp/build.db npm run build"
```

The restore script uses `@libsql/client` (already installed as a Payload dependency) because the Nixpacks build image doesn't have the `sqlite3` CLI.

### `sqlite3` CLI Not Available
Neither the Nixpacks build image nor the runtime container have `sqlite3` installed. All DB operations must use Node.js with `@libsql/client`:
```js
import { createClient } from '@libsql/client'
const client = createClient({ url: `file:${dbPath}` })
// Split SQL dump on ';\n' and execute each statement
```

### Next.js Won't Serve Symlinked `public/` Files
Symlinking `public/media -> /data/media` looks correct (`ls` works, Node `fs` works) but Next.js returns 404 for all files. Next.js doesn't follow symlinks that point outside the project root.

**Solution:** Create a dynamic API route that serves files from the volume:
```ts
// src/app/media/[...path]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import path from 'path'
import fs from 'fs'

const MIME_TYPES: Record<string, string> = {
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.png': 'image/png', '.gif': 'image/gif',
  '.webp': 'image/webp', '.pdf': 'application/pdf',
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const segments = (await params).path
  const filename = segments.join('/')
  if (filename.includes('..')) return new NextResponse('Not found', { status: 404 })

  const volumePath = path.join('/data/media', filename)
  const publicPath = path.join(process.cwd(), 'public', 'media', filename)
  const filePath = fs.existsSync(volumePath) ? volumePath : publicPath

  if (!fs.existsSync(filePath)) return new NextResponse('Not found', { status: 404 })

  const ext = path.extname(filename).toLowerCase()
  const contentType = MIME_TYPES[ext] || 'application/octet-stream'
  const stat = fs.statSync(filePath)
  const buffer = fs.readFileSync(filePath)

  return new NextResponse(buffer, {
    headers: {
      'Content-Type': contentType,
      'Content-Length': stat.size.toString(),
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  })
}
```

For general Railway gotchas (volumes in railway.toml, queued deploys, SSH stdin limitations), see the **railway** skill.

---

## 3. Config File Reference

### railway.toml
```toml
[build]
builder = "nixpacks"
buildCommand = "mkdir -p public/media && node scripts/restore-build-db.mjs /tmp/build.db backups/db-latest.sql && DATABASE_URI=file:/tmp/build.db npm run build"

[deploy]
startCommand = "bash scripts/railway-start.sh"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### scripts/railway-start.sh
```bash
#!/usr/bin/env bash
set -euo pipefail
DB_FILE="/data/your-database.db"

# Restore DB on first deploy
if [ ! -f "$DB_FILE" ]; then
  node scripts/restore-build-db.mjs "$DB_FILE" backups/db-latest.sql
fi

# Symlink media to volume
mkdir -p /data/media
rm -rf public/media 2>/dev/null || true
ln -sfn /data/media public/media

export DATABASE_URI="file:$DB_FILE"
exec npx next start --port "${PORT:-3000}"
```

### scripts/restore-build-db.mjs
```js
import { createClient } from '@libsql/client'
import { readFileSync } from 'fs'

const dbPath = process.argv[2] || '/tmp/build.db'
const dumpPath = process.argv[3] || 'backups/db-latest.sql'

const client = createClient({ url: `file:${dbPath}` })
const sql = readFileSync(dumpPath, 'utf-8')

const statements = sql
  .split(';\n')
  .map(s => s.trim())
  .filter(s => s.length > 0 && !s.startsWith('--'))

for (const stmt of statements) {
  try {
    await client.execute(stmt)
  } catch (e) {
    if (!stmt.startsWith('PRAGMA') && !stmt.startsWith('BEGIN') && !stmt.startsWith('COMMIT')) {
      console.warn(`Warning: ${e.message} — skipping: ${stmt.slice(0, 60)}...`)
    }
  }
}
console.log(`Build DB restored at ${dbPath}`)
```

### Required Environment Variables
| Variable | Value |
|----------|-------|
| `PAYLOAD_SECRET` | Random hex string (`openssl rand -hex 32`) |
| `NEXT_PUBLIC_SERVER_URL` | Full Railway domain URL |

`DATABASE_URI` is set by the startup script — do NOT set it in Railway env vars.

---

## 4. Required npm Scripts

```json
{
  "seed": "npx tsx seed/index.ts",
  "import:media": "python3 scripts/reimport-media.py",
  "backup:db": "bash scripts/backup-db.sh",
  "restore:db": "bash scripts/restore-db.sh"
}
```

### Backup Workflow
```bash
# Before any destructive operation or commit with schema changes
npm run backup:db
git add backups/db-latest.sql
git commit -m "Update DB backup"
git push  # triggers Railway redeploy with fresh data
```

---

## 5. .gitignore Essentials

```gitignore
# DO commit these
backups/db-latest.sql
src/payload-types.ts
public/payload-styles.css
railway.toml
scripts/

# Do NOT commit these
*.db
*.db-shm
*.db-wal
/public/media/
.env
```
