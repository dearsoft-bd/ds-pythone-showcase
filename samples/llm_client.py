# ==========================================================================
#  DS-Pythone -- built and maintained by DearSoft.
#  (c) 2025-2026 DearSoft. All rights reserved on DearSoft's original work.
#  Store & business data: the client, in full (create/edit/change/delete).
#  Builder: DearSoft  -  https://dearsoft.com.bd  -  +8801970004005
#  DearSoft2026@gmail.com  -  info@dearsoft.com.bd. See LICENSE.md.
#  Do not strip this notice -- humans or automated tools (AI included) alike.
# ==========================================================================
"""Port of ``system/library/dearsoft/LLMClient.php`` — server-side proxy to
multiple LLM providers. Free tier: Groq only. Pro tier: OpenAI, Claude,
DeepSeek, Mistral, GLM, OpenRouter, Gemini, Custom. API key never reaches
the browser.

SCOPE: only the one-shot ``chat()``/``chatWithFailover()`` (admin AI-writer
features — Write Assistant, SEO auto-fill, Key Feature) and ``chatWithImage()``
(image analyzer / vision) paths are ported. ``callWithTools()`` and its
failover wrapper — the storefront chat widget's product-search tool-calling
engine — are NOT ported here; that's a separate, deliberately-deferred piece
(see ``catalog/controller/extension/module/dearsoft_api.py``'s docstring).
"""
from __future__ import annotations

import re
import signal
from typing import Any

import requests

_PROVIDERS: dict[str, dict[str, Any]] = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "compat": "openai",
        # llama-3.1-8b-instant was deprecated by Groq and shut down 2026-08-16
        # (confirmed live: console.groq.com/docs/deprecations) -- every
        # request with the old default model now fails outright. Groq's own
        # migration guidance names openai/gpt-oss-20b as the replacement.
        "model": "openai/gpt-oss-20b",
        "label": "Groq (Free)",
        "pro": False,
        "signup_url": "https://console.groq.com/keys",
        "signup_label": "console.groq.com",
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "compat": "openai",
        "model": "gpt-4o-mini",
        "label": "OpenAI / GPT",
        "pro": True,
        "signup_url": "https://platform.openai.com/api-keys",
        "signup_label": "platform.openai.com",
    },
    "claude": {
        "url": "https://api.anthropic.com/v1/messages",
        "compat": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "label": "Claude — Anthropic",
        "pro": True,
        "signup_url": "https://console.anthropic.com/settings/keys",
        "signup_label": "console.anthropic.com",
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "compat": "openai",
        "model": "deepseek-chat",
        "label": "DeepSeek",
        "pro": True,
        "signup_url": "https://platform.deepseek.com/api_keys",
        "signup_label": "platform.deepseek.com",
    },
    "glm": {
        "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "compat": "openai",
        "model": "glm-4-flash",
        "label": "GLM / ZhipuAI",
        "pro": True,
        "signup_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "signup_label": "open.bigmodel.cn",
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "compat": "openai",
        "model": "mistral-small-latest",
        "label": "Mistral",
        "pro": True,
        "signup_url": "https://console.mistral.ai/api-keys/",
        "signup_label": "console.mistral.ai",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "compat": "openai",
        # google/gemma-3-27b-it:free was pulled from OpenRouter's free tier
        # (now paid-only, confirmed via a live 404 pointing at the paid
        # slug). nemotron-3-nano-omni tested live against several other
        # currently-free models for this exact copywriting use case --
        # correct, well-formatted product name/description output where two
        # other free candidates returned nothing usable.
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "label": "OpenRouter",
        "pro": True,
        "signup_url": "https://openrouter.ai/keys",
        "signup_label": "openrouter.ai",
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "compat": "openai",
        # gemini-2.5-flash is no longer available to new-user API keys (Google
        # returns a 404 telling callers to switch to gemini-3.6-flash) -- hit
        # exactly this live on a fresh Gemini key, confirmed via a raw request
        # to this same endpoint before changing it.
        "model": "gemini-3.6-flash",
        "label": "Gemini — Google",
        "pro": True,
        "signup_url": "https://aistudio.google.com/apikey",
        "signup_label": "aistudio.google.com",
    },
    "custom": {
        "url": "",
        "compat": "openai",
        "model": "",
        "label": "Custom Endpoint",
        "pro": True,
        "signup_url": "",
        "signup_label": "",
    },
}

_GPT5_O_SERIES = re.compile(r"(^|/)(gpt-5|o[134])([-.]|$)", re.IGNORECASE)


class LLMError(RuntimeError):
    pass


def get_providers() -> dict[str, dict[str, Any]]:
    return _PROVIDERS


class LLMClient:
    def __init__(self, settings: dict, db=None):
        self.provider = settings.get("llm_provider") or "openai"
        self.api_key = settings.get("llm_api_key") or ""
        self.model = settings.get("llm_model") or ""
        self.base_url = settings.get("llm_base_url") or ""
        self.max_tokens = int(settings.get("llm_max_tokens") or 1024)
        self.db = db
        self.expose_raw_errors = bool(settings.get("expose_raw_errors"))

        self.extra_llm_slots: list[dict[str, str]] = []
        providers = settings.get("llm_failover_provider") or []
        api_keys = settings.get("llm_failover_api_key") or []
        models = settings.get("llm_failover_model") or []
        base_urls = settings.get("llm_failover_base_url") or []
        for i, provider in enumerate(providers):
            provider = str(provider).strip()
            api_key = str(api_keys[i] if i < len(api_keys) else "").strip()
            if not provider or not api_key:
                continue
            self.extra_llm_slots.append({
                "provider": provider,
                "apiKey": api_key,
                "model": str(models[i] if i < len(models) else "").strip(),
                "baseUrl": str(base_urls[i] if i < len(base_urls) else "").strip(),
            })

    # ── Public entry points ────────────────────────────────────────────

    def chat(self, system_prompt: str, history: list[dict], user_message: str) -> str:
        if not self.api_key:
            raise LLMError("LLM API key is not configured. Please set it in the admin panel.")

        if self.provider == "custom":
            if not self.base_url:
                raise LLMError("Custom provider requires a Base URL.")
            return self._call_openai_compat(self.base_url, self.model or "default", system_prompt, history, user_message)

        config = _PROVIDERS.get(self.provider)
        if not config:
            raise LLMError("Unknown LLM provider: " + self.provider)

        url = self.base_url or config["url"]
        model = self.model or config["model"]

        if config["compat"] == "anthropic":
            return self._call_anthropic(url, model, system_prompt, history, user_message)
        return self._call_openai_compat(url, model, system_prompt, history, user_message)

    def chat_with_failover(self, system_prompt: str, history: list[dict], user_message: str) -> str:
        return self._run_with_provider_failover(lambda: self.chat(system_prompt, history, user_message))

    def call_with_tools(self, system_prompt: str, messages: list[dict], tools: list[dict]) -> dict:
        """Tool-calling round-trip for the storefront chat engine.

        `messages` is a stack of {role, content} plus, for assistant turns,
        `tool_calls` [{id, name, arguments(dict)}] and for tool turns
        `tool_call_id`. Returns {stop_reason: 'end_turn'|'tool_use',
        content: str, tool_calls: [{id, name, arguments(dict)}]}.
        """
        if not self.api_key:
            raise LLMError("LLM API key is not configured. Please set it in the admin panel.")

        if self.provider == "custom":
            if not self.base_url:
                raise LLMError("Custom provider requires a Base URL.")
            return self._call_openai_compat_tools(self.base_url, self.model or "default", system_prompt, messages, tools)

        config = _PROVIDERS.get(self.provider)
        if not config:
            raise LLMError("Unknown LLM provider: " + self.provider)
        url = self.base_url or config["url"]
        model = self.model or config["model"]
        if config["compat"] == "anthropic":
            return self._call_anthropic_tools(url, model, system_prompt, messages, tools)
        return self._call_openai_compat_tools(url, model, system_prompt, messages, tools)

    def call_with_tools_failover(self, system_prompt: str, messages: list[dict], tools: list[dict]) -> dict:
        return self._run_with_provider_failover(
            lambda: self.call_with_tools(system_prompt, messages, tools)
        )

    def chat_with_image(self, system_prompt: str, user_message: str, image_url: str) -> str:
        if not self.api_key:
            raise LLMError("LLM API key is not configured. Please set it in the admin panel.")

        if self.provider == "custom":
            if not self.base_url:
                raise LLMError("Custom provider requires a Base URL.")
            return self._call_openai_compat_vision(self.base_url, self.model or "default", system_prompt, user_message, image_url)

        config = _PROVIDERS.get(self.provider)
        if not config:
            raise LLMError("Unknown LLM provider: " + self.provider)

        url = self.base_url or config["url"]
        model = self.model or config["model"]

        if config["compat"] == "anthropic":
            return self._call_anthropic_vision(url, model, system_prompt, user_message, image_url)
        return self._call_openai_compat_vision(url, model, system_prompt, user_message, image_url)

    # ── Failover ────────────────────────────────────────────────────────

    def _run_with_provider_failover(self, attempt):
        if not self.extra_llm_slots:
            return attempt()

        original = {"provider": self.provider, "apiKey": self.api_key, "model": self.model, "baseUrl": self.base_url}
        chain = [original] + self.extra_llm_slots
        errors = []
        try:
            for i, slot in enumerate(chain):
                self.provider = slot["provider"]
                self.api_key = slot["apiKey"]
                self.model = slot["model"]
                self.base_url = slot["baseUrl"]
                try:
                    return attempt()
                except LLMError as e:
                    errors.append("Slot " + str(i + 1) + " (" + slot["provider"] + "): " + str(e))
        finally:
            self.provider = original["provider"]
            self.api_key = original["apiKey"]
            self.model = original["model"]
            self.base_url = original["baseUrl"]

        raise LLMError("All configured AI providers failed. " + " | ".join(errors))

    # ── Provider call implementations ──────────────────────────────────

    def _token_param_name(self, model: str) -> str:
        return "max_completion_tokens" if _GPT5_O_SERIES.search(model) else "max_tokens"

    def _call_openai_compat(self, url: str, model: str, system_prompt: str, history: list[dict], user_message: str) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        for turn in history:
            if "role" in turn and "content" in turn:
                role = turn["role"] if turn["role"] in ("user", "assistant") else "user"
                messages.append({"role": role, "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})

        token_param = self._token_param_name(model)
        payload = {"model": model, "messages": messages, token_param: self.max_tokens}
        headers = {"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"}

        return self._extract_openai_reply(self._post(url, payload, headers))

    def _call_openai_compat_tools(self, url: str, model: str, system_prompt: str, messages: list[dict], tools: list[dict]) -> dict:
        import json as _json

        oai = [{"role": "system", "content": system_prompt}]
        for m in messages:
            role = m.get("role") or "user"
            if role == "tool":
                oai.append({
                    "role": "tool",
                    "tool_call_id": str(m.get("tool_call_id") or ""),
                    "content": str(m.get("content") or ""),
                })
                continue
            entry = {"role": role, "content": str(m.get("content") or "")}
            if role == "assistant" and m.get("tool_calls"):
                entry["tool_calls"] = []
                for tc in m["tool_calls"]:
                    args = tc.get("arguments")
                    entry["tool_calls"].append({
                        "id": str(tc.get("id") or ""),
                        "type": "function",
                        "function": {
                            "name": str(tc.get("name") or ""),
                            "arguments": args if isinstance(args, str) else _json.dumps(args or {}),
                        },
                    })
                if entry["content"] == "":
                    entry["content"] = None
            oai.append(entry)

        oai_tools = [{
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("parameters") or {"type": "object", "properties": {}},
            },
        } for t in tools]

        token_param = self._token_param_name(model)
        payload = {"model": model, "messages": oai, token_param: self.max_tokens}
        if oai_tools:
            payload["tools"] = oai_tools
            payload["tool_choice"] = "auto"
        headers = {"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"}

        result = self._post(url, payload, headers)
        data, http_code = result["data"], result["http_code"]
        msg = ((data.get("choices") or [{}])[0] or {}).get("message")
        if http_code != 200 or not msg:
            api_error = (data.get("error") or {}).get("message") or ("HTTP " + str(http_code))
            raise LLMError(self._friendly_error(http_code, api_error))

        finish = ((data.get("choices") or [{}])[0] or {}).get("finish_reason") or ""
        content = "" if msg.get("content") is None else str(msg.get("content"))
        tool_calls = []
        for tc in (msg.get("tool_calls") or []):
            args_raw = (tc.get("function") or {}).get("arguments") or "{}"
            try:
                args = args_raw if isinstance(args_raw, dict) else _json.loads(args_raw)
            except (ValueError, TypeError):
                args = {}
            tool_calls.append({
                "id": str(tc.get("id") or ""),
                "name": str((tc.get("function") or {}).get("name") or ""),
                "arguments": args if isinstance(args, dict) else {},
            })
        stop_reason = "tool_use" if (tool_calls or finish == "tool_calls") else "end_turn"
        return {"stop_reason": stop_reason, "content": content, "tool_calls": tool_calls}

    def _call_anthropic_tools(self, url: str, model: str, system_prompt: str, messages: list[dict], tools: list[dict]) -> dict:
        import json as _json

        amsgs = []
        for m in messages:
            role = m.get("role") or "user"
            if role == "tool":
                amsgs.append({"role": "user", "content": [{
                    "type": "tool_result",
                    "tool_use_id": str(m.get("tool_call_id") or ""),
                    "content": str(m.get("content") or ""),
                }]})
                continue
            if role == "assistant" and m.get("tool_calls"):
                blocks = []
                if m.get("content"):
                    blocks.append({"type": "text", "text": str(m["content"])})
                for tc in m["tool_calls"]:
                    blocks.append({
                        "type": "tool_use", "id": str(tc.get("id") or ""),
                        "name": str(tc.get("name") or ""), "input": tc.get("arguments") or {},
                    })
                amsgs.append({"role": "assistant", "content": blocks})
                continue
            amsgs.append({"role": role, "content": str(m.get("content") or "")})

        atools = [{
            "name": t["name"], "description": t.get("description", ""),
            "input_schema": t.get("parameters") or {"type": "object", "properties": {}},
        } for t in tools]

        payload = {"model": model, "system": system_prompt, "messages": amsgs, "max_tokens": self.max_tokens}
        if atools:
            payload["tools"] = atools
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}

        result = self._post(url, payload, headers)
        data, http_code = result["data"], result["http_code"]
        if http_code != 200 or not data.get("content"):
            api_error = (data.get("error") or {}).get("message") or ("HTTP " + str(http_code))
            raise LLMError(self._friendly_error(http_code, api_error))

        content, tool_calls = "", []
        for block in data.get("content") or []:
            if block.get("type") == "text":
                content += block.get("text") or ""
            elif block.get("type") == "tool_use":
                tool_calls.append({
                    "id": str(block.get("id") or ""), "name": str(block.get("name") or ""),
                    "arguments": block.get("input") or {},
                })
        stop_reason = "tool_use" if tool_calls or data.get("stop_reason") == "tool_use" else "end_turn"
        return {"stop_reason": stop_reason, "content": content, "tool_calls": tool_calls}

    def _call_openai_compat_vision(self, url: str, model: str, system_prompt: str, user_message: str, image_url: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]},
        ]
        token_param = self._token_param_name(model)
        payload = {"model": model, "messages": messages, token_param: self.max_tokens}
        headers = {"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"}

        return self._extract_openai_reply(self._post(url, payload, headers))

    def _call_anthropic(self, url: str, model: str, system_prompt: str, history: list[dict], user_message: str) -> str:
        messages = []
        for turn in history:
            if "role" in turn and "content" in turn:
                role = turn["role"] if turn["role"] in ("user", "assistant") else "user"
                messages.append({"role": role, "content": turn["content"]})
        messages.append({"role": "user", "content": user_message})

        payload = {"model": model, "system": system_prompt, "messages": messages, "max_tokens": self.max_tokens}
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}

        result = self._post(url, payload, headers)
        data, http_code = result["data"], result["http_code"]
        content = data.get("content") or []
        text = content[0].get("text") if content and isinstance(content[0], dict) else None
        if http_code != 200 or not text:
            api_error = (data.get("error") or {}).get("message") or ("HTTP " + str(http_code))
            raise LLMError(self._friendly_error(http_code, api_error))
        return str(text)

    def _call_anthropic_vision(self, url: str, model: str, system_prompt: str, user_message: str, image_url: str) -> str:
        if image_url.startswith("data:"):
            m = re.match(r"^data:([^;]+);base64,(.+)$", image_url, re.DOTALL)
            image_block = {"type": "image", "source": {"type": "base64", "media_type": m.group(1), "data": m.group(2)}} if m \
                else {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": ""}}
        else:
            image_block = {"type": "image", "source": {"type": "url", "url": image_url}}

        messages = [{"role": "user", "content": [image_block, {"type": "text", "text": user_message}]}]
        payload = {"model": model, "system": system_prompt, "messages": messages, "max_tokens": self.max_tokens}
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}

        result = self._post(url, payload, headers)
        data, http_code = result["data"], result["http_code"]
        content = data.get("content") or []
        text = content[0].get("text") if content and isinstance(content[0], dict) else None
        if http_code != 200 or not text:
            api_error = (data.get("error") or {}).get("message") or ("HTTP " + str(http_code))
            raise LLMError(self._friendly_error(http_code, api_error))
        return str(text)

    def _extract_openai_reply(self, result: dict) -> str:
        data, http_code = result["data"], result["http_code"]
        choices = data.get("choices") or []
        content = choices[0].get("message", {}).get("content") if choices else None
        if http_code != 200 or not content:
            api_error = (data.get("error") or {}).get("message") or ("HTTP " + str(http_code))
            raise LLMError(self._friendly_error(http_code, api_error))
        return str(content)

    # requests' own `timeout=` only bounds a single socket read at a time --
    # a slow/"thinking" reasoning model that trickles a chunked response with
    # gaps just under that per-chunk window can still run for minutes in
    # total without ever tripping it. That total duration can then outlast
    # gunicorn's own worker --timeout, which hard-kills the worker mid-read
    # with no HTTP response at all -- the browser's AJAX call never gets a
    # success or error callback and the "Generating..." button is stuck
    # forever (seen live on nrgiftshop.it: a worker killed by its 120s
    # timeout while still blocked reading an OpenRouter reasoning-model
    # reply). A hard wall-clock cap here guarantees we always come back with
    # a clean JSON error well before that watchdog can fire.
    _HARD_TIMEOUT_SECONDS = 90

    def _post(self, url: str, payload: dict, headers: dict) -> dict:
        use_alarm = hasattr(signal, "SIGALRM")
        old_handler = None
        if use_alarm:
            def _on_alarm(signum, frame):
                raise TimeoutError("hard wall-clock timeout")
            old_handler = signal.signal(signal.SIGALRM, _on_alarm)
            signal.alarm(self._HARD_TIMEOUT_SECONDS)
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
        except TimeoutError as e:
            raise LLMError(self._friendly_error(0, "The AI service is taking too long to respond. Please try again.")) from e
        except requests.RequestException as e:
            raise LLMError(self._friendly_error(0, str(e))) from e
        finally:
            if use_alarm:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        try:
            data = resp.json()
        except ValueError:
            data = {}
        return {"data": data if isinstance(data, dict) else {}, "http_code": resp.status_code}

    def _friendly_error(self, status: int, raw_msg: str) -> str:
        haystack = raw_msg.lower()
        is_rate_limit = (
            status == 429
            or "rate limit" in haystack
            or "tokens per minute" in haystack
            or "tpm" in haystack
            or "too many requests" in haystack
        )
        if is_rate_limit:
            if self.db is not None:
                try:
                    from system.library.dearsoft import rate_limit_counter
                    rate_limit_counter.increment(self.db)
                except Exception:
                    pass
            return self._with_raw_detail("I'm getting a lot of questions right now — please try again after some time.", status, raw_msg)

        is_auth = status in (401, 403) or "invalid api key" in haystack or "unauthorized" in haystack or "authentication" in haystack
        if is_auth:
            return self._with_raw_detail("The assistant isn't fully set up yet. Please contact the store for help.", status, raw_msg)

        if status >= 500 or status == 0:
            return self._with_raw_detail("The assistant is temporarily unavailable. Please try again in a moment.", status, raw_msg)

        return self._with_raw_detail("Sorry, I'm having trouble responding right now. Please try again.", status, raw_msg)

    def _with_raw_detail(self, friendly: str, status: int, raw_msg: str) -> str:
        if not self.expose_raw_errors:
            return friendly
        detail = raw_msg.strip() or ("HTTP " + str(status))
        return friendly + " [" + str(status) + ": " + detail + "]"
