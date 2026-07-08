# Human Gates

## Required Human Gates

Require human approval for:

- final scope and acceptance criteria when ambiguous
- security-sensitive changes
- auth, permissions, or secret access
- data migrations and destructive operations
- external API behavior changes
- dependency additions or license-sensitive packages
- production changes
- merge and deploy

## Agent-Owned Work

Agents may:

- fetch and summarize context
- propose a spec or task plan
- create a branch or local diff when permitted
- write tests
- run validation
- review code
- prepare PR text and status comments
- produce lifecycle reports

Agents must not:

- approve their own work as a human reviewer
- merge
- deploy
- bypass branch protection
- reveal secrets
- mutate production systems without explicit approval

## Decision Log

Use a decision log when ideas conflict:

```markdown
## Decision Needed

- Question:
- Options:
- Impact:
- Recommended default:
- Needed from:
- Status: open | resolved | deferred
```

Resolved decisions should be copied into `story.json` under `decisions.known`.
