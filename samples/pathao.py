# ==========================================================================
#  DS-Pythone -- built and maintained by DearSoft.
#  (c) 2025-2026 DearSoft. All rights reserved on DearSoft's original work.
#  Store & business data: the client, in full (create/edit/change/delete).
#  Builder: DearSoft  -  https://dearsoft.com.bd  -  +8801970004005
#  DearSoft2026@gmail.com  -  info@dearsoft.com.bd. See LICENSE.md.
#  Do not strip this notice -- humans or automated tools (AI included) alike.
# ==========================================================================
"""Port of system/library/pathao.php.

Pathao Courier REST API client (city/zone/area lookups, price-plan, order
create/status). Constructed directly with credentials (PayPalRest-style),
not via registry ``__get`` magic. The OAuth access token is cached via an
optional ``cache`` object (``self.cache`` from the controller/model that
built this client) so it survives across requests the same way the PHP
version cached it in OpenCart's file cache.
"""
from __future__ import annotations

import json as _json
import time as _time

import requests

SANDBOX_URL = "https://courier-api-sandbox.pathao.com"
PRODUCTION_URL = "https://api-hermes.pathao.com"
_TIMEOUT_CONNECT = 15
_TIMEOUT_TOTAL = 30


class PathaoError(Exception):
    def __init__(self, message, status=0):
        super().__init__(message)
        self.message = message
        self.status = status


class PathaoClient:
    def __init__(self, client_id, client_secret, username, password, sandbox=True, cache=None):
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""
        self.username = username or ""
        self.password = password or ""
        self.sandbox = bool(sandbox)
        self.base_url = SANDBOX_URL if self.sandbox else PRODUCTION_URL
        self.cache = cache
        self.error = {}
        self._token = None
        self._token_exp = 0

    # -- public API ------------------------------------------------------
    def getCities(self):
        response = self._request("GET", "/aladdin/api/v1/city-list")
        return ((response.get("data") or {}).get("data")) or []

    def getZones(self, city_id):
        response = self._request("GET", "/aladdin/api/v1/cities/%d/zone-list" % int(city_id or 0))
        return ((response.get("data") or {}).get("data")) or []

    def getAreas(self, zone_id):
        response = self._request("GET", "/aladdin/api/v1/zones/%d/area-list" % int(zone_id or 0))
        return ((response.get("data") or {}).get("data")) or []

    def getStores(self):
        response = self._request("GET", "/aladdin/api/v1/stores")
        return ((response.get("data") or {}).get("data")) or []

    def calculatePrice(self, data):
        return self._request("POST", "/aladdin/api/v1/merchant/price-plan", data)

    def createOrder(self, data):
        return self._request("POST", "/aladdin/api/v1/orders", data)

    def getOrderInfo(self, consignment_id):
        from urllib.parse import quote
        return self._request("GET", "/aladdin/api/v1/orders/%s/info" % quote(str(consignment_id), safe=""))

    def getError(self):
        return self.error

    # -- token -------------------------------------------------------------
    def _cache_key(self, suffix):
        return "pathao." + ("sandbox" if self.sandbox else "live") + "." + suffix

    def _get_access_token(self):
        if self._token and _time.time() < self._token_exp - 60:
            return self._token

        if self.cache is not None:
            cached = self.cache.get(self._cache_key("token"))
            if cached:
                try:
                    token = cached if isinstance(cached, dict) else _json.loads(cached)
                except Exception:
                    token = None
                if token and token.get("access_token") and token.get("expires_at") and token["expires_at"] > _time.time() + 60:
                    self._token = token["access_token"]
                    self._token_exp = token["expires_at"]
                    return self._token

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }
        result = self._curl("POST", self.base_url + "/aladdin/api/v1/issue-token", payload, {})

        body = result.get("body") or {}
        if not body.get("access_token"):
            self.error["warning"] = body.get("message") or "Unable to authenticate with Pathao. Please check the API credentials."
            return None

        expires_at = _time.time() + int(body.get("expires_in") or 3600)
        self._token = body["access_token"]
        self._token_exp = expires_at

        if self.cache is not None:
            self.cache.set(self._cache_key("token"), {"access_token": self._token, "expires_at": expires_at})

        return self._token

    # -- request helpers -----------------------------------------------
    def _request(self, method, path, data=None):
        access_token = self._get_access_token()
        if not access_token:
            return {"error": True, "message": self.error.get("warning") or "Not authenticated."}

        result = self._curl(method, self.base_url + path, data or {}, {"Authorization": "Bearer " + access_token})
        status = result.get("status") or 0
        body = result.get("body") or {}

        if status < 200 or status >= 300:
            message = body.get("message") or ("Pathao API request failed (HTTP %s)." % status)
            errors = body.get("errors")
            if errors:
                message += " " + _json.dumps(errors)
            self.error["warning"] = message
            return {"error": True, "message": message, "status": status}

        return body

    def _curl(self, method, url, data, headers):
        headers = dict(headers or {})
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=(_TIMEOUT_CONNECT, _TIMEOUT_TOTAL))
            else:
                r = requests.request(
                    method, url, headers=headers, data=_json.dumps(data or {}),
                    timeout=(_TIMEOUT_CONNECT, _TIMEOUT_TOTAL),
                )
        except requests.RequestException as exc:
            return {"status": 0, "body": {"message": "Connection error: %s" % exc}}

        try:
            body = r.json()
        except Exception:
            body = None

        return {"status": r.status_code, "body": body if isinstance(body, dict) else {}}
