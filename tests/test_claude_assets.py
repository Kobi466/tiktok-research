"""Tests for Claude Code Skills and Research Agents (Task 7).

Verifies frontmatter, required sections, vocabulary consistency,
structured output contracts, and strict safety rules across all 9 assets.
"""

from __future__ import annotations

from pathlib import Path
import re
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_SKILLS = [
    "market-research",
    "product-research",
    "competitor-analysis",
    "content-strategy",
    "research-audit",
]

EXPECTED_AGENTS = [
    "market-analyst",
    "product-researcher",
    "competitor-researcher",
    "research-auditor",
]

CANONICAL_EVIDENCE_TYPES = {
    "direct_source",
    "calculated",
    "estimate",
    "hypothesis",
}

CANONICAL_CONFIDENCE_LEVELS = {
    "high",
    "medium",
    "low",
    "unverified",
}

AGENT_REQUIRED_HEADINGS = [
    "## Nhiệm vụ",
    "## Phạm vi",
    "## Công cụ được phép",
    "## Giới hạn",
    "## Định dạng đầu ra",
]

SAFETY_REQUIRED_TERMS = [
    "không bịa",
    "không suy ra doanh số",
    "nguồn",
    "confidence",
    "limitations",
]

PROHIBITED_PATTERNS = [
    r"bypass\s+login",
    r"vượt\s+qua\s+đăng\s+nhập",
    r"bypass\s+captcha",
    r"vượt\s+qua\s+captcha",
    r"giải\s+captcha",
    r"evade\s+anti-bot",
    r"tránh\s+anti-bot",
    r"private\s+api",
    r"crack\s+token",
    r"bẻ\s+khóa\s+token",
    r"buy\s+followers",
    r"mua\s+follower",
    r"scrape\s+private",
    r"tài\s+khoản\s+riêng\s+tư",
]

SKILL_CANONICAL_FIELDS = [
    "finding",
    "source_url",
    "accessed_at",
    "published_at",
    "observed_data",
    "collection_method",
    "confidence",
    "limitations",
]

ID_PREFIXES = [
    "SRC-",
    "OBS-",
    "PRD-",
    "CMP-",
    "VID-",
    "FND-",
    "HYP-",
    "AUD-",
]


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from markdown text without third-party dependencies."""
    if not content.startswith("---"):
        raise ValueError("File does not start with YAML frontmatter delimiters ('---')")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("File does not have matching closing YAML frontmatter delimiter ('---')")

    fm_text = parts[1].strip()
    body = parts[2]

    data: dict[str, str] = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip().strip("\"'")

    return data, body


class TestClaudeAssets(unittest.TestCase):
    """Test suite for Claude Code Skills and Agents."""

    def test_all_skills_exist_and_have_valid_frontmatter(self) -> None:
        """Verifies all 5 skills exist in .claude/skills/<name>/SKILL.md with valid frontmatter."""
        skills_dir = PROJECT_ROOT / ".claude" / "skills"
        self.assertTrue(skills_dir.is_dir(), f"Skills directory not found: {skills_dir}")

        for skill_name in EXPECTED_SKILLS:
            skill_file = skills_dir / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"Skill file not found: {skill_file}")

            content = skill_file.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(content)

            self.assertIn("name", frontmatter, f"{skill_file} missing 'name' in frontmatter")
            self.assertEqual(
                frontmatter["name"],
                skill_name,
                f"Skill name mismatch: expected '{skill_name}', got '{frontmatter.get('name')}'",
            )
            self.assertIn(
                "description", frontmatter, f"{skill_file} missing 'description' in frontmatter"
            )
            self.assertTrue(
                len(frontmatter["description"]) > 10,
                f"Skill '{skill_name}' description must be non-empty and substantive",
            )
            self.assertTrue(
                len(body.strip()) > 100, f"Skill '{skill_name}' body must be substantive"
            )

    def test_all_agents_exist_and_have_valid_frontmatter(self) -> None:
        """Verifies all 4 agents exist in .claude/agents/<name>.md with valid frontmatter."""
        agents_dir = PROJECT_ROOT / ".claude" / "agents"
        self.assertTrue(agents_dir.is_dir(), f"Agents directory not found: {agents_dir}")

        for agent_name in EXPECTED_AGENTS:
            agent_file = agents_dir / f"{agent_name}.md"
            self.assertTrue(agent_file.is_file(), f"Agent file not found: {agent_file}")

            content = agent_file.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(content)

            self.assertIn("name", frontmatter, f"{agent_file} missing 'name' in frontmatter")
            self.assertEqual(
                frontmatter["name"],
                agent_name,
                f"Agent name mismatch: expected '{agent_name}', got '{frontmatter.get('name')}'",
            )
            self.assertIn(
                "description", frontmatter, f"{agent_file} missing 'description' in frontmatter"
            )
            self.assertTrue(
                len(frontmatter["description"]) > 10,
                f"Agent '{agent_name}' description must be non-empty and substantive",
            )
            self.assertTrue(
                len(body.strip()) > 100, f"Agent '{agent_name}' body must be substantive"
            )

    def test_agent_required_sections_present(self) -> None:
        """Verifies every agent contains all 5 required headings in exact level-2 syntax."""
        agents_dir = PROJECT_ROOT / ".claude" / "agents"

        for agent_name in EXPECTED_AGENTS:
            agent_file = agents_dir / f"{agent_name}.md"
            self.assertTrue(agent_file.is_file(), f"Agent file not found: {agent_file}")

            content = agent_file.read_text(encoding="utf-8")
            _, body = parse_frontmatter(content)

            for heading in AGENT_REQUIRED_HEADINGS:
                self.assertIn(
                    heading,
                    body,
                    f"Agent '{agent_name}' is missing required section heading: '{heading}'",
                )

    def test_safety_and_no_sales_inference_rules_in_all_assets(self) -> None:
        """Verifies all 9 files contain required safety terms."""
        all_files: list[Path] = []
        for s in EXPECTED_SKILLS:
            all_files.append(PROJECT_ROOT / ".claude" / "skills" / s / "SKILL.md")
        for a in EXPECTED_AGENTS:
            all_files.append(PROJECT_ROOT / ".claude" / "agents" / f"{a}.md")

        for file_path in all_files:
            self.assertTrue(file_path.is_file(), f"Asset file not found: {file_path}")
            content = file_path.read_text(encoding="utf-8").lower()

            for term in SAFETY_REQUIRED_TERMS:
                self.assertIn(
                    term.lower(),
                    content,
                    f"Asset '{file_path.name}' in {file_path.parent.name} missing safety term: '{term}'",
                )

    def test_prohibited_access_and_bypass_language_absent(self) -> None:
        """Verifies no asset contains words advocating bypassing login, CAPTCHA, anti-bot, etc."""
        all_files: list[Path] = []
        for s in EXPECTED_SKILLS:
            all_files.append(PROJECT_ROOT / ".claude" / "skills" / s / "SKILL.md")
        for a in EXPECTED_AGENTS:
            all_files.append(PROJECT_ROOT / ".claude" / "agents" / f"{a}.md")

        for file_path in all_files:
            self.assertTrue(file_path.is_file(), f"Asset file not found: {file_path}")
            content = file_path.read_text(encoding="utf-8")

            for pattern in PROHIBITED_PATTERNS:
                match = re.search(pattern, content, re.IGNORECASE)
                self.assertIsNone(
                    match,
                    f"Asset '{file_path.name}' contains prohibited bypass language: '{match.group(0) if match else ''}'",
                )

    def test_evidence_vocabulary_consistency(self) -> None:
        """Verifies canonical evidence types are present and respected across all assets."""
        all_files: list[Path] = []
        for s in EXPECTED_SKILLS:
            all_files.append(PROJECT_ROOT / ".claude" / "skills" / s / "SKILL.md")
        for a in EXPECTED_AGENTS:
            all_files.append(PROJECT_ROOT / ".claude" / "agents" / f"{a}.md")

        for file_path in all_files:
            self.assertTrue(file_path.is_file(), f"Asset file not found: {file_path}")
            content = file_path.read_text(encoding="utf-8")

            for ev_type in CANONICAL_EVIDENCE_TYPES:
                self.assertIn(
                    ev_type,
                    content,
                    f"Asset '{file_path.name}' missing canonical evidence type: '{ev_type}'",
                )

    def test_skill_required_sections_and_fields(self) -> None:
        """Verifies skills include required guidance sections, user inputs, fields, and 'Thiếu dữ liệu'."""
        skills_dir = PROJECT_ROOT / ".claude" / "skills"

        required_inputs = [
            "market",
            "geography",
            "category",
            "target audience",
            "date range",
            "research question",
        ]

        for skill_name in EXPECTED_SKILLS:
            skill_file = skills_dir / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"Skill file not found: {skill_file}")
            content = skill_file.read_text(encoding="utf-8")
            content_lower = content.lower()

            # When to use / not use
            self.assertTrue(
                "khi nào" in content_lower and "không" in content_lower,
                f"Skill '{skill_name}' missing when to use / when not to use guidance",
            )

            # User inputs
            for inp in required_inputs:
                self.assertIn(
                    inp,
                    content_lower,
                    f"Skill '{skill_name}' missing required input specification: '{inp}'",
                )

            # Reusable output contract fields
            for field in SKILL_CANONICAL_FIELDS:
                self.assertIn(
                    field,
                    content,
                    f"Skill '{skill_name}' missing canonical output field: '{field}'",
                )

            # Dedicated Thiếu dữ liệu section
            self.assertTrue(
                "thiếu dữ liệu" in content_lower or "thieu du lieu" in content_lower,
                f"Skill '{skill_name}' missing dedicated 'Thiếu dữ liệu' section",
            )

    def test_agent_structured_output_contract_and_prefixes(self) -> None:
        """Verifies agents define structured outputs with canonical sections and proposed ID patterns."""
        agents_dir = PROJECT_ROOT / ".claude" / "agents"

        required_output_keys = [
            "sources",
            "observations",
            "findings",
            "hypotheses",
            "limitations",
            "tool_status",
        ]

        for agent_name in EXPECTED_AGENTS:
            agent_file = agents_dir / f"{agent_name}.md"
            self.assertTrue(agent_file.is_file(), f"Agent file not found: {agent_file}")
            content = agent_file.read_text(encoding="utf-8")

            for key in required_output_keys:
                self.assertIn(
                    key,
                    content,
                    f"Agent '{agent_name}' output contract missing structured key: '{key}'",
                )

            self.assertIn(
                "not_available",
                content,
                f"Agent '{agent_name}' output contract missing 'not_available' fallback for tool_status",
            )

            # Check ID prefixes
            for prefix in ID_PREFIXES:
                self.assertIn(
                    prefix,
                    content,
                    f"Agent '{agent_name}' missing reference to canonical ID prefix: '{prefix}'",
                )

        # research-auditor specific requirements
        auditor_file = agents_dir / "research-auditor.md"
        auditor_content = auditor_file.read_text(encoding="utf-8")
        self.assertIn("audit_findings", auditor_content)
        self.assertIn("pass", auditor_content)
        self.assertIn("warning", auditor_content)
        self.assertIn("fail", auditor_content)

    def test_frontmatter_line_count(self) -> None:
        """Verifies frontmatter inspection returns exactly 2 lines matching ^(name|description): for each asset."""
        all_files: list[Path] = []
        for s in EXPECTED_SKILLS:
            all_files.append(PROJECT_ROOT / ".claude" / "skills" / s / "SKILL.md")
        for a in EXPECTED_AGENTS:
            all_files.append(PROJECT_ROOT / ".claude" / "agents" / f"{a}.md")

        name_desc_pattern = re.compile(r"^(name|description):")

        for file_path in all_files:
            self.assertTrue(file_path.is_file(), f"Asset file not found: {file_path}")
            lines = file_path.read_text(encoding="utf-8").splitlines()
            matches = [line for line in lines if name_desc_pattern.match(line)]
            self.assertEqual(
                len(matches),
                2,
                f"Asset '{file_path}' has {len(matches)} lines matching ^(name|description): (expected exactly 2): {matches}",
            )


if __name__ == "__main__":
    unittest.main()
