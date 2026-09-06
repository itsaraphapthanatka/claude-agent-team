---
description: Full product pipeline for a new feature — PRD → design → scrutiny → checkpoint → devs in parallel → review + security → tests → docs
argument-hint: <feature idea or PRD path>
---
You are the engineering manager running {{PROJECT}}'s feature pipeline for: **$ARGUMENTS**

Read `{{TEAM_PATH}}`, `{{CONTEXT_PATH}}`, and `{{LEARNINGS_PATH}}` first. Use the Agent tool for every role below (if a role's subagent type is not loaded in this session, use `general-purpose` and tell it to `cat` its file under `.claude/agents/` and adopt it). Roles available in this project: {{ROLES}}.

1. **Product.** If `$ARGUMENTS` is not already a PRD path, run `product-manager` to write the PRD. Then run `architect` on that PRD to write `{{DOCS_DIR}}/design/DESIGN-<slug>.md`, and in parallel `ux-designer` if screens change.
2. **Scrutiny.** Invoke the `scrutinize` skill (if installed) on the design and PRD: simpler approach? every acceptance criterion covered? Feed material objections back to `architect` once; record the outcome in the design doc.
3. **Checkpoint.** Summarise in {{LANG}}: what will be built, per-repo scope, schema/migration changes, risks, estimated files. Use AskUserQuestion to confirm **proceed / change scope / stop** before touching code. Do not skip this.
4. **Build.** Launch the owning devs **in parallel**, one Agent call per repo, each given the PRD, design, and UX spec paths and told to stay in scope. Server first only if clients need an endpoint shape the design does not already fix.
5. **Verify.** In parallel: `code-reviewer` per touched repo, `security-engineer` scoped to the diff whenever it touches auth, money, personal data, uploads, or settings, and `test-engineer` for regression/feature tests. Blocking findings go back to the owning dev (one round), then run the relevant testers ({{TESTERS}}) for the touched areas.
6. **Docs.** `tech-writer` updates README/runbooks/context file if behaviour or setup changed, appends to `{{DOCS_DIR}}/releases/UNRELEASED.md`, adds lessons to `{{LEARNINGS_PATH}}`.
7. **Report** in {{LANG}}: what shipped (files per repo), how verified, review/security findings fixed vs deferred, migrations the owner must run, manual test steps, what was left out. No commits unless the user asked.
