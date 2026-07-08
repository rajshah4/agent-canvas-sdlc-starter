# Webhook Or Polling

## Choose The Trigger

Use webhooks when the OpenHands or Agent Canvas automation endpoint is publicly reachable by Jira, Linear, GitHub, or the source system.

Use polling when:

- the deployment is local or private
- the source system cannot send webhooks
- the team wants a simpler first integration
- webhook signing is not configured yet

Use manual start for the first run.

## Webhook Payload Handling

The webhook starts the workflow. It does not define the workflow contract.

1. Store raw payload when possible.
2. Extract source system, source id, source URL, title, body, labels, comments, priority, and repo hints.
3. Use MCP/API pull to enrich the story when the payload is sparse.
4. Normalize into `story.json`.
5. Start the supervisor with the normalized story.

## Polling Payload Handling

Polling should track which items were already processed. For a starter demo, keep polling out of the core skill unless the user explicitly asks to wire automation.

Polling adapters should:

- query for new or updated candidate stories
- skip stories without an explicit trigger marker or status
- normalize each story into `story.json`
- start one supervisor run per story
- write back a status marker to prevent repeat runs

## Safety Rules

- Verify webhook signatures when the source supports signatures.
- Do not print webhook secrets.
- Do not run implementation on every issue update unless a filter narrows the trigger.
- Avoid loops where the agent's own status comment retriggers the workflow.
