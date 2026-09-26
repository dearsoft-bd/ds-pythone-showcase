# Installing DS-Pythone

This is how a DS-Pythone store is installed. The installer package itself is not in this repository; it is provided with a licence.

## Requirements

| | |
|---|---|
| Python | 3.11 or newer |
| Database | An **empty** MySQL 5.7+ or MariaDB 10.3+ database and a user with full rights on it |
| Packages | Installed from [`requirements.txt`](../requirements.txt) |
| Disk | About 120 MB extracted |

## Local install (Windows, macOS, Linux)

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt        # Windows: .venv\Scripts\pip
```

Create an empty database and a user:

```sql
CREATE DATABASE dspythone CHARACTER SET utf8mb4;
CREATE USER 'dspythone'@'localhost' IDENTIFIED BY 'a-strong-password';
GRANT ALL ON dspythone.* TO 'dspythone'@'localhost';
```

Start the app and open the installer:

```bash
.venv/bin/waitress-serve --listen=127.0.0.1:8080 wsgi:app
# then open http://127.0.0.1:8080/install/
```

The web installer has four steps:

1. **Welcome.**
2. **Requirements check.** Python version, packages, writable folders.
3. **Database and admin account.** Tests the connection, imports the core schema (134 tables) and the theme data, creates the admin user, activates the DS-Pythone theme and writes `config.py`. If anything fails, the form is shown again with your input and no half-written configuration.
4. **Finish.** Links to the storefront and the admin panel.

Once installed, the installer refuses to run again (it answers 403), so it cannot import over a live store.

There is also a **command-line installer** that does the same in one run, for servers where opening a browser wizard is awkward.

## Linux VPS (Ubuntu / Debian)

[`scripts/setup-vps.sh`](../scripts/setup-vps.sh) prepares a fresh server. Run it as root from inside the extracted package:

```bash
sudo ./install/setup-vps.sh shop.example.com 8010
```

It installs system packages, creates the virtual environment, installs the requirements, and writes:

- a **systemd service** running gunicorn (4 sync workers, 120 s timeout) as `www-data`,
- an **nginx** reverse-proxy site with a rule that blocks well-known scanner user agents.

It does not touch the database and does not request certificates. After it finishes:

1. Point the domain's DNS at the server.
2. Create the empty database and user.
3. Open `http://shop.example.com/install/` and walk the wizard.
4. Enable HTTPS with `certbot --nginx -d shop.example.com`.
5. Rename the `install/` folder afterwards. The admin dashboard reminds you until you do.

Every step in the script checks before it changes anything, so it is safe to run again.

## Shared cPanel hosting

Create a Python app in cPanel with `passenger_wsgi.py` as the startup file, install the cPanel requirements file, and open `/install/` on the domain.

## Keeping source files private

Web servers must not serve Python files. The shipped `.htaccess` denies `.py`, `.pyc`, `.toml`, `.cfg` and similar files. On nginx, only the app port is proxied, so the source tree is never exposed.
