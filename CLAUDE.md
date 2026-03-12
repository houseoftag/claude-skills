# Claude Skills Marketplace

This repo is a Claude Code plugin marketplace containing custom skills. It's configured globally via `~/.claude/settings.json` under `extraKnownMarketplaces` with the name `tagvinzant-skills`, sourced from `houseoftag/claude-skills` on GitHub.

## Repo Structure

```
.claude-plugin/marketplace.json    # Plugin catalog (auto-updated by hooks)
.githooks/pre-commit               # CalVer auto-versioning hook
scripts/new-skill.sh               # Scaffold a new skill plugin
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json     # Plugin manifest (version auto-bumped)
    skills/
      <skill-name>/
        SKILL.md                   # The skill (required)
        reference/                 # Deep-dive docs loaded on demand (optional)
        scripts/                   # Executable helpers (optional)
```

## Adding a New Skill

Run the scaffold script:

```bash
./scripts/new-skill.sh <skill-name> "<description>"
```

This creates the plugin directory, plugin.json, a stub SKILL.md, and registers it in marketplace.json. Then:

1. Write the skill content in `plugins/<skill-name>/skills/<skill-name>/SKILL.md`
2. Add `reference/` or `scripts/` directories if the skill needs them
3. Commit and push — the pre-commit hook handles version bumping
4. Enable it in `~/.claude/settings.json`: `"<skill-name>@tagvinzant-skills": true`

## Versioning

Versions use CalVer format: `YYYY.M.patch` (e.g., `2026.3.1`). The patch number increments on each commit that changes a plugin's files, and resets to 1 each new month. This is handled automatically by `.githooks/pre-commit` — never manually edit version numbers.

**Important:** After cloning this repo on a new machine, configure git to use the hooks:

```bash
git config core.hooksPath .githooks
```

## Writing Skills

### SKILL.md Anatomy

```yaml
---
name: skill-name          # Becomes the /slash-command
description: >            # When Claude should use this skill — be specific
  Use when [specific triggers]. Also use for [related scenarios].
---

# Skill Title

Instructions for Claude go here.
```

### Conventions

- **Description field is the trigger.** Claude decides whether to load the skill based on the description. Be explicit about when it should activate — list specific keywords, file types, error messages, and scenarios.
- **Keep SKILL.md under 500 lines.** Move deep reference material to `reference/` files and point to them from SKILL.md.
- **Include code examples.** Show the correct API usage, not just descriptions of it. Wrong API calls are the #1 issue skills prevent.
- **Document pitfalls upfront.** Common mistakes should be near the top, not buried in a reference appendix.
- **Reference files** are only loaded when SKILL.md tells Claude to read them. Use them for detailed docs that aren't always needed.
- **Scripts** in `scripts/` can be executed without being loaded into context. Good for deterministic tasks like audits, linting, or data extraction.

### Testing Skills

Use the `skill-creator` plugin to run eval loops — it spawns test agents with and without the skill and compares output quality, API correctness, and token usage.

## Troubleshooting: Marketplace Plugin Cache

Claude Code clones GitHub marketplaces to `~/.claude/plugins/marketplaces/<name>/` and **never auto-pulls new commits**. After pushing new skills or updates, the local clone stays stale. Symptoms: missing plugins, wrong versions, empty install arrays in `installed_plugins.json`.

**Fix (all three steps required):**

```bash
# 1. Pull the latest into the marketplace clone
git -C ~/.claude/plugins/marketplaces/tagvinzant-skills/ pull origin main

# 2. Delete the plugin cache (forces rebuild from updated clone)
rm -rf ~/.claude/plugins/cache/tagvinzant-skills/

# 3. Clear stale commit SHAs in installed_plugins.json
# Set each tagvinzant-skills entry's array to [] so Claude Code re-installs
# e.g. "payload@tagvinzant-skills": [], "railway@tagvinzant-skills": []
```

Then restart Claude Code. It reads from the now-updated clone and re-populates the cache.

**Why clearing cache alone doesn't work:** `installed_plugins.json` stores a `gitCommitSha` per plugin. Claude Code uses this to read from the marketplace clone at that exact commit. If the clone itself is behind, pulling from a stale SHA returns stale content regardless of cache state.

## Current Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| scrapling | scrapling | Web scraping, website cloning, asset extraction with Scrapling |
| payload | payload, payload-railway-deploy | Payload CMS development + Railway deployment |
| railway | railway | Railway CLI command reference and deployment gotchas |
| divi-5 | divi-5 | Divi 5 theme builder for WordPress |
| wordpress | wordpress | WordPress frontend development via SSH/WP-CLI |
