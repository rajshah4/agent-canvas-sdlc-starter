# Agent Canvas SDLC Starter

A beginner-friendly Agent Canvas skill for learning how an automation factory works.
It turns a story into a small, inspectable workflow with a supervisor and real child
Agent Canvas conversations.

```text
story -> story.json -> supervisor -> implementation child -> review child -> QA child -> lifecycle report
```

This is intentionally a starter. The built-in workcells are local teaching versions.
For production PR review, QA, security, release notes, and repo readiness, use the
official OpenHands extensions listed in `references/upgrade-map.md`.

## First Run

Prerequisites:

- Local Agent Canvas/OpenHands Agent Server at `http://localhost:8000`.
- Python 3.
- A target repo that Agent Canvas can read. On macOS, prefer `/private/tmp` or
  `~/Code` for first runs.

Example prompt:

> Use the Agent Canvas SDLC starter to run the factory on `/private/tmp/my-repo`
> for this story: "Add a saved filter to the projects page so users return to the
> same view later."

The agent will:

1. Normalize the story into `factory_runs/<run-id>/story.json`.
2. Scaffold the Agent Canvas prompts and launcher into the target repo.
3. Start a supervisor conversation.
4. Have the supervisor create child conversations for implementation, review, and QA.
5. Write a lifecycle report with links, statuses, evidence, and human gates.

## What To Look For

Every run writes artifacts under `factory_runs/<run-id>/`:

| Artifact | Purpose |
| --- | --- |
| `story.json` | Stable handoff from intake into the factory. |
| `intake.md` | Human-readable story summary and decisions. |
| `children.json` | Child conversation IDs, links, artifact paths, and statuses. |
| `story-to-pr.md` | Implementation summary, changed files, tests, and gates. |
| `code-review.md` | Findings, risks, and review status. |
| `qa.md` | Commands, evidence, acceptance status, and residual risk. |
| `lifecycle-report.md` | Final run summary and next operator action. |

## Common Next Steps

- Connect intake to Jira, Linear, GitHub Issues, MCP, webhook, or polling sources.
- Replace the starter review child with OpenHands `pr-review` when there is a real PR.
- Replace the starter QA child with `qa-changes`, Playwright, or browser automation.
- Add security, release, repo-readiness, and observability extensions one step at a time.

See:

- `SKILL.md` for the agent-facing workflow.
- `references/upgrade-map.md` for the beginner upgrade path.
- `references/plugin-registry.md` for the short official OpenHands extension map.

## Safety

Agents prepare artifacts and recommendations. Humans approve scope, secrets, risky
decisions, merge, deploy, rollback, and customer-impacting rollout.
