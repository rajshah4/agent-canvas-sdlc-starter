# Tracker Integrations

## Integration Boundary

Keep tracker adapters outside the core workflow. Their job is to produce `story.json` and optionally write back a status comment.

The supervisor and workcells should not depend on Jira, Linear, GitHub, or any one payload shape.

## GitHub

Map:

- issue or PR title -> `request.title`
- body -> `request.body`
- labels -> `request.labels`
- comments -> `request.comments`
- repository -> `repo.url`
- issue or PR URL -> `source.url`

Use the GitHub connector or MCP tools when available. Otherwise accept copied issue text or exported JSON.

## Jira

Map:

- key -> `source.id`
- summary -> `request.title`
- description -> `request.body`
- issue type, labels, priority -> `request.labels` or `request.priority`
- comments -> `request.comments`
- linked repository field or custom field -> `repo.url`

Jira instances vary. Treat custom fields as hints unless the user documents them.

## Linear

Map:

- identifier or issue id -> `source.id`
- title -> `request.title`
- description -> `request.body`
- labels -> `request.labels`
- priority -> `request.priority`
- comments -> `request.comments`
- team/project/cycle -> optional metadata in `source.raw`

Use Linear MCP or API context when available. If only a webhook payload is present, normalize what is present and list missing decisions.

## Return Path

When requested and authorized, write back:

- intake summary
- link to lifecycle report
- child conversation links
- branch or PR link
- review and QA status
- human gates still required

Do not write back noisy intermediate logs unless the team asks for them.
