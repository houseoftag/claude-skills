---
name: scrapling
description: >
  Write Python code using the Scrapling library for web scraping, website cloning, and content extraction.
  Use this skill whenever the user wants to scrape websites, download web content, clone sites for redesign,
  extract multimedia assets (images, videos, PDFs, fonts, stylesheets), capture full-page screenshots,
  or build crawlers/spiders. Also use when the user mentions scrapling, web scraping with Python,
  fetching page content, or downloading site assets. Even if the user just says "scrape" or "grab content
  from a site", this skill applies.
---

# Scrapling — Web Scraping & Website Cloning

Scrapling is a high-performance Python web scraping framework. It provides HTML parsing, multiple fetcher backends (static HTTP, browser-based, stealth), and a spider framework for crawling.

## Quick Reference: Which Fetcher to Use

| Need | Fetcher | Why |
|------|---------|-----|
| Static HTML, fast | `Fetcher` | curl_cffi-based, no JS execution |
| JS-rendered pages | `DynamicFetcher` | Playwright + Chromium |
| Anti-bot sites | `StealthyFetcher` | Fingerprint spoofing, Cloudflare bypass |
| Async variant | `AsyncFetcher` / `async_fetch` | Same APIs, async/await |

## Installation

```bash
pip install scrapling[all]  # Everything
pip install scrapling[fetchers]  # Just fetching (no MCP/shell)
scrapling install  # Install browser dependencies for DynamicFetcher/StealthyFetcher
```

## Core Patterns

### Basic Fetch + Parse

```python
from scrapling import Fetcher, DynamicFetcher, StealthyFetcher

# Static fetch (fast, no JS)
response = Fetcher.fetch("https://example.com")

# Browser fetch (JS-rendered content)
response = DynamicFetcher.fetch("https://example.com", headless=True, network_idle=True)

# Stealth fetch (anti-bot bypass)
response = StealthyFetcher.fetch("https://example.com", headless=True, network_idle=True)
```

### Selecting Elements

Response extends Selector — use CSS, XPath, or find_all:

```python
# CSS selectors
titles = response.css("h1::text").getall()
links = response.css("a::attr(href)").getall()

# XPath
paragraphs = response.xpath("//p/text()").getall()

# BeautifulSoup-style
divs = response.find_all("div", class_="content")
first = response.find("div", id="main")

# Chaining
items = response.css(".product").css(".price::text").getall()
```

### Key Selector Methods

- `.css(selector)` — CSS selector, supports `::text` and `::attr(name)` pseudo-elements
- `.xpath(query)` — XPath query
- `.find(tag, **attrs)` / `.find_all(tag, **attrs)` — BS4-style filtering
- `.get()` — First match text/attribute value
- `.getall()` — All match values as list
- `.text` — Element's text content
- `.attrib` — Element's attributes dict
- `.re(pattern)` / `.re_first(pattern)` — Regex extraction
- `.parent` / `.next` / `.previous` / `.children` — Tree navigation
- `.urljoin(url)` — Resolve relative URLs against the response URL

## Website Cloning for Redesign

This is the primary workflow: clone a website's content, structure, and assets into a local dev environment.

### Step 1: Fetch the Page with Full Resources

When cloning, do NOT use `disable_resources=True` — that blocks images, fonts, and media.

```python
from scrapling import DynamicFetcher

response = DynamicFetcher.fetch(
    "https://example.com",
    headless=True,
    network_idle=True,  # Wait for all resources to load
)
```

### Step 2: Full-Page Screenshots via page_action

Scrapling does not have a built-in screenshot method, but `page_action` gives you direct access to the Playwright `page` object. Use it for screenshots:

```python
import os

screenshot_dir = "clone/screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def take_screenshot(page):
    page.screenshot(path=f"{screenshot_dir}/full_page.png", full_page=True)

response = DynamicFetcher.fetch(
    "https://example.com",
    headless=True,
    network_idle=True,
    page_action=take_screenshot,
)
```

The `page_action` callback runs after the page loads but before the page closes. You can do anything Playwright supports inside it — screenshots, PDF export, scroll actions, clicking through modals, etc.

For **async** usage:

```python
async def take_screenshot(page):
    await page.screenshot(path="screenshot.png", full_page=True)

response = await DynamicFetcher.async_fetch(
    "https://example.com",
    headless=True,
    network_idle=True,
    page_action=take_screenshot,
)
```

### Step 3: Extract and Download All Assets

Extract every asset URL from the page, then download them while preserving directory structure:

```python
import os
import hashlib
from urllib.parse import urlparse, urljoin
from pathlib import Path
from scrapling import Fetcher

def extract_asset_urls(response):
    """Extract all asset URLs from a page response."""
    base_url = response.url
    assets = {
        "images": [],
        "stylesheets": [],
        "scripts": [],
        "videos": [],
        "audio": [],
        "fonts": [],
        "pdfs": [],
        "other": [],
    }

    # Images: <img src>, <img srcset>, <picture><source>, CSS background-image
    for src in response.css("img::attr(src)").getall():
        assets["images"].append(urljoin(base_url, src))
    for srcset in response.css("img::attr(srcset)").getall():
        for entry in srcset.split(","):
            url = entry.strip().split()[0]
            if url:
                assets["images"].append(urljoin(base_url, url))
    for src in response.css("picture source::attr(srcset)").getall():
        for entry in src.split(","):
            url = entry.strip().split()[0]
            if url:
                assets["images"].append(urljoin(base_url, url))

    # Open Graph and meta images
    for attr in ["content"]:
        for sel in ['meta[property="og:image"]', 'meta[name="twitter:image"]']:
            for val in response.css(f"{sel}::attr({attr})").getall():
                assets["images"].append(urljoin(base_url, val))

    # Favicons and icons
    for href in response.css('link[rel*="icon"]::attr(href)').getall():
        assets["images"].append(urljoin(base_url, href))

    # Stylesheets
    for href in response.css('link[rel="stylesheet"]::attr(href)').getall():
        assets["stylesheets"].append(urljoin(base_url, href))

    # Scripts
    for src in response.css("script[src]::attr(src)").getall():
        assets["scripts"].append(urljoin(base_url, src))

    # Videos: <video src>, <video><source src>
    for src in response.css("video::attr(src)").getall():
        assets["videos"].append(urljoin(base_url, src))
    for src in response.css("video source::attr(src)").getall():
        assets["videos"].append(urljoin(base_url, src))
    # Video poster images
    for poster in response.css("video::attr(poster)").getall():
        assets["images"].append(urljoin(base_url, poster))

    # Audio
    for src in response.css("audio::attr(src)").getall():
        assets["audio"].append(urljoin(base_url, src))
    for src in response.css("audio source::attr(src)").getall():
        assets["audio"].append(urljoin(base_url, src))

    # Embedded objects and iframes (PDFs, etc.)
    for src in response.css("embed::attr(src)").getall():
        url = urljoin(base_url, src)
        if url.lower().endswith(".pdf"):
            assets["pdfs"].append(url)
        else:
            assets["other"].append(url)
    for href in response.css('a[href$=".pdf"]::attr(href)').getall():
        assets["pdfs"].append(urljoin(base_url, href))

    # Fonts (from <link> preloads)
    for href in response.css('link[rel="preload"][as="font"]::attr(href)').getall():
        assets["fonts"].append(urljoin(base_url, href))
    for href in response.css('link[as="font"]::attr(href)').getall():
        assets["fonts"].append(urljoin(base_url, href))

    # Deduplicate
    for key in assets:
        assets[key] = list(dict.fromkeys(assets[key]))

    return assets


def download_asset(url, output_dir="clone/assets"):
    """Download a single asset, preserving URL path structure."""
    try:
        parsed = urlparse(url)
        # Build local path from URL path
        rel_path = parsed.path.lstrip("/")
        if not rel_path or rel_path.endswith("/"):
            rel_path += "index.html"

        local_path = Path(output_dir) / parsed.netloc / rel_path
        local_path.parent.mkdir(parents=True, exist_ok=True)

        resp = Fetcher.fetch(url)
        if resp.status == 200:
            local_path.write_bytes(resp.body)
            return str(local_path)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return None
```

### Step 4: Save the HTML with Rewritten Asset Paths

After downloading assets, rewrite the HTML so asset references point to local files:

```python
def save_cloned_page(response, assets_dir="clone/assets", output="clone/index.html"):
    """Save the page HTML with asset paths rewritten to local."""
    html = response.html_content  # or str(response.body, 'utf-8')

    parsed_base = urlparse(response.url)

    # Rewrite absolute URLs to relative local paths
    for category, urls in extract_asset_urls(response).items():
        for url in urls:
            parsed = urlparse(url)
            rel_path = parsed.path.lstrip("/")
            local_rel = f"assets/{parsed.netloc}/{rel_path}"
            html = html.replace(url, local_rel)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(html, encoding="utf-8")
```

### Complete Cloning Script Pattern

```python
import os
from scrapling import Fetcher, DynamicFetcher

def clone_page(url, output_dir="clone"):
    os.makedirs(f"{output_dir}/screenshots", exist_ok=True)
    os.makedirs(f"{output_dir}/assets", exist_ok=True)

    # 1. Screenshot
    def screenshot(page):
        page.screenshot(
            path=f"{output_dir}/screenshots/full_page.png",
            full_page=True,
        )

    # 2. Fetch with full resources
    response = DynamicFetcher.fetch(
        url,
        headless=True,
        network_idle=True,
        page_action=screenshot,
    )

    # 3. Extract and download assets
    assets = extract_asset_urls(response)
    for category, urls in assets.items():
        for asset_url in urls:
            download_asset(asset_url, f"{output_dir}/assets")

    # 4. Save rewritten HTML
    save_cloned_page(response, f"{output_dir}/assets", f"{output_dir}/index.html")

    print(f"Cloned {url} to {output_dir}/")
    return response
```

### Extracting CSS Background Images

Stylesheets may reference images via `url()`. After downloading CSS files, parse them for additional assets:

```python
import re

def extract_css_urls(css_text, css_url):
    """Extract url() references from CSS content."""
    urls = []
    for match in re.finditer(r'url\(["\']?([^"\')\s]+)["\']?\)', css_text):
        ref = match.group(1)
        if not ref.startswith("data:"):
            urls.append(urljoin(css_url, ref))
    return urls
```

## Spider Framework (Multi-Page Crawling)

For cloning entire sites with multiple pages, use the Spider framework:

```python
import os
from scrapling.spiders import Spider, Request
from scrapling.engines.static import FetcherSession

class SiteCloneSpider(Spider):
    name = "site_cloner"
    start_urls = ["https://example.com"]
    concurrent_requests = 4
    concurrent_requests_per_domain = 2
    download_delay = 1.0  # Be polite

    def configure_sessions(self, manager):
        manager.add("default", FetcherSession(), default=True)

    async def parse(self, response):
        # Save page content
        slug = response.url.rstrip("/").split("/")[-1] or "index"
        os.makedirs("clone/pages", exist_ok=True)
        with open(f"clone/pages/{slug}.html", "w") as f:
            f.write(response.html_content)

        # Extract and yield asset downloads
        assets = extract_asset_urls(response)
        for urls in assets.values():
            for url in urls:
                download_asset(url)

        # Follow internal links
        for href in response.css("a::attr(href)").getall():
            full_url = response.urljoin(href)
            if full_url.startswith(self.start_urls[0]):
                yield response.follow(href, callback=self.parse)

        # Yield scraped data
        yield {
            "url": response.url,
            "title": response.css("title::text").get(""),
            "asset_count": sum(len(v) for v in assets.values()),
        }

# Run: SiteCloneSpider.start()
```

## Important Notes

### page_action is your escape hatch
Any Playwright operation works inside `page_action` — screenshots, PDF export (`page.pdf()`), scrolling, clicking cookie banners, filling forms, waiting for lazy-loaded content. The `page` object is a standard Playwright Page.

### disable_resources kills media downloads
When set to `True`, it blocks requests for fonts, images, media, stylesheets, and more. Never use it when cloning or downloading assets.

### Async is available everywhere
Every fetcher has an async variant (`async_fetch`, `AsyncFetcher`). Use async when downloading many assets in parallel:

```python
import asyncio
from scrapling import AsyncFetcher

async def download_all(urls):
    tasks = [AsyncFetcher.fetch(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Response is a Selector
The Response object inherits from Selector, so every parsing method (css, xpath, find_all, re, etc.) works directly on the response. No need to create a separate parser.

### Respect robots.txt and rate limits
When cloning sites, add `download_delay` in spiders and avoid hammering servers. This tool is for cloning sites you have permission to work with (your own sites, client sites for redesign, etc.).
