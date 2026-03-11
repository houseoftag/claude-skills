---
name: railway
description: >
  Use when running Railway CLI commands, deploying to Railway, managing Railway
  services, volumes, variables, domains, or troubleshooting Railway deployments.
  Triggers on: "railway", "railway CLI", "deploy to Railway", "railway volume",
  "railway variables", "railway ssh", "railway logs", "railway domain",
  "railway deploy", "railway up".
---

# Railway CLI Reference

This is a rigid reference skill. Use the exact syntax documented here — Railway CLI errors are often silent or misleading when flags/subcommands are wrong.

**CLI version this was verified against:** 4.31.0

---

## Command Quick Reference

| Task | Command |
|------|---------|
| Login | `railway login` |
| Create project | `railway init -n "my-project"` |
| Link to project | `railway link` |
| Deploy from directory | `railway up` |
| Generate domain | `railway domain` |
| Custom domain | `railway domain example.com` |
| Set variables | `railway variable set KEY=VALUE` |
| List variables | `railway variable list` |
| Add volume | `railway volume add --mount-path /data` |
| SSH into service | `railway ssh` |
| Run command with env | `railway run <command>` |
| View deploy logs | `railway logs` |
| View build logs | `railway logs --build` |
| Redeploy | `railway redeploy -y` |
| Restart (no rebuild) | `railway restart` |
| Check status | `railway status` |

---

## Project Setup

```bash
# Create and link a new project
railway login
railway init -n "my-project"
railway link

# Or link to an existing project (interactive picker)
railway link
```

### Targeting a Specific Service or Environment

Most commands accept `-s` (service) and `-e` (environment) flags:

```bash
railway logs -s backend -e production
railway variable set KEY=VALUE -s api
railway ssh -s worker
```

---

## Variables

**Subcommand style** (correct):

```bash
# Set one or more variables
railway variable set KEY=VALUE
railway variable set KEY1=VALUE1 KEY2=VALUE2

# Set from stdin (for secrets/multiline)
echo "long-value" | railway variable set KEY --stdin

# List all variables
railway variable list

# Delete a variable
railway variable delete KEY

# Skip triggering a redeploy
railway variable set KEY=VALUE --skip-deploys
```

**Common mistakes Claude makes:**
- `railway variables set` — works (alias) but `variable set` is canonical
- `railway variable KEY=VALUE` — WRONG, missing `set` subcommand
- `railway variable --set KEY=VALUE` — WRONG, legacy flag syntax, don't use

---

## Volumes

Volumes provide persistent storage that survives deploys.

```bash
# Add a volume (interactive service picker if not specified)
railway volume add --mount-path /data

# List volumes
railway volume list

# Delete a volume
railway volume delete

# Attach/detach from services
railway volume attach
railway volume detach
```

**Critical gotchas:**
- `[[volumes]]` in `railway.toml` does NOT work — volumes must be created via CLI or dashboard
- Volumes are NOT mounted during the build phase — only at runtime
- Each volume is per-environment (production volume is separate from staging)

---

## Domains

```bash
# Generate a railway-provided domain (*.up.railway.app)
railway domain

# Add a custom domain (returns required DNS records)
railway domain example.com

# Specify which service gets the domain
railway domain -s frontend

# Specify the port
railway domain --port 3000
```

---

## Deploying

### `railway up` — Deploy from local directory

```bash
# Deploy current directory
railway up

# Deploy without streaming logs
railway up --detach

# Deploy to a specific service
railway up -s backend

# Attach a deploy message
railway up -m "fix: resolve auth bug"
```

### GitHub-connected deploys

If your Railway project is connected to a GitHub repo, pushing to the branch triggers a deploy automatically. No CLI command needed — just `git push`.

### Redeploy / Restart

```bash
# Redeploy (full rebuild + deploy)
railway redeploy -y

# Restart (just restart the container, no rebuild)
railway restart
```

---

## Logs

```bash
# Stream live deploy logs
railway logs

# Stream build logs
railway logs --build

# Last 100 lines (no streaming)
railway logs --lines 100

# Logs from last hour
railway logs --since 1h

# Filter by level
railway logs --lines 50 --filter "@level:error"

# Logs from a specific service
railway logs -s backend

# JSON output
railway logs --json
```

---

## SSH

```bash
# Interactive shell
railway ssh

# Run a single command
railway ssh ls /data

# Target a specific service
railway ssh -s worker

# Use tmux session (installs tmux if needed)
railway ssh --session
```

**Critical gotcha:** `railway ssh` redirects stdin from `/dev/null`. You cannot pipe data into it. To transfer files, use an intermediary (GitHub releases, S3, etc.).

---

## Local Development

```bash
# Run a command with Railway env vars injected
railway run npm run dev

# Open a subshell with Railway env vars available
railway shell
```

---

## Services & Environments

```bash
# Link to a specific service
railway service link

# View service status
railway service status

# Create a new environment
railway environment new staging

# Link to an environment
railway environment link production

# Delete an environment
railway environment delete staging
```

---

## railway.toml

Controls build and deploy configuration. Place in project root.

```toml
[build]
builder = "nixpacks"
buildCommand = "npm run build"

[deploy]
startCommand = "npm start"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

**What goes in railway.toml:** build commands, start commands, healthchecks, restart policy.

**What does NOT go in railway.toml:** volumes (use CLI), environment variables (use `variable set`).

---

## Common Gotchas

### Multiple Deploys Queue Up

Setting env vars and adding volumes each trigger a new deploy. If you set 5 vars one at a time, you get 5 queued deploys. Solutions:

```bash
# Set multiple vars at once (single deploy)
railway variable set KEY1=VAL1 KEY2=VAL2 KEY3=VAL3

# Or skip deploys until you're done
railway variable set KEY1=VAL1 --skip-deploys
railway variable set KEY2=VAL2 --skip-deploys
railway variable set KEY3=VAL3
# Only the last one triggers a deploy
```

### Build Phase vs Runtime

- **Build phase:** No volumes mounted, no persistent storage, no database access (if DB is on a volume)
- **Runtime:** Volumes mounted, full access to persistent storage
- Your `buildCommand` cannot rely on anything in a volume

### SSH Stdin

`railway ssh` does not support stdin piping. This will not work:

```bash
# WRONG — stdin is /dev/null
cat file.sql | railway ssh "sqlite3 /data/db.sqlite"
echo "data" | railway ssh "cat > /data/file.txt"
```

Transfer files via GitHub releases, S3, or another HTTP-accessible location, then download inside the container.
