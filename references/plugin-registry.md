# Plugin Registry

Use this reference when the factory should become plugin-first: the starter skill defines the artifact contract, and each serious capability is delegated to a maintained plugin, skill, MCP server, CI workflow, or repo-specific guide.

The registry is a seed catalog, not a frozen source of truth. Before using a plugin in a production workflow, verify the plugin path, install method, inputs, permissions, and version pin.

## Pattern

Prefer this shape:

```text
factory slot -> plugin or skill adapter -> artifact contract -> human gate
```

Examples:

```text
code-review slot -> OpenHands pr-review plugin -> code-review.md + PR comments -> merge gate
qa slot -> qa-changes or Playwright -> qa.md + evidence -> acceptance gate
release slot -> release-notes plugin -> release.md + GitHub release notes -> publish gate
security slot -> vulnerability-remediation plugin -> security.md + fix PR -> approval gate
```

The starter factory should not copy the full prompts and scripts from these plugins. It should call them, link to their outputs, and preserve the run summary in `factory_runs/<run-id>/`.

## Useful Areas To Extend

These are common extension areas for teams building beyond the starter factory. Treat them as examples of where to connect stronger skills, plugins, MCP servers, CI jobs, or internal tools, not as dependencies bundled with this skill.

- Backlog and planning: Jira, Linear, GitHub Issues, Notion, Confluence, or custom spec-to-ticket workflows.
- Implementation context: repo-specific guides, AGENTS.md files, internal docs, architecture notes, and library documentation tools.
- Code review: OpenHands PR review, GitHub review automation, static analysis, policy checks, or custom review agents.
- QA: Playwright, browser automation, API tests, CLI tests, screenshots, traces, and user-flow verification.
- Security: Trivy, OSV-Scanner, Semgrep, Gitleaks, CodeQL, Dependabot, or commercial security scanners.
- CI and release: release-please, semantic-release, GitHub Actions, changelog generators, release-note tools, and publish gates.
- Observability and debugging: Sentry, Datadog, Grafana, logs, traces, incident reports, or repo-specific debugging scripts.
- Documentation: Notion, Confluence, docs generators, runbooks, architecture decision records, and handoff reports.

## OpenHands Extension Plugins

Authoritative plugin directory: https://github.com/OpenHands/extensions/tree/main/plugins

| Factory slot | Plugin | Good for | Factory output to capture |
| --- | --- | --- | --- |
| Repo readiness | `onboarding` | Preparing a repo for agent work: AGENTS.md, setup scripts, readiness report, and PR review workflow. | `repo-readiness.md`, setup links, generated AGENTS.md path. |
| Code review | `pr-review` | Automated PR review with inline comments, prior-review awareness, optional evidence enforcement, optional observability, and optional sub-agent delegation. | `code-review.md`, review URL, inline comment links, verdict. |
| QA | `qa-changes` | Running the software as a user would, exercising UI/API/CLI behavior, and posting a QA report with evidence. | `qa.md`, commands, screenshots, QA verdict, unable-to-verify notes. |
| Release | `release-notes` | Generating release notes from tags, PR metadata, commits, labels, and contributors. | `release.md`, release notes URL, changelog path. |
| Security | `vulnerability-remediation` | Scanning with Trivy, skipping the agent when clean, and creating fix PRs for actionable vulnerabilities. | `security.md`, scan report, fix PR links, exceptions. |
| Legacy modernization | `cobol-modernization` | Multi-phase COBOL-to-Java migration with build setup, mainframe dependency removal, and test-backed Java migration. | migration plan, test fixtures, Java project path, migration summary. |
| Migration QA | `migration-scoring` | Scoring completed migrations for coverage, correctness, style, risk, and executive reporting. | `migration_score.json`, `style_score.json`, `final_report.md`. |
| Intake triage | `issue-duplicate-checker` | Potential duplicate detection during issue intake. Verify current README and inputs before wiring it into a run. | `duplicate-check.md`, matched issue links, triage recommendation. |

There are also example or specialized plugins in the directory, such as `city-weather`, `magic-test`, and `openhands`. Treat them as demos or inspect them before including them in a software-factory path.

## Skills And Connectors To Prefer When Available

These are not always installed in every environment, but they are good examples of how a maximal factory should avoid reinventing common workflows:

| Factory slot | Skill or connector family | Good for |
| --- | --- | --- |
| Backlog creation | Jira/Confluence or Notion spec-to-backlog/spec-to-implementation skills | Turning PRDs and specs into structured work. |
| Tracker triage | Jira or GitHub issue triage skills | Duplicate detection, severity, ownership, and next action. |
| Company context | Confluence, Notion, Jira, or internal search skills | Pulling architecture, terminology, incident, or policy context into the story. |
| GitHub operations | GitHub PR, CI, issue, and release skills | Watching CI, fixing failures, addressing review comments, opening PRs, and publishing release artifacts. |
| Browser QA | Playwright CLI, Playwright MCP, or browser-control plugins | UI verification, screenshots, traces, videos, accessibility-tree snapshots, and durable E2E tests. |
| Documentation | Notion, Confluence, docs, or release-note skills | Publishing status reports, release notes, runbooks, and handoff docs. |

## How To Wire A Plugin Into The Factory

1. Pick the factory slot: intake, planning, implementation, review, QA, security, release, docs, or observability.
2. Verify the plugin is installed or installable in the target Agent Canvas/OpenHands environment.
3. Add a small adapter prompt or command that passes only the needed inputs: `story.json`, PR URL, diff, repo path, run ID, and any explicit human constraints.
4. Preserve the plugin's native output and summarize it into the factory artifact for that slot.
5. Add a gate when the plugin result is blocking, partial, policy-sensitive, or requires credentials.

## When To Build A New Skill Or Plugin

Build a new skill only when the needed behavior is mostly instructions, examples, or repo/team knowledge.

Build a new plugin when the behavior needs executable code, lifecycle hooks, CI integration, external API calls, custom scripts, or repeated installation into many repos.

Do not put a full code-review, QA, release, or security system inside the starter skill. Put that system in its own plugin, then let the starter call it.
