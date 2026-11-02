# Brand assets

Listing and README artwork for the `agent-team` skill.

| file | use |
|---|---|
| `logo.svg` | source of the mark — edit this, re-export the PNGs |
| `logo-512.png`, `logo-1024.png` | marketplace / repo avatar |
| `01-overview.png` | the 17 roles grouped by category |
| `02-real-output.png` | what `/agent-team init` writes into a project |
| `03-generated-agent.png` | a rendered `code-reviewer.md` |
| `04-pipelines.png` | `/feature` and `/fix` flows |

Palette: ink `#15171C`, paper `#F6F2E9`, amber `#D98A2B` (the context file),
sand `#EBD9A0` (think), teal `#5FB3A1` (build), clay `#D98A7A` (adversarial).

Screenshots are 2560×1600, rendered from `brand/*.html` sources with headless
Chrome at `--force-device-scale-factor=2`. Their contents come from a real
`render.py` run, not mock-ups.

Re-export:

```bash
for n in 01-overview 02-real-output 03-generated-agent 04-pipelines; do
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
    --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=1280,800 --screenshot="brand/$n.png" "file://$PWD/brand/$n.html"
done
```
