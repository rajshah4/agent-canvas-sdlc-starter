# Upgrade Map

Use this reference when a user has run or understood the minimal factory and wants to improve one step.

This map is capability-first. Do not present upgrades as a maturity ladder or as "add more prompts." Present each upgrade as a way to replace a starter workcell with a maintained skill, plugin, MCP server, CLI, CI workflow, or repo-specific guide.

```text
current minimal step -> proven skill/tool/approach -> new artifact or gate
```

## Operating Rules

- Keep the minimal demo runnable and visible: pasted story or local file, `story.json`, supervisor conversation, child Canvas conversations, workcell artifacts, and `lifecycle-report.md`.
- Prefer an existing team skill, OpenHands extension, MCP server, test framework, CI workflow, or repo tool before writing a custom long prompt.
- Put capability-specific prompts and scripts with the capability skill or plugin. The starter skill should define the handoff contract and link to the stronger capability.
- Upgrade one step at a time and keep the new artifact or human gate explicit.
- If a linked skill or plugin is not installed, record that as setup work instead of pretending the factory can already use it.
- Pin versions for production runs. Use `main` only for demos or active exploration.

## Minimal Factory

The starter path should stay small:

```text
pasted story or local file
-> normalize to story.json
-> supervisor conversation
-> child Canvas conversations
-> workcell artifacts
-> lifecycle-report.md
```

This teaches the shape of a software factory without requiring live tracker credentials, production access, CI, PR permissions, or deployment systems.

## Skill And Tool Registry

Start with this registry when users ask "what should I use instead of the starter prompt?"

For a plugin-first implementation, use `references/plugin-registry.md` as the longer seed catalog. Keep this table focused on capability slots and the most common upgrade targets.

That registry also includes a "Useful Areas To Extend" note for teams that want a broader menu without treating every advanced tool as part of the starter skill.

| Capability | Concrete starting point | How it connects |
| --- | --- | --- |
| Tracker intake | Jira, Linear, or GitHub connector/MCP; OpenHands MCP docs: https://docs.openhands.dev/overview/model-context-protocol | Fetch issue, comments, labels, links, and attachments into `raw-source.json`, then normalize to `story.json`. |
| Evented intake | OpenHands event automations: https://docs.openhands.dev/openhands/usage/automations/event-automations | Trigger factory runs from pull request, issue, webhook, or schedule events. |
| Repository setup and gates | OpenHands repository customization and hooks: https://docs.openhands.dev/openhands/usage/customization/repository | Add setup scripts, repo context, and stop hooks that enforce local checks before completion. |
| Code review | OpenHands Automated Code Review: https://docs.openhands.dev/openhands/usage/use-cases/code-review | Replace the starter `code-review` workcell with `/codereview`, the `pr-review` plugin, or an org automation. |
| Code review plugin | `OpenHands/extensions/plugins/pr-review`: https://github.com/OpenHands/extensions/tree/main/plugins/pr-review | Run as GitHub Action or OpenHands Automation; produce PR inline comments and a verdict. |
| Code review skill | `OpenHands/extensions/skills/code-review`: https://github.com/OpenHands/extensions/tree/main/skills/code-review | Use directly in a conversation with `/add-skill` and `/codereview`, or as part of the PR review plugin. |
| GitHub review posting | `OpenHands/extensions/skills/github-pr-review`: https://github.com/OpenHands/extensions/tree/main/skills/github-pr-review | Post structured inline comments and review summaries back to the PR. |
| QA changes | OpenHands Automated QA Testing: https://docs.openhands.dev/openhands/usage/use-cases/qa-changes | Replace the starter `qa` workcell with `/qa-changes`, the QA plugin, or an org automation. |
| QA plugin | `OpenHands/extensions/plugins/qa-changes`: https://github.com/OpenHands/extensions/tree/main/plugins/qa-changes | Run software as a user would, then post a structured QA report with evidence. |
| QA skill | `OpenHands/extensions/skills/qa-changes`: https://github.com/OpenHands/extensions/tree/main/skills/qa-changes | Use directly in a conversation with `/add-skill` and `/qa-changes`. |
| Browser QA | Playwright CLI for coding agents: https://playwright.dev/docs/getting-started-cli | Use installable Playwright skills, snapshots, screenshots, traces, and video from a QA workcell. |
| Browser MCP | Playwright MCP: https://playwright.dev/docs/getting-started-mcp | Connect a browser automation MCP server for persistent exploratory UI testing. |
| E2E evidence | Playwright Trace Viewer: https://playwright.dev/docs/trace-viewer-intro | Attach `trace.zip`, screenshots, videos, and HTML reports to QA artifacts. |
| CI and PR operations | GitHub Actions plus available GitHub skills or plugins | Watch checks, fix failing CI, request review, and link the PR back to the factory run. |
| Security | Existing org security skills, CodeQL, secret scanning, dependency audit, SAST/DAST tools | Add security findings and policy gates before merge or deploy. |
| Observability | Run timeline, child conversation IDs, OpenTelemetry/Laminar-style traces, cost and token metrics | Make the factory inspectable, debuggable, and auditable. |

Treat this registry as editable. If a team has a stronger internal Playwright skill, code review skill, security skill, or release skill, point to that first and keep the starter prompt as the fallback.

## Step Upgrades

### Story Intake

Use when the user wants real work to enter the factory from a tracker or automation.

Upgrade toward:

- Jira, Linear, GitHub, or internal tracker MCP connectors.
- Webhook or polling intake for continuous operation.
- Raw payload storage, idempotency by source issue ID, and status/comment sync back to the tracker.
- Backlog conversion skills such as a Confluence/Notion spec-to-backlog or spec-to-implementation skill when the source is a longer product document.

Wire into the factory:

- Fetch source data before normalization.
- Store `factory_runs/<run-id>/raw-source.json`.
- Keep `story.json` tracker-neutral.
- Add `source.kind`, `source.url`, `source.id`, and `source.sync_target` fields when known.

Artifacts or gates to add:

- `factory_runs/<run-id>/intake.md`
- `factory_runs/<run-id>/raw-source.json`
- `factory_runs/<run-id>/sync-log.md`
- human gate when tracker fields are incomplete, conflicting, or imply risky scope

### Story Normalization

Use when incoming stories vary widely in quality.

Upgrade toward:

- Stronger JSON Schema validation.
- Acceptance criteria extraction and coverage matrices.
- Decision extraction for unresolved product, UX, API, data, security, cost, or rollout questions.
- A repo or org-specific story-quality skill that knows the team's definition of ready.

Wire into the factory:

- Keep `story.json` as the only required supervisor input.
- Store unresolved decisions in `decisions.needed`, not in prose-only notes.
- Fail early when acceptance criteria are absent or contradictory.

Artifacts or gates to add:

- `factory_runs/<run-id>/story.json`
- `factory_runs/<run-id>/decision-log.md`
- `factory_runs/<run-id>/acceptance-matrix.md`
- human gate for ambiguous scope, missing acceptance criteria, or unresolved product decisions

### Supervisor Orchestration

Use when the minimal child-conversation factory should become more capable.

Upgrade toward:

- More specialized child Canvas conversations: planning, implementation, code review, QA, security, docs, release, and incident-readiness.
- Safe parallelism for independent workcells.
- Child retry, timeout, stuck-detection, and escalation policies.
- A child registry that records conversation IDs, task status, elapsed time, artifacts, and blockers.

Wire into the factory:

- Keep Agent Canvas child conversations visible in the starter path.
- Let the parent remain responsible for scope, sequencing, and final status.
- Use SDK sub-agent delegation only inside a mature plugin or workflow that benefits from it. For the Agent Canvas starter, visible Canvas children are the scaling signal.

Artifacts or gates to add:

- `factory_runs/<run-id>/children.json`
- `factory_runs/<run-id>/timeline.md`
- `factory_runs/<run-id>/lifecycle-report.md`
- human gate when a child reports `needs-human`

### Implementation

Use when the factory should touch code.

Upgrade toward:

- Branch or worktree creation.
- Repo setup via README, AGENTS.md, `.openhands/setup.sh`, or equivalent project instructions.
- Focused implementation of the smallest resolved slice.
- Local tests, lint, type checks, and repo-specific quality hooks.
- Pull request creation when credentials and approval are available.

Wire into the factory:

- Keep the starter `story-to-pr` prompt as the minimal fallback.
- Replace it with a repo-specific implementation skill when the team has one.
- Preserve the diff, commands run, assumptions, and any skipped checks.

Artifacts or gates to add:

- `factory_runs/<run-id>/story-to-pr.md`
- branch name, diff path, or PR URL
- `factory_runs/<run-id>/commands.log`
- human gate before merge, deploy, or production-impacting changes

### Code Review

Use when the factory should provide independent quality control.

Upgrade toward:

- OpenHands `code-review` skill for manual conversation review.
- OpenHands `pr-review` plugin for GitHub Actions or OpenHands Automation.
- Repo-specific review guide skill that activates with `/codereview` and adds local rules without shadowing the default review framework.
- Optional review sub-agents for large PRs when the chosen plugin supports them and the token/time budget is acceptable.
- Static analysis, secret scanning, dependency review, and code owner checks for policy-backed review.

Wire into the factory:

- Replace the starter `code-review` child prompt with a child that invokes `/codereview` or runs the PR review plugin.
- Pass the PR URL or diff, `story.json`, acceptance criteria, and previous findings.
- Store the raw review summary even when inline comments are posted to GitHub.
- Record whether findings are blocking, informational, or require a human owner.

Artifacts or gates to add:

- `factory_runs/<run-id>/code-review.md`
- PR review URL or inline comment links
- `pass`, `findings`, `needs-human`, or `failed` status
- human gate for security, ownership, policy, data, migration, or architecture questions

### QA

Use when the factory should validate behavior by running the software, not just reading code.

Upgrade toward:

- OpenHands `qa-changes` skill or plugin for PR-focused QA.
- A team Playwright skill for UI flows, screenshots, browser traces, videos, and repeatable evidence.
- Playwright MCP when the agent needs persistent exploratory browser control.
- Playwright Test when the team wants durable E2E tests committed to the repo.
- API, CLI, SDK, and data migration test harnesses for non-UI changes.

Wire into the factory:

- Replace the starter `qa` child prompt with `/qa-changes` or a Playwright-driven QA workcell.
- Pass `story.json`, PR URL or diff, dev server instructions, test credentials policy, and priority scenarios.
- Produce evidence from real execution: commands, HTTP responses, screenshots, traces, videos, or generated tests.
- Report missing environment, browsers, credentials, or services honestly as `partial`, not `pass`.

Artifacts or gates to add:

- `factory_runs/<run-id>/qa.md`
- `factory_runs/<run-id>/acceptance-matrix.md`
- `factory_runs/<run-id>/ui-evidence/`
- `factory_runs/<run-id>/playwright-report/`
- human gate when validation requires unavailable systems, secrets, payments, production access, or unsafe data changes

### Release And Delivery

Use when the factory should shepherd work beyond local validation.

Upgrade toward:

- CI monitoring and failing-check repair.
- Review request, merge readiness, and CODEOWNERS routing.
- Changelog, release notes, customer communication, feature flag, and rollback plans.
- Deployment workflows with explicit human approval.

Wire into the factory:

- Treat release as its own child conversation or automation after review and QA.
- Link CI, PR, tracker, QA evidence, and deployment plan from one release artifact.
- Never let the agent merge, deploy, or roll back without the configured approval gate.

Artifacts or gates to add:

- `factory_runs/<run-id>/release.md`
- CI links
- release notes path
- deployment and rollback notes
- human gate before merge, deploy, rollback, or customer-impacting rollout

### Security And Policy

Use when the work touches auth, data, secrets, infrastructure, dependencies, external APIs, compliance, or customer-impacting behavior.

Upgrade toward:

- Security review skill or threat-modeling skill.
- CodeQL, secret scanning, dependency audit, license policy, SBOM, SAST, DAST, or container scanning.
- Org-specific policy checks for data classification, privacy, and access control.

Wire into the factory:

- Add a security child conversation only when risk justifies it.
- Make policy tools deterministic where possible and have the agent summarize results.
- Route unresolved security decisions to humans with owner, risk, and recommendation.

Artifacts or gates to add:

- `factory_runs/<run-id>/security.md`
- scanner links or reports
- policy exceptions requested
- human gate for unresolved security, privacy, compliance, or production-risk questions

### Observability

Use when operators need to understand the factory run.

Upgrade toward:

- Run timeline and child conversation audit trail.
- Token, cost, elapsed time, model profile, and retry metrics.
- Links to tracker issue, PR, CI, code review, QA evidence, release notes, and deployment.
- OpenTelemetry or hosted trace tools when available.

Wire into the factory:

- Make `children.json` the machine-readable index.
- Make `lifecycle-report.md` the human-readable summary.
- Include enough context for a user to resume or debug the run without re-reading every child conversation.

Artifacts or gates to add:

- `factory_runs/<run-id>/timeline.md`
- `factory_runs/<run-id>/metrics.json`
- dashboard or status-report artifact

## Upgrade Recipes

### Better Code Review

Current minimal step:

```text
code-review child prompt -> code-review.md
```

Upgrade path:

```text
code-review child prompt
-> OpenHands code-review skill or pr-review plugin
-> PR inline comments, verdict, review URL, code-review.md
```

Add a repo-specific review guide only for local rules: architecture conventions, approval standards, risky files, test expectations, and known pitfalls. Do not copy the whole review framework into the starter skill.

### Better QA

Current minimal step:

```text
qa child prompt -> qa.md
```

Upgrade path:

```text
qa child prompt
-> OpenHands qa-changes skill or Playwright skill/MCP
-> commands, screenshots, traces, videos, acceptance matrix, qa.md
```

For UI work, prefer Playwright evidence over prose. For API, CLI, library, and backend work, prefer real commands or short reproducible scripts over "looks correct" review.

### Maximum Factory Shape

A maximal factory is not one huge skill. It is a set of replaceable skills and tools connected by stable artifacts:

```text
tracker/webhook/MCP
-> intake adapter
-> story normalizer
-> supervisor
-> planning child
-> implementation child
-> code review skill/plugin
-> QA skill/plugin/Playwright
-> security/policy gate
-> release/CI automation
-> lifecycle report and sync back
```

Each box can be upgraded independently. The starter skill should help users see the path, then point them to the best maintained capability for the box they want to strengthen.

## Choosing The Next Upgrade

Prefer the smallest upgrade that improves the user's current pain:

- If stories are hard to enter, upgrade intake.
- If stories are ambiguous, upgrade normalization and human gates.
- If the demo does not feel like a factory, upgrade supervisor delegation while keeping visible child Canvas conversations.
- If users want real engineering value, upgrade implementation, code review, and QA.
- If teams need trust, upgrade policy gates, deterministic checks, and evidence.
- If teams want continuous operation, upgrade webhook/polling, queues, retries, idempotency, and sync back.
- If teams already have a better internal skill, connect that skill before building another generic prompt.
