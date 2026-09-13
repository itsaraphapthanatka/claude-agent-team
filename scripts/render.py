#!/usr/bin/env python3
"""Render an agent team into a project from templates + config.
Usage: render.py --config <agent-team.json> [--only <role>] [--force] [--check] [--out <project_root>]
"""
import argparse, json, os, re, sys, datetime, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
T = HERE / "templates"
HEAVY = {"architect", "security-engineer", "code-reviewer", "backend-dev", "e2e-tester"}
PROFILES = {
    "max":      {"heavy": ("fable", "max"),   "other": ("fable", "xhigh"), "light": ("fable", "xhigh")},
    "balanced": {"heavy": ("opus", "high"),   "other": ("sonnet", "high"), "light": ("sonnet", "high")},
    "economy":  {"heavy": ("sonnet", "medium"), "other": ("sonnet", "medium"), "light": ("haiku", "medium")},
}
LIGHT = {"mobile-tester", "web-tester", "tech-writer"}
DEFAULT_SKILLS = {
    "architect": ["scrutinize"], "code-reviewer": ["scrutinize"],
    "backend-dev": ["debug-mantra"], "mobile-dev": ["debug-mantra"], "web-dev": ["debug-mantra"], "bug-triager": ["debug-mantra"],
    "ux-designer": ["artifact-design"], "ui-designer": ["artifact-design"], "tech-writer": ["post-mortem"],
}
CATEGORY = {
    "product-manager": "think", "architect": "think", "ux-designer": "think", "ui-designer": "think", "tech-writer": "think",
    "backend-dev": "build", "mobile-dev": "build", "web-dev": "build", "devops-engineer": "build", "test-engineer": "build",
    "api-tester": "adversarial", "e2e-tester": "adversarial", "mobile-tester": "adversarial", "web-tester": "adversarial",
    "code-reviewer": "adversarial", "bug-triager": "adversarial", "security-engineer": "adversarial",
}
CRITIC = {"build": "code reviewer and the QA team", "adversarial": "engineer who wrote the code", "think": "CTO who has to pay for it"}
VALID_MODELS = {"fable", "opus", "sonnet", "haiku", "inherit"}
VALID_EFFORT = {"low", "medium", "high", "xhigh", "max"}

def skill_exists(name):
    for base in (pathlib.Path.home() / ".claude/skills", pathlib.Path.cwd() / ".claude/skills"):
        if (base / name / "SKILL.md").exists():
            return True
    return False

def yaml_quote(s):
    return '"' + s.replace('"', "'") + '"'

def model_effort(role, cfg):
    prof = PROFILES[cfg.get("profile", "balanced")]
    tier = "heavy" if role in HEAVY else ("light" if role in LIGHT else "other")
    model, effort = prof[tier]
    # top-level "model" swaps the model for every role while keeping the profile's
    # effort tiers. Useful when one model runs out of quota but you still want the
    # max-effort setup, e.g. {"profile": "max", "model": "opus"}.
    model = cfg.get("model", model)
    ov = cfg.get("overrides", {}).get(role, {})
    return ov.get("model", model), ov.get("effort", effort)

def render_text(text, vars_):
    for k, v in vars_.items():
        text = text.replace("{{%s}}" % k, v)
    return text

def protocol(role, cfg, vars_):
    cat = CATEGORY[role]
    common = (T / "partials" / "expert-protocol.md").read_text()
    extra = (T / "partials" / f"protocol-{cat}.md").read_text()
    return render_text(common + "\n" + extra, {**vars_, "ROLE": role.replace("-", " "), "ROLE_SLUG": role, "CRITIC": CRITIC[cat]})

def render_agent(role, cfg, vars_):
    src = T / "agents" / f"{role}.md"
    if not src.exists():
        sys.exit(f"unknown role: {role}")
    text = src.read_text()
    model, effort = model_effort(role, cfg)
    skills = cfg.get("skills", {}).get(role, DEFAULT_SKILLS.get(role, []))
    skills = [s for s in skills if skill_exists(s)]
    skills_block = ("skills:\n" + "".join(f"  - {s}\n" for s in skills)) if skills else ""
    specifics = cfg.get("specifics", {}).get(role, "").strip()
    spec_block = f"# Project specifics (verified for {cfg['project']})\n\n{specifics}\n" if specifics else ""
    extra_tools = cfg.get("tools_extra", {}).get(role, [])
    text = render_text(text, {**vars_, "MODEL": model, "EFFORT": effort, "SKILLS_BLOCK": skills_block,
                              "SPECIFICS": spec_block, "PROTOCOL": protocol(role, cfg, vars_)})
    # tools_extra: append to tools line
    if extra_tools:
        text = re.sub(r"^tools: (.*)$", lambda m: "tools: " + m.group(1) + ", " + ", ".join(t for t in extra_tools if t not in m.group(1)), text, count=1, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def check_frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return f"{path.name}: no frontmatter"
    fm = m.group(1)
    problems = []
    kv = dict(re.findall(r"^([a-zA-Z_-]+):\s*(.*)$", fm, re.M))
    if path.parent.name == "agents":
        if kv.get("name") != path.stem: problems.append("name != filename")
        d = kv.get("description", "")
        if not d.startswith('"') and (" #" in d or ": " in d): problems.append("description has YAML hazard (' #' or ': ') and is not quoted")
        if kv.get("model") not in VALID_MODELS: problems.append(f"model={kv.get('model')}")
        if "effort" in kv and kv["effort"] not in VALID_EFFORT: problems.append(f"effort={kv['effort']}")
    if "{{" in text: problems.append("unrendered placeholder")
    return f"{path.name}: {', '.join(problems)}" if problems else None

def write(path, content, force, log):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        log.append(f"SKIP  {path} (exists; use --force)"); return
    if path.exists() and force:
        shutil.copy(path, str(path) + ".bak")
    path.write_text(content)
    log.append(f"WROTE {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--only")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    root = pathlib.Path(a.out or cfg["project_root"])
    docs = pathlib.Path(cfg.get("docs_dir") or root / "docs")
    lang = cfg.get("report_language", "English")
    ctx_name = cfg.get("context_file", "PROJECT-CONTEXT.md")
    # Paths written into agents are RELATIVE to project_root by default (portable across machines/users);
    # set "absolute_paths": true in the config to keep absolute paths.
    if cfg.get("absolute_paths"):
        P = lambda x: str(x)
    else:
        P = lambda x: os.path.relpath(str(x), str(root)) if os.path.isabs(str(x)) else str(x)
    vars_ = {
        "PROJECT": cfg["project"], "PROJECT_ROOT": P(root) if cfg.get("absolute_paths") else ".", "DOCS_DIR": P(docs),
        "CONTEXT_PATH": P(docs / ctx_name), "LEARNINGS_PATH": P(docs / "LEARNINGS.md"),
        "BACKLOG_PATH": P(docs / "product" / "BACKLOG.md"), "TEAM_PATH": P(docs / "TEAM.md"),
        "MEMORY_ROOT": ".claude/agent-memory" if not cfg.get("absolute_paths") else str(root / ".claude" / "agent-memory"), "LANG": lang,
        "LANG_RULE": f"Reports and documents addressed to the owner are written in {lang}; code identifiers, paths, commands, and HTTP details stay in English.",
        "DATE": datetime.date.today().isoformat(),
    }
    if a.check:
        probs = [p for p in (check_frontmatter(f) for f in sorted((root / ".claude/agents").glob("*.md"))) if p]
        probs += [p for p in (check_frontmatter(f) for f in sorted((root / ".claude/commands").glob("*.md"))) if p]
        print("\n".join(probs) if probs else f"OK: {len(list((root/'.claude/agents').glob('*.md')))} agents, {len(list((root/'.claude/commands').glob('*.md')))} commands, no frontmatter problems")
        sys.exit(1 if probs else 0)
    roles = [a.only] if a.only else cfg["roles"]
    log = []
    for role in roles:
        write(root / ".claude/agents" / f"{role}.md", render_agent(role, cfg, vars_), a.force, log)
    if not a.only:
        for src in sorted((T / "commands").glob("*.md")):
            # skip pipelines whose roles are absent
            need = {"test-all": {"api-tester", "e2e-tester", "mobile-tester", "web-tester"}, "security-audit": {"security-engineer"},
                    "release": {"devops-engineer", "tech-writer"}, "prd": {"product-manager"}, "adr": {"architect"}, "review": {"code-reviewer"}}
            if src.stem in need and not (need[src.stem] & set(cfg["roles"])):
                log.append(f"SKIP  command {src.stem} (no matching roles)"); continue
            text = render_text(src.read_text(), {**vars_, "ROLES": ", ".join(cfg["roles"]),
                                                  "TESTERS": ", ".join(r for r in cfg["roles"] if r.endswith("-tester"))})
            write(root / ".claude/commands" / src.name, text, a.force, log)
        repo_rows = "\n".join(f"| {r['name']} | `{P(r['path'])}` | {r.get('stack','TODO')} | {' · '.join('`'+c+'`' for c in r.get('checks', [])) or 'TODO'} |" for r in cfg.get("repos", []))
        role_rows = "\n".join(f"| `{r}` | {CATEGORY[r]} | {model_effort(r, cfg)[0]} / {model_effort(r, cfg)[1]} |" for r in cfg["roles"])
        dvars = {**vars_, "REPO_TABLE": repo_rows or "| TODO | | | |", "ROLE_TABLE": role_rows, "PROFILE": cfg.get("profile", "balanced")}
        for src in sorted((T / "docs").rglob("*.md")):
            rel = src.relative_to(T / "docs")
            if rel.name == "PROJECT-CONTEXT.md": rel = rel.with_name(ctx_name)
            write(docs / rel, render_text(src.read_text(), dvars), a.force, log)
        (root / ".claude/agent-memory").mkdir(parents=True, exist_ok=True)
    print("\n".join(log))
    probs = [p for p in (check_frontmatter(root / ".claude/agents" / f"{r}.md") for r in roles) if p]
    print("CHECK:", "; ".join(probs) if probs else "frontmatter OK")

if __name__ == "__main__":
    main()
