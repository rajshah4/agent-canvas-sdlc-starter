#!/usr/bin/env python3
"""Copy Agent Canvas SDLC starter prompts and schema into a target repo."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_file(src: Path, dst: Path, overwrite: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return f"skip existing {dst}"
    shutil.copy2(src, dst)
    return f"wrote {dst}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Target repository path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing starter files")
    args = parser.parse_args()

    repo = args.repo.resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo does not exist: {repo}")

    skill_root = Path(__file__).resolve().parents[1]
    assets = skill_root / "assets"
    outputs: list[str] = []

    prompt_src = assets / "prompts"
    prompt_dst = repo / "agent-canvas" / "prompts"
    for src in sorted(prompt_src.rglob("*.md")):
        outputs.append(copy_file(src, prompt_dst / src.relative_to(prompt_src), args.overwrite))

    script_src = assets / "scripts"
    script_dst = repo / "agent-canvas" / "scripts"
    for src in sorted(script_src.rglob("*.py")):
        dst = script_dst / src.relative_to(script_src)
        outputs.append(copy_file(src, dst, args.overwrite))
        dst.chmod(0o755)

    outputs.append(copy_file(assets / "schemas" / "story.schema.json", repo / "agent-canvas" / "schemas" / "story.schema.json", args.overwrite))
    outputs.append(copy_file(assets / "examples" / "small-story.md", repo / "stories" / "small-story.md", args.overwrite))

    run_dir = repo / "factory_runs"
    run_dir.mkdir(exist_ok=True)
    gitkeep = run_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
        outputs.append(f"wrote {gitkeep}")

    print("\n".join(outputs))
    print("\nNext:")
    print(f"  python3 {skill_root / 'scripts' / 'normalize_story.py'} --input {repo / 'stories' / 'small-story.md'} --output {repo / 'factory_runs' / 'demo-001' / 'story.json'} --repo-local-path {repo}")
    print("  If you are outside Agent Canvas, bootstrap the factory supervisor:")
    print(f"  python3 {skill_root / 'scripts' / 'start_agent_canvas_sdlc.py'} --base http://localhost:8000 --repo {repo} --run-id demo-001 --agent-profile default")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
