# Agent Canvas SDLC Starter

Let's build a software automation factory that starts simple, then grows as you add
your own integrations, gates, and team practices.

The core idea is small: the agent acts as a software factory supervisor in Agent
Canvas and creates real child conversations for implementation, review, and QA.
You can watch the work move from one step to the next instead of treating the
agent like one giant black box.

```text
story -> story.json -> factory supervisor -> implementation child -> review child -> QA child -> lifecycle report
```

A "story" is just the work request. It can be a pasted feature request, a bug report,
a PRD snippet, a Jira issue, a Linear issue, a GitHub issue, or a webhook payload.
For the first run, use something small and concrete.

## How It Works

The software factory shape is based on `references/agent-canvas-workflow.md`.
Start there when you want to understand and improve how the supervisor, child
conversations, artifacts, sequencing, or workcell prompts fit together.

This README is the human quickstart. `SKILL.md` is what the agent reads. The
workflow reference is the shared factory pattern behind both.

## Quick Start

Prerequisites:

- Local Agent Canvas/OpenHands Agent Server at `http://localhost:8000`.
- Python 3.
- A target repo that Agent Canvas can read. On macOS, prefer `/private/tmp` or
  `~/Code` for first runs.

Example prompt:

> Use the Agent Canvas SDLC starter to run the factory on `/private/tmp/my-repo`
> for this feature request: "Add a saved filter to the projects page so users return
> to the same view later."

The agent will:

1. Turn the story into the shared story file at `factory_runs/<run-id>/story.json`.
2. Add the starter Agent Canvas files to the target repo so the supervisor can run
   the factory there.
3. Act as the factory supervisor, or bootstrap one when starting from outside Agent Canvas.
4. Create child conversations for implementation, review, and QA.
5. End with a report summarizing links, statuses, evidence, and human gates.

## What To Look For

Every run writes artifacts under `factory_runs/<run-id>/`:

| Artifact | Purpose |
| --- | --- |
| `story.json` | The shared source of truth for the run. |
| `intake.md` | The readable story summary and open decisions. |
| `children.json` | Child conversation IDs, links, artifact paths, and statuses. |
| `story-to-pr.md` | What changed, what tests ran, and what still needs a human. |
| `code-review.md` | Review findings, risks, and review status. |
| `qa.md` | Commands, evidence, acceptance status, and residual risk. |
| `lifecycle-report.md` | The final run summary and next operator action. |

## Your Next Steps

You do not need the full factory on day one. Start with the local starter loop, then
upgrade one step at a time:

- Connect intake to Jira, Linear, GitHub Issues, MCP, webhook, or polling sources.
- Replace the starter review child with OpenHands `pr-review` when there is a real PR.
- Replace the starter QA child with `qa-changes`, Playwright, or browser automation.
- Add security, release, repo-readiness, and observability extensions when the workflow needs them.

See:

- `SKILL.md` for the agent-facing workflow.
- `references/story-intake.md` for tracker, webhook, polling, and story normalization.
- `references/upgrade-map.md` for the beginner upgrade path and OpenHands extension paths.

## Safety

Agents prepare artifacts and recommendations. Humans approve scope, secrets, risky
decisions, merge, deploy, rollback, and customer-impacting rollout.
