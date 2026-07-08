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


def _clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lstrip("-*").strip()).strip()


def _decision_section_lines(text: str) -> list[str]:
    lines = text.splitlines()
    in_section = False
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^#+\s*(open questions?|unresolved decisions?|decisions? needed|decision log|questions?)\b", stripped, re.I):
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            in_section = False
        if in_section and not stripped.startswith(("-", "*")) and re.match(r"^[A-Za-z][A-Za-z0-9 -]+:\s*$", stripped):
            in_section = False
        if in_section and stripped.startswith(("-", "*")):
            cleaned = _clean_line(stripped)
            if cleaned:
                result.append(cleaned)
    return result


def _stakeholder_options(text: str) -> list[str]:
    options: list[str] = []
    for line in text.splitlines():
        cleaned = _clean_line(line)
        match = re.match(r"([A-Z][A-Za-z0-9 _.-]{1,40})\s+(?:wants|prefers|asked for|is asking for)\s+(.+)", cleaned)
        if match:
            options.append(f"{match.group(1)}: {match.group(2).rstrip('.')}")
    return options


def _append_needed(needed: list[dict[str, Any]], question: str, *, options: list[str] | None = None, impact: str = "May change scope, behavior, UX, data, security, QA, or rollout.", needed_from: str = "human owner") -> None:
    normalized = question.rstrip(".")
    if not normalized.endswith("?"):
        normalized += "?"
    if any(item.get("question") == normalized for item in needed):
        return
    needed.append(
        {
            "question": normalized,
            "options": options or [],
            "impact": impact,
            "needed_from": needed_from,
        }
    )


def _decisions(text: str, criteria: list[str]) -> dict[str, list[Any]]:
    lower = text.lower()
    known: list[str] = []
    needed: list[dict[str, Any]] = []

    for item in criteria:
        item_lower = item.lower()
        if "not implemented" in item_lower or "out of scope" in item_lower:
            known.append(item)

    for line in _decision_section_lines(text):
        _append_needed(needed, line, needed_from="story owner")

    options = _stakeholder_options(text)
    if len(options) >= 2 and any(word in lower for word in ("disagree", "different", "vs", "but", "however", "has not weighed in", "not weighed in")):
        _append_needed(
            needed,
            "Which stakeholder option should be implemented for this slice?",
            options=options,
            impact="Changes user-visible behavior or implementation scope.",
            needed_from="product/design owner",
        )

    for line in text.splitlines():
        cleaned = _clean_line(line)
        cleaned_lower = cleaned.lower()
        if not cleaned:
            continue
        if "?" in cleaned and any(word in cleaned_lower for word in ("should", "which", "whether", "can we", "do we")):
            _append_needed(needed, cleaned, needed_from="story owner")
        if any(token in cleaned_lower for token in ("tbd", "todo decision", "needs decision", "decision needed", "not weighed in", "needs design", "needs product")):
            _append_needed(needed, cleaned, needed_from="human owner")

    if (
        not needed
        and (
            "decision needed" in lower
            or "out of scope" in lower
            or "not implemented" in lower
        )
    ):
        _append_needed(
            needed,
            "Which deferred or unresolved scope should remain out of the first slice?",
            impact="Changes the safe implementation boundary for this starter run.",
            needed_from="product owner",
        )

    if any(
        phrase in lower
        for phrase in (
            "sync across devices",
            "cross-device",
            "requires an api",
            "data model decision",
        )
    ):
        _append_needed(
            needed,
            "Should this story stay local-only for the first slice, or include cross-device/backend persistence?",
            options=[
                "Local-only first slice with no backend persistence",
                "Cross-device sync with API and data model work",
            ],
            impact="Changes scope from a starter UI/local behavior slice to backend API, data model, persistence, and broader QA work.",
            needed_from="product owner",
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
        if isinstance(data, str):
            source_system = "pasted" if args.input.suffix.lower() in {".md", ".markdown", ".txt"} else "file"
        else:
            source_system = "webhook"
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
