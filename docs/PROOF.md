# DS-Pythone proof sheet

*SaaS update: 10 October 2026 · Live checks: 14 October 2026 · Source snapshot: 13 October 2026 · DS-Pythone version 3.13.26. The same content is on <https://dearsoft.com.bd/proof>.*

DS-Pythone is an e-commerce CMS and storefront written in Python, created by DearSoft (Mr. Khandaker Readul Islam, [about the founder](https://dearsoft.com.bd/founder)). Three things prove it, and this sheet covers each one.

| 1. Live project link | 2. Source evidence | 3. Project details |
|---|---|---|
| Three public projects: commerce and service websites. | Code facts and review: numbers now, source access on request. | Client and catalog: country, business, size, status. |

## DearSoft Stores: managed Python commerce

**Working SaaS capabilities. Explicit limits.**

DS-Pythone now has a managed store workspace: verified owner accounts, isolated private hosting, free addresses, custom-domain verification, HTTPS and owner-only storefront preview. Start in private while visitors see a branded maintenance page.

- Verified on 10 October 2026: actual private provisioning, custom-domain ownership TXT, valid HTTPS and primary URL switching.
- Owner preview returns the real storefront; anonymous visitors receive maintenance (HTTP 503). Anonymous admin and direct upstream access remain restricted.
- 41 focused automated tests passed for portal/domain/preview behavior at the maintenance-design release. Tests are engineering checks, not an independent security certification.
- Billing and license-server promotional publishing remain unconnected; selecting Live alone does not publish a store.
- No comparative speed ranking or Lighthouse score is claimed. Product pages use one local stylesheet, system fonts and no application JavaScript bundle. Existing CDN analytics may add a beacon; network timing is not a full user-experience benchmark.

## 1. Live project link: three public projects you can open

These public project links are separate from new private SaaS tenants. The marker shown below was part of the September source snapshot; an HTML label alone does not prove the server runtime. Use a guided server/source review for runtime evidence.

| Project | Address | Status |
|---|---|---|
| Dear IT | <https://dearit.com.bd> | Live, DS-Pythone |
| NR Gift Shop | <https://nrgiftshop.it> | Live, DS-Pythone |
| DearService | <https://dearservice.com.bd> | Public live, DS-Pythone |

**Live checks, 14 October 2026.** The home pages of dearit.com.bd, nrgiftshop.it and dearservice.com.bd, and DearService's contact page, returned HTTP 200 over valid HTTPS without owner login. On 10 October 2026 DearService's active hosting service was reported as running Python 3.12. This is an existing public service website, not evidence that the new SaaS billing/publishing integration is complete.

```bash
# any terminal
curl -s https://dearit.com.bd/ | grep -o 'data-engine="[^"]*"'
curl -s https://nrgiftshop.it/ | grep -o 'data-engine="[^"]*"'
# both print:
data-engine="dspythone"
```

## 2. Source-code evidence: what the code looks like

Counted on the source tree on 13 October 2026 (engine folder; tests included), excluding virtual environments, caches, storage, uploaded images and build output.

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

DS-Pythone is a Python e-commerce platform. This section lists what it runs on, what DearSoft wrote, and the third-party licences that apply. Current version: 3.13.26. Source and showcase: [github.com/dearsoft-bd/ds-pythone-showcase](https://github.com/dearsoft-bd/ds-pythone-showcase).

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

**GitHub showcase:** [github.com/dearsoft-bd/ds-pythone-showcase](https://github.com/dearsoft-bd/ds-pythone-showcase) — this proof sheet, the architecture notes, install steps and a couple of standalone DearSoft-written source files, kept in sync with the proof page.

**Google Developer Groups:** member of Google Developer Groups (GDG) — membership ID `BCR2DN6DZKPLD6RF`. Google Developer Program profile with badges: <https://g.dev/dearsoft>.

## 3. Client and project details: the three projects

| Project | Country | Business | Catalog and speed | Status |
|---|---|---|---|---|
| [Dear IT](https://dearit.com.bd) | Bangladesh | IT accessories, laptop sales and repairs. DearSoft's own showcase store. | About 2,350 products (public sitemap, 14 October 2026), migrated intact. Home page about 0.8 s (median of 5 requests, 14 Oct 2026). HTTPS / HTTP 200, checked 14 October 2026. | Live |
| [NR Gift Shop](https://nrgiftshop.it) | Italy (Florence) | Premium gifts and retail for shoppers in Italy. | About 370 products (public sitemap, 14 October 2026). Moved from a PHP store to the Python engine. HTTPS / HTTP 200, checked 14 October 2026. | Live |
| [DearService](https://dearservice.com.bd) | Bangladesh | Repair and service website. | Homepage and contact page: HTTPS / HTTP 200, checked 14 October 2026. No catalog count or speed benchmark claimed. | Public live |

Other stores also run on the platform. Their details are shared only with each client's permission.

## Contact

Ask for a source walkthrough, a live server session or a clean install on a call.

- Email: founder@dearsoft.com.bd
- WhatsApp / phone: +880 1970 004005
- Web: <https://dearsoft.com.bd>
