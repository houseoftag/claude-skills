---
name: divi-5
description: >
  Use when building WordPress sites with Divi 5 theme builder. Triggers on: Divi modules,
  Divi theme options, Divi Builder, Visual Builder, Divi layouts, Divi templates, Divi CSS
  customization, Divi hooks, Divi child themes, divi-5, Divi API, et_pb shortcodes, WP-CLI
  with Divi content. Always use this skill when writing Divi shortcode content or pushing
  Divi layouts via WP-CLI — it prevents trial-and-error with attribute names and ensures
  output is editable in the Visual Builder.
---

# Divi 5 — Building Sites via SSH/WP-CLI

## Golden Rule

Use Divi's native block attributes for every visual property. Never use custom CSS, Code
modules, or inline styles for something Divi has a built-in control for. The test is simple:
**if a human can't edit it in the Visual Builder, you did it wrong.** The VB reads JSON
attributes from block comments — anything outside that JSON is invisible to the builder UI.


## How Divi 5 Stores Content

Divi 5 does NOT use `[et_pb_*]` shortcodes. That is Divi 4. Divi 5 stores content as
Gutenberg-compatible block comments with nested JSON attributes:

```html
<!-- wp:divi/module-name {JSON_ATTRS} -->
innerHTML goes here
<!-- /wp:divi/module-name -->
```

Self-closing modules (no inner HTML):

```html
<!-- wp:divi/module-name {JSON_ATTRS} /-->
```

Module names follow the `divi/*` namespace:
- `divi/section` — top-level container
- `divi/row` — horizontal grouping inside a section
- `divi/column` — vertical slot inside a row
- `divi/text`, `divi/button`, `divi/image`, `divi/blurb`, `divi/heading`, etc.

Pages nest in a strict hierarchy: **section > row > column > modules**. Every module must
live inside this structure. Skipping a level produces invalid output the VB cannot parse.

The JSON attributes ARE the native controls the VB reads. Getting them right means the
builder UI shows all your settings in the correct panels — colors, spacing, fonts,
responsive breakpoints, hover states — everything editable without touching code.


## JSON Attribute Structure

Each block's JSON has top-level keys representing the elements within that module:

- **`module`** — the module container itself (meta, decoration, advanced settings)
- **`content`** — content-related settings (innerContent, fonts)
- **Named elements** — `button`, `title`, `image`, `icon`, etc. (module-specific)

Under each element, the structure is:

- **`decoration`** — visual styling (background, spacing, border, font, sizing, etc.)
- **`advanced`** — behavioral settings (text orientation, link options, HTML attributes)
- **`meta`** — admin label
- **`innerContent`** — the actual content values

### Concrete Example

```json
{
  "module": {
    "meta": {"adminLabel": {"desktop": {"value": "Hero Section"}}},
    "decoration": {
      "background": {"desktop": {"value": {"color": "#ffffff"}}},
      "spacing": {"desktop": {"value": {"padding": {"top": "40px", "bottom": "40px"}}}},
      "border": {"desktop": {"value": {"styles": {"all": {"width": "1px", "color": "#eee", "style": "solid"}}}}},
      "animation": {"desktop": {"value": {"style": "fade", "direction": "up", "duration": "500ms"}}},
      "sizing": {"desktop": {"value": {"width": "100%", "maxWidth": "1200px"}}},
      "boxShadow": {"desktop": {"value": {"style": "preset1", "color": "rgba(0,0,0,0.1)"}}},
      "filters": {"desktop": {"value": {"brightness": "100%"}}},
      "transform": {"desktop": {"value": {"scale": "100%"}}},
      "position": {"desktop": {"value": {"mode": "relative"}}},
      "disabledOn": {"desktop": {"value": ""}}
    },
    "advanced": {
      "text": {"text": {"desktop": {"value": {"color": "light"}}}},
      "htmlAttributes": {"desktop": {"value": {"id": "hero-section", "class": "custom-class"}}},
      "link": {"desktop": {"value": {"url": "", "target": ""}}}
    }
  }
}
```

### Key Attribute Paths

Every value lives at a predictable path. Use these when constructing JSON:

| Property | Path |
|---|---|
| Background color | `module.decoration.background.{device}.value.color` |
| Background gradient | `module.decoration.background.{device}.value.gradient` |
| Background image | `module.decoration.background.{device}.value.image` |
| Padding | `module.decoration.spacing.{device}.value.padding.{top\|right\|bottom\|left}` |
| Margin | `module.decoration.spacing.{device}.value.margin.{top\|right\|bottom\|left}` |
| Border styles | `module.decoration.border.{device}.value.styles.{all\|top\|right\|bottom\|left}.{width\|color\|style}` |
| Border radius | `module.decoration.border.{device}.value.radius` |
| Box shadow | `module.decoration.boxShadow.{device}.value.{style\|horizontal\|vertical\|blur\|spread\|color\|position}` |
| Animation | `module.decoration.animation.{device}.value.{style\|direction\|duration\|delay}` |
| Sizing | `module.decoration.sizing.{device}.value.{width\|maxWidth\|height\|minHeight\|alignment}` |
| Filters | `module.decoration.filters.{device}.value.{hueRotate\|saturate\|brightness\|contrast\|invert\|sepia\|opacity\|blur}` |
| Transform | `module.decoration.transform.{device}.value.{scale\|translate\|rotate\|skew\|origin}` |
| Position | `module.decoration.position.{device}.value.{mode\|origin.*\|offset.*}` |
| Visibility | `module.decoration.disabledOn.{device}.value` |
| ID and Class | `module.advanced.htmlAttributes.{device}.value.{id\|class}` |
| Font | `{element}.decoration.font.font.{device}.value.{family\|weight\|style\|color\|size\|lineHeight\|letterSpacing\|textAlign}` |
| Icon | `{element}.decoration.icon.{device}.value.{color\|size\|useSize}` |
| Content | `{element}.innerContent.{device}.value` |

Replace `{device}` with `desktop`, `tablet`, or `phone`. Replace `{element}` with the
relevant element name (`module`, `content`, `button`, `title`, `image`, etc.).


## Responsive Values

Add tablet and phone device keys alongside desktop to set responsive values:

```json
{
  "module": {
    "decoration": {
      "spacing": {
        "desktop": {"value": {"padding": {"top": "80px", "bottom": "80px"}}},
        "tablet": {"value": {"padding": {"top": "40px", "bottom": "40px"}}},
        "phone": {"value": {"padding": {"top": "20px", "bottom": "20px"}}}
      }
    }
  }
}
```

No `_last_edited` flags needed in Divi 5. The VB detects responsive values from the
presence of tablet/phone keys automatically. If you only set desktop, the VB inherits
that value down — but spacing and font sizes almost always need explicit mobile values
or the layout will break on smaller screens.


## Hover and Sticky States

States use `__hover` and `__sticky` suffixes on the value key within the same device object:

```json
{
  "button": {
    "decoration": {
      "background": {
        "desktop": {
          "value": {"color": "#2ea3f2"},
          "value__hover": {"color": "#1a8cd8"}
        }
      },
      "font": {
        "font": {
          "desktop": {
            "value": {"color": "#ffffff"},
            "value__hover": {"color": "#f0f0f0"}
          }
        }
      }
    }
  }
}
```

This matters because hover effects set via custom CSS won't appear in the VB's hover
state panel, making them invisible to anyone editing the page later.


## Global Colors

Divi stores site-wide colors as Global Color IDs (GCIDs). Reference them instead of
hardcoding hex values so that changing a brand color in one place updates the entire site.

### Reference Format in JSON

```
"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})\$"
```

### Discover Existing GCIDs

```bash
wp option get et_global_colors
```

Always check for existing GCIDs before hardcoding hex values. If the site has a primary
brand color defined as a GCID, use the reference — otherwise a future color change will
miss your modules.


## Anti-Patterns

These mistakes produce output that looks correct on the front end but is broken in the
Visual Builder. Avoid them.

| Don't Do This | Do This Instead | Why |
|---|---|---|
| Use `divi/code` module with `<style>` tags | Set colors/fonts in the module's JSON attributes | Code modules are invisible to VB controls |
| Put CSS in `css.*.mainElement` for native properties | Use `decoration.{property}` paths | CSS fields don't map to VB control panels |
| Hardcode hex when a global color exists | Use the `$variable()` GCID reference | Global colors update site-wide from one place |
| Set only desktop values for spacing/fonts | Add tablet and phone device keys | Without responsive values, mobile layouts break |
| Use D4 shortcode format `[et_pb_*]` | Use D5 block format `<!-- wp:divi/* -->` | D4 shortcodes require conversion; D5 blocks are native |
| Guess at attribute names | Extract from existing content or reference docs | Wrong paths are silently ignored — the VB shows defaults |
| Nest modules outside section/row/column | Always wrap: section > row > column > module | Invalid nesting makes the VB unable to parse the page |


## Complete Page Example

A minimal but complete page with a section, row, column, heading, and button:

```html
<!-- wp:divi/section {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#f7f7f7"}}},"spacing":{"desktop":{"value":{"padding":{"top":"80px","bottom":"80px"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px"}}}}}}} -->
<!-- wp:divi/row {} -->
<!-- wp:divi/column {} -->

<!-- wp:divi/heading {"content":{"innerContent":{"desktop":{"value":"Welcome to Our Site"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"48px","weight":"bold","color":"#333333"}},"phone":{"value":{"size":"28px"}}}}}}} -->
<!-- /wp:divi/heading -->

<!-- wp:divi/text {"module":{"advanced":{"text":{"text":{"desktop":{"value":{"color":"light"}}}}}}} -->
<p>This is body text that appears below the heading.</p>
<!-- /wp:divi/text -->

<!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":"Get Started"}},"decoration":{"background":{"desktop":{"value":{"color":"#2ea3f2"},"value__hover":{"color":"#1a8cd8"}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff","size":"16px"}}}}}}} /-->

<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
<!-- /wp:divi/section -->
```

Note how every visual property lives in the JSON. A human opening this in the VB will see
all settings in the correct panels — background color, padding, font size, hover color —
everything editable with clicks rather than code.


## Workflow: Pushing Content via WP-CLI

### 1. Back Up First

```bash
wp post get <ID> --field=post_content > backup.txt
```

Never push content without a backup. One malformed JSON attribute can blank a page.

### 2. Build Block Content

Write the block comments with correct JSON attributes. Validate JSON before pushing — a
missing comma or unclosed brace silently breaks the module.

### 3. Push the Content

```bash
wp post update <ID> --post_content="$(cat content.html)"
```

### 4. Clear Caches

```bash
wp transient delete --all
```

Also clear any server-side cache (SiteGround, WP Rocket, etc.) to see changes immediately.

### 5. Verify

```bash
wp post get <ID> --field=post_content
```

Check that the output matches what you pushed. Look for escaped characters or truncation.

### 6. Rollback if Needed

```bash
wp post update <ID> --post_content="$(cat backup.txt)"
```


## Theme Builder Templates

Theme Builder templates use post type `et_template`. The same block format applies — they
contain sections, rows, columns, and modules in identical nested block comments. Query them
with:

```bash
wp post list --post_type=et_template --fields=ID,post_title
```


## Extracting Attribute Names from Existing Content

When you encounter a module type you haven't worked with before, extract its attributes
from an existing instance rather than guessing:

```bash
wp post get <ID> --field=post_content | grep -o 'wp:divi/module-name {[^}]*}'
```

This gives you the real attribute structure the VB wrote, which you can use as a template.


## References

For detailed attribute catalogs beyond what this skill covers:

- **Universal decoration paths:** see `reference/universal-attributes.md`
- **Module-specific attributes:** see `reference/module-attributes.md`
- **WP-CLI patterns for Divi sites:** see `reference/wp-cli-patterns.md`
