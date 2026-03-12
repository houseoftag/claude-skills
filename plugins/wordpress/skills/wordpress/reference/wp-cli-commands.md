# WP-CLI Command Reference

## Theme Management

```bash
wp theme list                              # List all themes with status
wp theme activate flavor-child             # Activate a theme
wp theme install flavor --activate         # Install + activate from wp.org
wp theme update --all                      # Update all themes
wp theme get flavor --fields=name,version  # Get specific theme info
wp theme is-active flavor-child            # Check if active (exit code)
wp theme mod list                          # List theme modifications
wp theme mod get header_image              # Get a specific theme mod
wp theme mod set background_color "ff0000" # Set a theme mod
wp theme path                              # Get themes directory path
```

## Plugin Management

```bash
wp plugin list                             # List all plugins with status
wp plugin list --status=active             # Only active plugins
wp plugin activate advanced-custom-fields  # Activate a plugin
wp plugin deactivate plugin-name           # Deactivate
wp plugin install plugin-name --activate   # Install + activate
wp plugin update --all                     # Update all plugins
wp plugin toggle plugin-name               # Toggle active/inactive
wp plugin uninstall plugin-name            # Deactivate + delete data
wp plugin delete plugin-name               # Delete files (no uninstall hook)
wp plugin is-active plugin-name            # Check if active (exit code)
wp plugin verify-checksums --all           # Security: verify file integrity
```

## Cache & Transients

```bash
wp cache flush                             # Flush object cache
wp transient delete --all                  # Delete all transients
wp transient delete --expired              # Delete only expired transients
wp transient get transient_name            # Read a specific transient
wp transient list                          # List all transients
```

## Options (Site Settings)

```bash
wp option get siteurl                      # Get site URL
wp option get blogname                     # Get site title
wp option update blogdescription "New tagline"
wp option list --search="*divi*"           # Search for Divi options
wp option get et_divi --format=json        # Get Divi theme options (JSON)
wp option update permalink_structure '/%postname%/'
wp option patch update et_divi key value   # Update nested serialized option
wp option pluck et_divi key                # Read nested serialized option
```

## Search-Replace (Domain Migrations)

```bash
# ALWAYS dry-run first
wp search-replace 'http://old-domain.com' 'https://new-domain.com' --dry-run

# Execute (skip guid column — it should never be changed)
wp search-replace 'http://old-domain.com' 'https://new-domain.com' --skip-columns=guid

# Staging to production
wp search-replace 'staging.example.com' 'example.com' --all-tables-with-prefix --skip-columns=guid

# Export to SQL instead of modifying in-place
wp search-replace 'old' 'new' --export=migrated.sql

# Regex mode
wp search-replace 'https?://old-domain\.com' 'https://new-domain.com' --regex

# Preview specific tables only
wp search-replace 'old' 'new' wp_posts wp_postmeta --dry-run
```

## Database Operations

```bash
wp db export backup.sql                    # Export full database
wp db export backup.sql --tables=wp_posts,wp_postmeta  # Specific tables
wp db import backup.sql                    # Import database
wp db query "SELECT option_value FROM wp_options WHERE option_name='siteurl'"
wp db optimize                             # Optimize tables
wp db repair                               # Repair corrupted tables
wp db size                                 # Database size
wp db tables                               # List all tables
wp db search "old-domain.com"              # Search for string in DB
wp db check                                # Check table integrity
```

## Media / Image Management

```bash
wp media regenerate --yes                  # Regenerate all thumbnails
wp media regenerate --only-missing         # Only missing sizes
wp media regenerate --image_size=large     # Specific size only
wp media regenerate 123 456               # Specific attachment IDs
wp media import /path/to/images/*          # Import files as attachments
wp media image-size                        # List registered image sizes
```

## Rewrites / Permalinks

```bash
wp rewrite flush                           # Flush rewrite rules
wp rewrite flush --hard                    # Flush + write .htaccess
wp rewrite list                            # List all rewrite rules
wp rewrite structure '/%postname%/'        # Set permalink structure
```

## Posts & Content

```bash
wp post list --post_type=page --fields=ID,post_title,post_status
wp post list --post_type=post --posts_per_page=20 --format=csv
wp post list --post_type=project --meta_key=_featured --meta_value=1
wp post get 123 --fields=post_title,post_status,post_date
wp post update 123 --post_status=draft
wp post delete 123 --force                 # Skip trash
wp post meta get 123 _wp_page_template     # Get page template
wp post meta update 123 custom_field "value"
wp post generate --count=10 --post_type=post  # Generate test posts
```

## Users

```bash
wp user list --role=administrator --fields=ID,user_login,user_email
wp user create newuser user@example.com --role=editor --user_pass=securepass
wp user update 1 --display_name="New Name"
wp user set-role 2 administrator
wp user delete 5 --reassign=1              # Delete user, reassign posts
wp user session destroy --all              # Log out all users
```

## Cron

```bash
wp cron event list                         # List scheduled events
wp cron event run --all                    # Run all due events now
wp cron event delete hook_name             # Delete scheduled event
wp cron test                               # Test if WP-Cron is working
```

## WordPress Core

```bash
wp core version                            # Current WP version
wp core update                             # Update WordPress
wp core update-db                          # Update database after core update
wp core verify-checksums                   # Security: verify core files
```

## Eval (Run PHP in WP Context)

```bash
wp eval 'echo get_option("siteurl");'
wp eval 'echo wp_get_theme()->get("Version");'
wp eval 'global $wp_version; echo $wp_version;'
wp eval-file script.php                    # Run a PHP file in WP context
```

## Performance Diagnostics

```bash
# Check autoloaded options size (common performance issue)
wp db query "SELECT SUM(LENGTH(option_value)) as autoload_size FROM wp_options WHERE autoload = 'yes'"

# Find large autoloaded options
wp db query "SELECT option_name, LENGTH(option_value) as size FROM wp_options WHERE autoload = 'yes' ORDER BY size DESC LIMIT 20"

# Count post revisions (DB bloat)
wp db query "SELECT COUNT(*) FROM wp_posts WHERE post_type = 'revision'"

# Delete all revisions
wp post delete $(wp post list --post_type=revision --format=ids) --force

# Limit revisions going forward
wp config set WP_POST_REVISIONS 5 --raw
```
