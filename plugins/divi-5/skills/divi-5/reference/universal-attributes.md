# Divi 5 Universal Attributes Reference

Divi 5 uses Gutenberg-compatible blocks with nested JSON attributes, NOT Divi 4 shortcodes. All visual styling lives in deeply nested JSON objects following a consistent path convention.

## Path Convention

```
{element}.{category}.{property}.{device}.value.{sub-property}
```

| Segment      | Description                                                        |
|--------------|--------------------------------------------------------------------|
| `{element}`  | `module` for the module itself, or named elements like `button`, `title`, `icon`, `content` |
| `{category}` | `decoration`, `advanced`, `meta`, `innerContent`                   |
| `{property}` | The styling concern: `background`, `spacing`, `font`, `border`, etc. |
| `{device}`   | `desktop`, `tablet`, `phone`                                       |
| `value`      | Literal key; hover uses `value__hover`, sticky uses `value__sticky` |
| `{sub-property}` | The actual CSS-mapped property                                 |

Almost every attribute supports responsive values via `desktop`, `tablet`, and `phone` keys. Tablet and phone inherit from desktop when absent.

---

## Table of Contents

1. [Background](#background)
2. [Spacing](#spacing)
3. [Typography / Font](#typography--font)
4. [Border](#border)
5. [Box Shadow](#box-shadow)
6. [Sizing](#sizing)
7. [Animation](#animation)
8. [Filters](#filters)
9. [Transform](#transform)
10. [Position](#position)
11. [Z-Index](#z-index)
12. [Visibility](#visibility)
13. [Overflow](#overflow)
14. [Text Shadow](#text-shadow)
15. [Transition](#transition)
16. [Icon](#icon)
17. [ID / Classes](#id--classes)
18. [Custom CSS](#custom-css)
19. [Hover / Sticky States](#hover--sticky-states)
20. [Global Color Variable Reference](#global-color-variable-reference)

---

## Background

**Path:** `{element}.decoration.background.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property               | Valid Values                                              |
|----------------------------|-----------------------------------------------------------|
| `color`                    | Hex string, GCID variable reference, or `""`              |
| `gradient.enabled`         | `"on"` / `"off"`                                          |
| `gradient.type`            | `"linear"`, `"radial"`, `"conic"`, `"elliptical"`         |
| `gradient.direction`       | Degrees string like `"180deg"`                             |
| `gradient.directionRadial` | `"center"`, `"top left"`, `"top right"`, `"bottom left"`, `"bottom right"`, etc. |
| `gradient.stops`           | Array of `{color, position}` objects                       |
| `gradient.repeat`          | `"on"` / `"off"`                                          |
| `gradient.overlaysImage`   | `"on"` / `"off"`                                          |
| `image.url`                | URL string                                                 |
| `image.parallax.enabled`   | `"on"` / `"off"`                                          |
| `image.parallax.method`    | `"on"` (true parallax) / `"off"` (CSS fixed)              |
| `image.size`               | `"cover"`, `"contain"`, `"initial"`, `"stretch"`, `"custom"` |
| `image.position`           | `"center"`, `"top_left"`, `"top_right"`, `"bottom_left"`, `"bottom_right"`, etc. |
| `image.repeat`             | `"no-repeat"`, `"repeat"`, `"repeat-x"`, `"repeat-y"`     |
| `image.blend`              | `"normal"`, `"multiply"`, `"overlay"`, `"screen"`, etc.    |
| `video.mp4`                | URL string                                                 |
| `video.webm`               | URL string                                                 |
| `pattern.*`                | Pattern overlay settings                                   |
| `mask.*`                   | Mask overlay settings                                      |

### Example

```json
{
  "module": {
    "decoration": {
      "background": {
        "desktop": {
          "value": {
            "color": "#ffffff",
            "gradient": {
              "enabled": "on",
              "type": "linear",
              "direction": "180deg",
              "stops": [
                { "color": "#2b87da", "position": "0%" },
                { "color": "#29c4a9", "position": "100%" }
              ]
            }
          }
        }
      }
    }
  }
}
```

---

## Spacing

**Path:** `{element}.decoration.spacing.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property                        | Valid Values                           |
|-------------------------------------|----------------------------------------|
| `padding.top`                       | CSS value: `"40px"`, `"5%"`, `"2em"`  |
| `padding.right`                     | Same                                   |
| `padding.bottom`                    | Same                                   |
| `padding.left`                      | Same                                   |
| `margin.top`                        | CSS value, supports `"auto"`           |
| `margin.right`                      | Same                                   |
| `margin.bottom`                     | Same                                   |
| `margin.left`                       | Same                                   |

### Example

```json
{
  "module": {
    "decoration": {
      "spacing": {
        "desktop": {
          "value": {
            "padding": { "top": "40px", "bottom": "40px", "left": "20px", "right": "20px" },
            "margin": { "top": "0px", "bottom": "30px" }
          }
        },
        "phone": {
          "value": {
            "padding": { "top": "20px", "bottom": "20px", "left": "10px", "right": "10px" }
          }
        }
      }
    }
  }
}
```

---

## Typography / Font

**Path:** `{element}.decoration.font.font.{device}.value.*`
**Responsive:** Yes

Note the double `font` in the path: the first is the font group name, the second is the property.

### Sub-properties

| Sub-property    | Valid Values                                              |
|-----------------|-----------------------------------------------------------|
| `family`        | Font family name string (e.g., `"Open Sans"`, `"Roboto"`) |
| `weight`        | `"100"` through `"900"`, `"bold"`, `"normal"`             |
| `style`         | `"italic"`, `"normal"`                                    |
| `color`         | Hex string or GCID variable reference                      |
| `size`          | CSS value: `"16px"`, `"1.2em"`, `"1rem"`                  |
| `lineHeight`    | CSS value: `"1.5"`, `"24px"`, `"1.8em"`                   |
| `letterSpacing` | CSS value: `"1px"`, `"0.05em"`                            |
| `textAlign`     | `"left"`, `"center"`, `"right"`, `"justify"`              |
| `lineColor`     | Text decoration color (hex string)                         |
| `lineStyle`     | `"none"`, `"underline"`, `"line-through"`, `"overline"`   |
| `headingLevel`  | `"h1"` through `"h6"` (when applicable)                   |

### Body Text Font Paths

Body text and heading fonts use different, deeper paths:

| Font Group | Path                                                         |
|------------|--------------------------------------------------------------|
| Body       | `content.decoration.bodyFont.body.font.{device}.value.*`     |
| Link       | `content.decoration.bodyFont.link.font.{device}.value.*`     |
| Heading h1 | `content.decoration.headingFont.h1.font.{device}.value.*`   |
| Heading h2 | `content.decoration.headingFont.h2.font.{device}.value.*`   |
| Heading h3 | `content.decoration.headingFont.h3.font.{device}.value.*`   |
| Heading h4 | `content.decoration.headingFont.h4.font.{device}.value.*`   |
| Heading h5 | `content.decoration.headingFont.h5.font.{device}.value.*`   |
| Heading h6 | `content.decoration.headingFont.h6.font.{device}.value.*`   |

### Example

```json
{
  "title": {
    "decoration": {
      "font": {
        "font": {
          "desktop": {
            "value": {
              "family": "Poppins",
              "weight": "700",
              "size": "32px",
              "lineHeight": "1.3",
              "color": "#333333",
              "textAlign": "center"
            }
          },
          "phone": {
            "value": {
              "size": "24px"
            }
          }
        }
      }
    }
  }
}
```

---

## Border

**Path:** `{element}.decoration.border.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property                                | Valid Values                                         |
|---------------------------------------------|------------------------------------------------------|
| `radius`                                    | String `"10px"` or object (see below)                |
| `radius.topLeft`                            | CSS value like `"10px"`                              |
| `radius.topRight`                           | Same                                                  |
| `radius.bottomRight`                        | Same                                                  |
| `radius.bottomLeft`                         | Same                                                  |
| `styles.{all\|top\|right\|bottom\|left}.width` | CSS value like `"1px"`                            |
| `styles.{all\|top\|right\|bottom\|left}.color` | Hex string                                        |
| `styles.{all\|top\|right\|bottom\|left}.style` | `"solid"`, `"dashed"`, `"dotted"`, `"double"`, `"none"` |

### Example

```json
{
  "module": {
    "decoration": {
      "border": {
        "desktop": {
          "value": {
            "radius": {
              "topLeft": "10px",
              "topRight": "10px",
              "bottomRight": "0px",
              "bottomLeft": "0px"
            },
            "styles": {
              "all": {
                "width": "2px",
                "color": "#e0e0e0",
                "style": "solid"
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Box Shadow

**Path:** `{element}.decoration.boxShadow.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                                        |
|--------------|-----------------------------------------------------|
| `style`      | `"none"`, `"preset1"` through `"preset7"`           |
| `horizontal` | CSS value like `"0px"`                               |
| `vertical`   | CSS value like `"2px"`                               |
| `blur`       | CSS value like `"18px"`                              |
| `spread`     | CSS value like `"0px"`                               |
| `color`      | Hex or rgba string like `"rgba(0,0,0,0.3)"`         |
| `position`   | `"outer"` / `"inner"`                                |

### Example

```json
{
  "module": {
    "decoration": {
      "boxShadow": {
        "desktop": {
          "value": {
            "style": "none",
            "horizontal": "0px",
            "vertical": "12px",
            "blur": "18px",
            "spread": "-6px",
            "color": "rgba(0,0,0,0.15)",
            "position": "outer"
          }
        }
      }
    }
  }
}
```

---

## Sizing

**Path:** `{element}.decoration.sizing.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                                    |
|--------------|-------------------------------------------------|
| `width`      | CSS value: `"100%"`, `"500px"`, `"auto"`        |
| `maxWidth`   | CSS value                                        |
| `height`     | CSS value                                        |
| `minHeight`  | CSS value                                        |
| `maxHeight`  | CSS value                                        |
| `alignment`  | `"left"`, `"center"`, `"right"`, `"none"`       |
| `flexGrow`   | Number as string like `"1"`                      |
| `flexShrink` | Number as string like `"0"`                      |

### Example

```json
{
  "module": {
    "decoration": {
      "sizing": {
        "desktop": {
          "value": {
            "width": "80%",
            "maxWidth": "1200px",
            "alignment": "center"
          }
        },
        "tablet": {
          "value": {
            "width": "100%"
          }
        }
      }
    }
  }
}
```

---

## Animation

**Path:** `{element}.decoration.animation.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property       | Valid Values                                                      |
|--------------------|-------------------------------------------------------------------|
| `style`            | `"none"`, `"fade"`, `"slide"`, `"bounce"`, `"zoom"`, `"flip"`, `"fold"`, `"roll"` |
| `direction`        | `"center"`, `"left"`, `"right"`, `"bottom"`, `"top"`             |
| `duration`         | Milliseconds: `"500ms"`, `"1000ms"`                               |
| `delay`            | Milliseconds: `"0ms"`, `"200ms"`                                  |
| `intensity.slide`  | Percentage: `"50%"`                                                |
| `startingOpacity`  | Percentage: `"0%"`, `"100%"`                                      |
| `speedCurve`       | `"ease-in-out"`, `"ease"`, `"linear"`, `"ease-in"`, `"ease-out"` |
| `repeat`           | `"once"`, `"loop"`                                                |

### Example

```json
{
  "module": {
    "decoration": {
      "animation": {
        "desktop": {
          "value": {
            "style": "fade",
            "direction": "bottom",
            "duration": "700ms",
            "delay": "0ms",
            "startingOpacity": "0%",
            "speedCurve": "ease-in-out",
            "repeat": "once"
          }
        }
      }
    }
  }
}
```

---

## Filters

**Path:** `{element}.decoration.filters.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                                              |
|--------------|-----------------------------------------------------------|
| `hueRotate`  | Degrees: `"0deg"`, `"180deg"`                             |
| `saturate`   | Percentage: `"100%"`, `"150%"`                            |
| `brightness` | Percentage: `"100%"`, `"80%"`                             |
| `contrast`   | Percentage: `"100%"`, `"120%"`                            |
| `invert`     | Percentage: `"0%"`, `"100%"`                              |
| `sepia`      | Percentage: `"0%"`, `"50%"`                               |
| `opacity`    | Percentage: `"100%"`, `"50%"`                             |
| `blur`       | CSS value: `"0px"`, `"5px"`                               |
| `blendMode`  | `"normal"`, `"multiply"`, `"screen"`, `"overlay"`, etc.   |

### Example

```json
{
  "module": {
    "decoration": {
      "filters": {
        "desktop": {
          "value": {
            "brightness": "110%",
            "contrast": "105%",
            "saturate": "120%",
            "blur": "0px"
          }
        }
      }
    }
  }
}
```

---

## Transform

**Path:** `{element}.decoration.transform.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                                             |
|--------------|----------------------------------------------------------|
| `scale`      | Percentage `"100%"` or object `{"x":"100%","y":"100%"}` |
| `translate`  | Object `{"x":"0px","y":"0px"}`                           |
| `rotate`     | Object `{"x":"0deg","y":"0deg","z":"0deg"}`              |
| `skew`       | Object `{"x":"0deg","y":"0deg"}`                         |
| `origin`     | Object `{"x":"50%","y":"50%"}`                           |

### Example

```json
{
  "module": {
    "decoration": {
      "transform": {
        "desktop": {
          "value": {
            "scale": { "x": "110%", "y": "110%" },
            "translate": { "x": "0px", "y": "-10px" },
            "rotate": { "x": "0deg", "y": "0deg", "z": "5deg" },
            "origin": { "x": "50%", "y": "50%" }
          }
        }
      }
    }
  }
}
```

---

## Position

**Path:** `{element}.decoration.position.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property      | Valid Values                                                  |
|-------------------|---------------------------------------------------------------|
| `mode`            | `"relative"`, `"absolute"`, `"fixed"`                         |
| `origin.relative` | `"top_left"`, `"top_center"`, `"top_right"`, `"center_left"`, `"center"`, `"center_right"`, `"bottom_left"`, `"bottom_center"`, `"bottom_right"` |
| `origin.absolute` | Same as above                                                  |
| `origin.fixed`    | Same as above                                                  |
| `offset.vertical` | CSS value like `"10px"`, `"5%"`                                |
| `offset.horizontal` | CSS value like `"10px"`, `"5%"`                              |

### Example

```json
{
  "module": {
    "decoration": {
      "position": {
        "desktop": {
          "value": {
            "mode": "absolute",
            "origin": { "absolute": "top_right" },
            "offset": { "vertical": "20px", "horizontal": "20px" }
          }
        }
      }
    }
  }
}
```

---

## Z-Index

**Path:** `{element}.decoration.zIndex.{device}.value`
**Responsive:** Yes

The value is an integer as a string. No sub-properties.

### Example

```json
{
  "module": {
    "decoration": {
      "zIndex": {
        "desktop": {
          "value": "10"
        }
      }
    }
  }
}
```

---

## Visibility

**Path:** `{element}.decoration.disabledOn.{device}.value`
**Responsive:** Yes (per-device by nature)

Set to `"on"` to hide the element on that device. Absent or `""` means visible.

### Example

```json
{
  "module": {
    "decoration": {
      "disabledOn": {
        "phone": {
          "value": "on"
        }
      }
    }
  }
}
```

---

## Overflow

**Path:** `{element}.decoration.overflow.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                                  |
|--------------|-----------------------------------------------|
| `x`          | `"visible"`, `"hidden"`, `"scroll"`, `"auto"` |
| `y`          | Same                                           |

### Example

```json
{
  "module": {
    "decoration": {
      "overflow": {
        "desktop": {
          "value": {
            "x": "hidden",
            "y": "hidden"
          }
        }
      }
    }
  }
}
```

---

## Text Shadow

**Path:** `{element}.advanced.text.textShadow.{device}.value.*`
**Responsive:** Yes

May also appear nested under a font group depending on context.

### Sub-properties

| Sub-property | Valid Values                                    |
|--------------|-------------------------------------------------|
| `style`      | `"none"`, `"preset1"` through `"preset5"`       |
| `horizontal` | CSS value like `"0px"`                           |
| `vertical`   | CSS value like `"1px"`                           |
| `blur`       | CSS value like `"2px"`                           |
| `color`      | Hex or rgba string                               |

### Example

```json
{
  "title": {
    "advanced": {
      "text": {
        "textShadow": {
          "desktop": {
            "value": {
              "style": "none",
              "horizontal": "0px",
              "vertical": "2px",
              "blur": "4px",
              "color": "rgba(0,0,0,0.3)"
            }
          }
        }
      }
    }
  }
}
```

---

## Transition

**Path:** `{element}.decoration.transition.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                                              |
|--------------|-----------------------------------------------------------|
| `duration`   | Milliseconds: `"300ms"`, `"500ms"`                        |
| `delay`      | Milliseconds: `"0ms"`, `"100ms"`                          |
| `speedCurve` | `"ease"`, `"linear"`, `"ease-in"`, `"ease-out"`, `"ease-in-out"` |

### Example

```json
{
  "module": {
    "decoration": {
      "transition": {
        "desktop": {
          "value": {
            "duration": "300ms",
            "delay": "0ms",
            "speedCurve": "ease"
          }
        }
      }
    }
  }
}
```

---

## Icon

**Path:** `{element}.decoration.icon.{device}.value.*`
**Responsive:** Yes

### Sub-properties

| Sub-property | Valid Values                     |
|--------------|----------------------------------|
| `color`      | Hex string                       |
| `size`       | CSS value like `"96px"`, `"2em"` |
| `useSize`    | `"on"` / `"off"`                 |

### Example

```json
{
  "icon": {
    "decoration": {
      "icon": {
        "desktop": {
          "value": {
            "color": "#2b87da",
            "size": "96px",
            "useSize": "on"
          }
        }
      }
    }
  }
}
```

---

## ID / Classes

**Path:** `{element}.advanced.htmlAttributes.{device}.value.*`
**Responsive:** Yes (though typically only set on desktop)

### Sub-properties

| Sub-property | Valid Values                         |
|--------------|--------------------------------------|
| `id`         | HTML ID string (no `#` prefix)       |
| `class`      | CSS class string (no `.` prefix)     |

### Example

```json
{
  "module": {
    "advanced": {
      "htmlAttributes": {
        "desktop": {
          "value": {
            "id": "hero-section",
            "class": "custom-hero dark-theme"
          }
        }
      }
    }
  }
}
```

---

## Custom CSS

**Path:** `css.{device}.{location}`
**Responsive:** Yes

Use as a last resort when built-in attributes cannot achieve the desired styling.

### Locations

| Location       | Applies To                                      |
|----------------|--------------------------------------------------|
| `before`       | `::before` pseudo-element                        |
| `mainElement`  | The main element itself                          |
| `after`        | `::after` pseudo-element                         |
| `freeForm`     | Free-form CSS (added to page)                    |

Module-specific CSS targets may also exist (e.g., `toggleTitle`, `toggleContent` for the accordion module).

### Example

```json
{
  "css": {
    "desktop": {
      "mainElement": "box-shadow: 0 4px 20px rgba(0,0,0,0.1);",
      "before": "content: ''; position: absolute; top: 0; left: 0;"
    },
    "phone": {
      "mainElement": "padding: 10px;"
    }
  }
}
```

---

## Hover / Sticky States

For any value path, hover and sticky states use parallel keys at the same level as `value`:

| Key              | Applies When                    |
|------------------|---------------------------------|
| `value`          | Default/normal state            |
| `value__hover`   | Mouse hover state               |
| `value__sticky`  | Sticky (fixed header) state     |

### Example

```json
{
  "module": {
    "decoration": {
      "background": {
        "desktop": {
          "value": {
            "color": "#ffffff"
          },
          "value__hover": {
            "color": "#f0f0f0"
          },
          "value__sticky": {
            "color": "#333333"
          }
        }
      }
    }
  }
}
```

This pattern applies to any attribute group: `font`, `border`, `boxShadow`, `filters`, `transform`, etc.

---

## Global Color Variable Reference

Instead of hardcoded hex values, Divi 5 supports Global Color ID (GCID) references. Use this format wherever a color value is accepted:

```
"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})\$"
```

Replace `gcid-primary-color` with the actual GCID name defined in the site's Global Colors settings.

### Example in context

```json
{
  "module": {
    "decoration": {
      "background": {
        "desktop": {
          "value": {
            "color": "$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})\$"
          }
        }
      }
    }
  }
}
```
