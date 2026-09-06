# agent-team — a software company of Claude Code agents, for any project

`/agent-team init` explores the current project, asks four questions (profile, roles, report language, docs location), then generates a team of subagents (`.claude/agents/`), pipeline commands (`.claude/commands/`: `/feature`, `/fix`, `/test-all`, `/prd`, `/adr`, `/security-audit`, `/release`, `/standup`, `/review`, `/team`) and a shared docs folder (`PROJECT-CONTEXT.md`, `TEAM.md`, `LEARNINGS.md`, `product/BACKLOG.md`) — all grounded in that project's real code. Every agent reads the context file and its own persistent memory first, follows an expert protocol (plan → verify → self-review → leave lessons), and reports in your language.

Roles: product-manager · architect · ux-designer · backend-dev · mobile-dev · web-dev · test-engineer · api-tester · e2e-tester · mobile-tester · web-tester · code-reviewer · bug-triager · security-engineer · devops-engineer · tech-writer. Profiles: `max` (fable/max), `balanced` (opus+sonnet), `economy` (sonnet+haiku). Details: `reference/roles.md`.

## Install on another machine (pick one)

**A. As a personal skill (simplest)** — available in every project on that machine:
```bash
git clone <this-repo-url> ~/.claude/skills/agent-team
```

**B. As a plugin from this repo (also works as a marketplace)** — inside Claude Code:
```
/plugin marketplace add <github-owner>/<repo>
/plugin install agent-team@itsaraphap-tools
```

**C. Ad hoc, no install** — from a local clone:
```bash
claude --plugin-dir /path/to/agent-team
```

Then open the target project in Claude Code and run `/agent-team init`. Agent types load on the next session start.

## Update
```bash
cd ~/.claude/skills/agent-team && git pull
```
Projects already bootstrapped keep their generated files; use `/agent-team upgrade <role>` to re-render a role from the newer templates (a `.bak` is kept).

## Layout
```
SKILL.md                  entry point (/agent-team init | add | status | upgrade)
scripts/render.py         deterministic renderer + frontmatter checker (--check)
templates/agents/*.md     16 generic role templates ({{PLACEHOLDERS}})
templates/commands/*.md   10 pipeline commands
templates/docs/           context file, team chart, learnings, backlog templates
templates/partials/       shared expert protocol
reference/roles.md        roles, profiles, config schema
.claude-plugin/           plugin + marketplace manifests
```

## Moving a generated team to another machine
The team lives in the project's `.claude/` (agents, commands, `agent-team.json`, `agent-memory/`) and its docs folder — commit both. Generated paths are relative to the project root, so cloning the repo(s) in the same folder layout is all that is needed; the context file documents the required layout.

## ภาษาไทย
ติดตั้งบนเครื่องใหม่: `git clone <url> ~/.claude/skills/agent-team` แล้วเปิดโปรเจกต์ใน Claude Code พิมพ์ `/agent-team init` ตอบคำถาม 4 ข้อ ระบบจะสำรวจโค้ดจริงและสร้างทีมให้ เปิด session ใหม่หนึ่งครั้งเพื่อโหลด agent ทีมที่สร้างแล้วอยู่ใน `.claude/` ของโปรเจกต์ commit ไปกับ repo ได้เลย
