# DS-Pythone

**DS-Pythone is an e-commerce CMS and storefront written in Python, built by [DearSoft](https://dearsoft.com.bd) in Bangladesh.**

It runs real online stores today, on Flask, Jinja2 and MySQL/MariaDB, with a visual page builder, an admin panel and built-in AI tools.

> **Proof page:** <https://dearsoft.com.bd/proof> (also in this repo: [`docs/PROOF.md`](docs/PROOF.md))
> Live stores, code facts and how to review the source.

This repository is a **showcase**. It explains how DS-Pythone is built and includes a few DearSoft-written source files. The full source is not published here; it can be reviewed privately on request (see [Review the source](#review-the-source)).

## Live projects

| Project | Country | Notes |
|---|---|---|
| [Dear IT](https://dearit.com.bd) | Bangladesh | IT accessories, laptop sales and repairs. 2,357 products. |
| [NR Gift Shop](https://nrgiftshop.it) | Italy (Florence) | Gifts and retail. 320 products. Moved from a PHP store to DS-Pythone. |

Every DS-Pythone storefront marks its engine in the page HTML, so you can check it yourself:

```bash
curl -s https://dearit.com.bd/   | grep -o 'data-engine="[^"]*"'
curl -s https://nrgiftshop.it/   | grep -o 'data-engine="[^"]*"'
# data-engine="dspythone"
```

| Dear IT | NR Gift Shop |
|---|---|
| ![Dear IT home page](docs/screenshots/dearit.jpg) | ![NR Gift Shop home page](docs/screenshots/nrgiftshop.jpg) |

*Screenshots of the public home pages, taken 24 September 2026.*

## What it is

- **Language and stack:** Python 3.11+, Flask 3, Jinja2, PyMySQL (MySQL / MariaDB), bcrypt, Pillow, gunicorn or waitress. See [`requirements.txt`](requirements.txt).
- **Size:** about 1,161 Python files (roughly 100,800 lines) and 745 Twig templates. The engine executes no PHP.
- **Storefront and admin:** catalog, cart and checkout, customer accounts, orders, a visual Studio for headers, menus, sliders and product pages.
- **DearSoft additions:** AI writing and SEO tools, a background remover, image tools, Pathao courier integration, WhatsApp, verified customer accounts and order tracking, and a licence and installer system.
- **Deployment:** gunicorn behind nginx (systemd), or Passenger on shared cPanel hosting.

## Why we built it

DS-Pythone is DearSoft's own product. We built it to help store owners who already run an OpenCart-based shop &mdash; commonly with a theme system like Journal 3 &mdash; move that same store to Python without losing their catalog, customers, orders or theme settings, and without starting over. That is the whole point of the project: existing OpenCart-based stores, kept running, on Python.

## Where the code comes from

We say this plainly:

- The base platform is **OpenCart 3.0.5.1** (GPL-3.0), ported to Python.
- The storefront theme engine and the visual Studio builder derive from the **Journal 3** theme, also ported to Python. The Studio's admin front end is a compiled JavaScript bundle from that theme, unmodified apart from renamed labels. We are replacing this layer with newly written code over time.
- The Python port of the engine and DearSoft's own features (AI, image tools, Pathao, WhatsApp, customer accounts, licence system, installer) are written by DearSoft.
- DS-Pythone is compatible with OpenCart and Journal 3 and is not affiliated with, sponsored by, or endorsed by OpenCart or Journal 3.

Details are in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## What is in this repository

| Path | What it is |
|---|---|
| [`docs/PROOF.md`](docs/PROOF.md) | Proof sheet: live links, code facts, provenance and project details |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Folder structure, request flow and the rules used to port PHP to Python |
| [`docs/INSTALL.md`](docs/INSTALL.md) | How a store is installed (local, and on a Linux VPS) |
| [`scripts/setup-vps.sh`](scripts/setup-vps.sh) | The Ubuntu/Debian bootstrap script: venv, gunicorn service, nginx |
| [`samples/pathao.py`](samples/pathao.py) | Pathao Courier REST client (token caching, error handling) |
| [`samples/llm_client.py`](samples/llm_client.py) | Multi-provider LLM client with failover, used by the AI tools |
| [`requirements.txt`](requirements.txt) | Runtime dependencies |
| [`NOTICE.md`](NOTICE.md) | Rights and licensing note |

The two files in `samples/` are shown unchanged. They import nothing from the rest of the codebase except a settings dictionary and a cache object passed in by the caller, so they can be read on their own.

## Review the source

The complete source is commercial software and is shared on request:

- read-only access to a private repository, or
- a guided screen-share walkthrough of the engine, controllers and templates, or
- a live server session showing the Python version and the running service.

Contact: **DearSoft**, <https://dearsoft.com.bd>, WhatsApp / phone +880 1970 004005, founder@dearsoft.com.bd.
