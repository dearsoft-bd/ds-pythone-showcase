# DS-Pythone architecture

This document describes how DS-Pythone is put together, and the rules used when the OpenCart PHP code was ported to Python.

## Folder structure

```
wsgi.py               Flask application: routes, static files, hands every page request to the engine
passenger_wsgi.py     entry point for Passenger / LiteSpeed shared hosting
index.py              same app, alternative entry
config.py             per-site settings (database, URLs). Created by the installer, never committed

admin/                the admin application
  controller/         request handlers, one module per route (e.g. catalog/product.py)
  model/              database access for the admin side
  language/en-gb/     language strings (Python dicts)
  view/               Twig templates, JavaScript and CSS for the admin

catalog/              the storefront application
  controller/         request handlers (product/category.py, checkout/cart.py, ...)
  model/              database access for the storefront
  language/en-gb/     language strings
  view/theme/         Twig templates and assets of the DS-Pythone theme

system/               the engine and shared libraries
  framework.py        builds a request context and runs a request
  engine/             Registry, Loader, Router, Action, Event, Controller, Model
  library/            cart, db, session, cache, mail, template (Jinja2), and the extras below
  library/dearsoft/   DearSoft AI (LLM client, chat engine, SEO fill, image tools), WhatsApp
  library/dspythone/  licence client, customer accounts, blog and layout helpers
  helper/             small utility functions used across the code
  config/             default, catalog and admin configuration (pre-action lists, events)

install/              4-step web installer, command-line installer, SQL schema and setup scripts
tools/                maintenance scripts (database doctor, smoke test, bytecode packaging)
tests/                tests
image/                uploaded images and a generated image cache
```

## Request flow

1. **`wsgi.py`** receives the HTTP request through Flask.
   - Static paths (`/image/...`, `/catalog/view/...`, `/admin/view/...`) are served directly from disk.
   - `/index.php` and `/` go to the storefront, `/admin/...` goes to the admin application. The `index.php?route=...` URL style of the original platform is kept, and pretty URLs are resolved by a SEO-URL step.
2. **`system/framework.py::start(application, source)`** builds a fresh **Registry** for the request. The registry holds the config, database, session, cache, language, document, response, loader, event system and URL helper. Nothing is shared between requests.
3. **Pre-actions** run in order. They are listed in `system/config/*.py` (`action_pre_action`): session, startup, error handling, events, maintenance mode, licence and billing gates, SEO URL resolution.
4. The **Router** picks the route (for example `product/category`) and an **Action** resolves it to a controller file and method.
5. **`system/engine/_modules.py`** loads the controller module and runs it with the shared names (see the porting rules). The class name is computed from the route, so `product/category` becomes `ControllerProductCategory`.
6. The controller calls **models** (through a proxy that fires `before` and `after` events), builds a data dictionary and renders a **Twig template** with Jinja2 (`system/library/template/`). Twig syntax is preprocessed to Jinja2.
7. The result is a **Response** object, which `wsgi.py` turns into a Flask response. A redirect is raised as an exception, replacing PHP's `exit`.

Events (`before` / `after` hooks on controllers, models and views) are how modules such as the AI tools, courier integrations and licence gates attach without editing core files.

## Porting rules (PHP to Python)

The port is a deliberate **line-for-line translation**, not an idiomatic rewrite, so that behaviour matches the original and upstream fixes can be compared.

- **Names stay the same.** Class names keep the PHP form (`ControllerProductCategory`, `ModelCatalogCategory`). Method names stay camelCase (`setOutput`, `isLogged`, `link`), so call sites read like the original.
- **Shared globals are injected.** Controllers and models do not import the platform globals. The loader injects `Controller`, `Model`, `Action`, table prefix, directory constants, version and the helper functions into each module. Real library classes are imported normally.
- **PHP truthiness is preserved where it matters.** Configuration strings are wrapped in a small string type where `""` and `"0"` are false, as in PHP. Plain Python code does not get this for free, so ports of `if ($x)` on values that may be `'0'` need an explicit check.
- **SQL stays string-built** with escaping helpers and `int()` casts exactly as in the original, so every cast is kept during translation.
- **Loops keep their inner guards.** A translation bug class is dropping a PHP `if` guard inside a `foreach`, which then raises on an empty value. Each such loop is checked when ported.
- **Event handlers** receive the shared mutable argument list, because the engine calls them without spreading it.
- **Runtime context** (storefront or admin) is held in a `contextvars` variable.
- **Templates** keep the `.twig` extension. The Jinja2 environment uses lenient undefined values and shims for the Twig filters that differ.

## Extension points

| Mechanism | Used for |
|---|---|
| Events (`catalog/controller/event/`, `admin/controller/event/`) | Attach behaviour before or after any controller, model or view |
| Modules and layouts | Studio-built pages are stored as data and rendered by module controllers |
| Language files | Python dictionaries per route and language |
| Pre-actions | Gates that run on every request (maintenance, billing notice, licence checks) |

## Deployment shapes

- **Linux VPS:** gunicorn (4 sync workers, 120 s timeout) as a systemd service behind nginx. [`scripts/setup-vps.sh`](scripts/setup-vps.sh) sets this up.
- **Shared cPanel hosting:** Passenger / LiteSpeed through `passenger_wsgi.py`.
- **Local development:** waitress or the Flask development server.

## Provenance

- **Platform base:** OpenCart 3.0.5.1 (GPL-3.0), ported to Python.
- **Theme engine and Studio:** derived from the Journal 3 theme, ported to Python. The Studio's admin front end was originally a compiled JavaScript bundle from that theme; it has since been fully replaced with DearSoft-written code.
- **DearSoft's own work:** the Python engine port, DearSoft AI, image tools, Pathao and WhatsApp integrations, customer accounts, the licence system, the installer, and the Studio admin front end.

The samples in [`samples/`](samples/) are from the last group.
