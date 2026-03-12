# Divi 5 Module-Specific Attributes Reference

Module-specific properties unique to each module. For universal decoration attributes (background, spacing, border, font, sizing, position, scroll, transform, filters, animation, conditions, CSS), see `universal-attributes.md`.

## Table of Contents

1. [Section](#section)
2. [Row](#row)
3. [Column](#column)
4. [Text](#text)
5. [Heading](#heading)
6. [Blurb](#blurb)
7. [Image](#image)
8. [Button](#button)
9. [Icon](#icon)
10. [Slider](#slider)
11. [Accordion](#accordion)
12. [Tabs](#tabs)
13. [Toggle](#toggle)
14. [Blog](#blog)
15. [Contact Form](#contact-form)
16. [Fullwidth Header](#fullwidth-header)

---

## Block Format Reminder

Divi 5 uses Gutenberg blocks, NOT D4 shortcodes:

```html
<!-- wp:divi/module-name {"attrs":{"module":{...},"element":{...}}} -->innerHTML<!-- /wp:divi/module-name -->
```

Top-level element keys vary per module (e.g., `module`, `button`, `title`, `content`, `image`, `icon`). Each element can contain `decoration`, `advanced`, `meta`, and `innerContent`.

The `{device}` placeholder represents responsive breakpoints: `desktop`, `tablet`, `phone`.

---

## Section

- **Block:** `divi/section`
- **D4 shortcode:** `et_pb_section`
- **Element:** `module`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.type.{device}.value` | `"regular"`, `"fullwidth"`, `"specialty"` | Section type |
| `module.advanced.innerShadow.{device}.value` | `"on"` / `"off"` | Inner shadow effect |
| `module.advanced.gutter.{device}.value.width` | `"1"` to `"4"` | Column gutter width |
| `module.advanced.gutter.{device}.value.makeEqual` | `"on"` / `"off"` | Equalize column heights |
| `module.advanced.dividers.top.*` | object | Top section divider config |
| `module.advanced.dividers.bottom.*` | object | Bottom section divider config |
| `innerSizing.decoration.sizing.{device}.value.width` | CSS value | Inner content width |
| `innerSizing.decoration.sizing.{device}.value.maxWidth` | CSS value | Inner content max-width |
| `innerSizing.decoration.sizing.{device}.value.alignment` | `"left"`, `"center"`, `"right"` | Inner content alignment |

### Example

```html
<!-- wp:divi/section {"attrs":{"module":{"decoration":{"background":{"desktop":{"value":{"color":"#f7f7f7"}}}},"spacing":{"desktop":{"value":{"padding":{"top":"60px","bottom":"60px"}}}}},"advanced":{"type":{"desktop":{"value":"regular"}},"gutter":{"desktop":{"value":{"width":"3","makeEqual":"on"}}}}}}} -->
<!-- wp:divi/row ... -->...<!-- /wp:divi/row -->
<!-- /wp:divi/section -->
```

---

## Row

- **Block:** `divi/row`
- **D4 shortcode:** `et_pb_row`
- **Element:** `module`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.columnStructure.{device}.value` | `"4_4"`, `"2_4,2_4"`, `"1_4,3_4"`, `"1_4,1_4,2_4"`, `"1_4,1_4,1_4,1_4"`, etc. | Column layout using quarters (1_4=25%, 2_4=50%, 3_4=75%, 4_4=100%) |

### Example

```html
<!-- wp:divi/row {"attrs":{"module":{"advanced":{"columnStructure":{"desktop":{"value":"2_4,2_4"}}},"decoration":{"sizing":{"desktop":{"value":{"width":"80%","maxWidth":"1080px"}}}}}}} -->
<!-- wp:divi/column ... -->...<!-- /wp:divi/column -->
<!-- wp:divi/column ... -->...<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
```

---

## Column

- **Block:** `divi/column`
- **D4 shortcode:** `et_pb_column`
- **Element:** `module`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.type.{device}.value` | `"4_4"`, `"2_4"`, `"1_4"`, `"3_4"` | Column width fraction (quarters) |

### Example

```html
<!-- wp:divi/column {"attrs":{"module":{"advanced":{"type":{"desktop":{"value":"2_4"}}},"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"20px","right":"20px","bottom":"20px","left":"20px"}}}}}}}} -->
<!-- wp:divi/text ... -->...<!-- /wp:divi/text -->
<!-- /wp:divi/column -->
```

---

## Text

- **Block:** `divi/text`
- **D4 shortcode:** `et_pb_text`
- **Elements:** `module`, `content`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `content.innerContent.{device}.value` | HTML string | The text/HTML content |
| `content.decoration.bodyFont.body.font.{device}.value.*` | font properties | Body text font settings |
| `content.decoration.bodyFont.link.font.{device}.value.*` | font properties | Link font settings |
| `content.decoration.bodyFont.ul.font.{device}.value.*` | font properties | Unordered list font settings |
| `content.decoration.bodyFont.ol.font.{device}.value.*` | font properties | Ordered list font settings |
| `content.decoration.bodyFont.quote.font.{device}.value.*` | font properties | Blockquote font settings |
| `content.decoration.headingFont.h1.font.{device}.value.*` | font properties | H1 font settings |
| `content.decoration.headingFont.h2.font.{device}.value.*` | font properties | H2 font settings |
| `content.decoration.headingFont.h3.font.{device}.value.*` | font properties | H3 font settings |
| `content.decoration.headingFont.h4.font.{device}.value.*` | font properties | H4 font settings |
| `content.decoration.headingFont.h5.font.{device}.value.*` | font properties | H5 font settings |
| `content.decoration.headingFont.h6.font.{device}.value.*` | font properties | H6 font settings |

### Example

```html
<!-- wp:divi/text {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"20px"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>Welcome to our site. We build <strong>beautiful</strong> websites with Divi 5.</p>"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"size":"16px","lineHeight":"1.8","color":"#333333"}}}}},"headingFont":{"h2":{"font":{"desktop":{"value":{"size":"28px","weight":"700","color":"#2d3436"}}}}}}}}} -->
<!-- /wp:divi/text -->
```

---

## Heading

- **Block:** `divi/heading`
- **D4 shortcode:** `et_pb_heading` (new in D5, no direct D4 equivalent)
- **Elements:** `module`, `title`, `subtitle`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Heading text |
| `title.decoration.font.font.{device}.value.headingLevel` | `"h1"` through `"h6"` | HTML heading level |
| `title.decoration.font.font.{device}.value.*` | font properties | Heading font (size, weight, color, etc.) |
| `subtitle.innerContent.{device}.value` | string | Subtitle text |
| `subtitle.decoration.font.font.{device}.value.*` | font properties | Subtitle font settings |

### Example

```html
<!-- wp:divi/heading {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"30px"}}}}}},"title":{"innerContent":{"desktop":{"value":"Our Services"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","size":"42px","weight":"700","color":"#2d3436","letterSpacing":"1px"}}}}}},"subtitle":{"innerContent":{"desktop":{"value":"What we do best"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"18px","color":"#636e72","style":["italic"]}}}}}}}} -->
<!-- /wp:divi/heading -->
```

---

## Blurb

- **Block:** `divi/blurb`
- **D4 shortcode:** `et_pb_blurb`
- **Elements:** `module`, `image`, `title`, `content`, `icon`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.imageIcon.{device}.value.use` | `"icon"`, `"image"`, `"none"` | Display icon, image, or neither |
| `module.advanced.imageIcon.{device}.value.placement` | `"top"`, `"left"` | Icon/image position relative to text |
| `image.innerContent.{device}.value.src` | URL | Image source (when using image) |
| `title.innerContent.{device}.value` | string | Blurb title |
| `title.decoration.font.font.{device}.value.*` | font properties | Title font settings |
| `content.innerContent.{device}.value` | HTML string | Body content |
| `icon.decoration.icon.{device}.value.color` | hex color | Icon color |
| `icon.decoration.icon.{device}.value.size` | CSS value | Icon size |

### Example

```html
<!-- wp:divi/blurb {"attrs":{"module":{"advanced":{"imageIcon":{"desktop":{"value":{"use":"icon","placement":"top"}}}},"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"30px","right":"30px","bottom":"30px","left":"30px"}}}},"background":{"desktop":{"value":{"color":"#ffffff"}}}}},"icon":{"decoration":{"icon":{"desktop":{"value":{"color":"#0984e3","size":"64px"}}}}},"title":{"innerContent":{"desktop":{"value":"Web Design"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"22px","weight":"600","color":"#2d3436"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>We craft responsive, modern websites tailored to your brand.</p>"}}}}} -->
<!-- /wp:divi/blurb -->
```

---

## Image

- **Block:** `divi/image`
- **D4 shortcode:** `et_pb_image`
- **Elements:** `module`, `image`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `image.innerContent.{device}.value.src` | URL | Image source URL |
| `image.innerContent.{device}.value.alt` | string | Alt text |
| `image.advanced.lightbox.{device}.value` | `"on"` / `"off"` | Enable lightbox |
| `image.advanced.showInLightbox.{device}.value` | `"on"` / `"off"` | Show in lightbox gallery |

### Example

```html
<!-- wp:divi/image {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"20px"}}}},"border":{"desktop":{"value":{"radius":{"topLeft":"8px","topRight":"8px","bottomRight":"8px","bottomLeft":"8px"}}}}}},"image":{"innerContent":{"desktop":{"value":{"src":"https://example.com/photo.jpg","alt":"Team photo at the office"}}},"advanced":{"lightbox":{"desktop":{"value":"on"}}}}}} -->
<!-- /wp:divi/image -->
```

---

## Button

- **Block:** `divi/button`
- **D4 shortcode:** `et_pb_button`
- **Elements:** `module`, `button`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `button.innerContent.{device}.value.text` | string | Button label |
| `button.innerContent.{device}.value.linkUrl` | URL | Button link |
| `button.innerContent.{device}.value.linkTarget` | `"_blank"` / `""` | Open in new tab or same window |
| `button.decoration.button.{device}.value.enable` | `"on"` / `"off"` | Enable custom button styling |
| `button.decoration.button.{device}.value.icon.enable` | `"on"` / `"off"` | Show button icon |
| `button.decoration.button.{device}.value.icon.settings` | icon identifier | Icon unicode or identifier |
| `button.decoration.button.{device}.value.icon.color` | hex color | Icon color |
| `button.decoration.button.{device}.value.icon.placement` | `"right"` / `"left"` | Icon position |
| `button.decoration.button.{device}.value.icon.onHover` | `"on"` / `"off"` | Show icon only on hover |
| `button.decoration.button.{device}.value.alignment` | `"left"`, `"center"`, `"right"` | Button alignment |

The `button` element also supports its own `decoration` properties for font, spacing, border, and background (independent of the module-level decoration).

### Example

```html
<!-- wp:divi/button {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"top":"20px"}}}}}},"button":{"innerContent":{"desktop":{"value":{"text":"Get Started","linkUrl":"https://example.com/signup","linkTarget":"_blank"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on","alignment":"center","icon":{"enable":"on","placement":"right","onHover":"on","color":"#ffffff"}}}},"background":{"desktop":{"value":{"color":"#0984e3"}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff","size":"16px","weight":"600"}}}},"spacing":{"desktop":{"value":{"padding":{"top":"12px","right":"32px","bottom":"12px","left":"32px"}}}},"border":{"desktop":{"value":{"radius":{"topLeft":"4px","topRight":"4px","bottomRight":"4px","bottomLeft":"4px"}}}}}}}} -->
<!-- /wp:divi/button -->
```

---

## Icon

- **Block:** `divi/icon`
- **D4 shortcode:** `et_pb_icon`
- **Elements:** `module`, `icon`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `icon.innerContent.{device}.value` | icon identifier | The icon to display |
| `icon.decoration.icon.{device}.value.color` | hex color | Icon color |
| `icon.decoration.icon.{device}.value.size` | CSS value | Icon size |
| `icon.decoration.icon.{device}.value.useSize` | `"on"` / `"off"` | Use custom size |

### Example

```html
<!-- wp:divi/icon {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"15px"}}}}}},"icon":{"innerContent":{"desktop":{"value":"&#xe090;"}},"decoration":{"icon":{"desktop":{"value":{"color":"#e17055","size":"48px","useSize":"on"}}}}}}} -->
<!-- /wp:divi/icon -->
```

---

## Slider

- **Block:** `divi/slider`
- **D4 shortcode:** `et_pb_slider`
- **Elements:** `module`, child `divi/slide` blocks

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.showArrows.{device}.value` | `"on"` / `"off"` | Show navigation arrows |
| `module.advanced.showPagination.{device}.value` | `"on"` / `"off"` | Show dot pagination |
| `module.advanced.autoPlay.{device}.value` | `"on"` / `"off"` | Auto-advance slides |
| `module.advanced.autoPlaySpeed.{device}.value` | string (ms) | Auto-play interval in milliseconds |

Each `divi/slide` child block has its own heading, content/description, button, and background elements.

### Example

```html
<!-- wp:divi/slider {"attrs":{"module":{"advanced":{"showArrows":{"desktop":{"value":"on"}},"showPagination":{"desktop":{"value":"on"}},"autoPlay":{"desktop":{"value":"on"}},"autoPlaySpeed":{"desktop":{"value":"5000"}}}}}} -->
<!-- wp:divi/slide {"attrs":{"title":{"innerContent":{"desktop":{"value":"Welcome to Our Agency"}}},"content":{"innerContent":{"desktop":{"value":"<p>We create digital experiences that matter.</p>"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Learn More","linkUrl":"/about"}}}},"module":{"decoration":{"background":{"desktop":{"value":{"color":"#2d3436"}}}}}}} -->
<!-- /wp:divi/slide -->
<!-- wp:divi/slide {"attrs":{"title":{"innerContent":{"desktop":{"value":"Our Portfolio"}}},"content":{"innerContent":{"desktop":{"value":"<p>Browse our latest work.</p>"}}},"module":{"decoration":{"background":{"desktop":{"value":{"color":"#0984e3"}}}}}}} -->
<!-- /wp:divi/slide -->
<!-- /wp:divi/slider -->
```

---

## Accordion

- **Block:** `divi/accordion`
- **D4 shortcode:** `et_pb_accordion`
- **Elements:** `module`, `title`, `content`, `closedToggleIcon`, `openToggle`, `closedToggle`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.decoration.font.font.{device}.value.headingLevel` | `"h1"` through `"h6"` | Heading level for toggle titles |
| `closedToggleIcon.decoration.icon.{device}.value.*` | icon properties | Closed state icon (color, size) |

Contains `divi/accordion-item` child blocks, each with their own `title` and `content` elements.

### Example

```html
<!-- wp:divi/accordion {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"30px"}}}}}},"title":{"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","size":"18px","weight":"600","color":"#2d3436"}}}}}}}} -->
<!-- wp:divi/accordion-item {"attrs":{"title":{"innerContent":{"desktop":{"value":"What services do you offer?"}}},"content":{"innerContent":{"desktop":{"value":"<p>We offer web design, development, SEO, and digital marketing services.</p>"}}}}} -->
<!-- /wp:divi/accordion-item -->
<!-- wp:divi/accordion-item {"attrs":{"title":{"innerContent":{"desktop":{"value":"What is your turnaround time?"}}},"content":{"innerContent":{"desktop":{"value":"<p>Most projects are completed within 4-6 weeks depending on scope.</p>"}}}}} -->
<!-- /wp:divi/accordion-item -->
<!-- /wp:divi/accordion -->
```

---

## Tabs

- **Block:** `divi/tabs`
- **D4 shortcode:** `et_pb_tabs`
- **Elements:** `module`, child `divi/tab` blocks

Contains `divi/tab` child blocks, each with its own `title` and `content` elements.

### Example

```html
<!-- wp:divi/tabs {"attrs":{"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"30px"}}}}}}}} -->
<!-- wp:divi/tab {"attrs":{"title":{"innerContent":{"desktop":{"value":"Overview"}}},"content":{"innerContent":{"desktop":{"value":"<p>Our company was founded in 2010 with a mission to transform digital experiences.</p>"}}}}} -->
<!-- /wp:divi/tab -->
<!-- wp:divi/tab {"attrs":{"title":{"innerContent":{"desktop":{"value":"Features"}}},"content":{"innerContent":{"desktop":{"value":"<p>Key features include responsive design, SEO optimization, and fast load times.</p>"}}}}} -->
<!-- /wp:divi/tab -->
<!-- wp:divi/tab {"attrs":{"title":{"innerContent":{"desktop":{"value":"Pricing"}}},"content":{"innerContent":{"desktop":{"value":"<p>Plans start at $99/month. Contact us for enterprise pricing.</p>"}}}}} -->
<!-- /wp:divi/tab -->
<!-- /wp:divi/tabs -->
```

---

## Toggle

- **Block:** `divi/toggle`
- **D4 shortcode:** `et_pb_toggle`
- **Elements:** `module`, `title`, `content`, `openToggleIcon`, `closedToggleIcon`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.open.{device}.value` | `"on"` / `"off"` | Default open state |
| `title.innerContent.{device}.value` | string | Toggle title text |

### Example

```html
<!-- wp:divi/toggle {"attrs":{"module":{"advanced":{"open":{"desktop":{"value":"off"}}},"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"15px"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"1px","style":"solid","color":"#dfe6e9"}}}}}}},"title":{"innerContent":{"desktop":{"value":"Is there a free trial?"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"18px","weight":"600","color":"#2d3436"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>Yes, we offer a 14-day free trial with full access to all features.</p>"}}}}} -->
<!-- /wp:divi/toggle -->
```

---

## Blog

- **Block:** `divi/blog`
- **D4 shortcode:** `et_pb_blog`
- **Element:** `module`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.postsNumber.{device}.value` | string (number) | Number of posts to display |
| `module.advanced.includeCategories.{device}.value` | string | Comma-separated category IDs |
| `module.advanced.layout.{device}.value` | `"grid"`, `"fullwidth"` | Blog layout style |
| `module.advanced.showThumbnail.{device}.value` | `"on"` / `"off"` | Show featured images |
| `module.advanced.showContent.{device}.value` | `"on"` / `"off"` | Show post content/excerpt |
| `module.advanced.showAuthor.{device}.value` | `"on"` / `"off"` | Show author name |
| `module.advanced.showDate.{device}.value` | `"on"` / `"off"` | Show publish date |
| `module.advanced.showCategories.{device}.value` | `"on"` / `"off"` | Show category labels |

### Example

```html
<!-- wp:divi/blog {"attrs":{"module":{"advanced":{"postsNumber":{"desktop":{"value":"6"}},"layout":{"desktop":{"value":"grid"}},"showThumbnail":{"desktop":{"value":"on"}},"showContent":{"desktop":{"value":"on"}},"showAuthor":{"desktop":{"value":"on"}},"showDate":{"desktop":{"value":"on"}},"showCategories":{"desktop":{"value":"on"}}},"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"40px"}}}}}}}} -->
<!-- /wp:divi/blog -->
```

---

## Contact Form

- **Block:** `divi/contact-form`
- **D4 shortcode:** `et_pb_contact_form`
- **Element:** `module`, child `divi/contact-field` blocks

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.email.{device}.value` | email address | Recipient email |
| `module.advanced.successMessage.{device}.value` | string | Message shown after successful submission |
| `module.advanced.redirectUrl.{device}.value` | URL | Redirect URL after submission |

Contains `divi/contact-field` child blocks for each form field.

### Example

```html
<!-- wp:divi/contact-form {"attrs":{"module":{"advanced":{"email":{"desktop":{"value":"hello@example.com"}},"successMessage":{"desktop":{"value":"Thanks for reaching out! We'll get back to you within 24 hours."}}},"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"40px","right":"40px","bottom":"40px","left":"40px"}}}},"background":{"desktop":{"value":{"color":"#f5f6fa"}}}}}}} -->
<!-- wp:divi/contact-field {"attrs":{"module":{"advanced":{"fieldId":{"desktop":{"value":"name"}},"fieldTitle":{"desktop":{"value":"Name"}},"required":{"desktop":{"value":"on"}}}}}} -->
<!-- /wp:divi/contact-field -->
<!-- wp:divi/contact-field {"attrs":{"module":{"advanced":{"fieldId":{"desktop":{"value":"email"}},"fieldTitle":{"desktop":{"value":"Email"}},"fieldType":{"desktop":{"value":"email"}},"required":{"desktop":{"value":"on"}}}}}} -->
<!-- /wp:divi/contact-field -->
<!-- wp:divi/contact-field {"attrs":{"module":{"advanced":{"fieldId":{"desktop":{"value":"message"}},"fieldTitle":{"desktop":{"value":"Message"}},"fieldType":{"desktop":{"value":"text"}},"fullWidth":{"desktop":{"value":"on"}},"required":{"desktop":{"value":"on"}}}}}} -->
<!-- /wp:divi/contact-field -->
<!-- /wp:divi/contact-form -->
```

---

## Fullwidth Header

- **Block:** `divi/fullwidth-header`
- **D4 shortcode:** `et_pb_fullwidth_header`
- **Elements:** `module`, `title`, `subtitle`, `content`, `button1`, `button2`, `image`, `logo`

Must be placed inside a fullwidth section (`module.advanced.type` = `"fullwidth"`).

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Main heading text |
| `subtitle.innerContent.{device}.value` | string | Subheading text |
| `content.innerContent.{device}.value` | HTML string | Body content |
| `button1.innerContent.{device}.value.text` | string | Primary CTA button text |
| `button1.innerContent.{device}.value.linkUrl` | URL | Primary CTA link |
| `button2.innerContent.{device}.value.text` | string | Secondary CTA button text |
| `button2.innerContent.{device}.value.linkUrl` | URL | Secondary CTA link |
| `image.innerContent.{device}.value.src` | URL | Hero image source |
| `module.advanced.text.text.{device}.value.orientation` | `"left"`, `"center"`, `"right"` | Text alignment/orientation |

### Example

```html
<!-- wp:divi/section {"attrs":{"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}}}}} -->
<!-- wp:divi/fullwidth-header {"attrs":{"module":{"advanced":{"text":{"text":{"desktop":{"value":{"orientation":"center"}}}}},"decoration":{"background":{"desktop":{"value":{"color":"#2d3436","image":{"src":"https://example.com/hero-bg.jpg","parallax":"on"}}}},"spacing":{"desktop":{"value":{"padding":{"top":"120px","bottom":"120px"}}}}}},"title":{"innerContent":{"desktop":{"value":"Build Something Amazing"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"56px","weight":"700","color":"#ffffff","letterSpacing":"2px"}}}}}},"subtitle":{"innerContent":{"desktop":{"value":"Modern web solutions for modern businesses"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"22px","color":"#b2bec3"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>From concept to launch, we bring your vision to life with cutting-edge technology and thoughtful design.</p>"}}},"button1":{"innerContent":{"desktop":{"value":{"text":"Get Started","linkUrl":"/contact"}}},"decoration":{"background":{"desktop":{"value":{"color":"#0984e3"}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff"}}}}}},"button2":{"innerContent":{"desktop":{"value":{"text":"View Portfolio","linkUrl":"/portfolio"}}}},"image":{"innerContent":{"desktop":{"value":{"src":"https://example.com/hero-mockup.png"}}}}}} -->
<!-- /wp:divi/fullwidth-header -->
<!-- /wp:divi/section -->
```
