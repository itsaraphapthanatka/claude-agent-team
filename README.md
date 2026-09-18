# agent-team — a software company of Claude Code agents, for any project

`/agent-team init` explores the current project, asks four questions (profile, roles, report language, docs location), then generates a team of subagents (`.claude/agents/`), pipeline commands (`.claude/commands/`: `/feature`, `/fix`, `/test-all`, `/prd`, `/adr`, `/security-audit`, `/release`, `/standup`, `/review`, `/team`) and a shared docs folder (`PROJECT-CONTEXT.md`, `TEAM.md`, `LEARNINGS.md`, `product/BACKLOG.md`) — all grounded in that project's real code. Every agent reads the context file and its own persistent memory first, follows an expert protocol (plan → verify → self-review → leave lessons), and reports in your language.

Roles: product-manager · architect · ux-designer · ui-designer · backend-dev · mobile-dev · web-dev · test-engineer · api-tester · e2e-tester · mobile-tester · web-tester · code-reviewer · bug-triager · security-engineer · devops-engineer · tech-writer. Profiles: `max` (fable/max), `balanced` (opus+sonnet), `economy` (sonnet+haiku). Details: `reference/roles.md`.

## Install on another machine (pick one)

**A. As a personal skill (simplest)** — available in every project on that machine:
```bash
git clone https://github.com/itsaraphapthanatka/claude-agent-team.git ~/.claude/skills/agent-team
```

**B. As a plugin from this repo (also works as a marketplace)** — inside Claude Code:
```
/plugin marketplace add itsaraphapthanatka/claude-agent-team
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
Projects already bootstrapped keep their generated files; use `/agent-team upgrade <role>` to re-render one role, or `/agent-team upgrade all` for every role plus the pipeline commands (a `.bak` is kept). Neither touches the hand-filled docs — only an explicit `render.py --scope docs` rewrites those.

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

## Optional skills the team picks up
Roles preload a skill only when it exists on the machine (`~/.claude/skills`, the project's `.claude/skills`, or an installed plugin); otherwise the reference degrades to a no-op.

| skill | roles | install |
|---|---|---|
| [impeccable](https://impeccable.style/) | ux-designer, ui-designer, web-dev, mobile-dev | `npx impeccable install --global --providers=claude-code` |
| scrutinize | architect, code-reviewer | — |
| debug-mantra | backend-dev, mobile-dev, web-dev, bug-triager | — |
| post-mortem | tech-writer | — |

With `impeccable` installed, designers run its `audit` / `critique` / `shape` before writing a spec and front-end devs run `polish` on user-visible changes; its `DESIGN.md` and the ui-designer's `DESIGN-SYSTEM.md` are reconciled rather than kept as two sources of truth.

## Moving a generated team to another machine
The team lives in the project's `.claude/` (agents, commands, `agent-team.json`, `agent-memory/`) and its docs folder — commit both. Generated paths are relative to the project root, so cloning the repo(s) in the same folder layout is all that is needed; the context file documents the required layout.

## ภาษาไทย
ติดตั้งบนเครื่องใหม่: `git clone https://github.com/itsaraphapthanatka/claude-agent-team.git ~/.claude/skills/agent-team` แล้วเปิดโปรเจกต์ใน Claude Code พิมพ์ `/agent-team init` ตอบคำถาม 4 ข้อ ระบบจะสำรวจโค้ดจริงและสร้างทีมให้ เปิด session ใหม่หนึ่งครั้งเพื่อโหลด agent ทีมที่สร้างแล้วอยู่ใน `.claude/` ของโปรเจกต์ commit ไปกับ repo ได้เลย
