# Upgrade Map

Use this reference after the user has run or understood the minimal factory and wants
to improve one step.

Keep the first run small:

```text
pasted story or local file
-> story.json
-> supervisor
-> implementation, review, and QA child conversations
-> lifecycle-report.md
```

Then upgrade one box at a time. Prefer a maintained OpenHands extension, MCP server,
CI workflow, repo guide, or team skill before writing a bigger prompt.

## Rule Of Thumb

- Keep the starter workcells for local demos, first-time learning, and runs without
  PRs, credentials, CI, release tags, or production access.
- Use the real extension when the production surface exists.
- Do not imitate a mature extension with a paragraph. Run or install the extension
  and summarize its output into the factory artifacts.

## Beginner Upgrade Menu

| Step | Starter path | Upgrade when ready |
| --- | --- | --- |
| Intake | Paste a story or normalize a local file to `story.json`. | Connect Jira, Linear, GitHub Issues, MCP, webhook, or polling intake. |
| Implementation | Use `story-to-pr` child for the smallest resolved local slice. | Add repo `AGENTS.md`, setup scripts, branch/PR creation, and repo-specific implementation guidance. |
| Code review | Use local `code-review` child for demo diffs. | Use OpenHands `pr-review` for real PRs, or `code-review` skill for direct conversation review. |
| QA | Use local `qa` child for focused commands and evidence. | Use OpenHands `qa-changes`, Playwright, browser MCP, API tests, or team QA skills. |
| Security | Record a human gate for risky work. | Use `vulnerability-remediation`, CodeQL, secret scanning, dependency audit, SAST/DAST, or org policy tools. |
| Release | End with `lifecycle-report.md` and handoff notes. | Use `release-notes`, release-please, semantic-release, GitHub Actions, and deploy approval gates. |
| Repo readiness | Note setup gaps in the lifecycle report. | Use `onboarding`, `AGENTS.md`, setup scripts, and repo customization hooks. |
| Observability | Use `children.json` and `lifecycle-report.md`. | Add timelines, metrics, trace links, CI links, tracker links, and status reports. |

## Practical Recipes

### Connect A Tracker

Use when stories should enter from Jira, Linear, GitHub, or another tracker.

1. Fetch or receive the raw issue payload.
2. Store it as `factory_runs/<run-id>/raw-source.json` when possible.
3. Normalize only the useful fields into `story.json`.
4. Keep workcells tracker-neutral.
5. Write back status only when explicitly authorized.

### Upgrade Code Review

Use the starter child while learning or reviewing a local diff.

Use the actual OpenHands `pr-review` plugin when there is a GitHub PR, workflow,
automation runner, or review token. Capture the PR review URL, inline comment links,
verdict, and any blocking findings in `factory_runs/<run-id>/code-review.md`.

### Upgrade QA

Use the starter child while learning or when the environment is too small for a full
QA run.

Use OpenHands `qa-changes`, Playwright, browser MCP, API tests, or CLI tests when the
software can actually be run. Capture commands, screenshots, traces, videos, generated
tests, acceptance status, and unable-to-verify notes in `factory_runs/<run-id>/qa.md`.

### Add Security Or Release

Add these only when the story needs them.

- Security: use `vulnerability-remediation` or the team's scanners and policy gates.
- Release: use `release-notes` or the team's release workflow after review and QA.
- Human approval remains required for secrets, production actions, merge, deploy,
  rollback, and customer-impacting rollout.

## Maximum Factory Shape

A larger factory is a set of replaceable parts, not one giant skill:

```text
tracker/webhook/MCP
-> story normalizer
-> supervisor
-> implementation
-> PR review extension
-> QA extension or Playwright
-> security or release gate
-> lifecycle report and sync back
```

Each part can be upgraded independently. The starter should help the user see the
path, then point to the best maintained capability for the part they want to improve.
