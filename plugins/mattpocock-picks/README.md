# mattpocock-picks

A curated subset of [mattpocock/skills](https://github.com/mattpocock/skills), vendored here instead
of installing the full 35-skill plugin from Anthropic's official marketplace. Vendored 2026-08-14
from upstream `main`. MIT licensed — see `LICENSE-mattpocock`.

## Why vendored, not subscribed

The upstream plugin is a read-only bundle of 35 skills. All 35 names and descriptions load into
every session, and roughly two thirds of them are a poor fit (a per-repo issue-tracker flow, and
several TypeScript-course-specific skills). Vendoring the wanted ones keeps the session skill list
short and lets us edit them.

## Skills

| Skill | What it does |
|---|---|
| `grill-me` | User-invoked. Runs a `grilling` session. |
| `grilling` | Relentless interview that maps a plan as a decision tree, one round of questions at a time. |
| `grill-with-docs` | Same interview, plus it writes `CONTEXT.md` glossary entries and ADRs as it goes. |
| `domain-modeling` | Builds and sharpens the project's shared vocabulary. Required by `grill-with-docs`. |
| `wait-what` | Say this when a message did not land. Forces a re-pitch in ASD-STE100. |
| `handoff` | Compacts the session into a handoff document for the next agent. |
| `writing-for-agents` | How to write a good `SKILL.md`, `AGENTS.md`, or `CLAUDE.md`. |
| `wizard` | Generates an interactive bash script that walks a human through steps only a human can do. |
| `to-questionnaire` | Turns a decision you cannot answer alone into a Markdown questionnaire for a client. |
| `spec-and-standards-review` | Two-axis diff review — repo standards, and fidelity to the spec — in parallel sub-agents. |

## Local changes to upstream

- `code-review` is renamed `spec-and-standards-review`. Upstream's name collides with Claude Code's
  built-in `/code-review` command.
- That skill's issue lookup pointed at `docs/agents/issue-tracker.md`, written by upstream's
  `setup-matt-pocock-skills` skill, which is not vendored. It now uses `gh` directly.

## Not vendored, and why

- `setup-matt-pocock-skills`, `triage`, `to-tickets`, `to-spec`, `implement`, `wayfinder` — a
  per-repo issue-tracker workflow that overlaps the `lead-dev` plugin.
- `git-guardrails-claude-code` — installs hooks that block `git push` and `git reset --hard`. That
  breaks the pre-authorized push flow for `houseoftag/claude-skills` and `houseoftag/claude-config`.
- `migrate-to-shoehorn`, `setup-ts-deep-modules`, `scaffold-exercises`, `setup-pre-commit` —
  TypeScript-specific, little value for WordPress, Divi, or Shopify work.
- Everything under upstream `skills/in-progress/` — unfinished.
- `ask-matt`, `research`, `tdd`, `codebase-design`, `prototype`, `improve-codebase-architecture`,
  `diagnosing-bugs`, `resolving-merge-conflicts`, `teach` — decent, but overlapping or optional.

## Updating

Upstream ships changes often. To refresh, diff against upstream and re-copy by hand:

```bash
git clone --depth 1 https://github.com/mattpocock/skills.git /tmp/mp-skills
diff -r /tmp/mp-skills/skills/productivity/grilling plugins/mattpocock-picks/skills/grilling
```

Re-apply the two local changes listed above after any refresh of `spec-and-standards-review`.
