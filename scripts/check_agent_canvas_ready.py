#!/usr/bin/env python3
"""Check Agent Canvas API health and starter files in a target repo."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


REQUIRED_FILES = [
    "agent-canvas/prompts/supervisor.md",
    "agent-canvas/prompts/intake-normalizer.md",
    "agent-canvas/prompts/workcells/story-to-pr.md",
    "agent-canvas/prompts/workcells/code-review.md",
    "agent-canvas/prompts/workcells/qa.md",
    "agent-canvas/schemas/story.schema.json",
    "agent-canvas/scripts/agent_canvas_delegate.py",
    "agent-canvas/scripts/run_agent_canvas_factory.py",
]

REQUIRED_TOOLS = ["terminal", "file_editor", "task_tracker"]


def check_server(base: str) -> tuple[bool, str]:
    url = base.rstrip("/") + "/server_info"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        usable_tools = set(data.get("usable_tools") or [])
        missing_tools = [tool for tool in REQUIRED_TOOLS if tool not in usable_tools]
        if missing_tools:
            return False, f"Agent Server {data.get('version', 'unknown')} is reachable, but missing tools: {', '.join(missing_tools)}"
        return True, f"Agent Server {data.get('version', 'unknown')} at {base} with required factory supervisor and child-conversation tools"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return False, f"cannot reach {url}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--repo", type=Path)
    args = parser.parse_args()

    ok = True
    server_ok, server_msg = check_server(args.base)
    print(("OK " if server_ok else "FAIL ") + server_msg)
    ok = ok and server_ok

    if not args.repo:
        print("INFO no --repo provided; skipped scaffolded file checks.")
        return 0 if ok else 1

    repo = args.repo.resolve()
    if not repo.is_dir():
        print(f"FAIL repo does not exist: {repo}")
        return 1
    print(f"OK repo exists: {repo}")
    if "/Documents/" in str(repo) or "/Desktop/" in str(repo):
        print("WARN repo is under Documents/Desktop; local Agent Canvas may be blocked by macOS privacy permissions. Prefer /private/tmp or ~/Code for first runs.")
    print("INFO use a tool-enabled factory supervisor conversation; the repo-local factory helper creates visible child conversations.")

    for rel in REQUIRED_FILES:
        path = repo / rel
        exists = path.is_file()
        print(("OK " if exists else "FAIL ") + rel)
        ok = ok and exists

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
