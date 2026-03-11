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

## CRITICAL: Non-Interactive Mode

Claude Code runs in a non-interactive terminal. Railway CLI commands that trigger interactive pickers (service select, project select, confirmation prompts) will FAIL. **Always pass explicit flags.**

### Rules

1. **Always specify `-s <service>`** on commands that target a service
2. **Always specify `-e <environment>`** on commands that target an environment
3. **Always pass `-y`** on destructive commands (delete, redeploy, restart)
4. **Use `--json`** when you need to parse output
5. **Never run bare `railway link`** — always pass `--project`, `--service`, `--environment`

### Authentication

| Env Var | Scope | When to use |
|---------|-------|-------------|
| `RAILWAY_TOKEN` | Single project | CI deploys — scopes all commands to that project automatically, no `--project` needed |
| `RAILWAY_API_TOKEN` | Account/workspace | Cross-project ops — requires `--project` or `railway link` first |

If `railway status` works without auth flags, the user is already logged in via `railway login` and linked via `railway link`.

### Non-Interactive Patterns

```bash
# Link to project (NEVER run bare `railway link`)
railway link --project <PROJECT_ID> --environment production --service backend

# Deploy without streaming
railway up --detach -s backend

# List services (there is NO `railway service list`)
railway service status --all --json

# Redeploy without confirmation
railway service redeploy -s backend -y

# SSH: run a single command (use -- before the command)
railway ssh -s backend -- ls -la /data

# Logs: finite output (no streaming)
railway logs -s backend --lines 100
```

### Common Non-Interactive Mistakes

| Wrong | Right | Why |
|-------|-------|-----|
| `railway link` | `railway link --project X --service Y --environment Z` | Bare link triggers interactive picker |
| `railway service list` | `railway service status --all --json` | `list` subcommand doesn't exist |
| `railway ssh command` | `railway ssh -s name -- command` | Use `--` separator for non-interactive commands |
| `railway volume delete` | `railway volume delete -v <ID> -y` | Needs volume ID and confirmation skip |
| `railway redeploy -y` | `railway service redeploy -s name -y` | Use `service redeploy` subcommand with `-s` |

---

## Command Quick Reference

| Task | Command |
|------|---------|
| Login | `railway login` |
| Create project | `railway init -n "my-project"` |
| Link to project | `railway link --project <ID> --service <NAME> --environment <NAME>` |
| Deploy from directory | `railway up --detach -s <service>` |
| Generate domain | `railway domain -s <service>` |
| Custom domain | `railway domain example.com -s <service>` |
| Set variables | `railway variable set KEY=VALUE -s <service>` |
| List variables | `railway variable list -s <service> --json` |
| Add volume | `railway volume add --mount-path /data -s <service>` |
| List services | `railway service status --all --json` |
| SSH into service | `railway ssh -s <service>` |
| SSH run command | `railway ssh -s <service> -- <command>` |
| Run command with env | `railway run <command>` |
| View deploy logs | `railway logs -s <service> --lines 100` |
| View build logs | `railway logs -s <service> --build --lines 200` |
| Redeploy | `railway service redeploy -s <service> -y` |
| Restart (no rebuild) | `railway service restart -s <service> -y` |
| Check status | `railway status` |

---

## Project Setup

```bash
# Create and link a new project
railway login
railway init -n "my-project"
railway link --project <PROJECT_ID> --service <SERVICE_NAME> --environment production

# Link to an existing project (ALWAYS pass flags — never bare `railway link`)
railway link --project <PROJECT_ID> --service <SERVICE_NAME> --environment production

# With workspace (if user has multiple workspaces)
railway link --project <PROJECT_ID> --service <SERVICE_NAME> --environment production --workspace <WORKSPACE_NAME>
```

### Targeting a Specific Service or Environment

Most commands accept `-s` (service) and `-e` (environment) flags. **Always use them:**

```bash
railway logs -s backend -e production
railway variable set KEY=VALUE -s api -e production
railway ssh -s worker -e production
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
# Add a volume to a specific service
railway volume add --mount-path /data -s backend -e production

# List volumes (JSON for parsing)
railway volume list -s backend -e production --json

# Delete a volume (requires volume ID and -y)
railway volume delete -v <VOLUME_ID> -y

# Attach/detach from services
railway volume attach -v <VOLUME_ID> -s backend
railway volume detach -v <VOLUME_ID> -y

# Update mount path or name
railway volume update -v <VOLUME_ID> --mount-path /new/path --name my-volume
```

**Critical gotchas:**
- `[[volumes]]` in `railway.toml` does NOT work — volumes must be created via CLI or dashboard
- Volumes are NOT mounted during the build phase — only at runtime
- Each volume is per-environment (production volume is separate from staging)

---

## Domains

```bash
# Generate a railway-provided domain (*.up.railway.app)
railway domain -s frontend --json

# Add a custom domain (returns required DNS records)
railway domain example.com -s frontend --json

# Specify the port
railway domain -s frontend --port 3000 --json
```

---

## Deploying

### `railway up` — Deploy from local directory

```bash
# Deploy current directory (always use --detach in non-interactive)
railway up --detach -s backend

# Deploy to a specific service and environment
railway up --detach -s backend -e production

# CI mode (streams build logs, exits after build)
railway up --ci -s backend

# JSON CI mode (implies --ci)
railway up --json -s backend

# Deploy with explicit project (requires --environment too)
railway up --project <PROJECT_ID> --environment production -s backend --detach

# Deploy a subdirectory
railway up ./backend -s backend --detach

# Attach a deploy message
railway up --detach -s backend -m "fix: resolve auth bug"
```

### GitHub-connected deploys

If your Railway project is connected to a GitHub repo, pushing to the branch triggers a deploy automatically. No CLI command needed — just `git push`.

### Redeploy / Restart

```bash
# Redeploy (full rebuild + deploy) — use `service redeploy`
railway service redeploy -s backend -y

# Restart (just restart the container, no rebuild)
railway service restart -s backend -y
```

---

## Logs

**In non-interactive mode, always use `--lines`, `--since`, or `--until` to get finite output instead of streaming.**

```bash
# Last 100 lines (finite, no streaming — preferred for non-interactive)
railway logs -s backend --lines 100

# Build logs
railway logs -s backend --build --lines 200

# Logs from last hour
railway logs -s backend --since 1h

# Time-bounded
railway logs -s backend --since 2026-03-10T00:00:00Z --until 2026-03-11T00:00:00Z

# Filter by level
railway logs -s backend --lines 50 --filter "@level:error"

# JSON output
railway logs -s backend --lines 100 --json

# Stream live (only when user explicitly wants streaming)
railway logs -s backend
```

---

## SSH

```bash
# Interactive shell (always specify service)
railway ssh -s backend

# Run a single command (use -- separator for non-interactive)
railway ssh -s backend -- ls -la /data
railway ssh -s backend -- sqlite3 /data/db.sqlite ".tables"

# With explicit project/environment IDs
railway ssh --project <PROJECT_ID> -s <SERVICE_ID> -e <ENV_ID> -- cat /data/config.json

# Use tmux session (installs tmux if needed)
railway ssh -s backend --session my-debug
```

**Critical gotcha:** `railway ssh` redirects stdin from `/dev/null`. You cannot pipe data into it. To transfer files, use an intermediary (GitHub releases, S3, etc.).

**Critical gotcha:** Without `--` before the command, arguments may be interpreted as railway flags, not as arguments to the remote command.

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
# List all services (there is NO `service list` — use status --all)
railway service status --all --json

# Link to a specific service
railway service link -s backend

# View service status
railway service status -s backend --json

# Redeploy (full rebuild + deploy, skip confirmation)
railway service redeploy -s backend -y

# Restart (container restart only, no rebuild)
railway service restart -s backend -y

# Create a new environment
railway environment new staging

# Delete an environment
railway environment delete staging
```

**Common mistake:** `railway service list` does NOT exist. Use `railway service status --all --json`.

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
