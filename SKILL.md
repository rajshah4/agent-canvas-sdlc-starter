---
name: agent-canvas-sdlc-starter
description: Scaffold and run beginner-friendly Agent Canvas SDLC workflows from a story, PRD, Jira issue, Linear issue, GitHub issue, MCP-fetched tracker item, webhook payload, or polling automation. Use when Codex should help new Agent Canvas users normalize incoming work into story.json, create supervisor and workcell prompts, connect tracker intake adapters, preserve human gates, and produce implementation, code-review, QA, and lifecycle artifacts.
---

# Agent Canvas SDLC Starter

Use this skill to help a new Agent Canvas user turn a work request into a small, inspectable SDLC workflow.

The minimal factory pattern is:

```text
story intake -> story.json -> supervisor -> child Canvas conversations -> lifecycle report
```

Keep the first run simple, but still create real child Agent Canvas conversations so the demo looks like a factory that can scale. Start with pasted text or a local PRD, then add Jira, Linear, GitHub, MCP, webhook, polling, repo changes, or extra gates only when the user wants to upgrade that step.

## Workflow

1. Identify where the story comes from:
   - pasted text or local file
   - GitHub, Jira, or Linear URL
   - MCP connector result
   - webhook or polling payload
2. Normalize the source into `story.json` before starting Agent Canvas.
3. Scaffold starter prompts and schema into the target repo with `scripts/scaffold_agent_canvas_sdlc.py`.
4. Check local Agent Canvas readiness with `scripts/check_agent_canvas_ready.py`.
5. Start or guide a tool-enabled supervisor conversation using `scripts/start_agent_canvas_sdlc.py` or `assets/prompts/supervisor.md`.
6. Have the supervisor run `agent-canvas/scripts/run_agent_canvas_factory.py` so it creates `story-to-pr`, `code-review`, and `qa` child Canvas conversations.
7. Inspect `children.json` plus artifacts under `factory_runs/<run-id>/` and iterate on decisions or blockers.

## Upgrade Map

Present the workflow as a minimal path with optional upgrades. Do not turn a first run into the maximal factory by default.

Use this rule of thumb:

- Use the built-in child prompts for the first local Agent Canvas demo and for runs without a PR, CI workflow, tracker credentials, release tag, or production access.
- Use the actual maintained OpenHands extension when the user has the production surface that extension expects.
- Do not replace a real extension with a paragraph describing what it should do. The starter prompt is only a fallback and teaching scaffold.

Use `references/upgrade-map.md` when the user asks how to improve the demo, add more factory behavior, connect more systems, introduce delegated agents, add additional gates, or replace starter workcells with maintained skills, plugins, MCP servers, CI workflows, Playwright-style QA, or repo-specific guides.

Use `references/plugin-registry.md` when the user wants to make the factory plugin-first, pick callable OpenHands plugins, or avoid putting deep code-review, QA, release, security, or tracker logic into this starter skill.

Default stance:

- Run the minimal child-conversation factory first.
- Identify which step the user wants to improve.
- Add the smallest maintained skill, plugin, capability, tool, or gate that improves that step.
- Prefer official OpenHands extensions for production PR review, QA, security remediation, release notes, repo onboarding, and OpenHands automation when their setup requirements are met.
- Keep each upgrade visible in the artifact contract.

## Story Intake

Always make intake explicit. Do not let downstream prompts depend on tracker-specific fields.

Use `references/story-intake.md` when the user has a Jira, Linear, GitHub, PRD, pasted story, webhook payload, or polling result.

Use this boundary:

- MCP and connectors fetch or write context.
- Webhooks and polling trigger runs.
- `story.json` is the handoff into Agent Canvas.

If a connector is available, use it to fetch full issue context. If no connector is available, ask for a pasted/exported story or raw webhook payload. Store the raw source payload when available, but pass normalized fields to the supervisor.

## Disagreement And Quality Loop

When people have different ideas, do not collapse disagreement into a guessed implementation. Preserve options in `decisions.known` and `decisions.needed`.

Use this loop:

1. Extract facts from the source material.
2. Separate product decisions from implementation details.
3. Record competing options and who asked for them when known.
4. Ask for human resolution only when the decision changes scope, risk, UX, API behavior, data model, security, cost, or rollout.
5. Let workcells implement only the resolved slice.
6. Have code review and QA check the result against `story.json`, acceptance criteria, and human gates.

## Agent Canvas Workflow

Use `references/agent-canvas-workflow.md` for the supervisor/workcell model and artifact contract.

Default artifacts:

```text
factory_runs/<run-id>/story.json
factory_runs/<run-id>/intake.md
factory_runs/<run-id>/children.json
factory_runs/<run-id>/story-to-pr.md
factory_runs/<run-id>/code-review.md
factory_runs/<run-id>/qa.md
factory_runs/<run-id>/lifecycle-report.md
```

The supervisor conversation coordinates. Child Canvas conversations do focused implementation, review, and QA work. Humans approve scope, secrets, risky decisions, merge, and deploy.

The parent conversation must have terminal and file tools so it can run the repo-local launcher. A server may be reachable while the selected agent profile lacks the tools needed to scaffold files, start child conversations, or write artifacts.

The repository path must also be readable by Agent Canvas. On macOS, prefer `/private/tmp` or `~/Code` for first runs instead of protected folders such as `Documents` or `Desktop`.

## Tracker Integrations

Use `references/tracker-integrations.md` for GitHub, Jira, Linear, and local-file mapping.

Use `references/webhook-or-polling.md` when the user wants automatic triggering. If the Agent Canvas or OpenHands deployment cannot receive public webhooks, recommend polling or manual start first.

## Human Gates

Use `references/human-gates.md` whenever a request touches:

- ambiguous scope or acceptance criteria
- security, auth, data model, or migration changes
- secrets or production systems
- external API behavior
- merge, deploy, rollback, or customer-impacting rollout

Agents may prepare artifacts and recommendations. Humans own approval.

## Scripts

Normalize a pasted story, PRD, issue export, or webhook payload:

```bash
python3 scripts/normalize_story.py --input path/to/source.txt --output factory_runs/demo-001/story.json
```

Scaffold starter prompts into a repo:

```bash
python3 scripts/scaffold_agent_canvas_sdlc.py --repo /path/to/repo
```

Check local Agent Canvas and scaffolded files:

```bash
python3 scripts/check_agent_canvas_ready.py --base http://localhost:8000 --repo /path/to/repo
```

Start the parent supervisor conversation:

```bash
python3 scripts/start_agent_canvas_sdlc.py --base http://localhost:8000 --repo /path/to/repo --run-id demo-001
```

## Bundled Assets

- `assets/schemas/story.schema.json`: stable story handoff contract.
- `assets/scripts/agent_canvas_delegate.py`: local Agent Canvas API helper used by the child launcher.
- `assets/scripts/run_agent_canvas_factory.py`: repo-local parent-side launcher that creates child Canvas conversations.
- `assets/prompts/intake-normalizer.md`: agent prompt for fuzzy or connector-fetched story normalization.
- `assets/prompts/supervisor.md`: parent Agent Canvas conversation prompt.
- `assets/prompts/workcells/story-to-pr.md`: implementation workcell prompt.
- `assets/prompts/workcells/code-review.md`: review workcell prompt.
- `assets/prompts/workcells/qa.md`: QA workcell prompt.
- `assets/examples/`: starter story and tracker payload examples.
