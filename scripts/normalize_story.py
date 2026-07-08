#!/usr/bin/env python3
"""Normalize a story, issue export, or webhook payload into story.json."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _read_input(path: Path) -> tuple[Any, str]:
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        return raw, raw


def _labels(values: Any) -> list[str]:
    if not values:
        return []
    result: list[str] = []
    for value in values:
        if isinstance(value, str):
            result.append(value)
        elif isinstance(value, dict):
            name = value.get("name") or value.get("value") or value.get("title")
            if name:
                result.append(str(name))
    return result


def _comments(values: Any) -> list[dict[str, str]]:
    if not values:
        return []
    result: list[dict[str, str]] = []
    for value in values:
        if isinstance(value, str):
            result.append({"author": "", "body": value})
        elif isinstance(value, dict):
            author = value.get("author") or value.get("user") or value.get("creator") or ""
            if isinstance(author, dict):
                author = author.get("displayName") or author.get("name") or author.get("login") or ""
            body = value.get("body") or value.get("text") or value.get("comment") or ""
            if body:
                result.append({"author": str(author), "body": str(body)})
    return result


def _acceptance_criteria(text: str) -> list[str]:
    criteria: list[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#+\s*acceptance criteria\b", stripped, re.I) or re.match(r"^acceptance criteria\s*:\s*$", stripped, re.I):
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            in_section = False
        if in_section and criteria and re.match(r"^[A-Za-z][A-Za-z0-9 -]+:\s*$", stripped):
            in_section = False
        if in_section and stripped.startswith(("-", "*")):
            criteria.append(stripped.lstrip("-* [xX]").strip())
        elif re.match(r"^- \[[ xX]\]\s+", stripped):
            criteria.append(re.sub(r"^- \[[ xX]\]\s+", "", stripped))
    return [item for item in criteria if item]


def _decisions(text: str, criteria: list[str]) -> dict[str, list[Any]]:
    lower = text.lower()
    known: list[str] = []
    needed: list[dict[str, Any]] = []

    for item in criteria:
        item_lower = item.lower()
        if "not implemented" in item_lower or "out of scope" in item_lower:
            known.append(item)

    if (
        "decision needed" in lower
        or "out of scope" in lower
        or "not implemented" in lower
        or "sync across devices" in lower
        or "cross-device" in lower
        or "requires an api" in lower
        or "data model decision" in lower
    ):
        needed.append(
            {
                "question": "Should this story stay local-only for the first slice, or include cross-device/backend persistence?",
                "options": [
                    "Local-only first slice with no backend persistence",
                    "Cross-device sync with API and data model work"
                ],
                "impact": "Changes scope from a starter UI/local behavior slice to backend API, data model, persistence, and broader QA work.",
                "needed_from": "product owner"
            }
        )

    return {"known": known, "needed": needed}


def _text_story(raw: str, source_system: str) -> dict[str, Any]:
    lines = [line.rstrip() for line in raw.splitlines()]
    non_empty = [line.strip("# ").strip() for line in lines if line.strip()]
    title = non_empty[0] if non_empty else "Untitled story"
    body = raw.strip()
    criteria = _acceptance_criteria(body)
    return {
        "source": {"system": source_system, "url": "", "id": "", "raw_payload_path": ""},
        "request": {
            "title": title,
            "body": body,
            "acceptance_criteria": criteria,
            "priority": "",
            "labels": [],
            "comments": [],
            "attachments": [],
        },
        "repo": {"url": "", "local_path": "", "base_branch": ""},
        "decisions": _decisions(body, criteria),
    }


def _linear_story(data: dict[str, Any]) -> dict[str, Any]:
    issue = data.get("data", data)
    body = str(issue.get("description") or "")
    criteria = _acceptance_criteria(body)
    return {
        "source": {
            "system": "linear",
            "url": str(issue.get("url") or ""),
            "id": str(issue.get("identifier") or issue.get("id") or ""),
            "raw_payload_path": "",
        },
        "request": {
            "title": str(issue.get("title") or "Untitled Linear issue"),
            "body": body,
            "acceptance_criteria": criteria,
            "priority": str(issue.get("priority") or ""),
            "labels": _labels(issue.get("labels")),
            "comments": _comments(issue.get("comments")),
            "attachments": _labels(issue.get("attachments")),
        },
        "repo": {"url": "", "local_path": "", "base_branch": ""},
        "decisions": _decisions(body, criteria),
    }


def _jira_story(data: dict[str, Any]) -> dict[str, Any]:
    issue = data.get("issue", data)
    fields = issue.get("fields", {}) if isinstance(issue, dict) else {}
    description = fields.get("description") or issue.get("description") or ""
    criteria = _acceptance_criteria(str(description))
    priority = fields.get("priority") or {}
    if isinstance(priority, dict):
        priority = priority.get("name") or ""
    return {
        "source": {
            "system": "jira",
            "url": str(issue.get("self") or ""),
            "id": str(issue.get("key") or issue.get("id") or ""),
            "raw_payload_path": "",
        },
        "request": {
            "title": str(fields.get("summary") or issue.get("summary") or "Untitled Jira issue"),
            "body": str(description),
            "acceptance_criteria": criteria,
            "priority": str(priority),
            "labels": _labels(fields.get("labels") or issue.get("labels")),
            "comments": _comments(fields.get("comment", {}).get("comments") if isinstance(fields.get("comment"), dict) else issue.get("comments")),
            "attachments": _labels(fields.get("attachment") or issue.get("attachments")),
        },
        "repo": {"url": "", "local_path": "", "base_branch": ""},
        "decisions": _decisions(str(description), criteria),
    }


def _github_story(data: dict[str, Any]) -> dict[str, Any]:
    issue = data.get("issue") or data.get("pull_request") or data
    repo = data.get("repository") or {}
    body = str(issue.get("body") or "")
    criteria = _acceptance_criteria(body)
    return {
        "source": {
            "system": "github",
            "url": str(issue.get("html_url") or ""),
            "id": str(issue.get("number") or issue.get("id") or ""),
            "raw_payload_path": "",
        },
        "request": {
            "title": str(issue.get("title") or "Untitled GitHub issue"),
            "body": body,
            "acceptance_criteria": criteria,
            "priority": "",
            "labels": _labels(issue.get("labels")),
            "comments": _comments(data.get("comments")),
            "attachments": [],
        },
        "repo": {
            "url": str(repo.get("html_url") or repo.get("clone_url") or ""),
            "local_path": "",
            "base_branch": str(repo.get("default_branch") or ""),
        },
        "decisions": _decisions(body, criteria),
    }


def _json_story(data: dict[str, Any], source_system: str) -> dict[str, Any]:
    if "source" in data and "request" in data:
        return data
    if data.get("type") == "Issue" or "linear" in source_system:
        return _linear_story(data)
    if "webhookEvent" in data or "jira" in source_system or "fields" in data:
        return _jira_story(data)
    if "repository" in data or "github" in source_system or "issue" in data or "pull_request" in data:
        return _github_story(data)
    title = str(data.get("title") or data.get("summary") or "Untitled story")
    body = str(data.get("body") or data.get("description") or "")
    return _text_story(f"{title}\n\n{body}", source_system if source_system != "auto" else "webhook")


def normalize(args: argparse.Namespace) -> dict[str, Any]:
    data, raw = _read_input(args.input)
    source_system = args.source_system
    if source_system == "auto":
        source_system = "file" if isinstance(data, str) else "webhook"
    story = _text_story(data, source_system) if isinstance(data, str) else _json_story(data, source_system)

    if args.source_url:
        story["source"]["url"] = args.source_url
    if args.story_id:
        story["source"]["id"] = args.story_id
    if args.repo_url:
        story["repo"]["url"] = args.repo_url
    if args.repo_local_path:
        story["repo"]["local_path"] = args.repo_local_path
    if args.base_branch:
        story["repo"]["base_branch"] = args.base_branch
    story["source"]["raw_payload_path"] = args.raw_payload_path or ""
    return story


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-system", default="auto", choices=["auto", "pasted", "file", "github", "jira", "linear", "webhook", "unknown"])
    parser.add_argument("--source-url", default="")
    parser.add_argument("--story-id", default="")
    parser.add_argument("--repo-url", default="")
    parser.add_argument("--repo-local-path", default="")
    parser.add_argument("--base-branch", default="")
    parser.add_argument("--raw-payload-path", default="")
    args = parser.parse_args()

    story = normalize(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(story, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"title: {story['request']['title']}")
    print(f"source: {story['source']['system']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
