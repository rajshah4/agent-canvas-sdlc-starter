# Plugin Registry

Use this reference when the user asks which real OpenHands extension should replace
or strengthen a starter workcell.

Authoritative directory: https://github.com/OpenHands/extensions/tree/main/plugins

## Pattern

```text
factory slot -> real extension or team tool -> factory artifact -> human gate
```

The starter skill should not copy full prompts or scripts from these plugins. Run or
install the plugin, preserve its native output, and summarize the result into
`factory_runs/<run-id>/`.

## Local Fallback Or Real Plugin

| Capability | Keep starter local when... | Use the real plugin when... |
| --- | --- | --- |
| Code review | There is only a local diff, demo repo, or no PR credentials. | There is a GitHub PR, workflow, automation runner, or review token. |
| QA | The app cannot be run or the user is learning the loop. | The app can be exercised through UI, API, or CLI behavior. |
| Security | The change only needs a human gate or local note. | The repo needs repeatable scanning or vulnerability fix PRs. |
| Release | The run ends at handoff. | There is a tag, changelog, release workflow, or GitHub release target. |
| Repo readiness | The user only needs first-run setup notes. | The repo needs repeatable AGENTS.md, setup scripts, or agent-readiness checks. |

## Official OpenHands Extension Starting Points

| Factory slot | Extension | Use for |
| --- | --- | --- |
| Repo readiness | `onboarding` | AGENTS.md, setup scripts, readiness notes, and repo guidance. |
| Code review | `pr-review` | Automated PR review with inline comments and verdicts. |
| QA | `qa-changes` | Running the software as a user would and posting evidence. |
| Security | `vulnerability-remediation` | Trivy-backed vulnerability scanning and fix PRs. |
| Release | `release-notes` | Release notes from tags, PR metadata, commits, labels, and contributors. |
| Intake triage | `issue-duplicate-checker` | Duplicate detection during issue intake. |

Also consider connector or skill families for Jira, Linear, GitHub, Notion,
Confluence, Playwright/browser automation, GitHub Actions, docs, and observability.
Use the team's existing stronger skill first when one exists.
