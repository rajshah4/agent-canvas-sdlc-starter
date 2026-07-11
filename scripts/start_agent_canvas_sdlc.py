#!/usr/bin/env python3
"""Bootstrap a tool-enabled SDLC factory supervisor in local Agent Canvas."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE = "http://localhost:8000"
DEFAULT_TOOLS = (
    {"name": "terminal", "params": {}},
    {"name": "file_editor", "params": {}},
    {"name": "task_tracker", "params": {}},
)


class CanvasError(RuntimeError):
    """Raised when the local Agent Canvas API cannot start the run."""


def read_session_key() -> str:
    for env_name in ("SESSION_API_KEY", "OH_SESSION_API_KEYS_0", "LOCAL_BACKEND_API_KEY"):
        value = os.getenv(env_name)
        if value:
            return value.strip()

    for key_path in (
        Path.home() / ".openhands" / "agent-canvas" / "api-key.txt",
        Path.home() / ".openhands" / "agent-canvas" / "session-api-key.txt",
    ):
        if key_path.exists():
            value = key_path.read_text(encoding="utf-8").strip()
            if value:
                return value

    raise CanvasError("No Agent Canvas session API key found")


def request_json(
    method: str,
    url: str,
    *,
    key: str | None = None,
    payload: dict[str, Any] | None = None,
    expose_encrypted_secrets: bool = False,
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    body = None
    if key:
        headers["X-Session-API-Key"] = key
    if expose_encrypted_secrets:
        headers["X-Expose-Secrets"] = "encrypted"
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise CanvasError(f"{method} {url} returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise CanvasError(f"{method} {url} failed: {exc.reason}") from exc

    return json.loads(text) if text else {}


def merge_tools(existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name: dict[str, dict[str, Any]] = {}
    for tool in [*existing, *DEFAULT_TOOLS]:
        name = tool.get("name")
        if name:
            by_name[name] = tool
    return list(by_name.values())


def settings_summary(settings: dict[str, Any]) -> dict[str, Any]:
    agent_settings = settings.get("agent_settings") or {}
    llm = agent_settings.get("llm") or {}
    return {
        "agent_profile_selection": "blank",
        "active_profile": settings.get("active_profile"),
        "raw_model": llm.get("model") if isinstance(llm, dict) else None,
    }


def active_llm_profile(
    base: str,
    key: str,
    settings: dict[str, Any],
) -> dict[str, Any] | None:
    profile_name = settings.get("active_profile")
    if not isinstance(profile_name, str) or not profile_name.strip():
        return None

    profile = request_json(
        "GET",
        f"{base}/api/profiles/{quote(profile_name, safe='')}",
        key=key,
        expose_encrypted_secrets=True,
    )
    config = profile.get("config")
    if not isinstance(config, dict) or not config.get("model"):
        return None

    llm = dict(config)
    llm.setdefault("stream", True)
    llm["usage_id"] = f"profile:{profile_name}"
    return llm


def render_supervisor(repo: Path, run_id: str) -> str:
    prompt_path = repo / "agent-canvas" / "prompts" / "supervisor.md"
    if not prompt_path.is_file():
        raise CanvasError(f"missing supervisor prompt: {prompt_path}")

    text = prompt_path.read_text(encoding="utf-8")
    return (
        text.replace("{{run_id}}", run_id)
        .replace("{{repo_path}}", str(repo))
        .replace("{{story_path}}", f"factory_runs/{run_id}/story.json")
    )


def build_payload(
    args: argparse.Namespace,
    settings: dict[str, Any],
    llm_profile: dict[str, Any] | None,
) -> dict[str, Any]:
    repo = args.repo.resolve()
    conversation_settings = settings.get("conversation_settings") or {}
    agent_settings = dict(settings.get("agent_settings") or {})
    agent_settings.pop("schema_version", None)
    agent_settings.pop("mcp_config", None)
    agent_settings.pop("agent", None)
    if llm_profile:
        agent_settings["llm"] = llm_profile
    agent_settings["tools"] = merge_tools(list(agent_settings.get("tools") or []))

    return {
        "secrets_encrypted": True,
        "agent_settings": agent_settings,
        "workspace": {"kind": "LocalWorkspace", "working_dir": str(repo)},
        "worktree": False,
        "confirmation_policy": {"kind": "NeverConfirm"},
        "max_iterations": args.max_iterations
        or conversation_settings.get("max_iterations")
        or 500,
        "stuck_detection": True,
        "autotitle": True,
        "initial_message": {
            "role": "user",
            "content": [{"type": "text", "text": render_supervisor(repo, args.run_id)}],
            "run": not args.no_run,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--run-id", default="demo-001")
    parser.add_argument("--max-iterations", type=int)
    parser.add_argument("--no-run", action="store_true")
    args = parser.parse_args()

    key = read_session_key()
    base = args.base.rstrip("/")
    settings = request_json(
        "GET",
        f"{base}/api/settings",
        key=key,
        expose_encrypted_secrets=True,
    )
    llm_profile = active_llm_profile(base, key, settings)
    payload = build_payload(args, settings, llm_profile)
    response = request_json("POST", f"{base}/api/conversations", key=key, payload=payload)

    conversation_id = response.get("id")
    summary = {
        "id": conversation_id,
        "status": response.get("execution_status"),
        "max_iterations": response.get("max_iterations") or payload["max_iterations"],
        "settings": {
            **settings_summary(settings),
            "resolved_model": payload["agent_settings"].get("llm", {}).get("model"),
            "llm_source": (
                f"active_profile:{settings.get('active_profile')}"
                if llm_profile
                else "agent_settings.llm"
            ),
        },
        "tools": [tool["name"] for tool in payload["agent_settings"]["tools"]],
        "ui_url": f"{base}/conversations/{conversation_id}" if conversation_id else None,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
