# Roles, profiles, config schema

## Roles (templates/agents/<role>.md)
| role | category | when to include | default tools |
|---|---|---|---|
| product-manager | think | always | Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch |
| architect | think | always | + WebSearch, WebFetch |
| ux-designer | think | any UI | Read, Grep, Glob, Bash, Write, WebSearch, WebFetch |
| backend-dev | build | server code | Read, Edit, Write, Grep, Glob, Bash, WebSearch, WebFetch |
| mobile-dev | build | RN/Expo/Flutter/native | same |
| web-dev | build | web front-end | same |
| devops-engineer | build | always (CI/Docker/deploy) | same |
| test-engineer | build | always | same |
| api-tester | adversarial | server code | Bash, Read, Write, Grep, Glob |
| e2e-tester | adversarial | server + clients | same |
| mobile-tester | adversarial | mobile stack | same |
| web-tester | adversarial | web front-end | same |
| code-reviewer | adversarial | always | Bash, Read, Grep, Glob |
| bug-triager | adversarial | always | Read, Grep, Glob, Bash, Write, WebSearch, WebFetch |
| security-engineer | adversarial | always (money/PII → mandatory) | Read, Grep, Glob, Bash, Write, WebSearch, WebFetch |
| tech-writer | think | always | Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch |

Heavy roles (get the top effort in every profile): architect, security-engineer, code-reviewer, backend-dev, e2e-tester.

## Profiles
| profile | heavy roles | other roles |
|---|---|---|
| max | fable / max | fable / xhigh |
| balanced | opus / high | sonnet / high |
| economy | sonnet / medium | sonnet / medium (haiku for mobile-tester, web-tester, tech-writer) |

Per-role override in config: `"overrides": {"code-reviewer": {"model": "opus", "effort": "max"}}`.

## Default preloaded skills (only if the skill exists on the machine; render checks `~/.claude/skills` and `.claude/skills`)
architect, code-reviewer → scrutinize · backend-dev, mobile-dev, web-dev, bug-triager → debug-mantra · ux-designer → artifact-design · tech-writer → post-mortem

## Config schema (`.claude/agent-team.json`)
```json
{
  "project": "PetGo",
  "project_root": "/abs/path/to/main/repo",
  "docs_dir": "/abs/path/to/docs",
  "report_language": "Thai",
  "context_file": "PROJECT-CONTEXT.md",
  "absolute_paths": false,
  "profile": "max",
  "roles": ["product-manager", "architect", "..."],
  "repos": [
    {"name": "Backend API", "path": "/abs/path", "stack": "FastAPI 0.123, Postgres", "checks": ["venv/bin/pytest -q tests/"], "run": "venv/bin/uvicorn app.main:app --reload"}
  ],
  "specifics": {"backend-dev": "Layered layout: app/routers → app/crud → app/models → app/schemas. ..."},
  "overrides": {"code-reviewer": {"model": "opus"}},
  "skills": {"tech-writer": ["post-mortem"]}
}
```


## Portability
Generated agents reference paths relative to `project_root` (docs, other repos, `.claude/agent-memory`) so the same `.claude/` works on any machine that clones the repos in the same layout. Set `"absolute_paths": true` only for single-machine setups.
