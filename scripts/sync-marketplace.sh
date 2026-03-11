#!/bin/bash
# Syncs the local marketplace clone and clears stale plugin cache.
# Run automatically via Claude Code SessionStart hook.

MARKETPLACE_NAME="tagvinzant-skills"
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/$MARKETPLACE_NAME"
CACHE_DIR="$HOME/.claude/plugins/cache/$MARKETPLACE_NAME"
INSTALLED="$HOME/.claude/plugins/installed_plugins.json"

# Exit silently if marketplace clone doesn't exist yet
[ -d "$MARKETPLACE_DIR/.git" ] || exit 0

# Check if remote has new commits
LOCAL_SHA=$(git -C "$MARKETPLACE_DIR" rev-parse HEAD 2>/dev/null)
git -C "$MARKETPLACE_DIR" fetch origin main --quiet 2>/dev/null
REMOTE_SHA=$(git -C "$MARKETPLACE_DIR" rev-parse origin/main 2>/dev/null)

# Nothing to do if already up to date
[ "$LOCAL_SHA" = "$REMOTE_SHA" ] && exit 0

# Pull latest
git -C "$MARKETPLACE_DIR" pull origin main --quiet 2>/dev/null || exit 0

# Clear the cache so plugins rebuild from the updated clone
rm -rf "$CACHE_DIR"

# Clear stale commit SHAs in installed_plugins.json
if [ -f "$INSTALLED" ]; then
  python3 -c "
import json, sys

with open('$INSTALLED', 'r') as f:
    data = json.load(f)

changed = False
for key in list(data.get('plugins', {})):
    if key.endswith('@$MARKETPLACE_NAME'):
        if data['plugins'][key]:  # non-empty array = stale entry
            data['plugins'][key] = []
            changed = True

if changed:
    with open('$INSTALLED', 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
" 2>/dev/null
fi

echo "Marketplace '$MARKETPLACE_NAME' synced to $(git -C "$MARKETPLACE_DIR" rev-parse --short HEAD)"
