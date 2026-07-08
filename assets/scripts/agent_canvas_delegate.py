#!/usr/bin/env python3
"""Small Agent Canvas API helper for SDLC child conversations."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_CANDIDATES = (
    "http://localhost:8000",
    "http://127.0.0.1:18000",
)
DEFAULT_UI_BASE = "http://localhost:8000"
TERMINAL_STATUSES = {"finished", "idle", "error", "stuck", "stopped"}
DEFAULT_TOOLS = (
    {"name": "terminal", "params": {}},
    {"name": "file_editor", "params": {}},
    {"name": "task_tracker", "params": {}},
)


class CanvasAPIError(RuntimeError):
    """Raised when the local Agent Canvas API cannot satisfy a request."""


def read_session_key() -> str:
    for env_name in ("SESSION_API_KEY", "OH_SESSION_API_KEYS_0", "LOCAL_BACKEND_API_KEY"):
        value = os.getenv(env_name)
        if value:
            return value.strip()

    for key_file in (
        Path.home() / ".openhands" / "agent-canvas" / "api-key.txt",
        Path.home() / ".openhands" / "agent-canvas" / "session-api-key.txt",
    ):
        if key_file.exists():
            value = key_file.read_text(encoding="utf-8").strip()
            if value:
                return value

    raise CanvasAPIError("No Agent Canvas session API key found")


def http_json(
    method: str,
    url: str,
    *,
    key: str | None = None,
    payload: dict[str, Any] | None = None,
    expose_encrypted_secrets: bool = False,
    timeout: int = 60,
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    data = None
    if key:
        headers["X-Session-API-Key"] = key
    if expose_encrypted_secrets:
        headers["X-Expose-Secrets"] = "encrypted"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise CanvasAPIError(f"{method} {url} returned HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise CanvasAPIError(f"{method} {url} failed: {exc.reason}") from exc

    if not body:
        return {}
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise CanvasAPIError(f"{method} {url} returned non-JSON response") from exc


def base_candidates(explicit_base: str | None = None) -> list[str]:
    candidates: list[str] = []
    for value in (
        explicit_base,
        os.getenv("AGENT_CANVAS_BACKEND"),
        os.getenv("AGENT_CANVAS_BASE"),
        *DEFAULT_BASE_CANDIDATES,
    ):
        if value and value.rstrip("/") not in candidates:
            candidates.append(value.rstrip("/"))
    return candidates


def discover_base(explicit_base: str | None, key: str) -> str:
    errors: list[str] = []
    for candidate in base_candidates(explicit_base):
        try:
            http_json("GET", f"{candidate}/server_info", timeout=10)
            http_json("GET", f"{candidate}/api/settings", key=key, timeout=10)
            return candidate
        except CanvasAPIError as exc:
            errors.append(f"{candidate}: {exc}")
    raise CanvasAPIError("No reachable Agent Canvas API found. Tried: " + "; ".join(errors))


def unique_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for tool in tools:
        name = tool.get("name")
        if name:
            merged[name] = tool
    return list(merged.values())


def build_agent_settings(settings_response: dict[str, Any]) -> dict[str, Any]:
    agent_settings = dict(settings_response.get("agent_settings") or {})
    agent_settings.pop("schema_version", None)
    agent_settings.pop("mcp_config", None)
    agent_settings["tools"] = unique_tools(
        [*list(agent_settings.get("tools") or []), *DEFAULT_TOOLS]
    )
    return agent_settings


def build_conversation_payload(
    *,
    settings_response: dict[str, Any],
    prompt: str,
    workspace: Path,
    max_iterations: int | None,
    run: bool = True,
) -> dict[str, Any]:
    conversation_settings = settings_response.get("conversation_settings") or {}
    return {
        "secrets_encrypted": True,
        "agent_settings": build_agent_settings(settings_response),
        "workspace": {"kind": "LocalWorkspace", "working_dir": str(workspace.resolve())},
        "confirmation_policy": {"kind": "NeverConfirm"},
        "max_iterations": max_iterations
        or conversation_settings.get("max_iterations")
        or 500,
        "stuck_detection": True,
        "autotitle": True,
        "worktree": False,
        "initial_message": {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
            "run": run,
        },
    }


def create_conversation(
    *,
    base: str,
    key: str,
    settings_response: dict[str, Any],
    prompt: str,
    workspace: Path,
    max_iterations: int | None,
    run: bool = True,
) -> dict[str, Any]:
    payload = build_conversation_payload(
        settings_response=settings_response,
        prompt=prompt,
        workspace=workspace,
        max_iterations=max_iterations,
        run=run,
    )
    return http_json("POST", f"{base}/api/conversations", key=key, payload=payload)


def conversation_summary(base: str, ui_base: str, response: dict[str, Any]) -> dict[str, Any]:
    conversation_id = response.get("id")
    summary = {
        "id": conversation_id,
        "title": response.get("title"),
        "execution_status": response.get("execution_status"),
        "workspace": response.get("workspace"),
        "max_iterations": response.get("max_iterations"),
    }
    if conversation_id:
        summary["ui_url"] = f"{ui_base.rstrip('/')}/conversations/{conversation_id}"
        summary["api_url"] = f"{base.rstrip('/')}/api/conversations/{conversation_id}"
    return summary


def wait_for_conversation(
    *,
    base: str,
    key: str,
    conversation_id: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_response: dict[str, Any] = {}
    while True:
        last_response = http_json("GET", f"{base}/api/conversations/{conversation_id}", key=key)
        status = last_response.get("execution_status")
        if status in TERMINAL_STATUSES:
            return last_response
        if time.monotonic() >= deadline:
            last_response["wait_timeout"] = True
            return last_response
        time.sleep(poll_seconds)


def final_response(base: str, key: str, conversation_id: str) -> dict[str, Any]:
    return http_json(
        "GET",
        f"{base}/api/conversations/{conversation_id}/agent_final_response",
        key=key,
    )
