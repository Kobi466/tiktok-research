import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_GITIGNORE_PATTERNS = {
    ".venv/",
    ".env",
    ".env.*",
    "credentials/",
    "secrets/",
    "__pycache__/",
    "*.py[cod]",
    ".pytest_cache/",
    ".mypy_cache/",
    "data/raw/private/",
    "*.sqlite-wal",
    "*.sqlite-shm",
}


class ProjectLayoutTests(unittest.TestCase):
    def test_gitignore_contains_required_safety_patterns(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertTrue(REQUIRED_GITIGNORE_PATTERNS.issubset(set(gitignore)))

    def test_readme_contains_setup_and_no_sales_language(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for required_text in (
            ".venv/bin/python",
            "python3 -m venv .venv",
            "Không suy ra doanh số",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, readme)


if __name__ == "__main__":
    unittest.main()
