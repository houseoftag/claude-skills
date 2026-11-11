# tstack

All nine skills from [t3dotgg/tstack](https://github.com/t3dotgg/tstack), vendored verbatim on
2026-11-10 from upstream `main` at `1085050f3baed1ac724caa4a8166145fb2ac88af`. MIT licensed — see
`LICENSE-t3dotgg`. The `agents/openai.yaml` files are Codex metadata and are kept unchanged.

## Skills

| Skill | Trigger | What it does |
|---|---|---|
| `full-send` | "full send" | Takes a change to a merged PR unattended: proves it, reviews it, files it, babysits it, merges it. |
| `full-stop` | "full stop" | Same as `full-send`, but stops with the PR ready for the user to merge. |
| `council` | "council" | Review from three models from different providers, looped until they agree. |
| `sol-loop` | "sol loop" | Reviews a change with GPT Sol in a loop until both agents agree. |
| `file-pr` | "file a PR" | Files a short PR that leads with the problem. |
| `takeover` | "take over" | Finishes someone else's PR, branch, or agent thread, and keeps their credit. |
| `babysit-pr` | "babysit" | Watches a PR through CI and review bots, and fixes the real findings. Needs `python3`. |
| `modernize` | "modernize" | Rebases an old PR and decides whether it should still exist. |
| `leaving-pr-comments` | automatic | Formats comments an agent posts on the user's behalf. |

## House settings (2026-11-10)

The skills stay unchanged. The house settings for them live in `houseoftag/claude-config`, in
`skills/merge-gate/SKILL.md` and the "Git & deploy safety" section of the global `CLAUDE.md`:

- With no trigger word, a PR merges when the merge gate passes. "full stop" prevents the merge.
  "full send" means Tag is not watching.
- A merge that deploys to production waits for Tag, unless he said "full send".
- Reviewers are GPT Sol and a new Claude Opus worker. `sol-loop` runs Sol at high effort.
- `council` has two seats, Claude Opus and GPT Sol, and no round limit. No Gemini, Grok, or Fable.

## Local changes to upstream

None.
