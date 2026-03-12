# WP-CLI Patterns for Divi 5

Divi 5 stores content as Gutenberg-compatible block comments with nested JSON in `post_content`:

```html
<!-- wp:divi/section {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#fff"}}}}}} -->
<!-- wp:divi/row {} -->
<!-- wp:divi/column {} -->
<!-- wp:divi/text {} -->
<p>Content</p>
<!-- /wp:divi/text -->
<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
<!-- /wp:divi/section -->
```

## 1. Pushing Content to Posts

The safest pattern uses a heredoc or temp file to avoid shell escaping nightmares with nested JSON.

### Temp File Approach (Recommended)

```bash
# Write content to a temp file
cat > /tmp/divi-content.html << 'DIVIEOF'
<!-- wp:divi/section {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#ffffff"}}}}}} -->
<!-- wp:divi/row {} -->
<!-- wp:divi/column {} -->
<!-- wp:divi/text {} -->
<p>Hello World</p>
<!-- /wp:divi/text -->
<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
<!-- /wp:divi/section -->
DIVIEOF

# Push to post
wp post update 42 --post_content="$(cat /tmp/divi-content.html)"

# Clean up
rm /tmp/divi-content.html
```

### Direct Approach (simple content only)

```bash
wp post update 42 --post_content='<!-- wp:divi/text {} --><p>Simple</p><!-- /wp:divi/text -->'
```

### Creating a New Post

```bash
wp post create --post_type=page --post_title="My Page" --post_status=publish --post_content="$(cat /tmp/divi-content.html)"
```

## 2. Reading Content Back

```bash
# Get the raw post_content
wp post get 42 --field=post_content

# Save to file for inspection
wp post get 42 --field=post_content > page-backup.txt

# Check specific attributes in content
wp post get 42 --field=post_content | python3 -c "
import sys, re, json
content = sys.stdin.read()
# Find all Divi block JSON attributes
for m in re.finditer(r'<!-- wp:divi/(\S+)\s+(\{.*?\})\s*(?:/)?-->', content):
    name, attrs = m.groups()
    try:
        parsed = json.loads(attrs)
        print(f'{name}: {json.dumps(parsed, indent=2)[:200]}')
    except: pass
"
```

## 3. Backup Before Changes

ALWAYS back up before modifying content:

```bash
# Single post backup
wp post get 42 --field=post_content > backup-post-42.txt

# All Divi pages backup
wp post list --post_type=page --posts_per_page=-1 --format=ids | xargs -I{} sh -c 'wp post get {} --field=post_content > backup-post-{}.txt'

# Database backup (nuclear option)
wp db export backup-$(date +%Y%m%d).sql
```

Rollback:

```bash
wp post update 42 --post_content="$(cat backup-post-42.txt)"
```

## 4. Divi Theme Options

```bash
# Read all Divi options
wp option get et_divi

# Read a specific option
wp option get et_divi --format=json | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('accent_color','not set'))"

# Common Divi option keys
# accent_color, secondary_accent_color, font_color, header_color
# page_layout (right_sidebar, left_sidebar, full_width)
# divi_logo, divi_breadcrumb, footer_columns
# vertical_nav, divi_header_style

# Update a Divi option
wp eval "
\$options = get_option('et_divi');
\$options['accent_color'] = '#e74c3c';
update_option('et_divi', \$options);
"
```

## 5. Global Colors

```bash
# List all global colors (GCIDs)
wp option get et_global_colors --format=json

# The output shows color definitions with their gcid slugs
# Use in JSON as: "$variable({"type":"color","value":{"name":"gcid-primary-color","settings":{}}})\$"
```

## 6. Cache Clearing

After any content change, clear caches:

```bash
# Clear all transients (includes Divi's static CSS cache)
wp transient delete --all

# Clear object cache
wp cache flush

# If using a caching plugin
wp cache flush
wp rewrite flush

# Clear Divi-specific static files (if static CSS generation is enabled)
wp eval "
if (function_exists('et_core_clear_wp_cache')) {
    et_core_clear_wp_cache();
}
"
```

## 7. Theme Builder Templates

```bash
# List all Theme Builder templates
wp post list --post_type=et_template --format=table --fields=ID,post_title,post_status

# Read a template's content
wp post get <TEMPLATE_ID> --field=post_content

# Theme Builder templates use the same block format
# They're assigned to pages via conditions stored in post meta

# List template assignments
wp post meta get <TEMPLATE_ID> _et_template_conditions
```

## 8. Shell Escaping Pitfalls

The biggest risk when pushing Divi block content via WP-CLI is JSON escaping. The content contains:
- HTML comment tags (`<!-- -->`)
- Nested JSON with double quotes
- Special characters in content

### Rules:
1. **Always use a temp file** for anything beyond trivial content
2. **Use single-quoted heredoc** (`<< 'EOF'`) to prevent shell variable expansion
3. **Never try to inline complex JSON** in shell arguments
4. **Test with `echo` first** before pushing to a post

### Common mistakes:

```bash
# WRONG: Double quotes in JSON get eaten by shell
wp post update 42 --post_content="<!-- wp:divi/text {"module":{}} -->"

# WRONG: Single quotes break if content has apostrophes
wp post update 42 --post_content='<!-- wp:divi/text {"content":"it's broken"} -->'

# RIGHT: Use a temp file
cat > /tmp/content.html << 'EOF'
<!-- wp:divi/text {"module":{"advanced":{"text":{"text":{"desktop":{"value":{"color":"light"}}}}}}} -->
<p>It's working correctly</p>
<!-- /wp:divi/text -->
EOF
wp post update 42 --post_content="$(cat /tmp/content.html)"
```

## 9. Verification

After pushing content, verify it's correct:

```bash
# Check content was saved correctly
wp post get 42 --field=post_content

# Check for anti-pattern indicators (should return 0)
wp post get 42 --field=post_content | grep -c 'et_pb_code.*<style>'

# Check for responsive values
wp post get 42 --field=post_content | grep -c '"tablet"'
wp post get 42 --field=post_content | grep -c '"phone"'

# Verify JSON is valid within blocks
wp post get 42 --field=post_content | python3 -c "
import sys, re, json
content = sys.stdin.read()
errors = 0
for m in re.finditer(r'<!-- wp:divi/\S+\s+(\{.*?\})\s*(?:/)?-->', content):
    try:
        json.loads(m.group(1))
    except json.JSONDecodeError as e:
        print(f'Invalid JSON: {e}')
        errors += 1
print(f'Checked blocks: {\"all valid\" if errors == 0 else f\"{errors} errors\"}')"
```

## 10. Bulk Operations

```bash
# Update all pages with a specific pattern
wp post list --post_type=page --format=ids | while read id; do
    content=$(wp post get $id --field=post_content)
    # Only modify if it contains Divi blocks
    if echo "$content" | grep -q 'wp:divi'; then
        echo "Processing post $id"
        # Your modification logic here
    fi
done

# Find all posts using a specific module
wp post list --post_type=page --format=ids | while read id; do
    if wp post get $id --field=post_content | grep -q 'wp:divi/contact-form'; then
        echo "Post $id has a contact form"
    fi
done
```
