# DS-Pythone Version 3.13.26 Showcase

Release notes. This is a **documentation release**: it contains no DS-Pythone source code.

## Version
DS-Pythone **3.13.26**, by [DearSoft](https://dearsoft.com.bd). Facts below were checked on 13-14 October 2026.

## What is in this release
- `README.md`, `ARCHITECTURE.md`, `docs/PROOF.md`, `docs/INSTALL.md`: how the platform is built, what it runs on, how it installs.
- `samples/pathao.py` and `samples/llm_client.py`: two DearSoft-written files, shown unchanged.
- `scripts/setup-vps.sh`: the server bootstrap script.

## What is not in this release
- The DS-Pythone source code, the Studio, the themes and the install package. They are commercial software and can be reviewed privately on request (see the README, section "Review the source").

## Code facts (engine folder, 13 October 2026)
- About 1,487 Python files (roughly 155,000 lines) and 869 Twig templates. The engine folder contains no PHP files.
- Python 3.11 or newer, Flask 3, Jinja2, PyMySQL on MySQL / MariaDB.
- Installs from an empty database in minutes: one command or a four-step web installer.

## Live stores (HTTP 200 over valid HTTPS on 14 October 2026)
- https://dearit.com.bd and https://nrgiftshop.it. Check the engine mark yourself: `curl -s https://dearit.com.bd/ | grep -o 'data-engine="[^"]*"'` prints `data-engine="dspythone"`.

## Rights
Copyright (c) DearSoft. All rights reserved. No licence is granted to copy, scrape, republish or adapt this repository's text, structure, diagrams, screenshots or samples, or to use them to train machine-learning models, without DearSoft's written permission. See `LICENSE.md` and `NOTICE.md`.

## Provenance and licences
The storefront theme layer and its settings definitions were created from the Journal 3 theme and are still partly derived from it; builds installed on client sites that still use it also include a compiled Journal 3-derived JavaScript bundle in the Studio admin. DearSoft is replacing derived parts with its own code, and new installs no longer include the bundle. The commerce core builds on OpenCart 3.0.5.1 (GPL-3.0). The Python engine, DS Studio, the AI tools, courier integration, customer accounts and the licence and installer system are written by DearSoft. OpenCart and Journal 3 belong to their respective owners; DS-Pythone is not affiliated with, sponsored by, or endorsed by them.

Contact: https://dearsoft.com.bd
