r"""Regression tests for scripts/render.py.

Two bugs made the skill unusable on a Thai-locale Windows machine, and both were
invisible on a UTF-8 machine, which is why they shipped:

1. **Default encoding.** Every read/write used the locale encoding. With
   `locale.getpreferredencoding(False) == "cp874"` the very first template read raised
   `UnicodeDecodeError: 'charmap' codec can't decode byte 0x81` — the script could not
   read its own `templates/agents/architect.md`. The workaround was to remember to set
   `PYTHONUTF8=1` before every run.

2. **Backslash paths.** `os.path.relpath` returns `docs\PROJECT-CONTEXT.md` on Windows.
   That string is written into every rendered agent as a markdown link and as an argument
   the agent passes to its tools; neither accepts backslashes.

The encoding test uses `-X warn_default_encoding -W error::EncodingWarning`, which turns
any encoding-less `open()`/`read_text()`/`write_text()` into a hard error on every OS —
so it reproduces the Windows-only bug on a UTF-8 CI machine too.

Run: python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[1]
RENDER = REPO / "scripts" / "render.py"
ROLES = ["architect", "backend-dev", "code-reviewer"]


class _Rendered(unittest.TestCase):
    """Render a throwaway project once per test class."""

    extra_args: tuple[str, ...] = ()
    config_extra: dict = {}

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = pathlib.Path(tempfile.mkdtemp(prefix="agent-team-test-")).resolve()
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        cls.project = cls.tmp / "proj"
        (cls.project / "docs").mkdir(parents=True)
        cfg = {
            "project": "demo",
            "project_root": str(cls.project),
            "docs_dir": str(cls.project / "docs"),
            "profile": "balanced",
            "roles": ROLES,
            "repos": [{"name": "app", "path": str(cls.project), "stack": "python"}],
            **cls.config_extra,
        }
        cls.config = cls.tmp / "agent-team.json"
        cls.config.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        cls.result = cls._render(*cls.extra_args)

    @classmethod
    def _render(cls, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-X", "warn_default_encoding",
             "-W", "error::EncodingWarning",
             str(RENDER), "--config", str(cls.config), *extra],
            capture_output=True, text=True, encoding="utf-8", errors="replace")

    @property
    def agents(self) -> list[pathlib.Path]:
        return sorted((self.project / ".claude" / "agents").glob("*.md"))


class TestItRunsWithoutRelyingOnTheLocaleEncoding(_Rendered):

    def test_it_exits_zero(self):
        self.assertEqual(self.result.returncode, 0,
                         f"stdout:\n{self.result.stdout}\nstderr:\n{self.result.stderr}")

    def test_no_read_or_write_used_the_default_encoding(self):
        # EncodingWarning is raised as an error above, so it can only appear here if a
        # call slipped through without encoding= — the original bug, exactly.
        self.assertNotIn("EncodingWarning", self.result.stderr)

    def test_it_wrote_one_file_per_role(self):
        self.assertEqual([p.stem for p in self.agents], sorted(ROLES))

    def test_every_file_it_wrote_is_valid_utf8(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                path.read_bytes().decode("utf-8")   # raises if it is not

    def test_the_non_ascii_text_in_the_templates_survived(self):
        # cp874 round-tripping mangles these silently instead of raising
        source = (REPO / "templates" / "agents" / "architect.md").read_text(encoding="utf-8")
        marks = {c for c in source if ord(c) > 127}
        self.assertTrue(marks, "template has no non-ASCII left to check")
        rendered = (self.project / ".claude" / "agents" / "architect.md").read_text(
            encoding="utf-8")
        self.assertTrue(marks & set(rendered),
                        "none of the template's non-ASCII characters reached the output")


class TestPathsAreForwardSlashOnly(_Rendered):

    def test_no_rendered_agent_contains_a_backslash_path(self):
        for path in self.agents:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("\\", text,
                                 "backslash in a rendered agent — markdown links and tool "
                                 "arguments both break on it")

    def test_the_context_path_is_written_with_slashes(self):
        text = (self.project / ".claude" / "agents" / "architect.md").read_text(
            encoding="utf-8")
        self.assertIn("docs/PROJECT-CONTEXT.md", text)

    def test_the_docs_it_wrote_use_slashes_too(self):
        for path in sorted((self.project / "docs").rglob("*.md")):
            with self.subTest(path=path.name):
                self.assertNotIn("\\", path.read_text(encoding="utf-8"))


class TestAbsolutePathsModeIsNormalisedToo(_Rendered):
    """`absolute_paths: true` used to skip the relpath call — and the normalisation."""

    config_extra = {"absolute_paths": True}

    def test_it_exits_zero(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)

    def test_absolute_paths_also_come_out_with_slashes(self):
        text = (self.project / ".claude" / "agents" / "architect.md").read_text(
            encoding="utf-8")
        self.assertNotIn("\\", text)
        # still absolute, just spelled portably
        self.assertIn(str(self.project).replace("\\", "/"), text)


class TestCheckModeAlsoReadsAsUtf8(_Rendered):

    def test_check_passes_on_what_it_just_rendered(self):
        out = self._render("--check")
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertNotIn("EncodingWarning", out.stderr)


if __name__ == "__main__":
    unittest.main()
