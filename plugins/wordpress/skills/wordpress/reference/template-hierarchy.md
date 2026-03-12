# WordPress Template Hierarchy

## Fallback Chains

```
Front Page:       front-page.php → home.php (posts) / page.php (static) → index.php
Blog Home:        home.php → index.php
Single Post:      single-{post-type}-{slug}.php → single-{post-type}.php → single.php → singular.php → index.php
Page:             {custom-template}.php → page-{slug}.php → page-{id}.php → page.php → singular.php → index.php
Category:         category-{slug}.php → category-{id}.php → category.php → archive.php → index.php
Tag:              tag-{slug}.php → tag-{id}.php → tag.php → archive.php → index.php
Custom Taxonomy:  taxonomy-{tax}-{term}.php → taxonomy-{tax}.php → taxonomy.php → archive.php → index.php
Author:           author-{nicename}.php → author-{id}.php → author.php → archive.php → index.php
Date:             date.php → archive.php → index.php
Search:           search.php → index.php
404:              404.php → index.php
Attachment:       {mime-type}.php → attachment.php → single-attachment-{slug}.php → single.php → index.php
```

## Custom Page Templates

```php
<?php
/**
 * Template Name: Full Width No Sidebar
 * Template Post Type: page, post
 */
get_header();
// template content
get_footer();
```

## Template Parts

```php
// Load a template part
get_template_part( 'template-parts/content', 'page' );
// Looks for: template-parts/content-page.php → template-parts/content.php

// Pass data to template parts (WP 5.5+)
get_template_part( 'template-parts/card', 'project', array(
    'title' => $project_title,
    'image' => $thumbnail_url,
));
// Access in the part via $args['title'], $args['image']
```

## Filter Template Selection

```php
add_filter( 'page_template', function( $template ) {
    if ( is_page( 'special-page' ) ) {
        $new_template = get_stylesheet_directory() . '/templates/special.php';
        if ( file_exists( $new_template ) ) {
            return $new_template;
        }
    }
    return $template;
});
```

## Divi + Template Hierarchy

Divi's Theme Builder overrides the standard template hierarchy. When a Theme Builder template is assigned to a page/post type, it takes precedence over PHP template files. To use standard PHP templates, ensure no Theme Builder template is assigned to that content.

## PHP Patterns for Frontend

### Custom Post Types

```php
function register_project_cpt() {
    register_post_type( 'project', array(
        'labels' => array(
            'name'          => 'Projects',
            'singular_name' => 'Project',
            'add_new_item'  => 'Add New Project',
            'edit_item'     => 'Edit Project',
        ),
        'public'             => true,
        'show_in_rest'       => true,
        'has_archive'        => true,
        'rewrite'            => array( 'slug' => 'projects' ),
        'supports'           => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
        'menu_icon'          => 'dashicons-portfolio',
    ));
}
add_action( 'init', 'register_project_cpt' );
// After registering: wp rewrite flush
```

### Custom Taxonomy

```php
function register_project_taxonomy() {
    register_taxonomy( 'project_type', 'project', array(
        'labels' => array(
            'name'          => 'Project Types',
            'singular_name' => 'Project Type',
        ),
        'public'       => true,
        'hierarchical' => true,  // true = categories, false = tags
        'show_in_rest' => true,
        'rewrite'      => array( 'slug' => 'project-type' ),
    ));
}
add_action( 'init', 'register_project_taxonomy' );
```

### Custom Queries (WP_Query)

```php
$projects = new WP_Query( array(
    'post_type'      => 'project',
    'posts_per_page' => 6,
    'orderby'        => 'date',
    'order'          => 'DESC',
    'post_status'    => 'publish',
));

if ( $projects->have_posts() ) :
    while ( $projects->have_posts() ) : $projects->the_post();
        the_title( '<h2>', '</h2>' );
        the_excerpt();
        the_post_thumbnail( 'medium' );
    endwhile;
    wp_reset_postdata();  // CRITICAL
endif;
```

### Meta Query and Tax Query

```php
// Meta query (custom fields / ACF)
$featured = new WP_Query( array(
    'post_type'  => 'project',
    'meta_query' => array(
        array( 'key' => 'is_featured', 'value' => '1', 'compare' => '=' ),
    ),
));

// Tax query
$web_projects = new WP_Query( array(
    'post_type' => 'project',
    'tax_query' => array(
        array( 'taxonomy' => 'project_type', 'field' => 'slug', 'terms' => 'web-design' ),
    ),
));

// Combined with performance optimization
$complex = new WP_Query( array(
    'post_type'     => 'project',
    'no_found_rows' => true,  // skip pagination count if not paginating
    'meta_query'    => array(
        'relation' => 'AND',
        array( 'key' => 'is_featured', 'value' => '1' ),
        array( 'key' => 'year', 'value' => '2025', 'compare' => '>=' ),
    ),
));
```

### Pagination

```php
$paged = get_query_var( 'paged' ) ? get_query_var( 'paged' ) : 1;
$query = new WP_Query( array(
    'post_type'      => 'project',
    'posts_per_page' => 9,
    'paged'          => $paged,
));

// After loop:
echo paginate_links( array(
    'total'   => $query->max_num_pages,
    'current' => $paged,
));
wp_reset_postdata();
```

### ACF Fields

```php
$value    = get_field( 'field_name' );             // current post
$value    = get_field( 'field_name', $post_id );   // specific post
$option   = get_field( 'phone_number', 'option' ); // options page

// Repeater
if ( have_rows( 'team_members' ) ) :
    while ( have_rows( 'team_members' ) ) : the_row();
        echo esc_html( get_sub_field( 'name' ) );
    endwhile;
endif;
```

### Menus and Sidebars

```php
// Register (in after_setup_theme)
register_nav_menus( array(
    'primary' => 'Primary Navigation',
    'footer'  => 'Footer Navigation',
));

// Output
wp_nav_menu( array(
    'theme_location' => 'primary',
    'container'      => 'nav',
    'container_class'=> 'main-navigation',
    'menu_class'     => 'nav-menu',
    'depth'          => 2,
    'fallback_cb'    => false,
));

// Sidebar
register_sidebar( array(
    'name'          => 'Footer Widget Area',
    'id'            => 'footer-widgets',
    'before_widget' => '<div class="footer-widget %2$s">',
    'after_widget'  => '</div>',
    'before_title'  => '<h4 class="widget-title">',
    'after_title'   => '</h4>',
));

// Display
if ( is_active_sidebar( 'footer-widgets' ) ) {
    dynamic_sidebar( 'footer-widgets' );
}
```

## Body Classes WordPress Provides

Available via `body_class()` for CSS targeting:

| Class | When |
|-------|------|
| `home` | Front page |
| `blog` | Blog posts index |
| `single`, `single-{post-type}`, `postid-{id}` | Single posts |
| `page`, `page-id-{id}`, `page-template-{slug}` | Pages |
| `archive`, `category-{slug}`, `tag-{slug}` | Archives |
| `search`, `search-results`, `search-no-results` | Search |
| `error404` | 404 page |
| `logged-in` | Authenticated user |
| `admin-bar` | Admin toolbar visible |

### Divi Body Classes

| Class | When |
|-------|------|
| `et_divi_theme` | Divi theme active |
| `et_pb_pagebuilder_layout` | Page uses Divi Builder |
| `et_fb` | Visual Builder is open (editing) |
| `et-db` | Divi Builder mode |
