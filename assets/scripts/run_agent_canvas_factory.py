#!/usr/bin/env python3
"""Create visible Agent Canvas child conversations for the active factory supervisor."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import agent_canvas_delegate as canvas


ACTIVE_WORK_CELLS = ("story-to-pr", "code-review", "qa")
VALID_STATUSES = {
    "done",
    "pass",
    "findings",
    "needs-human",
    "failed",
    "fail",
    "partial",
    "blocked",
}
STATUS_MARKER_RE = re.compile(r"<!--\s*status:\s*([A-Za-z0-9_. -]+)\s*-->", re.IGNORECASE)
STATUS_INLINE_RE = re.compile(r"(?:^|\|)\s*[*_`#\s-]*status[*_`#\s-]*[:|]\s*[*_` ]*([A-Za-z0-9_. -]+)", re.IGNORECASE)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_existing_children(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = read_json(path)
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def render_prompt(path: Path, variables: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def artifact_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="replace")

    marker = STATUS_MARKER_RE.search(text)
    if marker:
        return normalize_status(marker.group(1))

    lines = text.splitlines()
    for index, line in enumerate(lines):
        inline = STATUS_INLINE_RE.search(line)
        if inline:
            return normalize_status(inline.group(1))
        if re.match(r"^\s*#+\s*status\s*$", line, re.IGNORECASE):
            for next_line in lines[index + 1:]:
                stripped = strip_status_cell(next_line)
                if stripped:
                    return normalize_status(stripped)
        if re.search(r"\bstatus\b", line, re.IGNORECASE) and "|" in line:
            cells = [strip_status_cell(cell) for cell in line.split("|")]
            for cell_index, cell in enumerate(cells):
                if cell.lower() == "status" and cell_index + 1 < len(cells):
                    return normalize_status(cells[cell_index + 1])
    return "written"


def strip_status_cell(value: str) -> str:
    stripped = value.strip().strip("|").strip()
    stripped = re.sub(r"^[#*\-_\s`]+|[#*\-_\s`]+$", "", stripped)
    return stripped.strip()


def normalize_status(value: str) -> str:
    token = strip_status_cell(value).lower()
    token = token.replace("_", "-").replace(" ", "-")
    if token in {"needs-human", "need-human", "human-needed", "blocked"}:
        return "needs-human" if token != "blocked" else "blocked"
    if token in {"passes", "passed"}:
        return "pass"
    if token in {"failure"}:
        return "failed"
    return token if token in VALID_STATUSES else strip_status_cell(value)


def child_prompt(args: argparse.Namespace, cell: str) -> str:
    prompt_path = args.repo / "agent-canvas" / "prompts" / "workcells" / f"{cell}.md"
    if not prompt_path.is_file():
        raise canvas.CanvasAPIError(f"missing workcell prompt: {prompt_path}")
    variables = {
        "run_id": args.run_id,
        "repo_path": str(args.repo.resolve()),
    }
    artifact = args.repo / "factory_runs" / args.run_id / f"{cell}.md"
    return (
        render_prompt(prompt_path, variables)
        + "\n\n"
        + "This is a child Agent Canvas conversation created by the SDLC starter "
        + "factory supervisor. Work only in the repository path above. "
        + f"Write the required artifact at `{artifact}` and finish when it is written."
    )


def write_children_summary(run_dir: Path, entries: list[dict[str, Any]]) -> None:
    lines = [
        "# Child Conversation Summary",
        "",
        "| Workcell | Status | Conversation | Artifact |",
        "| --- | --- | --- | --- |",
    ]
    for entry in entries:
        link = entry.get("id") or ""
        if entry.get("ui_url") and entry.get("id"):
            link = f"[{entry['id']}]({entry['ui_url']})"
        lines.append(
            f"| `{entry['name']}` | {entry.get('artifact_status', 'pending')} | "
            f"{link} | `{entry['artifact']}` |"
        )
    lines.append("")
    (run_dir / "children-summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_lifecycle_report(args: argparse.Namespace, run_dir: Path, entries: list[dict[str, Any]]) -> None:
    story = read_json(run_dir / "story.json")
    request = story.get("request", {}) if isinstance(story.get("request"), dict) else {}
    source = story.get("source", {}) if isinstance(story.get("source"), dict) else {}
    lines = [
        "# SDLC Starter Lifecycle Report",
        "",
        f"- Run ID: `{args.run_id}`",
        f"- Story: {request.get('title', 'Untitled story')}",
        f"- Source: {source.get('system', 'unknown')}",
        "",
        "## Child Conversations",
        "",
        "| Workcell | Artifact Status | Conversation | Artifact |",
        "| --- | --- | --- | --- |",
    ]
    for entry in entries:
        link = entry.get("id") or ""
        if entry.get("ui_url") and entry.get("id"):
            link = f"[{entry['id']}]({entry['ui_url']})"
        lines.append(
            f"| `{entry['name']}` | {entry.get('artifact_status', 'pending')} | "
            f"{link} | `{entry['artifact']}` |"
        )
    lines.extend(
        [
            "",
            "## Human Gates",
            "",
            "- Review unresolved product decisions before merge.",
            "- Do not merge, deploy, or expose secrets without human approval.",
            "- Treat child outputs as recommendations until a human reviews the artifacts.",
            "",
            "## Next Operator Action",
            "",
            "Open the child conversations and artifacts above, resolve any `needs-human` gates, then decide whether to continue with a PR, more QA, or a narrower story.",
            "",
        ]
    )
    (run_dir / "lifecycle-report.md").write_text("\n".join(lines), encoding="utf-8")


def start_child(
    *,
    args: argparse.Namespace,
    base: str,
    key: str,
    settings_response: dict[str, Any],
    run_dir: Path,
    cell: str,
) -> dict[str, Any]:
    response = canvas.create_conversation(
        base=base,
        key=key,
        settings_response=settings_response,
        prompt=child_prompt(args, cell),
        workspace=args.repo,
        max_iterations=args.child_max_iterations,
        run=True,
    )
    summary = canvas.conversation_summary(base, args.ui_base, response)
    summary["name"] = cell
    summary["artifact"] = f"factory_runs/{args.run_id}/{cell}.md"
    write_json(run_dir / f"{cell}.conversation.json", summary)
    return summary


def should_reuse_entry(args: argparse.Namespace, entry: dict[str, Any]) -> bool:
    artifact = args.repo / str(entry.get("artifact", ""))
    status = artifact_status(artifact)
    entry["artifact_status"] = status
    if status in VALID_STATUSES:
        return True
    return bool(entry.get("id"))


def wait_existing_child(
    *,
    args: argparse.Namespace,
    base: str,
    key: str,
    run_dir: Path,
    entry: dict[str, Any],
) -> dict[str, Any]:
    if not entry.get("id"):
        return entry

    if args.no_wait:
        entry["artifact_status"] = artifact_status(args.repo / entry["artifact"])
        return entry

    status_response = canvas.wait_for_conversation(
        base=base,
        key=key,
        conversation_id=entry["id"],
        timeout_seconds=args.cell_timeout_seconds,
        poll_seconds=args.poll_seconds,
    )
    entry["wait"] = canvas.conversation_summary(base, args.ui_base, status_response)
    try:
        entry["final_response"] = canvas.final_response(base, key, entry["id"])
    except canvas.CanvasAPIError as exc:
        entry["final_response_error"] = str(exc)
    entry["artifact_status"] = artifact_status(args.repo / entry["artifact"])
    return entry


def run_factory(args: argparse.Namespace) -> int:
    args.repo = args.repo.resolve()
    run_dir = args.repo / "factory_runs" / args.run_id
    if not (run_dir / "story.json").is_file():
        raise canvas.CanvasAPIError(f"missing story.json: {run_dir / 'story.json'}")

    key = canvas.read_session_key()
    base = canvas.discover_base(args.base, key)
    settings_response = canvas.http_json(
        "GET",
        f"{base}/api/settings",
        key=key,
        expose_encrypted_secrets=True,
    )

    children_path = run_dir / "children.json"
    entries: list[dict[str, Any]] = read_existing_children(children_path)
    entries_by_name = {entry.get("name"): entry for entry in entries}

    for cell in args.cells:
        existing = entries_by_name.get(cell)
        if existing and should_reuse_entry(args, existing):
            entry = existing
        else:
            entry = start_child(
                args=args,
                base=base,
                key=key,
                settings_response=settings_response,
                run_dir=run_dir,
                cell=cell,
            )
            entries.append(entry)
            entries_by_name[cell] = entry

        write_json(children_path, entries)
        write_children_summary(run_dir, entries)

        if existing and existing is entry and entry.get("artifact_status") in VALID_STATUSES:
            time.sleep(args.child_spacing_seconds)
            continue

        if existing and existing is entry and entry.get("id"):
            entry = wait_existing_child(
                args=args,
                base=base,
                key=key,
                run_dir=run_dir,
                entry=entry,
            )
            write_json(children_path, entries)
            write_children_summary(run_dir, entries)
            if entry.get("wait", {}).get("execution_status") in {"error", "stuck", "stopped"} or entry.get("wait", {}).get("wait_timeout"):
                break
        elif not args.no_wait:
            status_response = canvas.wait_for_conversation(
                base=base,
                key=key,
                conversation_id=entry["id"],
                timeout_seconds=args.cell_timeout_seconds,
                poll_seconds=args.poll_seconds,
            )
            entry["wait"] = canvas.conversation_summary(base, args.ui_base, status_response)
            entry["final_response"] = canvas.final_response(base, key, entry["id"])
            entry["artifact_status"] = artifact_status(args.repo / entry["artifact"])
            write_json(run_dir / f"{cell}.final.json", entry["final_response"])
            write_json(children_path, entries)
            write_children_summary(run_dir, entries)
            if status_response.get("execution_status") in {"error", "stuck", "stopped"} or status_response.get("wait_timeout"):
                break

        time.sleep(args.child_spacing_seconds)

    write_lifecycle_report(args, run_dir, entries)
    print(json.dumps({"run_dir": str(run_dir), "children": entries}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--ui-base", default=canvas.DEFAULT_UI_BASE)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cells", nargs="+", choices=ACTIVE_WORK_CELLS, default=list(ACTIVE_WORK_CELLS))
    parser.add_argument("--child-max-iterations", type=int, default=60)
    parser.add_argument("--cell-timeout-seconds", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--child-spacing-seconds", type=int, default=1)
    parser.add_argument("--no-wait", action="store_true")
    return parser


if __name__ == "__main__":
    raise SystemExit(run_factory(build_parser().parse_args()))
