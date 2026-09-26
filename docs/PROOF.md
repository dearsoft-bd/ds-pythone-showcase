# DS-Pythone proof sheet

*Technical evidence, 25 September 2026. The same content is on <https://dearsoft.com.bd/proof>.*

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

Counted on the source tree on 25 September 2026, excluding virtual environments, caches and build output.

| Measure | Value | Note |
|---|---|---|
| Python files | 1,161 | about 100,800 lines |
| Twig templates | 745 | storefront and admin views |
| PHP executed | 0 | 220 legacy PHP language files remain for reference. Each has a Python twin, and the engine loads only the Python ones. |
| Fresh install | minutes | One command or a 4-step web installer creates the 134 core tables. |

| Layer | What it uses |
|---|---|
| Language | Python 3.11 and 3.12 |
| Web framework | Flask 3, Jinja2, MarkupSafe |
| Data | PyMySQL on MySQL / MariaDB |
| Security | bcrypt, cryptography, per-site licence check |
| Media | Pillow (WebP), optional rembg for background removal |
| Serving | gunicorn behind nginx, or Passenger on shared hosting |

### Built to be compatible, written by us

OpenCart is a widely used open-source e-commerce platform. Many stores in Bangladesh and elsewhere run on it. We designed DS-Pythone so those stores can move to Python without starting over.

**OpenCart-compatible structure**

- DS-Pythone uses the same database schema as OpenCart 3.0.5.1 with the Journal 3 theme: the same tables, down to names like `dspythone_module` and `dspythone_skin`.
- An existing store's catalog, customers, orders and Journal 3 theme settings work without conversion.
- URLs and SEO links carry over, so a store keeps its Google rankings after moving.
- This is exactly how dearit.com.bd and nrgiftshop.it were moved from PHP to Python: the live database was reused as-is, in production.

**What is DearSoft's own work**

- The complete Python engine: framework, loader, request handling, controllers, models and installer.
- The DS-Pythone theme system and Studio builder, ported to Python from the Journal 3 theme's design.
- DearSoft AI, image tools, Pathao courier integration, customer accounts, and the licence and installer system.

> **Where a piece is still shared code.** The Studio admin's front end includes a compiled JavaScript bundle derived from the Journal 3 theme, unmodified apart from renamed labels; we are replacing it with DearSoft-written code over time. Everywhere else (the engine, the storefront theme, the admin backend and every feature listed above) is Python written by DearSoft.

OpenCart (GPL-3.0) and Journal 3 are the work of their respective owners. DS-Pythone is compatible with OpenCart and Journal 3 and is not affiliated with, sponsored by, or endorsed by OpenCart or Journal 3.

### How to review it

- **Source review.** Read-only access to the code, or a guided walkthrough of the engine, controllers and templates. It is commercial software, so it is shared on request rather than published.
- **Live server session.** A screen share showing the Python version, the running service and the process list on a production machine.
- **Admin dashboard.** A working demonstration of the catalog, orders, theme studio and AI tools.
- **Clean install.** A new store installed from scratch on a call, from empty database to working storefront.

## 3. Client and project details: the two projects

| Project | Country | Business | Catalog and speed | Status |
|---|---|---|---|---|
| [Dear IT](https://dearit.com.bd) | Bangladesh | IT accessories, laptop sales and repairs. DearSoft's own showcase store. | 2,357 products, migrated intact. Home page about 0.8 s (median of 5 requests, measured from Bangladesh on 24 Sep 2026). | Live |
| [NR Gift Shop](https://nrgiftshop.it) | Italy (Florence) | Premium gifts and retail for shoppers in Italy. | 320 products. Moved from a PHP store to the Python engine. | Live |

Other stores also run on the platform. Their details are shared only with each client's permission.

## Contact

Ask for a source walkthrough, a live server session or a clean install on a call.

- Email: founder@dearsoft.com.bd
- WhatsApp / phone: +880 1970 004005
- Web: <https://dearsoft.com.bd>
