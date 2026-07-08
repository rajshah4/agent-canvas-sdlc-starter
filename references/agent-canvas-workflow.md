# Agent Canvas Workflow

## Mental Model

The parent conversation is the supervisor. It keeps the lifecycle coherent and starts focused child Agent Canvas conversations.

The minimal child conversations are:

- `story-to-pr`: turn the normalized story into implementation artifacts and a small change.
- `code-review`: inspect the change against the story, repo standards, and risks.
- `qa`: run focused validation and collect evidence.

The repo-local launcher reads the workcell prompts from `agent-canvas/prompts/workcells/` and creates separate Agent Canvas conversations through the local REST API.

## Artifact Contract

Every run should write:

```text
factory_runs/<run-id>/story.json
factory_runs/<run-id>/intake.md
factory_runs/<run-id>/children.json
factory_runs/<run-id>/story-to-pr.md
factory_runs/<run-id>/code-review.md
factory_runs/<run-id>/qa.md
factory_runs/<run-id>/lifecycle-report.md
```

Optional artifacts:

```text
factory_runs/<run-id>/raw-source.json
factory_runs/<run-id>/decision-log.md
factory_runs/<run-id>/ui-evidence/
```

## Supervisor Rules

- Read `story.json` first.
- Preserve known facts and unresolved decisions.
- Run `agent-canvas/scripts/run_agent_canvas_factory.py` to create implementation, review, and QA child conversations.
- Record child conversation IDs, UI URLs, responsibilities, and status in `children.json`.
- Stop or narrow scope when a human gate is required.
- Never merge, deploy, approve, bypass branch protection, or reveal secrets.
- End with a lifecycle report that a human can inspect.

## Required Tooling

A starter run needs more than a healthy Agent Canvas server. The parent conversation needs tools that can run commands and write artifacts, because it launches the repo-local child-conversation script.

The repository path must also be readable by the Agent Canvas process. On macOS, protected folders such as `Documents` and `Desktop` can be blocked even when Codex itself can read them. For first runs, prefer a repo under `/private/tmp` or `~/Code`.

When creating a conversation through the API, configure a tool-enabled agent with terminal, file, and task-tracking tools. If the agent can only call MCP tools, it can discuss the workflow but cannot scaffold prompts, run the normalizer, start child conversations, or write artifacts.

Minimum useful capabilities:

- terminal command execution
- file reading
- file writing
- directory listing

For Agent Server `1.31.0`, API-created parent and child conversations can use the short tool names advertised by `/server_info`, such as `terminal`, `file_editor`, and `task_tracker`.

Use `scripts/check_agent_canvas_ready.py` to check the server advertises these tools before a live run.

Use `scripts/start_agent_canvas_sdlc.py` to start the parent conversation with the right tool list and the server's configured max-iteration setting.

Inside the parent conversation, run:

```bash
python3 agent-canvas/scripts/run_agent_canvas_factory.py --base http://localhost:8000 --repo <repo> --run-id <run-id>
```

## Child Conversation Rules

- Work from `story.json`, not tracker-specific payloads.
- Write one artifact to the run directory.
- Report exact commands run and evidence collected.
- Mark `needs-human` when blocked by credentials, scope, security, missing environment, or unsafe production action.

## First Successful Run

For a new user, prefer:

```text
pasted story -> normalize_story.py -> scaffold prompts and launcher -> supervisor conversation -> child Canvas conversations -> local artifacts
```

Then add:

```text
tracker URL -> MCP connector -> story.json -> same supervisor
```

Then add:

```text
webhook or polling trigger -> raw payload -> story.json -> same supervisor
```
