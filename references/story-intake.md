# Story Intake

## Purpose

Normalize every incoming request into `story.json` before Agent Canvas orchestration begins. The tracker is the front door; `story.json` is the handoff.

## Intake Modes

Manual starter:

- Use when the user is learning the workflow or running a demo.
- Accept pasted text, a local markdown file, or a PRD export.
- Prefer this for the first successful run.

MCP pull:

- Use when the user gives a Jira, Linear, GitHub, Confluence, Notion, or similar URL and the matching connector is available.
- Fetch title, body, comments, labels, linked docs, acceptance criteria, repo hints, assignee, and status.
- Write back status only when the user asks or the workflow explicitly includes a return path.

Webhook or polling payload:

- Use when an automation starts the workflow.
- Treat the payload as raw input, not the story contract.
- Store the raw payload path and normalize the useful fields into `story.json`.

## MCP Versus Webhook

- MCP and connectors are for reading and writing context.
- Webhooks are for triggering a run when an external event happens.
- Polling is the fallback trigger when the deployment cannot receive public webhooks.

Do not require webhook setup for a first run. First prove that `story.json` drives the workflow.

## Normalized Fields

Required:

- `source.system`
- `request.title`
- `request.body`

Recommended:

- `source.url`
- `source.id`
- `source.raw_payload_path`
- `request.acceptance_criteria`
- `request.comments`
- `request.labels`
- `repo.url`
- `repo.local_path`
- `repo.base_branch`
- `decisions.known`
- `decisions.needed`

## Missing Data Rules

Infer small formatting details, but do not invent product decisions.

Ask for human input when missing information changes:

- scope
- acceptance criteria
- customer-visible behavior
- API behavior
- data model or migration
- security or auth
- dependency policy
- rollout and merge decision

## Disagreement Handling

When stakeholders disagree:

1. Record each option in `decisions.needed`.
2. Include the source comment or person when known.
3. Let the supervisor continue only on resolved slices.
4. Mark blocked slices as human-gated.

Example:

```json
{
  "question": "Should the dashboard show archived projects by default?",
  "options": ["hide archived by default", "show archived with warning"],
  "impact": "Changes default user-visible behavior",
  "needed_from": "product owner"
}
```
