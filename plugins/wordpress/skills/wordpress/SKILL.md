---
name: wordpress
description: >
  Use when building or modifying WordPress sites via SSH and WP-CLI.
  Triggers on: WordPress theme customization, custom CSS, child themes,
  wp-cli commands, enqueue scripts, wp_enqueue_style, add_action,
  add_filter, functions.php, style.css, frontend styling, WordPress hooks,
  WordPress PHP templates, header.php, footer.php, page templates.
  Also use when troubleshooting CSS conflicts with WordPress admin,
  admin toolbar styling issues, or frontend changes bleeding into wp-admin.
---

# WordPress Frontend Development

This skill covers frontend WordPress development via SSH and WP-CLI. It focuses on safely building and styling the public-facing site without breaking the admin panel.

## The #1 Rule: Protect the Admin

Every CSS rule and PHP hook you write must be scoped to the frontend. Broad selectors and wrong hooks are the most common source of admin breakage.

### CSS That Breaks Admin

These selectors target elements shared with the admin toolbar and wp-admin UI:

```css
/* NEVER write these without scoping */
* { margin: 0; padding: 0; }
ul, li { list-style: none; }
a { text-decoration: none; color: inherit; }
img { max-width: 100%; }
input, select, textarea { font-family: inherit; }
body { overflow-x: hidden; }  /* hides admin bar dropdowns */
```

### Safe CSS Scoping

```css
/* Option 1: Exclude wp-admin body class */
body:not(.wp-admin) a { text-decoration: none; }

/* Option 2: Scope under a frontend wrapper */
#page ul { list-style: none; }
#et-main-area a { color: inherit; }  /* Divi wrapper */

/* Option 3: Scope under Divi content areas */
.et_pb_section a { text-decoration: none; }
#main-content .entry-content ul { list-style: none; }
```

### Respect the Admin Bar on Frontend

The admin bar renders on the frontend for logged-in users. WordPress adds `admin-bar` body class and 32px `margin-top` on `<html>`.

```css
/* Sticky headers MUST offset for admin bar */
.admin-bar header.fixed { top: 32px; }
@media screen and (max-width: 782px) {
    .admin-bar header.fixed { top: 46px; }
}
```

The admin bar uses `z-index: 99999`. Frontend elements must stay below this.

### Visual Builder Protection (Divi)

Divi adds `et_fb` body class when the Visual Builder is open. Exclude it to avoid styling the editor:

```css
body:not(.et_fb) .et_pb_section { /* safe frontend-only styles */ }
```

## PHP Hook Safety

### Frontend-Only Hooks

```php
// CORRECT: frontend assets only
add_action( 'wp_enqueue_scripts', 'my_frontend_assets' );

// WRONG: loads on frontend AND admin
add_action( 'init', function() {
    wp_enqueue_style( 'my-style', '...' );  // breaks admin!
});
```

Three enqueue hooks exist — use the right one:
- `wp_enqueue_scripts` — **frontend only** (almost always what you want)
- `admin_enqueue_scripts` — wp-admin only
- `login_enqueue_scripts` — login page only

### The pre_get_posts Guard

This is the most common source of admin breakage from PHP:

```php
// WRONG: modifies admin post listings too
add_action( 'pre_get_posts', function( $query ) {
    $query->set( 'posts_per_page', 5 );
});

// CORRECT: frontend main query only
add_action( 'pre_get_posts', function( $query ) {
    if ( ! is_admin() && $query->is_main_query() ) {
        $query->set( 'posts_per_page', 5 );
    }
});
```

### is_admin() Gotcha

`is_admin()` returns `true` for AJAX requests (they route through `admin-ajax.php`). For true admin-screen-only code:

```php
if ( is_admin() && ! wp_doing_ajax() ) {
    // genuinely admin-only code
}
```

### Key Frontend Hooks Reference

| Hook | Type | Use For |
|------|------|---------|
| `wp_enqueue_scripts` | Action | Enqueue CSS/JS |
| `wp_head` | Action | Meta tags, inline CSS, analytics |
| `wp_footer` | Action | Tracking scripts, modals |
| `body_class` | Filter | Add/remove body CSS classes |
| `the_content` | Filter | Modify post content |
| `pre_get_posts` | Action | Modify main query (guard it!) |
| `template_redirect` | Action | Redirects, access control |
| `after_setup_theme` | Action | Register menus, image sizes, theme support |
| `widgets_init` | Action | Register sidebars/widget areas |
| `script_loader_tag` | Filter | Add defer/async to script tags |
| `excerpt_length` | Filter | Change excerpt word count |
| `excerpt_more` | Filter | Change "read more" text |
| `wp_nav_menu_items` | Filter | Modify menu HTML output |
| `upload_mimes` | Filter | Allow additional file upload types |

### Hooks That Affect Admin (Use With Care)

| Hook | Risk |
|------|------|
| `init` | Fires on admin AND frontend — always guard with `!is_admin()` if frontend-only |
| `admin_init` | Also fires on AJAX requests from frontend |
| `wp_loaded` | Fires everywhere — same caution as `init` |

## Enqueue System

See `reference/enqueue-patterns.md` for complete enqueue examples including conditional loading, dequeuing plugin assets, inline styles, script strategies (defer/async), and wp_localize_script patterns.

Quick reference:

```php
function my_frontend_assets() {
    wp_enqueue_style( 'my-css', get_stylesheet_directory_uri() . '/assets/css/custom.css',
        array(), '1.0.0' );

    wp_enqueue_script( 'my-js', get_stylesheet_directory_uri() . '/assets/js/main.js',
        array(), '1.0.0', array( 'strategy' => 'defer', 'in_footer' => true ) );
}
add_action( 'wp_enqueue_scripts', 'my_frontend_assets' );
```

## Child Theme Essentials

**style.css** (required — `Template` must match parent directory name exactly):
```css
/*
 Theme Name:   Divi Child
 Template:     Divi
 Version:      1.0.0
*/
```

**functions.php** (does NOT override parent — both load, child first):
```php
<?php
function divi_child_enqueue() {
    wp_enqueue_style( 'divi-child', get_stylesheet_uri(), array(), '1.0.0' );
}
add_action( 'wp_enqueue_scripts', 'divi_child_enqueue' );
```

Key rules:
- Template files (page.php, header.php) in child **override** parent
- functions.php in child **does not override** — both run
- `get_stylesheet_directory_uri()` → child theme URL
- `get_template_directory_uri()` → parent theme URL
- `get_theme_file_uri()` → checks child first, falls back to parent

## WP-CLI Quick Reference

Full command reference: `reference/wp-cli-commands.md`

Most-used commands for frontend work:

```bash
wp cache flush                               # Clear object cache
wp transient delete --all                    # Clear transients (incl Divi CSS cache)
wp rewrite flush --hard                      # Rebuild permalinks + .htaccess
wp theme activate flavor-child               # Switch active theme
wp option list --search="*divi*"             # Find Divi options
wp search-replace 'old.com' 'new.com' --skip-columns=guid --dry-run  # ALWAYS dry-run first
wp db export backup.sql                      # Backup before changes
wp media regenerate --only-missing --yes     # Fix missing thumbnails
wp eval 'echo get_option("siteurl");'        # Quick PHP eval in WP context
```

## Security on Output

Always escape when rendering user-controlled or dynamic data:

```php
esc_html( $text );          // Plain text in HTML
esc_attr( $value );         // Inside HTML attributes
esc_url( $url );            // In href/src attributes
wp_kses_post( $content );   // Allow post-safe HTML
```

Always sanitize on input:
```php
sanitize_text_field( $_POST['name'] );
sanitize_email( $_POST['email'] );
absint( $_GET['id'] );
```

## Template Hierarchy

WordPress resolves templates in a fallback chain. See `reference/template-hierarchy.md` for the full chain. Key points:

- Divi's Theme Builder overrides the standard PHP template hierarchy
- Custom page templates need a header comment: `/* Template Name: My Template */`
- Use `get_template_part()` for reusable sections (supports passing `$args` since WP 5.5)
- If a Theme Builder template is assigned, PHP templates are ignored for that content

## Common Mistakes Checklist

- [ ] CSS resets without frontend scoping → breaks admin toolbar
- [ ] `z-index` above 99999 → covers admin bar dropdowns
- [ ] `overflow: hidden` on body → hides admin bar menus
- [ ] Fixed headers without `.admin-bar` offset → covers toolbar
- [ ] Enqueuing on `init` instead of `wp_enqueue_scripts` → loads in admin
- [ ] `pre_get_posts` without `!is_admin()` guard → breaks admin post lists
- [ ] Using `query_posts()` → never use it; use `WP_Query` or `pre_get_posts`
- [ ] Forgetting `wp_reset_postdata()` after custom queries → corrupts global `$post`
- [ ] Echoing in filters instead of returning → output in wrong position
- [ ] Divi numbered classes (`.et_pb_text_0`) → dynamic, changes with module order
- [ ] CSS in Divi Theme Options instead of child theme → not version-controllable
