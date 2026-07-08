# Agent Canvas SDLC Starter

A beginner-friendly [Agent Canvas](https://docs.openhands.dev/) skill that turns a
work request, such as pasted text, a local PRD, or a Jira / Linear / GitHub / webhook
payload into code via a small, inspectable software factory.  Once you understand the basics here, you can go and customize your own software factory according to your integrations, requirements, and preferences.

The SDLC starter starts by taking the input and normalizing it into a stable `story.json`, then runs a supervisor that creates real child Agent Canvas conversations for implementation, code review, and
QA. Humans keep the gates: scope, secrets, risky decisions, merge, and deploy. You can view the supervisor and child agents within Agent Canvas.

```text
story intake  ->  story.json  ->  supervisor  ->  child Canvas conversations  ->  lifecycle report
```

> **This is an agent skill, not an app you run directly.** `SKILL.md` is the source
> of truth the agent executes; this README orients humans. Start minimal, then use
> the upgrade map to extend one step at a time.

## What it produces

Every run writes an inspectable artifact set under `factory_runs/<run-id>/`:

| Artifact | Written by | Contents |
| --- | --- | --- |
| `story.json` | normalizer | the stable handoff contract (source, request, repo, decisions) |
| `intake.md` | supervisor | story source, goal, acceptance criteria, unresolved decisions |
| `decision-log.md` | supervisor | competing options + owners when stakeholders disagree |
| `story-to-pr.md` | implementation workcell | change summary, tests run, assumptions, gates |
| `code-review.md` | review workcell | findings, security notes, acceptance-criteria coverage |
| `qa.md` | QA workcell | validation evidence, residual risk, merge-readiness |
| `children.json` | launcher | child conversation IDs, URLs, status |
| `lifecycle-report.md` | supervisor | the human-readable roll-up and next operator action |

## Requirements

- A local Agent Canvas / OpenHands Agent Server (tested against **1.31.0**),
  reachable at `http://localhost:8000`.
- Python 3. The scripts use only the standard library.
- The target repository must be readable by Agent Canvas. On macOS prefer
  `/private/tmp` or `~/Code` for first runs — `Documents` / `Desktop` can be blocked
  by privacy permissions.

## Using this skill

Two ways to use it, depending on whether you want to install anything:

- **Directly, no install.** Point your agent at this repo and tell it to read
  `SKILL.md` and run — or run the scripts yourself (see the "under the hood" steps
  below). Nothing is registered; this is the fastest way to see it work.
- **Installed as a skill (recommended for repeat use).** Copy the folder into a skills
  directory and it's discovered from disk automatically. You then never invoke it by
  name — you just describe the work and its `description` keywords trigger it:
  - `.agents/skills/agent-canvas-sdlc-starter/` — scoped to one repo (takes precedence).
  - `~/.agents/skills/agent-canvas-sdlc-starter/` — available in every conversation.

If your Agent Canvas deployment bundles this into its global skills, users get the
installed experience with no setup — they just prompt.

See the [OpenHands Agent Skills docs](https://docs.openhands.dev/overview/skills) for skill locations, precedence, and triggering.

## Quickstart

You don't run the scripts by hand — your agent does. Once the skill is available, a
run is just a prompt:

1. Open a conversation in Agent Canvas.
2. Describe the work and point at a target repo:

   > Use the Agent Canvas SDLC starter to run the factory on `/private/tmp/my-repo`
   > for this story: "Add a saved filter to the projects page so users can return to
   > the same view later."

The agent normalizes the story into `story.json`, scaffolds the target repo, starts a
supervisor conversation, and the supervisor creates the implementation, review, and QA
child conversations. Watch them appear in Agent Canvas and inspect
`factory_runs/<run-id>/` for the artifacts above.

<details>
<summary>Under the hood — the commands the agent runs (you can also run them by hand)</summary>

```bash
SKILL=/path/to/agent-canvas-sdlc-starter
REPO=/private/tmp/my-repo          # a repo Agent Canvas can read

# 1. Scaffold prompts, schema, and the repo-local launcher into the target repo
python3 "$SKILL/scripts/scaffold_agent_canvas_sdlc.py" --repo "$REPO"

# 2. Normalize a story into story.json
python3 "$SKILL/scripts/normalize_story.py" \
  --input "$REPO/stories/small-story.md" \
  --output "$REPO/factory_runs/demo-001/story.json" \
  --repo-local-path "$REPO" --source-system file

# 3. Confirm the server, tools, and scaffolded files are ready
python3 "$SKILL/scripts/check_agent_canvas_ready.py" --base http://localhost:8000 --repo "$REPO"

# 4. Start the supervisor conversation (it creates the child conversations)
python3 "$SKILL/scripts/start_agent_canvas_sdlc.py" \
  --base http://localhost:8000 --repo "$REPO" --run-id demo-001
```

</details>

## Story intake

The story can come from pasted text, a local file, or a tracker / webhook payload —
whatever the source, it is normalized into `story.json` before orchestration begins.
`normalize_story.py` already auto-detects **Jira, Linear, and GitHub** payloads (see
`assets/examples/`) and generic webhook JSON; pass `--source-system` to force an
adapter:

```bash
python3 "$SKILL/scripts/normalize_story.py" \
  --input issue.json --output "$REPO/factory_runs/gh-128/story.json" \
  --source-system github --repo-local-path "$REPO"
```

For *live* tracker connectors, evented/webhook triggers, and status write-back, see
the intake section of `references/upgrade-map.md`.

## Advanced: run or re-run individual workcells

The supervisor runs the whole lifecycle. If you need to re-run just one step — for
example, re-run QA after a fix — invoke the repo-local launcher with `--cells`:

```bash
cd "$REPO"
python3 agent-canvas/scripts/run_agent_canvas_factory.py \
  --base http://localhost:8000 --repo "$REPO" --run-id demo-001 --cells qa
```

The launcher reuses existing children whose artifacts are already present, so it picks
up where a run left off rather than starting over.

## Repository layout

```text
SKILL.md              # source of truth: what the agent reads and executes
scripts/              # host-side CLI: normalize, scaffold, check, start supervisor
assets/
  prompts/            # supervisor + workcell prompts (copied into target repos)
  scripts/            # repo-local launcher + Agent Canvas API helper
  schemas/            # story.schema.json — the story.json contract
  examples/           # sample story + Jira/Linear payloads
references/           # workflow, intake, human gates, upgrade map, plugin registry
```

## Extending it

Keep the minimal factory runnable, then upgrade one step at a time:

- **`references/upgrade-map.md`** — replace a starter workcell with a maintained
  skill, plugin, MCP server, CI workflow, or repo guide (tracker MCP, evented
  intake, `/codereview`, `/qa-changes`, Playwright QA, security gates,
  observability).
- **`references/plugin-registry.md`** — a plugin-first catalog for teams that want to
  keep deep review / QA / release / security logic out of this starter.

## Human gates

Agents prepare artifacts and recommendations. Humans own approval. The factory will
not merge, deploy, approve its own work, bypass branch protection, or expose secrets.
Ambiguous scope, security / data-model / auth changes, and any customer-impacting
rollout are surfaced for a human rather than guessed.
