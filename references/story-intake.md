# Story Intake

Use this reference whenever work enters the factory from pasted text, a local file,
Jira, Linear, GitHub, MCP, webhook, or polling.

The rule is simple: the source can vary, but the supervisor should receive one stable
handoff file: `story.json`.

## First Run

For a first-time user, start with pasted text or a local markdown file. Do not require
webhooks, tracker credentials, or status write-back before the basic factory loop works.

```text
pasted story or local file -> story.json -> supervisor
```

## Intake Modes

Manual starter:

- Use for demos and first successful runs.
- Accept pasted text, a local markdown file, or a PRD snippet.

MCP or connector pull:

- Use when the user gives a Jira, Linear, GitHub, Confluence, Notion, or similar URL.
- Fetch title, body, comments, labels, links, acceptance criteria, repo hints, assignee, and status when available.
- Write status back only when the user asks or the workflow explicitly includes a return path.

Webhook or polling payload:

- Use when an automation starts the workflow.
- Treat the payload as raw input, not as the story contract.
- Store the raw payload when useful, then normalize the useful fields into `story.json`.

## Tracker Field Mapping

Keep tracker adapters outside the core workflow. Their job is to produce `story.json`
and optionally write back a status comment. The supervisor and workcells should not
depend on Jira, Linear, GitHub, or any one payload shape.

GitHub:

- issue or PR title -> `request.title`
- body -> `request.body`
- labels -> `request.labels`
- comments -> `request.comments`
- repository -> `repo.url`
- issue or PR URL -> `source.url`

Jira:

- key -> `source.id`
- summary -> `request.title`
- description -> `request.body`
- issue type, labels, priority -> `request.labels` or `request.priority`
- comments -> `request.comments`
- linked repository field or custom field -> `repo.url`

Linear:

- identifier or issue id -> `source.id`
- title -> `request.title`
- description -> `request.body`
- labels -> `request.labels`
- priority -> `request.priority`
- comments -> `request.comments`

Treat custom tracker fields as hints unless the user documents them.

## Webhook Or Polling

Use manual start for the first run.

Use webhooks when the OpenHands or Agent Canvas automation endpoint is publicly
reachable by the source system. Verify webhook signatures when the source supports
signatures, and do not print webhook secrets.

Use polling when:

- the deployment is local or private
- the source system cannot send webhooks
- the team wants a simpler first integration
- webhook signing is not configured yet

Polling adapters should track processed items, skip stories without an explicit trigger
marker or status, and avoid loops where the agent's own status comment retriggers the
workflow.

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

## Missing Data And Disagreement

Infer small formatting details, but do not invent product decisions.

Ask for human input when missing information changes scope, acceptance criteria,
customer-visible behavior, API behavior, data model, security, dependencies, rollout,
merge, or deployment.

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

## Return Path

When requested and authorized, write back:

- intake summary
- lifecycle report link
- child conversation links
- branch or PR link
- review and QA status
- human gates still required

Do not write back noisy intermediate logs unless the team asks for them.
