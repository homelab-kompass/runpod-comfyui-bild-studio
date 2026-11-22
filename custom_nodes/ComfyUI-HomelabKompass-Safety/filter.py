"""Prompt-side content filter for Homelab-Kompass Bild-Studio.

The Krea 2 Community License requires deployers to implement content filters
or an equivalent review process. This module is a reasonable baseline for a
self-hosted pod: it inspects prompt text and blocks clearly disallowed
requests. It is not a substitute for output classifiers or human review.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

LOG = logging.getLogger("homelab-kompass-safety")

BLOCK_MESSAGE = (
    "This request was blocked by the Homelab-Kompass content filter, which is "
    "required for deployments that use Krea 2 under the Krea 2 Community License. "
    "Disallowed categories include sexual content involving minors (including "
    "fictional depictions), child sexual abuse material, and non-consensual "
    "intimate imagery. The filter is a baseline, not a complete moderator."
)

_SEXUAL = re.compile(
    r"\b("
    r"nsfw|nude|nudes|naked|nudity|porn|pornographic|xxx|sex|sexual|sexy|"
    r"erotic|erotica|sensual|hentai|rule\s*34|r34|"
    r"topless|bottomless|undress(?:ed|ing)?|strip(?:ped|ping)?|"
    r"lingerie|onlyfans|sex\s*tape|explicit"
    r")\b",
    re.IGNORECASE,
)

_MINOR = re.compile(
    r"\b("
    r"child|children|kid|kids|toddler|infant|baby|babies|minor|minors|"
    r"underage|under[\s-]?age|under[\s-]?18|u18|u-18|"
    r"pre[\s-]?teen|preteen|teen(?:ager)?s?|young\s*girl|young\s*boy|"
    r"schoolgirl|schoolboy|loli|lolita|shota|shotacon|"
    r"pedophile|paedophile|pedophilia|paedophilia|csam|child\s*porn"
    r")\b"
    r"|\b([1-9]|1[0-7])\s*(?:year|yr|jahre|j[äa]hrig)s?\s*old\b",
    re.IGNORECASE,
)

_ABSOLUTE = re.compile(
    r"\b("
    r"csam|child\s*porn(?:ography)?|child\s*sexual|"
    r"loli(?:con)?|shotacon|"
    r"non[\s-]?consensual\s+(?:intimate|nude|sexual)|"
    r"revenge\s*porn|deepfake\s+(?:nude|porn)|"
    r"undress\s+(?:her|him|them|this)|"
    r"remove\s+(?:her|his|their|the)\s+clothes|"
    r"take\s+off\s+(?:her|his|their)\s+clothes"
    r")\b",
    re.IGNORECASE,
)


def truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def filter_disabled() -> bool:
    return truthy(os.environ.get("HK_DISABLE_CONTENT_FILTER"))


def extract_strings(obj: Any, acc: list[str] | None = None) -> list[str]:
    """Collect reasonably prompt-like strings from a ComfyUI /prompt payload."""
    if acc is None:
        acc = []
    if isinstance(obj, str):
        text = obj.strip()
        if 2 <= len(text) <= 20000:
            acc.append(text)
        return acc
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Skip bulky binary / image payloads
            if key in {"image", "images", "pixels", "data", "preview"}:
                continue
            extract_strings(value, acc)
        return acc
    if isinstance(obj, (list, tuple)):
        for item in obj:
            extract_strings(item, acc)
    return acc


def check_text(text: str) -> str | None:
    """Return a short reason if the text should be blocked, else None."""
    if not text or not text.strip():
        return None
    if _ABSOLUTE.search(text):
        return "absolute"
    if _MINOR.search(text) and _SEXUAL.search(text):
        return "minor+sexual"
    return None


def check_payload(payload: dict[str, Any]) -> tuple[bool, str | None]:
    """Inspect a ComfyUI POST /prompt body. Returns (blocked, reason_code)."""
    if filter_disabled():
        return False, None
    strings = extract_strings(payload.get("prompt", payload))
    extra = payload.get("extra_data")
    if extra:
        strings.extend(extract_strings(extra))
    # Also evaluate the concatenation so split fields still match.
    joined = "\n".join(strings)
    for candidate in (*strings, joined):
        reason = check_text(candidate)
        if reason:
            return True, reason
    return False, None


def error_response_body() -> dict[str, Any]:
    return {
        "error": {
            "type": "homelab_kompass_content_filter",
            "message": BLOCK_MESSAGE,
            "details": "The request matched a disallowed content category.",
            "extra_info": {},
        },
        "node_errors": {},
    }


def install() -> None:
    """Register the aiohttp middleware on the running PromptServer, if present."""
    if filter_disabled():
        LOG.warning(
            "[homelab-kompass-safety] HK_DISABLE_CONTENT_FILTER is set. "
            "The prompt filter is off. For Krea 2 this can breach the "
            "Krea 2 Community License, which requires content filters or "
            "an equivalent review process."
        )
        return

    try:
        from aiohttp import web
        from server import PromptServer
    except Exception as exc:  # noqa: BLE001
        LOG.warning("[homelab-kompass-safety] Could not import ComfyUI server (%s). Filter not installed.", exc)
        return

    instance = getattr(PromptServer, "instance", None)
    if instance is None or getattr(instance, "app", None) is None:
        LOG.warning("[homelab-kompass-safety] PromptServer is not ready. Filter not installed.")
        return

    @web.middleware
    async def hk_content_filter(request, handler):
        path = request.path.rstrip("/") or "/"
        if request.method == "POST" and path in {"/prompt", "/api/prompt"}:
            try:
                body = await request.read()
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                return await handler(request)
            blocked, reason = check_payload(payload if isinstance(payload, dict) else {})
            if blocked:
                LOG.warning("[homelab-kompass-safety] blocked a /prompt request (%s)", reason)
                return web.json_response(error_response_body(), status=400)
        return await handler(request)

    instance.app.middlewares.append(hk_content_filter)
    LOG.info("[homelab-kompass-safety] prompt filter enabled (Krea 2 Community License).")


__all__ = [
    "BLOCK_MESSAGE",
    "check_payload",
    "check_text",
    "error_response_body",
    "extract_strings",
    "filter_disabled",
    "install",
]
