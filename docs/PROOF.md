# DS-Pythone proof sheet

*Technical evidence, updated 14 October 2026 (DS-Pythone version 3.13.26). The same content is on <https://dearsoft.com.bd/proof>.*

DS-Pythone is an e-commerce CMS and storefront written in Python, created by DearSoft (Mr. Khandaker Readul Islam, [about the founder](https://dearsoft.com.bd/founder)). Three things prove it.

| 1. Live project link | 2. Source evidence | 3. Project details |
|---|---|---|
| Two public stores. Open them and check the page source. | Code facts now, source access on request. | Client, country, business, catalog size, status. |

## 1. Live project link: two stores you can open right now

Each storefront marks its engine in the HTML of every page, so you can confirm it yourself in ten seconds.

| Store | Address | Status |
|---|---|---|
| Dear IT | <https://dearit.com.bd> | Live, DS-Pythone |
| NR Gift Shop | <https://nrgiftshop.it> | Live, DS-Pythone |

```bash
# any terminal
curl -s https://dearit.com.bd/ | grep -o 'data-engine="[^"]*"'
curl -s https://nrgiftshop.it/ | grep -o 'data-engine="[^"]*"'
# both print:
data-engine="dspythone"
```

## 2. Source-code evidence: what the code looks like

Counted on the source tree on 13 October 2026 (engine folder, tests included), excluding virtual environments, caches, storage, uploaded images and build output.

| Measure | Value | Note |
|---|---|---|
| Python files | 1,487 | about 155,000 lines |
| Twig templates | 869 | storefront and admin views |
| PHP executed | 0 | The engine folder contains no PHP files. All language files are Python. |
| Fresh install | minutes | One command or a 4-step web installer creates the 134 core tables. |

| Layer | What it uses |
|---|---|
| Language | Python 3.11 and 3.12 |
| Web framework | Flask 3, Jinja2, MarkupSafe |
| Data | PyMySQL on MySQL / MariaDB |
| Security | bcrypt, cryptography, per-site licence check |
| Media | Pillow (WebP), optional rembg for background removal |
| Serving | gunicorn behind nginx, or Passenger on shared hosting |

### Our technology

DS-Pythone is a Python e-commerce platform. Current version: 3.13.26.

**What it runs on**

- Python 3.11 or newer, with Flask and Jinja2 for the web layer and MySQL / MariaDB for data.
- One engine serves the storefront, the admin panel and DS Studio, the visual builder for layouts, pages, blog and settings.
- The built-in import tool brings an existing store's catalog, customers, orders and page addresses across, so search rankings carry over.
- Installs in minutes: one command or a four-step web installer.

**What is DearSoft's own work**

- The complete Python engine: framework, loader, request handling, controllers, models and installer.
- DS Studio, the visual builder, with its blog, style, filter and settings tools.
- DearSoft AI, image tools, Pathao courier integration, customer accounts, and the licence and installer system.

> **Provenance and licences.** The storefront theme layer and its settings definitions were created from the Journal 3 theme and are still partly derived from it; builds installed on client sites that still use it also include a compiled Journal 3-derived JavaScript bundle in the Studio admin. DearSoft is replacing derived parts with its own code, and new installs no longer include the bundle. The commerce core builds on OpenCart 3.0.5.1 (GPL-3.0). The Python engine, DS Studio, the AI tools, courier integration, customer accounts and the licence and installer system are written by DearSoft.

OpenCart (GPL-3.0) and Journal 3 are the work of their respective owners. DS-Pythone is not affiliated with, sponsored by, or endorsed by OpenCart or Journal 3.

### How to review it

- **Source review.** Read-only access to the code, or a guided walkthrough of the engine, controllers and templates. It is commercial software, so it is shared on request rather than published.
- **Live server session.** A screen share showing the Python version, the running service and the process list on a production machine.
- **Admin dashboard.** A working demonstration of the catalog, orders, theme studio and AI tools.
- **Clean install.** A new store installed from scratch on a call, from empty database to working storefront.

## 3. Client and project details: the two projects

| Project | Country | Business | Catalog and speed | Status |
|---|---|---|---|---|
| [Dear IT](https://dearit.com.bd) | Bangladesh | IT accessories, laptop sales and repairs. DearSoft's own showcase store. | About 2,350 products (public sitemap, 14 October 2026), migrated intact. Home page about 0.8 s (median of 5 requests, measured from Bangladesh on 24 Sep 2026). | Live |
| [NR Gift Shop](https://nrgiftshop.it) | Italy (Florence) | Premium gifts and retail for shoppers in Italy. | About 370 products (public sitemap, 14 October 2026). Moved from a PHP store to the Python engine. | Live |

Other stores also run on the platform. Their details are shared only with each client's permission.

## Contact

Ask for a source walkthrough, a live server session or a clean install on a call.

- Email: founder@dearsoft.com.bd
- WhatsApp / phone: +880 1970 004005
- Web: <https://dearsoft.com.bd>
