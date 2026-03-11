#!/usr/bin/env bash
#
# Scaffold a new skill plugin and register it in the marketplace.
#
# Usage: ./scripts/new-skill.sh <skill-name> "<description>"
#
# Example:
#   ./scripts/new-skill.sh agent-browser "UI/UX auditing and browser automation with agent-browser CLI"
#
# Creates:
#   plugins/<skill-name>/.claude-plugin/plugin.json
#   plugins/<skill-name>/skills/<skill-name>/SKILL.md (stub)
#   Adds entry to .claude-plugin/marketplace.json

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <skill-name> \"<description>\""
    echo "Example: $0 agent-browser \"UI/UX auditing with agent-browser CLI\""
    exit 1
fi

SKILL_NAME="$1"
DESCRIPTION="$2"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/$SKILL_NAME"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
YEAR_MONTH="$(date +%Y.%-m)"
VERSION="${YEAR_MONTH}.0"

# Check if plugin already exists
if [ -d "$PLUGIN_DIR" ]; then
    echo "Error: Plugin '$SKILL_NAME' already exists at $PLUGIN_DIR"
    exit 1
fi

# Create directory structure
mkdir -p "$PLUGIN_DIR/.claude-plugin"
mkdir -p "$PLUGIN_DIR/skills/$SKILL_NAME"

# Create plugin.json
cat > "$PLUGIN_DIR/.claude-plugin/plugin.json" << EOF
{
  "name": "$SKILL_NAME",
  "version": "$VERSION",
  "description": "$DESCRIPTION",
  "author": {
    "name": "Tag Vinzant"
  },
  "keywords": ["$SKILL_NAME"]
}
EOF

# Create stub SKILL.md
cat > "$PLUGIN_DIR/skills/$SKILL_NAME/SKILL.md" << EOF
---
name: $SKILL_NAME
description: >
  $DESCRIPTION
---

# $SKILL_NAME

TODO: Write skill instructions here.
EOF

# Add to marketplace.json
python3 -c "
import json

with open('$MARKETPLACE', 'r') as f:
    data = json.load(f)

# Check not already registered
for p in data['plugins']:
    if p['name'] == '$SKILL_NAME':
        print('Already registered in marketplace.json')
        exit(0)

data['plugins'].append({
    'name': '$SKILL_NAME',
    'description': '$DESCRIPTION',
    'version': '$VERSION',
    'source': './plugins/$SKILL_NAME',
    'category': 'development'
})

with open('$MARKETPLACE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

echo ""
echo "Scaffolded plugin: $SKILL_NAME (v$VERSION)"
echo ""
echo "  $PLUGIN_DIR/"
echo "  ├── .claude-plugin/plugin.json"
echo "  └── skills/$SKILL_NAME/SKILL.md  ← write your skill here"
echo ""
echo "Registered in marketplace.json."
echo ""
echo "Next steps:"
echo "  1. Write the skill in plugins/$SKILL_NAME/skills/$SKILL_NAME/SKILL.md"
echo "  2. Add reference/ or scripts/ dirs if needed"
echo "  3. Commit — the pre-commit hook handles versioning"
echo "  4. Add \"$SKILL_NAME@tagvinzant-skills\": true to ~/.claude/settings.json"
