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
17. [Divider](#divider)
18. [CTA (Call to Action)](#cta-call-to-action)
19. [Number Counter](#number-counter)
20. [Testimonial](#testimonial)
21. [Pricing Tables](#pricing-tables)
22. [Video](#video)
23. [Team Member](#team-member)
24. [Social Media Follow](#social-media-follow)
25. [Bar Counters](#bar-counters)
26. [Circle Counter](#circle-counter)
27. [Countdown Timer](#countdown-timer)
28. [Icon List](#icon-list)
29. [Audio](#audio)
30. [Login](#login)
31. [Search](#search)
32. [Before/After Image](#beforeafter-image)
33. [Code](#code)
34. [Gallery](#gallery)
35. [Sidebar](#sidebar)
36. [Menu](#menu)
37. [Link](#link)
38. [Signup](#signup-email-optin)
39. [Dropdown](#dropdown)
40. [Group / Group Carousel](#group--group-carousel)
41. [Comments](#comments)
42. [Post Title](#post-title)
43. [Post Content](#post-content)
44. [Portfolio](#portfolio)
45. [Post Navigation](#post-navigation)

---

## Block Format Reminder

Divi 5 uses Gutenberg blocks, NOT D4 shortcodes:

```html
<!-- wp:divi/module-name {"module":{...},"element":{...}} -->innerHTML<!-- /wp:divi/module-name -->
```

**IMPORTANT:** The JSON goes directly in the block comment — do NOT wrap it in an `"attrs"` key.
The WordPress block parser stores this JSON as `$block['attrs']` automatically.

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
<!-- wp:divi/section {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#f7f7f7"}}},"spacing":{"desktop":{"value":{"padding":{"top":"60px","bottom":"60px"}}}}},"advanced":{"type":{"desktop":{"value":"regular"}},"gutter":{"desktop":{"value":{"width":"3","makeEqual":"on"}}}}}} -->
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
<!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"2_4,2_4"}}},"decoration":{"sizing":{"desktop":{"value":{"width":"80%","maxWidth":"1080px"}}}}}} -->
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
<!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"2_4"}}},"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"20px","right":"20px","bottom":"20px","left":"20px"}}}}}}} -->
<!-- wp:divi/text ... -->...<!-- /wp:divi/text -->
<!-- /wp:divi/column -->
```

---

## Text

- **Block:** `divi/text`
- **D4 shortcode:** `et_pb_text`
- **Elements:** `module`, `content`

### Content Approaches

The Text module supports **two ways** to set content:

1. **innerHTML (preferred):** Place HTML between the block tags. The module reads this via `$elements->render(['attrName' => 'content'])` which pulls innerHTML.
2. **JSON attribute:** Set `content.innerContent.{device}.value` in the JSON. Both approaches work.

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| innerHTML (between block tags) | HTML string | The text/HTML content (preferred approach) |
| `content.innerContent.{device}.value` | HTML string | Alternative: content via JSON attributes |
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

### Example (innerHTML approach — preferred)

```html
<!-- wp:divi/text {"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"20px"}}}}}}} -->
<p>Welcome to our site. We build <strong>beautiful</strong> websites with Divi 5.</p>
<!-- /wp:divi/text -->
```

### Example (JSON content approach)

```html
<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"<p>Welcome to our site. We build <strong>beautiful</strong> websites with Divi 5.</p>"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"size":"16px","lineHeight":"1.8","color":"#333333"}}}}}}}} -->
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

**Note:** The heading text goes in `title.innerContent`, NOT `content.innerContent`. The module's render method uses `$elements->render(['attrName' => 'title'])`.

### Example

```html
<!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our Services"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","size":"42px","weight":"700","color":"#2d3436","letterSpacing":"1px"}}}}}},"subtitle":{"innerContent":{"desktop":{"value":"What we do best"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"18px","color":"#636e72","style":"italic"}}}}}}} -->
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
| `title.innerContent.{device}.value.text` | string | Blurb title (**must use `.text` sub-key**) |
| `title.decoration.font.font.{device}.value.*` | font properties | Title font settings |
| `content.innerContent.{device}.value` | HTML string | Body content (plain HTML string, no `.text` needed) |
| `icon.decoration.icon.{device}.value.color` | hex color | Icon color |
| `icon.decoration.icon.{device}.value.size` | CSS value | Icon size |

**IMPORTANT:** The blurb title value is an **object** with a `.text` key, not a plain string. The module checks `$value['text']` internally (BlurbModule.php). Using a plain string for the title will render nothing.

### Example

```html
<!-- wp:divi/blurb {"module":{"advanced":{"imageIcon":{"desktop":{"value":{"use":"icon","placement":"top"}}}},"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"30px","right":"30px","bottom":"30px","left":"30px"}}}},"background":{"desktop":{"value":{"color":"#ffffff"}}}}},"icon":{"decoration":{"icon":{"desktop":{"value":{"color":"#0984e3","size":"64px"}}}}},"title":{"innerContent":{"desktop":{"value":{"text":"Web Design"}}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"22px","weight":"600","color":"#2d3436"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>We craft responsive, modern websites tailored to your brand.</p>"}}}} -->
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
<!-- wp:divi/image {"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"20px"}}}},"border":{"desktop":{"value":{"radius":{"topLeft":"8px","topRight":"8px","bottomRight":"8px","bottomLeft":"8px"}}}}}},"image":{"innerContent":{"desktop":{"value":{"src":"https://example.com/photo.jpg","alt":"Team photo at the office"}}},"advanced":{"lightbox":{"desktop":{"value":"on"}}}}} -->
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
| `button.innerContent.{device}.value.rel` | string | Link rel attribute |
| `button.decoration.button.{device}.value.enable` | `"on"` / `"off"` | Enable custom button styling |
| `button.decoration.button.{device}.value.icon.enable` | `"on"` / `"off"` | Show button icon |
| `button.decoration.button.{device}.value.icon.settings` | icon identifier | Icon unicode or identifier |
| `button.decoration.button.{device}.value.icon.color` | hex color | Icon color |
| `button.decoration.button.{device}.value.icon.placement` | `"right"` / `"left"` | Icon position |
| `button.decoration.button.{device}.value.icon.onHover` | `"on"` / `"off"` | Show icon only on hover |
| `button.decoration.button.{device}.value.alignment` | `"left"`, `"center"`, `"right"` | Button alignment |

**IMPORTANT:** The button value is an **object** with `text`, `linkUrl`, `linkTarget`, and `rel` keys — NOT a plain string. The module reads `$attrs['button']['innerContent']['desktop']['value']['text']` and `['linkUrl']` (ButtonModule.php:138-139).

The `button` element also supports its own `decoration` properties for font, spacing, border, and background (independent of the module-level decoration).

### Example

```html
<!-- wp:divi/button {"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"top":"20px"}}}}}},"button":{"innerContent":{"desktop":{"value":{"text":"Get Started","linkUrl":"https://example.com/signup","linkTarget":"_blank"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on","alignment":"center","icon":{"enable":"on","placement":"right","onHover":"on","color":"#ffffff"}}}},"background":{"desktop":{"value":{"color":"#0984e3"}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff","size":"16px","weight":"600"}}}},"spacing":{"desktop":{"value":{"padding":{"top":"12px","right":"32px","bottom":"12px","left":"32px"}}}},"border":{"desktop":{"value":{"radius":{"topLeft":"4px","topRight":"4px","bottomRight":"4px","bottomLeft":"4px"}}}}}}} -->
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
<!-- wp:divi/icon {"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"15px"}}}}}},"icon":{"innerContent":{"desktop":{"value":"&#xe090;"}},"decoration":{"icon":{"desktop":{"value":{"color":"#e17055","size":"48px","useSize":"on"}}}}}} -->
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

### Slide Child Block (`divi/slide`)

Each `divi/slide` child block has its own elements:

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Slide heading text |
| `content.innerContent.{device}.value` | HTML string | Slide description |
| `button.innerContent.{device}.value.text` | string | Slide button label |
| `button.innerContent.{device}.value.linkUrl` | URL | Slide button link |

### Example

```html
<!-- wp:divi/slider {"module":{"advanced":{"showArrows":{"desktop":{"value":"on"}},"showPagination":{"desktop":{"value":"on"}},"autoPlay":{"desktop":{"value":"on"}},"autoPlaySpeed":{"desktop":{"value":"5000"}}}}} -->
<!-- wp:divi/slide {"title":{"innerContent":{"desktop":{"value":"Welcome to Our Agency"}}},"content":{"innerContent":{"desktop":{"value":"<p>We create digital experiences that matter.</p>"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Learn More","linkUrl":"/about"}}}},"module":{"decoration":{"background":{"desktop":{"value":{"color":"#2d3436"}}}}}} -->
<!-- /wp:divi/slide -->
<!-- wp:divi/slide {"title":{"innerContent":{"desktop":{"value":"Our Portfolio"}}},"content":{"innerContent":{"desktop":{"value":"<p>Browse our latest work.</p>"}}},"module":{"decoration":{"background":{"desktop":{"value":{"color":"#0984e3"}}}}}} -->
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

### Accordion Item Child Block (`divi/accordion-item`)

Each `divi/accordion-item` has:

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Item title text |
| `content.innerContent.{device}.value` | HTML string | Item body content |

### Example

```html
<!-- wp:divi/accordion {"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"30px"}}}}}},"title":{"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","size":"18px","weight":"600","color":"#2d3436"}}}}}}} -->
<!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"What services do you offer?"}}},"content":{"innerContent":{"desktop":{"value":"<p>We offer web design, development, SEO, and digital marketing services.</p>"}}}} -->
<!-- /wp:divi/accordion-item -->
<!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"What is your turnaround time?"}}},"content":{"innerContent":{"desktop":{"value":"<p>Most projects are completed within 4-6 weeks depending on scope.</p>"}}}} -->
<!-- /wp:divi/accordion-item -->
<!-- /wp:divi/accordion -->
```

---

## Tabs

- **Block:** `divi/tabs`
- **D4 shortcode:** `et_pb_tabs`
- **Elements:** `module`, child `divi/tab` blocks

### Tab Child Block (`divi/tab`)

Each `divi/tab` has:

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Tab label |
| `content.innerContent.{device}.value` | HTML string | Tab body content |

### Example

```html
<!-- wp:divi/tabs {"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"30px"}}}}}}} -->
<!-- wp:divi/tab {"title":{"innerContent":{"desktop":{"value":"Overview"}}},"content":{"innerContent":{"desktop":{"value":"<p>Our company was founded in 2010 with a mission to transform digital experiences.</p>"}}}} -->
<!-- /wp:divi/tab -->
<!-- wp:divi/tab {"title":{"innerContent":{"desktop":{"value":"Features"}}},"content":{"innerContent":{"desktop":{"value":"<p>Key features include responsive design, SEO optimization, and fast load times.</p>"}}}} -->
<!-- /wp:divi/tab -->
<!-- wp:divi/tab {"title":{"innerContent":{"desktop":{"value":"Pricing"}}},"content":{"innerContent":{"desktop":{"value":"<p>Plans start at $99/month. Contact us for enterprise pricing.</p>"}}}} -->
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
| `content.innerContent.{device}.value` | HTML string | Toggle body content |

### Example

```html
<!-- wp:divi/toggle {"module":{"advanced":{"open":{"desktop":{"value":"off"}}},"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"15px"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"1px","style":"solid","color":"#dfe6e9"}}}}}}},"title":{"innerContent":{"desktop":{"value":"Is there a free trial?"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"18px","weight":"600","color":"#2d3436"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>Yes, we offer a 14-day free trial with full access to all features.</p>"}}}} -->
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
<!-- wp:divi/blog {"module":{"advanced":{"postsNumber":{"desktop":{"value":"6"}},"layout":{"desktop":{"value":"grid"}},"showThumbnail":{"desktop":{"value":"on"}},"showContent":{"desktop":{"value":"on"}},"showAuthor":{"desktop":{"value":"on"}},"showDate":{"desktop":{"value":"on"}},"showCategories":{"desktop":{"value":"on"}}},"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"40px"}}}}}}} -->
<!-- /wp:divi/blog -->
```

---

## Contact Form

- **Block:** `divi/contact-form`
- **D4 shortcode:** `et_pb_contact_form`
- **Elements:** `module`, `title`, `button`, child `divi/contact-field` blocks

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.email.{device}.value` | email address | Recipient email |
| `module.advanced.successMessage.{device}.value` | string | Message shown after successful submission |
| `module.advanced.redirectUrl.{device}.value` | URL | Redirect URL after submission |

### Contact Field Child Block (`divi/contact-field`)

Contact fields use the `fieldItem` element — NOT `module.advanced`:

| Attribute Path | Values | Description |
|---|---|---|
| `fieldItem.innerContent.{device}.value` | string | Field label / placeholder text |
| `fieldItem.advanced.type.{device}.value` | `"input"`, `"email"`, `"text"` | Field input type |
| `fieldItem.advanced.id.{device}.value` | string | Field ID (used in form submission) |
| `fieldItem.advanced.required.{device}.value` | `"on"` / `"off"` | Whether field is required |
| `fieldItem.advanced.allowedSymbols.{device}.value` | string | Allowed input symbols |
| `fieldItem.advanced.maxLength.{device}.value` | string | Maximum input length |
| `fieldItem.advanced.minLength.{device}.value` | string | Minimum input length |
| `fieldItem.advanced.radioOptions.{device}.value` | array | Radio button options |
| `fieldItem.advanced.checkboxOptions.{device}.value` | array | Checkbox options |
| `fieldItem.advanced.selectOptions.{device}.value` | array | Select dropdown options |

### Example

```html
<!-- wp:divi/contact-form {"module":{"advanced":{"email":{"desktop":{"value":"hello@example.com"}},"successMessage":{"desktop":{"value":"Thanks for reaching out!"}}},"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"40px","right":"40px","bottom":"40px","left":"40px"}}}},"background":{"desktop":{"value":{"color":"#f5f6fa"}}}}}} -->
<!-- wp:divi/contact-field {"fieldItem":{"innerContent":{"desktop":{"value":"Name"}},"advanced":{"type":{"desktop":{"value":"input"}},"id":{"desktop":{"value":"name"}},"required":{"desktop":{"value":"on"}}}}} -->
<!-- /wp:divi/contact-field -->
<!-- wp:divi/contact-field {"fieldItem":{"innerContent":{"desktop":{"value":"Email"}},"advanced":{"type":{"desktop":{"value":"email"}},"id":{"desktop":{"value":"email"}},"required":{"desktop":{"value":"on"}}}}} -->
<!-- /wp:divi/contact-field -->
<!-- wp:divi/contact-field {"fieldItem":{"innerContent":{"desktop":{"value":"Message"}},"advanced":{"type":{"desktop":{"value":"text"}},"id":{"desktop":{"value":"message"}},"required":{"desktop":{"value":"on"}}}}} -->
<!-- /wp:divi/contact-field -->
<!-- /wp:divi/contact-form -->
```

---

## Fullwidth Header

- **Block:** `divi/fullwidth-header`
- **D4 shortcode:** `et_pb_fullwidth_header`
- **Elements:** `module`, `title`, `subhead`, `content`, `buttonOne`, `buttonTwo`, `image`, `logo`

Must be placed inside a fullwidth section (`module.advanced.type` = `"fullwidth"`).

**IMPORTANT:** Element names differ from what you might expect:
- Subtitle uses `subhead` (NOT `subtitle`)
- Buttons use `buttonOne` / `buttonTwo` (NOT `button1` / `button2`)

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Main heading text |
| `subhead.innerContent.{device}.value` | string | Subheading text |
| `content.innerContent.{device}.value` | HTML string | Body content |
| `buttonOne.innerContent.{device}.value.text` | string | Primary CTA button text |
| `buttonOne.innerContent.{device}.value.linkUrl` | URL | Primary CTA link |
| `buttonTwo.innerContent.{device}.value.text` | string | Secondary CTA button text |
| `buttonTwo.innerContent.{device}.value.linkUrl` | URL | Secondary CTA link |
| `image.innerContent.{device}.value.src` | URL | Hero image source |
| `logo.innerContent.{device}.value.src` | URL | Logo image source |
| `module.advanced.text.text.{device}.value.orientation` | `"left"`, `"center"`, `"right"` | Text alignment/orientation |

### Example

```html
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}}}} -->
<!-- wp:divi/fullwidth-header {"module":{"advanced":{"text":{"text":{"desktop":{"value":{"orientation":"center"}}}}},"decoration":{"background":{"desktop":{"value":{"color":"#2d3436"}}},"spacing":{"desktop":{"value":{"padding":{"top":"120px","bottom":"120px"}}}}}},"title":{"innerContent":{"desktop":{"value":"Build Something Amazing"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"56px","weight":"700","color":"#ffffff","letterSpacing":"2px"}}}}}},"subhead":{"innerContent":{"desktop":{"value":"Modern web solutions for modern businesses"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"22px","color":"#b2bec3"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>From concept to launch, we bring your vision to life.</p>"}}},"buttonOne":{"innerContent":{"desktop":{"value":{"text":"Get Started","linkUrl":"/contact"}}},"decoration":{"background":{"desktop":{"value":{"color":"#0984e3"}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff"}}}}}},"buttonTwo":{"innerContent":{"desktop":{"value":{"text":"View Portfolio","linkUrl":"/portfolio"}}}}} -->
<!-- /wp:divi/fullwidth-header -->
<!-- /wp:divi/section -->
```

---

## Divider

- **Block:** `divi/divider`
- **D4 shortcode:** `et_pb_divider`
- **Element:** `module`

### Module-Specific Attributes

The divider has no content attributes — only decoration. It renders as a horizontal line.

| Attribute Path | Values | Description |
|---|---|---|
| `module.decoration.divider.{device}.value.color` | hex color | Divider line color |
| `module.decoration.divider.{device}.value.weight` | CSS value | Divider line thickness |
| `module.decoration.sizing.{device}.value.width` | CSS value | Divider width |

### Example

```html
<!-- wp:divi/divider {"module":{"decoration":{"divider":{"desktop":{"value":{"color":"#0097CE","weight":"3px"}}},"sizing":{"desktop":{"value":{"width":"60px"}}}}}} /-->
```

---

## CTA (Call to Action)

- **Block:** `divi/cta`
- **D4 shortcode:** `et_pb_cta`
- **Elements:** `module`, `title`, `content`, `button`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | CTA heading text |
| `content.innerContent.{device}.value` | HTML string | CTA body content |
| `button.innerContent.{device}.value.text` | string | Button label |
| `button.innerContent.{device}.value.linkUrl` | URL | Button link |

### Example

```html
<!-- wp:divi/cta {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#2d3436"}}},"spacing":{"desktop":{"value":{"padding":{"top":"60px","bottom":"60px"}}}}}},"title":{"innerContent":{"desktop":{"value":"Ready to Get Started?"}},"decoration":{"font":{"font":{"desktop":{"value":{"color":"#ffffff","size":"36px","weight":"700"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>Contact us today for a free consultation.</p>"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Contact Us","linkUrl":"/contact"}}},"decoration":{"background":{"desktop":{"value":{"color":"#0984e3"}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff"}}}}}}} -->
<!-- /wp:divi/cta -->
```

---

## Number Counter

- **Block:** `divi/number-counter`
- **D4 shortcode:** `et_pb_number_counter`
- **Elements:** `module`, `title`, `number`

The number value is animated client-side via JavaScript. It renders as a data attribute, not static text.

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Counter label text |
| `number.innerContent.{device}.value` | string (number) | Target number for animation |
| `number.advanced.enablePercentSign.{device}.value` | `"on"` / `"off"` | Show percent sign after number |

### Example

```html
<!-- wp:divi/number-counter {"title":{"innerContent":{"desktop":{"value":"Projects Completed"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"18px","color":"#636e72"}}}}}},"number":{"innerContent":{"desktop":{"value":"500"}},"advanced":{"enablePercentSign":{"desktop":{"value":"off"}}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"48px","weight":"700","color":"#2d3436"}}}}}}} -->
<!-- /wp:divi/number-counter -->
```

---

## Testimonial

- **Block:** `divi/testimonial`
- **D4 shortcode:** `et_pb_testimonial`
- **Elements:** `module`, `author`, `jobTitle`, `company`, `content`, `portrait`, `quoteIcon`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `author.innerContent.{device}.value` | string | Author name |
| `jobTitle.innerContent.{device}.value` | string | Author job title / position |
| `company.innerContent.{device}.value` | string | Author company name |
| `content.innerContent.{device}.value` | HTML string | Testimonial body text |
| `portrait.innerContent.{device}.value.src` | URL | Author portrait image |

### Example

```html
<!-- wp:divi/testimonial {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#f5f6fa"}}},"border":{"desktop":{"value":{"radius":{"topLeft":"8px","topRight":"8px","bottomRight":"8px","bottomLeft":"8px"}}}}}},"author":{"innerContent":{"desktop":{"value":"John Doe"}},"decoration":{"font":{"font":{"desktop":{"value":{"weight":"600","color":"#2d3436"}}}}}},"content":{"innerContent":{"desktop":{"value":"<p>Excellent service and outstanding results. Highly recommended!</p>"}}},"company":{"innerContent":{"desktop":{"value":"CEO, Acme Corp"}}}} -->
<!-- /wp:divi/testimonial -->
```

---

## Pricing Tables

- **Block:** `divi/pricing-tables` (container)
- **D4 shortcode:** `et_pb_pricing_tables`
- **Child block:** `divi/pricing-table` (individual table)

### Pricing Table Item Elements

Each `divi/pricing-table` child block uses:

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Plan name |
| `subtitle.innerContent.{device}.value` | string | Plan description |
| `price.innerContent.{device}.value` | string | Price amount |
| `currencyFrequency.innerContent.{device}.value.currency` | string | Currency symbol (e.g., `"$"`, `"USD"`) |
| `currencyFrequency.innerContent.{device}.value.per` | string | Billing period (e.g., `"month"`, `"year"`) |
| `content.innerContent.{device}.value` | HTML string | Features list (typically `<ul><li>` items) |
| `button.innerContent.{device}.value.text` | string | CTA button label |
| `button.innerContent.{device}.value.linkUrl` | URL | CTA button link |
| `excluded.innerContent.{device}.value` | HTML string | Excluded features list |

### Example

```html
<!-- wp:divi/pricing-tables {} -->
<!-- wp:divi/pricing-table {"title":{"innerContent":{"desktop":{"value":"Basic"}}},"subtitle":{"innerContent":{"desktop":{"value":"For individuals"}}},"price":{"innerContent":{"desktop":{"value":"29"}}},"currencyFrequency":{"innerContent":{"desktop":{"value":{"currency":"$","per":"month"}}}},"content":{"innerContent":{"desktop":{"value":"<ul><li>10 Projects</li><li>5GB Storage</li><li>Email Support</li></ul>"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Get Started","linkUrl":"/signup"}}}}} -->
<!-- /wp:divi/pricing-table -->
<!-- /wp:divi/pricing-tables -->
```

---

## Video

- **Block:** `divi/video`
- **D4 shortcode:** `et_pb_video`
- **Elements:** `module`, `video`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `video.innerContent.{device}.value.src` | URL | Video URL (YouTube, Vimeo, or direct MP4/WebM) |

### Example

```html
<!-- wp:divi/video {"video":{"innerContent":{"desktop":{"value":{"src":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}}}},"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"bottom":"30px"}}}}}}} -->
<!-- /wp:divi/video -->
```

---

## Team Member

- **Block:** `divi/team-member`
- **D4 shortcode:** `et_pb_team_member`
- **Elements:** `module`, `name`, `position`, `content`, `image`, `social`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `name.innerContent.{device}.value` | string | Team member name |
| `position.innerContent.{device}.value` | string | Job title / position |
| `content.innerContent.{device}.value` | HTML string | Bio / description |
| `image.innerContent.{device}.value.url` | URL | Portrait image (**uses `.url` not `.src`**) |

### Example

```html
<!-- wp:divi/team-member {"name":{"innerContent":{"desktop":{"value":"Jane Smith"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"22px","weight":"700","color":"#2d3436"}}}}}},"position":{"innerContent":{"desktop":{"value":"Chief Executive Officer"}}},"content":{"innerContent":{"desktop":{"value":"<p>Jane brings 15 years of industry leadership.</p>"}}},"image":{"innerContent":{"desktop":{"value":{"url":"https://example.com/jane.jpg"}}}}} -->
<!-- /wp:divi/team-member -->
```

---

## Social Media Follow

- **Block:** `divi/social-media-follow` (container)
- **D4 shortcode:** `et_pb_social_media_follow`
- **Child block:** `divi/social-media-follow-network`

### Social Media Follow Network Elements

Each `divi/social-media-follow-network` child block uses `socialNetwork`:

| Attribute Path | Values | Description |
|---|---|---|
| `socialNetwork.innerContent.{device}.value.title` | string | Network name (e.g., `"facebook"`, `"twitter"`, `"linkedin"`, `"instagram"`) |
| `socialNetwork.innerContent.{device}.value.link` | URL | Profile URL |
| `socialNetwork.innerContent.{device}.value.label` | string | Display label |

### Example

```html
<!-- wp:divi/social-media-follow {} -->
<!-- wp:divi/social-media-follow-network {"socialNetwork":{"innerContent":{"desktop":{"value":{"title":"facebook","link":"https://facebook.com/example","label":"Facebook"}}}}} -->
<!-- /wp:divi/social-media-follow-network -->
<!-- wp:divi/social-media-follow-network {"socialNetwork":{"innerContent":{"desktop":{"value":{"title":"linkedin","link":"https://linkedin.com/company/example","label":"LinkedIn"}}}}} -->
<!-- /wp:divi/social-media-follow-network -->
<!-- /wp:divi/social-media-follow -->
```

---

## Bar Counters

- **Block:** `divi/counters` (container)
- **D4 shortcode:** `et_pb_counters`
- **Child block:** `divi/counter`

### Bar Counter Item Elements

Each `divi/counter` child block uses:

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Bar label text |
| `barProgress.innerContent.{device}.value` | string (number) | Percentage value (0-100) |

### Example

```html
<!-- wp:divi/counters {} -->
<!-- wp:divi/counter {"title":{"innerContent":{"desktop":{"value":"Web Design"}}},"barProgress":{"innerContent":{"desktop":{"value":"90"}}}} -->
<!-- /wp:divi/counter -->
<!-- wp:divi/counter {"title":{"innerContent":{"desktop":{"value":"Development"}}},"barProgress":{"innerContent":{"desktop":{"value":"85"}}}} -->
<!-- /wp:divi/counter -->
<!-- /wp:divi/counters -->
```

---

## Circle Counter

- **Block:** `divi/circle-counter`
- **D4 shortcode:** `et_pb_circle_counter`
- **Elements:** `module`, `title`, `number`, `contentContainer`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Counter label |
| `number.innerContent.{device}.value` | string (number) | Target number (animated via JS) |

### Example

```html
<!-- wp:divi/circle-counter {"title":{"innerContent":{"desktop":{"value":"Customer Satisfaction"}}},"number":{"innerContent":{"desktop":{"value":"95"}}}} -->
<!-- /wp:divi/circle-counter -->
```

---

## Countdown Timer

- **Block:** `divi/countdown-timer`
- **D4 shortcode:** `et_pb_countdown_timer`
- **Elements:** `module`, `title`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Timer heading text |
| `module.advanced.date.{device}.value` | string | Target date (format: `"YYYY-MM-DD HH:MM"`) |

### Example

```html
<!-- wp:divi/countdown-timer {"title":{"innerContent":{"desktop":{"value":"Launch Day"}}},"module":{"advanced":{"date":{"desktop":{"value":"2027-01-01 00:00"}}}}} -->
<!-- /wp:divi/countdown-timer -->
```

---

## Icon List

- **Block:** `divi/icon-list` (container)
- **D4 shortcode:** `et_pb_icon_list` (new in D5)
- **Child block:** `divi/icon-list-item`

### Icon List Item Elements

Each `divi/icon-list-item` child block uses:

| Attribute Path | Values | Description |
|---|---|---|
| `content.innerContent.{device}.value` | string | List item text |
| `icon.innerContent.{device}.value` | icon identifier | Item icon |

### Example

```html
<!-- wp:divi/icon-list {} -->
<!-- wp:divi/icon-list-item {"content":{"innerContent":{"desktop":{"value":"Free shipping on all orders"}}},"icon":{"innerContent":{"desktop":{"value":"&#xe090;"}}}} -->
<!-- /wp:divi/icon-list-item -->
<!-- wp:divi/icon-list-item {"content":{"innerContent":{"desktop":{"value":"24/7 customer support"}}},"icon":{"innerContent":{"desktop":{"value":"&#xe091;"}}}} -->
<!-- /wp:divi/icon-list-item -->
<!-- /wp:divi/icon-list -->
```

---

## Audio

- **Block:** `divi/audio`
- **D4 shortcode:** `et_pb_audio`
- **Elements:** `module`, `title`, `image`, `caption`, `artistName`, `albumName`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Track title |
| `artistName.innerContent.{device}.value` | string | Artist name |
| `albumName.innerContent.{device}.value` | string | Album name |
| `caption.innerContent.{device}.value` | HTML string | Track description |
| `image.innerContent.{device}.value.src` | URL | Album art / cover image |

### Example

```html
<!-- wp:divi/audio {"title":{"innerContent":{"desktop":{"value":"Track Title"}}},"artistName":{"innerContent":{"desktop":{"value":"Artist Name"}}},"albumName":{"innerContent":{"desktop":{"value":"Album Name"}}}} -->
<!-- /wp:divi/audio -->
```

---

## Login

- **Block:** `divi/login`
- **D4 shortcode:** `et_pb_login`
- **Elements:** `module`, `title`, `content`, `button`

No content attributes required — renders WordPress login form. Optional title and description.

### Example

```html
<!-- wp:divi/login {"title":{"innerContent":{"desktop":{"value":"Member Login"}}},"content":{"innerContent":{"desktop":{"value":"<p>Please sign in to access your account.</p>"}}}} -->
<!-- /wp:divi/login -->
```

---

## Search

- **Block:** `divi/search`
- **D4 shortcode:** `et_pb_search`
- **Elements:** `module`, `button`

Renders WordPress search form. Minimal configuration needed.

### Example

```html
<!-- wp:divi/search {} -->
<!-- /wp:divi/search -->
```

---

## Before/After Image

- **Block:** `divi/before-after-image`
- **D4 shortcode:** (new in D5)
- **Elements:** `module`, `beforeImage`, `afterImage`, `beforeLabel`, `afterLabel`, `slider`, `labels`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `beforeImage.innerContent.{device}.value.src` | URL | "Before" image URL |
| `afterImage.innerContent.{device}.value.src` | URL | "After" image URL |
| `beforeLabel.innerContent.{device}.value` | string | "Before" label text |
| `afterLabel.innerContent.{device}.value` | string | "After" label text |

### Example

```html
<!-- wp:divi/before-after-image {"beforeImage":{"innerContent":{"desktop":{"value":{"src":"https://example.com/before.jpg"}}}},"afterImage":{"innerContent":{"desktop":{"value":{"src":"https://example.com/after.jpg"}}}},"beforeLabel":{"innerContent":{"desktop":{"value":"Before"}}},"afterLabel":{"innerContent":{"desktop":{"value":"After"}}}} -->
<!-- /wp:divi/before-after-image -->
```

---

## Code

- **Block:** `divi/code`
- **D4 shortcode:** `et_pb_code`
- **Elements:** `module`, `content`

Outputs raw HTML/CSS/JavaScript. Content goes in innerHTML between block tags. Use this only when no native Divi module can achieve the desired result.

### Example

```html
<!-- wp:divi/code {} -->
<div class="custom-embed">
  <iframe src="https://example.com/embed" width="100%" height="400"></iframe>
</div>
<!-- /wp:divi/code -->
```

---

## Gallery

- **Block:** `divi/gallery`
- **D4 shortcode:** `et_pb_gallery`
- **Elements:** `module`, `title`, `caption`, `pagination`, `item`, `image`, `overlay`, `galleryGrid`

Displays WordPress media library images. Requires media IDs.

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.galleryIds.{device}.value` | string | Comma-separated media attachment IDs |
| `module.advanced.layout.{device}.value` | `"grid"` / `"slider"` | Gallery layout |
| `module.advanced.postsNumber.{device}.value` | string | Number of images to show |

### Example

```html
<!-- wp:divi/gallery {"module":{"advanced":{"galleryIds":{"desktop":{"value":"10,11,12,13"}},"layout":{"desktop":{"value":"grid"}},"postsNumber":{"desktop":{"value":"4"}}}}} -->
<!-- /wp:divi/gallery -->
```

---

## Sidebar

- **Block:** `divi/sidebar`
- **D4 shortcode:** `et_pb_sidebar`
- **Elements:** `module`

Renders a WordPress widget area/sidebar.

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.area.{device}.value` | string | Widget area ID |

### Example

```html
<!-- wp:divi/sidebar {"module":{"advanced":{"area":{"desktop":{"value":"sidebar-1"}}}}} -->
<!-- /wp:divi/sidebar -->
```

---

## Menu

- **Block:** `divi/menu`
- **D4 shortcode:** `et_pb_menu`
- **Elements:** `module`

Renders a WordPress navigation menu.

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.menuId.{device}.value` | string | WordPress menu ID |

### Example

```html
<!-- wp:divi/menu {"module":{"advanced":{"menuId":{"desktop":{"value":"2"}}}}} -->
<!-- /wp:divi/menu -->
```

---

## Link

- **Block:** `divi/link`
- **D4 shortcode:** (new in D5)
- **Elements:** `module`, `content`, `icon`

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `content.innerContent.{device}.value.text` | string | Link text |
| `content.innerContent.{device}.value.linkUrl` | URL | Link URL |
| `content.innerContent.{device}.value.linkTarget` | `"_blank"` / `""` | Open in new tab |

### Example

```html
<!-- wp:divi/link {"content":{"innerContent":{"desktop":{"value":{"text":"Learn More","linkUrl":"https://example.com","linkTarget":"_blank"}}}}} -->
<!-- /wp:divi/link -->
```

---

## Signup (Email Optin)

- **Block:** `divi/signup`
- **D4 shortcode:** `et_pb_signup`
- **Elements:** `module`, `title`, `content`, `button`

Renders an email signup form. Requires email service provider configuration in Divi settings.

### Module-Specific Attributes

| Attribute Path | Values | Description |
|---|---|---|
| `title.innerContent.{device}.value` | string | Form heading |
| `content.innerContent.{device}.value` | HTML string | Description text |

### Example

```html
<!-- wp:divi/signup {"title":{"innerContent":{"desktop":{"value":"Subscribe to Our Newsletter"}}},"content":{"innerContent":{"desktop":{"value":"<p>Get the latest updates delivered to your inbox.</p>"}}}} -->
<!-- /wp:divi/signup -->
```

---

## Dropdown

- **Block:** `divi/dropdown`
- **D4 shortcode:** (new in D5)
- **Element:** `module`

A container module that wraps child blocks in a collapsible dropdown. Functions as a parent — place modules inside it, similar to how section/row/column work.

### Example

```html
<!-- wp:divi/dropdown {} -->
<!-- wp:divi/text {} -->
<p>Content inside the dropdown</p>
<!-- /wp:divi/text -->
<!-- /wp:divi/dropdown -->
```

---

## Group / Group Carousel

- **Block:** `divi/group` / `divi/group-carousel`
- **Element:** `module`

Container modules for grouping child blocks. Group Carousel turns children into a carousel slider. No content attributes — purely structural containers.

### Example

```html
<!-- wp:divi/group {} -->
<!-- wp:divi/blurb ... /-->
<!-- wp:divi/blurb ... /-->
<!-- /wp:divi/group -->
```

---

## Comments

- **Block:** `divi/comments`
- **D4 shortcode:** `et_pb_comments`
- **Element:** `module`

Renders the WordPress comment form and comment list for the current post. No content attributes needed.

### Example

```html
<!-- wp:divi/comments {} -->
<!-- /wp:divi/comments -->
```

---

## Post Title

- **Block:** `divi/post-title`
- **D4 shortcode:** `et_pb_post_title`
- **Element:** `module`, `title`, `meta`, `featuredImage`

Used in Theme Builder templates to display the current post/page title dynamically.

### Example

```html
<!-- wp:divi/post-title {} -->
<!-- /wp:divi/post-title -->
```

---

## Post Content

- **Block:** `divi/post-content`
- **D4 shortcode:** `et_pb_post_content`
- **Element:** `module`

Used in Theme Builder templates to display the current post/page content dynamically.

### Example

```html
<!-- wp:divi/post-content {} -->
<!-- /wp:divi/post-content -->
```

---

## Portfolio

- **Block:** `divi/portfolio`
- **D4 shortcode:** `et_pb_portfolio`
- **Element:** `module`

Displays project posts in a grid or list. Dynamic module that queries portfolio post type.

| Attribute Path | Values | Description |
|---|---|---|
| `module.advanced.postsNumber.{device}.value` | string | Number of projects |
| `module.advanced.layout.{device}.value` | `"grid"` / `"fullwidth"` | Portfolio layout |
| `module.advanced.includeCategories.{device}.value` | string | Comma-separated project category IDs |

### Example

```html
<!-- wp:divi/portfolio {"module":{"advanced":{"postsNumber":{"desktop":{"value":"8"}},"layout":{"desktop":{"value":"grid"}}}}} -->
<!-- /wp:divi/portfolio -->
```

---

## Post Navigation

- **Block:** `divi/post-nav`
- **D4 shortcode:** `et_pb_post_nav`
- **Element:** `module`

Displays previous/next post navigation. Used in Theme Builder templates.

### Example

```html
<!-- wp:divi/post-nav {} -->
<!-- /wp:divi/post-nav -->
```
