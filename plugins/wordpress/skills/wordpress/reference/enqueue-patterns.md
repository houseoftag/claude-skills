# Enqueue System Patterns

## Core Functions

```php
wp_enqueue_style( $handle, $src, $deps, $ver, $media );
wp_enqueue_script( $handle, $src, $deps, $ver, $args );
wp_register_style( $handle, $src, $deps, $ver, $media );   // register without loading
wp_register_script( $handle, $src, $deps, $ver, $args );
wp_dequeue_style( $handle );    // prevent from loading
wp_dequeue_script( $handle );
wp_deregister_style( $handle ); // remove from registry entirely
wp_deregister_script( $handle );
```

## Complete Example

```php
function my_frontend_assets() {
    // Stylesheet with dependency chain
    wp_enqueue_style( 'my-custom-css',
        get_stylesheet_directory_uri() . '/assets/css/custom.css',
        array('my-theme-style'),  // loads after theme style
        '1.0.0',
        'all'  // media: 'all', 'screen', 'print'
    );

    // Script with defer (WordPress 6.3+)
    wp_enqueue_script( 'my-script',
        get_stylesheet_directory_uri() . '/assets/js/main.js',
        array(),
        '1.0.0',
        array( 'strategy' => 'defer', 'in_footer' => true )
    );

    // Script depending on jQuery
    wp_enqueue_script( 'my-jquery-script',
        get_stylesheet_directory_uri() . '/assets/js/slider.js',
        array('jquery'),
        '1.0.0',
        true  // legacy: boolean = in_footer
    );
}
add_action( 'wp_enqueue_scripts', 'my_frontend_assets' );
```

## Conditional Loading

```php
function my_conditional_assets() {
    if ( is_page_template('templates/contact.php') ) {
        wp_enqueue_script( 'google-maps', '...' );
    }
    if ( is_single() ) {
        wp_enqueue_style( 'single-post-styles', '...' );
    }
    if ( is_page('about') ) {
        wp_enqueue_style( 'about-page', '...' );
    }
    if ( function_exists('is_woocommerce') && is_woocommerce() ) {
        wp_enqueue_style( 'woo-custom', '...' );
    }
}
add_action( 'wp_enqueue_scripts', 'my_conditional_assets' );
```

## Dequeuing Plugin Assets (Performance)

```php
function remove_unwanted_assets() {
    // Remove CF7 assets from pages without forms
    if ( ! is_page('contact') ) {
        wp_dequeue_style( 'contact-form-7' );
        wp_dequeue_script( 'contact-form-7' );
    }

    // Remove block library CSS if not using Gutenberg
    wp_dequeue_style( 'wp-block-library' );
    wp_dequeue_style( 'wp-block-library-theme' );
    wp_dequeue_style( 'wc-blocks-style' );

    // Remove emoji scripts
    remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
    remove_action( 'wp_print_styles', 'print_emoji_styles' );
}
// Priority 100 — runs AFTER plugins enqueue
add_action( 'wp_enqueue_scripts', 'remove_unwanted_assets', 100 );
```

## Inline Styles and Scripts

```php
// Inline CSS after an enqueued stylesheet
wp_add_inline_style( 'my-theme-style', '
    .site-header { background-color: #333; }
');

// Inline JS before/after an enqueued script
wp_add_inline_script( 'my-script', '
    const MY_CONFIG = { apiUrl: "https://api.example.com" };
', 'before' );

// Pass PHP data to JavaScript
wp_localize_script( 'my-script', 'myScriptData', array(
    'ajaxUrl'  => admin_url( 'admin-ajax.php' ),
    'nonce'    => wp_create_nonce( 'my_nonce' ),
    'siteUrl'  => home_url(),
    'postId'   => get_the_ID(),
));
```

## Script Loading Strategies (WordPress 6.3+)

```php
// Defer — executes after DOM, maintains order
wp_enqueue_script( 'analytics', '...', array(), '1.0', array( 'strategy' => 'defer' ));

// Async — executes immediately when loaded, NO order guarantee
wp_enqueue_script( 'tracking', '...', array(), '1.0', array( 'strategy' => 'async' ));

// Pre-6.3 fallback via filter
function add_defer_attribute( $tag, $handle ) {
    if ( in_array( $handle, array( 'my-script', 'analytics' ) ) ) {
        return str_replace( ' src', ' defer src', $tag );
    }
    return $tag;
}
add_filter( 'script_loader_tag', 'add_defer_attribute', 10, 2 );
```

## Cleanup: Remove WP Head Bloat

```php
remove_action( 'wp_head', 'wp_generator' );           // WP version
remove_action( 'wp_head', 'wlwmanifest_link' );       // WLW manifest
remove_action( 'wp_head', 'rsd_link' );                // RSD link
remove_action( 'wp_head', 'wp_shortlink_wp_head' );   // Shortlink
remove_action( 'wp_head', 'feed_links_extra', 3 );    // Extra feeds
```
