# Claude Skills

A collection of custom [Claude Code](https://claude.ai/claude-code) skills for web scraping, CMS development, and deployment.

## Skills

### Scrapling

**Plugin:** `scrapling@tagvinzant-skills`

Write Python code using the [Scrapling](https://github.com/D4Vinci/Scrapling) library for web scraping, website cloning, and content extraction. Built for cloning websites into a local dev environment for redesign.

**Covers:**
- Fetching pages with static HTTP, browser-based, and stealth fetchers
- Full-page screenshots via Playwright's `page_action` callback
- Extracting and downloading all multimedia assets (images, videos, PDFs, fonts, stylesheets)
- HTML rewriting with local asset paths
- Multi-page crawling with the Spider framework
- Correct API usage (selectors, response handling, async patterns)

### Payload CMS

**Plugin:** `payload@tagvinzant-skills`

Two skills for [Payload CMS](https://payloadcms.com) development and deployment:

- **payload** — Collections, fields, hooks, access control, queries, database adapters, endpoints, plugin development, and common gotchas. Includes detailed reference docs for each topic.
- **payload-railway-deploy** — Step-by-step deployment playbook for Payload CMS 3 + Next.js 15 + SQLite on [Railway](https://railway.app), covering volume setup, environment variables, media uploads, and disaster recovery.

## Installation

Add the marketplace to your `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "tagvinzant-skills": {
      "source": {
        "source": "github",
        "repo": "houseoftag/claude-skills"
      }
    }
  },
  "enabledPlugins": {
    "scrapling@tagvinzant-skills": true,
    "payload@tagvinzant-skills": true
  }
}
```

Enable whichever plugins you need. Claude Code will pull them from this repo automatically.

## Repo Structure

```
.claude-plugin/
  marketplace.json              # Marketplace catalog
plugins/
  scrapling/
    .claude-plugin/plugin.json  # Plugin manifest
    skills/
      scrapling/SKILL.md        # Scrapling skill
  payload/
    .claude-plugin/plugin.json  # Plugin manifest
    skills/
      payload/
        SKILL.md                # Payload CMS skill
        reference/              # 12 detailed reference docs
      payload-railway-deploy/
        SKILL.md                # Railway deployment skill
```

## Attribution

The Payload CMS skill (`payload` and `payload-railway-deploy`) is derived from the [official Payload CMS Claude plugin](https://github.com/payloadcms/payload/tree/main/tools/claude-plugin), maintained by the Payload team. The reference documentation and core guidance originate from that project. This repo bundles a snapshot for personal portability alongside other skills — if you're only looking for Payload CMS support, consider using the official plugin directly:

```json
{
  "extraKnownMarketplaces": {
    "payload-cms": {
      "source": {
        "source": "git-subdir",
        "url": "https://github.com/payloadcms/payload.git",
        "path": "tools/claude-plugin"
      }
    }
  }
}
```

## License

The Scrapling skill is original work. The Payload CMS skills are derived from the [Payload CMS project](https://github.com/payloadcms/payload) (MIT License).
