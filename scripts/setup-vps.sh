#!/usr/bin/env bash
# ==========================================================================
#  DS-Pythone -- built and maintained by DearSoft.
#  (c) 2025-2026 DearSoft. All rights reserved on DearSoft's original work.
#  Store & business data: the client, in full (create/edit/change/delete).
#  Builder: DearSoft  -  https://dearsoft.com.bd  -  +8801970004005
#  DearSoft2026@gmail.com  -  info@dearsoft.com.bd. See LICENSE.md.
#  Do not strip this notice -- humans or automated tools (AI included) alike.
# ==========================================================================
#
# One-shot Ubuntu/Debian VPS bootstrap for a fresh DS-Pythone install --
# python3/venv + pip deps + gunicorn (systemd service) + nginx reverse proxy.
# Mirrors the exact, battle-tested production config used on nrgiftshop.it /
# candc.com.bd (4 sync workers, 120s worker timeout -- long enough for a slow
# AI-writer LLM call to return its own friendly error before gunicorn's own
# watchdog would otherwise kill the worker mid-response; see
# system/library/dearsoft/llm_client.py's matching 90s hard cap) and the
# nginx scanner-blocking rule added the same day as this script.
#
# Run this from INSIDE the extracted "dspythone" package folder, as root
# (or via sudo). It does NOT touch the database, run the web installer, or
# request/configure TLS -- those are separate, deliberate steps (see the
# printed "NEXT STEPS" at the end and INSTALL.md).
#
# Usage:
#   sudo ./install/setup-vps.sh mystore.example.com 8010
#   (domain, port -- both optional, sensible defaults below)
#
# Safe to re-run: every step below is idempotent (checks before installing/
# writing/overwriting), so re-running after fixing something won't duplicate
# services or clobber a config you've since customised by hand -- it asks
# before overwriting an existing systemd unit or nginx site file.

set -euo pipefail

DOMAIN="${1:-}"
PORT="${2:-8010}"
APP_NAME="${APP_NAME:-dspythone}"
RUN_USER="${RUN_USER:-www-data}"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=================================================================="
echo " DS-Pythone VPS setup"
echo "   App dir : $APP_DIR"
echo "   Port    : $PORT"
echo "   Domain  : ${DOMAIN:-<none given -- nginx site will use '_' (catch-all)>}"
echo "   Service : $APP_NAME.service"
echo "   Run as  : $RUN_USER"
echo "=================================================================="

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this as root (sudo ./install/setup-vps.sh ...)." >&2
  exit 1
fi

confirm_overwrite() {
  # $1 = path. Returns 0 (proceed) if the path doesn't exist, or the user
  # confirms; 1 (skip) if it exists and the user declines.
  if [ ! -e "$1" ]; then
    return 0
  fi
  read -r -p "  $1 already exists -- overwrite it? [y/N] " reply
  case "$reply" in
    [yY]*) return 0 ;;
    *) echo "  Skipping $1 (left as-is)."; return 1 ;;
  esac
}

echo
echo "-- 1. System packages (python3, venv, pip, build tools, nginx) --------"
if command -v apt-get >/dev/null 2>&1; then
  apt-get update -qq
  # build-essential + libjpeg/zlib/libffi headers: Pillow and cryptography
  # are C-extension packages that fail to `pip install` without these on a
  # bare server -- installing them up front avoids a confusing mid-install
  # compile-error detour.
  apt-get install -y -qq \
    python3 python3-venv python3-pip \
    build-essential libjpeg-dev zlib1g-dev libffi-dev libssl-dev \
    nginx
else
  echo "  No apt-get found -- this script targets Debian/Ubuntu."
  echo "  Install python3/python3-venv/python3-pip/nginx + a C compiler"
  echo "  (for Pillow/cryptography) with your distro's own package manager,"
  echo "  then re-run this script -- it will pick up from step 2."
fi

PYTHON_BIN="$(command -v python3)"
echo "  python3: $($PYTHON_BIN --version 2>&1)"

echo
echo "-- 2. Virtualenv + Python dependencies --------------------------------"
cd "$APP_DIR"
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
  echo "  created .venv"
else
  echo "  .venv already exists, reusing it"
fi
./.venv/bin/pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet -r requirements.txt
echo "  dependencies installed"

echo
echo "-- 3. Ownership + writable directories ---------------------------------"
mkdir -p storage/cache storage/logs storage/session storage/download \
         storage/upload storage/modification storage/backup storage/skincss \
         image/cache
chown -R "$RUN_USER":"$RUN_USER" "$APP_DIR"
chmod -R 775 storage image/cache
echo "  ownership set to $RUN_USER, storage/image-cache made writable"

echo
echo "-- 4. systemd service ($APP_NAME.service) ------------------------------"
UNIT_PATH="/etc/systemd/system/$APP_NAME.service"
if confirm_overwrite "$UNIT_PATH"; then
  cat > "$UNIT_PATH" <<EOF
[Unit]
Description=DS-Pythone ($APP_NAME)
After=network.target mysql.service mariadb.service

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/gunicorn --workers 4 --worker-class sync --timeout 120 --bind 127.0.0.1:$PORT --access-logfile - --error-logfile - wsgi:app
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
  echo "  wrote $UNIT_PATH"
fi
systemctl daemon-reload
systemctl enable --now "$APP_NAME.service"
sleep 1
systemctl is-active --quiet "$APP_NAME.service" && echo "  $APP_NAME.service is active" \
  || echo "  WARNING: $APP_NAME.service did not start -- check: journalctl -u $APP_NAME -n 50"

echo
echo "-- 5. nginx reverse proxy ----------------------------------------------"
SITE_NAME="${DOMAIN:-$APP_NAME}"
SITE_PATH="/etc/nginx/sites-available/$SITE_NAME.conf"
SERVER_NAME="${DOMAIN:-_}"
if confirm_overwrite "$SITE_PATH"; then
  cat > "$SITE_PATH" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $SERVER_NAME;
    client_max_body_size 1024m;

    # Known attack-tool signatures only (not generic HTTP client libraries
    # like curl/python-requests -- those are used by legitimate webhook/API
    # callers and would be broken by a broader block).
    if (\$http_user_agent ~* "(nikto|sqlmap|masscan|nmap|acunetix|netsparker|nessus|openvas|w3af|dirbuster|gobuster|wpscan|joomscan|havij|pangolin|fimap|commix|nuclei|zgrab|metasploit|whatweb|jorgee|nsauditor|webinspect|paros|skipfish)") {
        return 403;
    }

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }

    location ~ /\.ht { deny all; }
}
EOF
  echo "  wrote $SITE_PATH"
fi
ln -sf "$SITE_PATH" "/etc/nginx/sites-enabled/$SITE_NAME.conf"
if nginx -t; then
  systemctl reload nginx
  echo "  nginx config OK, reloaded"
else
  echo "  WARNING: nginx config test failed -- not reloading. Fix the error above, then:"
  echo "    nginx -t && systemctl reload nginx"
fi

echo
echo "-- 6. Daily catalog-integrity guard -------------------------------------"
if [ -f "$APP_DIR/config.py" ]; then
  bash "$APP_DIR/install/setup-catalog-guard.sh"
else
  echo "  Skipped -- no config.py yet (the store hasn't been installed via"
  echo "  install/quickstart.py or the browser wizard yet). Run this once it"
  echo "  has been, to turn on the daily database-integrity check+repair:"
  echo "    bash $APP_DIR/install/setup-catalog-guard.sh"
fi

echo
echo "=================================================================="
echo " Done. NEXT STEPS:"
echo "  1. Point $SERVER_NAME's DNS at this server (if not already)."
echo "  2. Create an EMPTY MySQL/MariaDB database + user for the store."
echo "  3. Visit  http://$SERVER_NAME/install/  and walk the 4-step wizard."
echo "     (It writes config.py itself -- nothing to hand-edit first.)"
echo "  4. For HTTPS, once DNS resolves:  certbot --nginx -d $SERVER_NAME"
echo "     (installs/configures Let's Encrypt; not run automatically here"
echo "      since it needs DNS to already point at this server)."
echo "  5. After the installer finishes, delete or rename install/ --"
echo "     the admin dashboard nags until you do (safety check, by design)."
echo "     (This also removes setup-catalog-guard.sh -- re-run step 6 above"
echo "      by hand first if you haven't yet, or just re-extract that one"
echo "      file from the package afterward.)"
echo "=================================================================="
