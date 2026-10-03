# TikTok Affiliate Research System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng hệ thống nghiên cứu TikTok Affiliate Việt Nam có Skills/Agents tái sử dụng, dữ liệu có provenance, validator, SQLite index và báo cáo Markdown; mọi script chạy trong `./.venv` bằng Python standard library.

**Architecture:** Dùng CSV/JSON/Markdown làm định dạng trao đổi chính, với `config/field-definitions.json` là nguồn schema và SQLite là chỉ mục có thể tái tạo. Các script nhỏ chia theo trách nhiệm: khởi tạo workspace, validate/cross-reference, phát hiện trùng, xây index và xuất báo cáo; Skills/Agents chỉ điều phối quy trình và không giả định quyền truy cập web/TikTok/API. Dữ liệu raw không bị sửa, còn báo cáo chỉ đưa phát hiện đã có liên kết bằng chứng và ghi rõ giới hạn.

**Tech Stack:** Python 3.14 standard library (`csv`, `json`, `sqlite3`, `urllib.parse`, `hashlib`, `datetime`, `argparse`, `unittest`), SQLite, CSV, JSON, Markdown, Claude Code Skills/Agents, Exa/Playwright chỉ khi công cụ thực tế được cấp.

**Spec:** `docs/superpowers/specs/2026-10-02-tiktok-affiliate-research-system-design.md`

## Global Constraints

- Workspace dùng `./.venv`. Không cài package vào Python hệ thống.
- Script và kiểm tra phải chạy qua `.venv/bin/python` sau khi môi trường được tạo.
- Giai đoạn đầu chỉ dùng standard library (`csv`, `json`, `sqlite3`, `urllib`, `hashlib`, `datetime`, `argparse`, `unittest` nếu cần).
- CSV/JSON/Markdown là định dạng dữ liệu chính; SQLite chỉ là lớp chỉ mục/truy vấn cục bộ được tái tạo từ dữ liệu chuẩn hóa.
- Raw evidence được bảo toàn, không sửa trực tiếp.
- Không tạo sản phẩm, giá, hoa hồng, lượt xem hay kết luận mẫu có vẻ như dữ liệu thực.
- Dữ liệu thiếu hoặc chưa xác minh không được tự động biến thành số liệu chắc chắn.
- Không yêu cầu hoặc sử dụng đăng nhập TikTok, cookie, CAPTCHA bypass, private data hay API credential chưa được cấp quyền.
- Không suy ra doanh số, lợi nhuận hoặc hoa hồng của đối thủ từ lượt xem/lượt thích.
- Không tự mua hàng, đăng video, gửi lời mời Affiliate, thay đổi tài khoản hoặc gọi API trả phí.
- Không lưu API key, token, mật khẩu, cookie hoặc thông tin định danh cá nhân vào project.
- Không khởi tạo Git hoặc commit trong kế hoạch này; project hiện chưa là Git repository.
- Trước khi cài package ngoài hoặc kết nối dịch vụ trả phí, phải dừng và xin xác nhận riêng.
- Khi nguồn bị block/partial, phải lưu trạng thái, lý do và thời điểm; không thay thế bằng số liệu đoán.
- Agent nghiên cứu có thể chạy song song chỉ khi nhiệm vụ độc lập; `research-auditor` luôn chạy sau các agent nghiên cứu.

## Review Focus

- **Template/CSV trống hoặc có giá trị `null`:** được coi là schema/template, không bị ingest như dữ liệu nghiên cứu; test thuộc Task 2.
- **Record có URL/ID hợp lệ nhưng thiếu source link, timestamp hoặc evidence metadata:** bị báo lỗi theo từng record và không được coi là audited; test thuộc Task 3.
- **Record `calculated`, `estimate` hoặc `hypothesis`:** phải có method/limitation phù hợp và không xuất hiện trong verified findings nếu chưa được audit; test thuộc Task 3 và Task 6.
- **Hai source khác nhau dùng cùng URL hoặc cùng ID:** được báo duplicate nhưng không tự động xóa/sửa; test thuộc Task 4.
- **Nguồn TikTok/Exa/Playwright không truy cập được:** báo `blocked`/`partial`/`not_available`, tạo danh sách dữ liệu cần bổ sung và vẫn xuất báo cáo trung thực; test thuộc Task 7.

---

## File Map

### Bootstrap, documentation, and tests

- Create: `.gitignore` — loại trừ `.venv/`, secrets, cache, private raw data và bytecode.
- Create: `README.md` — hướng dẫn tiếng Việt cho người mới, lệnh chạy bằng `.venv/bin/python`, data flow và giới hạn an toàn.
- Create: `tests/__init__.py` — package test standard library.
- Create: `tests/test_project_layout.py` — kiểm tra layout, `.gitignore` và không có dependency ngoài.
- Create: `tests/test_research_io.py` — kiểm tra shared I/O và CSV headers.

### Schema and templates

- Create: `config/field-definitions.json` — schema canonical cho các bảng, headers, required fields, enums và foreign keys.
- Create: `config/research-policy.md` — policy về evidence, confidence, provenance, raw data và unsupported claims.
- Create: `config/source-policy.md` — thứ tự ưu tiên nguồn, trạng thái truy cập và giới hạn công cụ.
- Create: `templates/source-record.json` — template metadata nguồn, không phải dữ liệu thật.
- Create: `templates/observation-record.json` — template quan sát.
- Create: `templates/product-record.json` — template sản phẩm.
- Create: `templates/video-record.json` — template video công khai.
- Create: `templates/finding-record.json` — template phát hiện.
- Create: `templates/hypothesis-record.json` — template giả thuyết.
- Create: `templates/research-report.md` — outline báo cáo.
- Create: `templates/audit-report.md` — outline audit report.

### Python scripts and tests

- Create: `scripts/__init__.py` — cho phép import shared modules trong test.
- Create: `scripts/research_io.py` — constants, path resolution, CSV/JSON read-write, UTC timestamp và safe text helpers.
- Create: `scripts/init_research.py` — tạo directories và empty CSVs từ schema, không ghi đè file tồn tại.
- Create: `scripts/validate_records.py` — validate schema, enums, URL, timestamp, cross-references và evidence rules.
- Create: `scripts/deduplicate_sources.py` — phát hiện duplicate source IDs/URLs và xuất report, không xóa.
- Create: `scripts/build_sqlite_index.py` — tạo SQLite từ processed CSVs bằng transaction, rebuild được.
- Create: `scripts/export_research_summary.py` — tạo Markdown summary từ records đã validated, hiển thị limitations và không suy luận mới.
- Create: `tests/test_init_research.py` — test init không ghi đè và tạo headers đúng.
- Create: `tests/test_validate_records.py` — test valid/invalid records, enums, provenance và evidence rules.
- Create: `tests/test_deduplicate_sources.py` — test duplicate IDs/URLs.
- Create: `tests/test_build_sqlite_index.py` — test schema/index rebuild và SQLite row counts.
- Create: `tests/test_export_research_summary.py` — test verified/unverified sections và thiếu dữ liệu.

### Claude Code Skills and Agents

- Create: `.claude/skills/market-research/SKILL.md` — nghiên cứu thị trường và nhu cầu có nguồn.
- Create: `.claude/skills/product-research/SKILL.md` — nghiên cứu sản phẩm, giá, hoa hồng và điều kiện Affiliate có xác minh.
- Create: `.claude/skills/competitor-analysis/SKILL.md` — phân tích public channel/video, hook, CTA và metrics quan sát.
- Create: `.claude/skills/content-strategy/SKILL.md` — chuyển findings thành hypotheses và test plan, không bịa demand.
- Create: `.claude/skills/research-audit/SKILL.md` — kiểm tra provenance, duplicate, dates, evidence và overclaim.
- Create: `.claude/agents/market-analyst.md` — nhiệm vụ, scope, tools và output contract cho market work.
- Create: `.claude/agents/product-researcher.md` — nhiệm vụ, scope, tools và output contract cho product work.
- Create: `.claude/agents/competitor-researcher.md` — nhiệm vụ, scope, tools và output contract cho public content.
- Create: `.claude/agents/research-auditor.md` — audit-only agent, không sửa raw data.
- Create: `tests/test_claude_assets.py` — frontmatter, required sections và safety language.

### Data/report artifacts

- Create: `data/raw/.gitkeep` — giữ raw directory khi chưa có raw data.
- Create: `data/processed/.gitkeep` — giữ processed directory khi chưa có records.
- Create: `reports/.gitkeep` — giữ report directory.
- Generated: `data/processed/*.csv` — tạo bởi `init_research.py`; chỉ headers ban đầu.
- Generated: `data/research.sqlite` — tạo bởi `build_sqlite_index.py`; có thể xóa và rebuild.
- Generated: `.venv/` — tạo bằng `python3 -m venv .venv`; không commit.
- Generated later: `reports/YYYY-MM-DD-smart-home-tiktok-affiliate.md` — chỉ tạo sau khi nguồn công khai được thu thập và audit.

---

### Task 1: Bootstrap the isolated Python workspace and safety boundary

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `tests/__init__.py`
- Create: `tests/test_project_layout.py`

**Interfaces:**
- Produces the project contract used by every later task: commands run from the project root with `.venv/bin/python`, no package installation, and sensitive paths excluded.
- `README.md` must document the exact commands later scripts expose: `init_research.py`, `validate_records.py`, `deduplicate_sources.py`, `build_sqlite_index.py`, and `export_research_summary.py`.

- [ ] **Step 1: Write the failing layout test**

Create `tests/test_project_layout.py` with standard-library `unittest` tests that assert:

```python
class ProjectLayoutTests(unittest.TestCase):
    def test_gitignore_excludes_virtualenv_and_secrets(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for required in (".venv/", ".env", "credentials/", "secrets/", "__pycache__/", "data/raw/private/"):
            self.assertIn(required, text)

    def test_readme_requires_project_python(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(".venv/bin/python", text)
        self.assertIn("python3 -m venv .venv", text)
        self.assertIn("Không suy ra doanh số", text)
```

Use `ROOT = Path(__file__).resolve().parents[1]`. Do not import third-party modules.

- [ ] **Step 2: Run the test and verify it fails**

Run:

```bash
python3 -m unittest tests.test_project_layout -v
```

Expected: FAIL because `.gitignore` and `README.md` do not exist yet.

- [ ] **Step 3: Create the safety files**

Write `.gitignore` with at least:

```gitignore
.venv/
.env
.env.*
credentials/
secrets/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
data/raw/private/
*.sqlite-wal
*.sqlite-shm
```

Write `README.md` in Vietnamese with these sections and exact operational rules:

1. Mục tiêu.
2. Cấu trúc workspace.
3. Tạo và kích hoạt virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   .venv/bin/python --version
   ```
4. Khởi tạo dữ liệu:
   ```bash
   .venv/bin/python scripts/init_research.py --root .
   ```
5. Validate/audit/index/export commands with their `--root`, `--output`, and `--database` flags.
6. Data evidence types: `direct_source`, `calculated`, `estimate`, `hypothesis`.
7. Công cụ web chỉ dùng nguồn công khai; nếu blocked, ghi trạng thái thay vì đoán.
8. Không suy ra doanh số/lợi nhuận từ view/like; không lưu credential.
9. Quy trình nghiên cứu 11 bước from the spec.

- [ ] **Step 4: Create the isolated environment without installing packages**

Run only after the layout files are present:

```bash
python3 -m venv .venv
.venv/bin/python --version
.venv/bin/python -c 'import csv, json, sqlite3, urllib.request, hashlib, datetime, argparse, unittest; print("standard library ready")'
```

Do not run `pip install`, `ensurepip`, npm install, or any external package command.

- [ ] **Step 5: Run the layout test with the project interpreter**

Run:

```bash
.venv/bin/python -m unittest tests.test_project_layout -v
```

Expected: PASS. Also verify the system Python was not modified by comparing the command output to the previously observed interpreter.

- [ ] **Step 6: Record the verification result**

Add a short “Kiểm tra hiện trạng” section to `README.md` stating that the project starts with standard library only and that `.venv/` is generated locally. Do not record secrets, host tokens, or user-level endpoint values.

No commit is possible because the project is not a Git repository.

---

### Task 2: Define the canonical schema, policies, and empty data templates

**Files:**
- Create: `config/field-definitions.json`
- Create: `config/research-policy.md`
- Create: `config/source-policy.md`
- Create: `templates/source-record.json`
- Create: `templates/observation-record.json`
- Create: `templates/product-record.json`
- Create: `templates/video-record.json`
- Create: `templates/finding-record.json`
- Create: `templates/hypothesis-record.json`
- Create: `templates/research-report.md`
- Create: `templates/audit-report.md`
- Create: `scripts/__init__.py`
- Create: `scripts/research_io.py`
- Create: `tests/test_research_io.py`

**Interfaces:**
- `config/field-definitions.json` is the canonical input for all later CSV creation and validation.
- `scripts.research_io.load_definitions(root: Path) -> dict` loads and validates the JSON object.
- `scripts.research_io.table_fields(definitions: dict, table_name: str) -> list[str]` returns ordered fields.
- `scripts.research_io.processed_csv_path(root: Path, table_name: str) -> Path` maps table names to `data/processed/<table>.csv`.
- `scripts.research_io.utc_now() -> str` returns an ISO 8601 UTC timestamp ending in `Z`.
- `scripts.research_io.read_csv_records(path: Path) -> list[dict[str, str]]` and `write_csv_records(path, fields, records)` use UTF-8 and `csv.DictReader`/`DictWriter`.
- `scripts.research_io.write_json(path: Path, value: object)` writes UTF-8 JSON with stable indentation and a final newline.

- [ ] **Step 1: Write the schema-loading tests**

Create tests that assert the schema names and exact ordered fields. The canonical tables are:

```python
EXPECTED_TABLES = {
    "sources": ["source_id", "url", "title", "publisher", "source_type", "accessed_at", "published_at", "access_status", "collection_method", "content_hash", "limitations", "notes"],
    "observations": ["observation_id", "source_id", "entity_type", "entity_id", "attribute", "observed_value", "unit", "observed_at", "published_at", "evidence_excerpt", "collection_method", "confidence", "limitations"],
    "products": ["product_id", "product_name", "category", "seller_name", "product_url", "price_value", "currency", "price_observed_at", "commission_value", "commission_type", "commission_source_id", "customer_problem", "benefits_observed", "video_potential", "competition_notes", "evidence_type", "confidence", "limitations"],
    "competitors": ["competitor_id", "platform", "handle_or_name", "profile_url", "niche", "observed_at", "public_metrics", "metrics_observed_at", "content_patterns", "confidence", "limitations"],
    "videos": ["video_id", "competitor_id", "video_url", "published_at", "observed_at", "views_observed", "likes_observed", "comments_observed", "hook_observed", "story_structure", "product_presentation", "call_to_action", "affiliate_disclosure", "evidence_type", "confidence", "limitations"],
    "findings": ["finding_id", "finding_text", "source_ids", "observation_ids", "evidence_type", "calculation_method", "confidence", "limitations", "created_at", "status"],
    "hypotheses": ["hypothesis_id", "hypothesis", "basis_finding_ids", "target_audience", "proposed_test", "success_metric", "required_data", "status", "limitations"],
    "audit_findings": ["audit_id", "record_type", "record_id", "audit_rule", "result", "issue", "recommended_action", "audited_at"],
}
```

Also test that `utc_now()` parses as ISO 8601 UTC, CSV round-trip preserves Vietnamese text, and an unknown table raises `KeyError`.

- [ ] **Step 2: Run the tests and verify they fail**

Run:

```bash
.venv/bin/python -m unittest tests.test_research_io -v
```

Expected: FAIL because the schema, shared module, and templates do not exist.

- [ ] **Step 3: Write the canonical schema**

Create `config/field-definitions.json` with a top-level object containing:

```json
{
  "version": 1,
  "evidence_types": ["direct_source", "calculated", "estimate", "hypothesis"],
  "confidence_levels": ["high", "medium", "low", "unverified"],
  "access_statuses": ["accessible", "partial", "blocked", "not_verified"],
  "tables": {
    "sources": {"id_field": "source_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "observations": {"id_field": "observation_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "products": {"id_field": "product_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "competitors": {"id_field": "competitor_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "videos": {"id_field": "video_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "findings": {"id_field": "finding_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "hypotheses": {"id_field": "hypothesis_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}},
    "audit_findings": {"id_field": "audit_id", "fields": [], "required": [], "enums": {}, "foreign_keys": {}}
  }
}
```

Fill `fields` with the exact lists in Step 1. Required fields must include IDs and the fields needed for provenance:

- `sources`: `source_id`, `url`, `title`, `source_type`, `accessed_at`, `access_status`, `collection_method`.
- `observations`: `observation_id`, `source_id`, `entity_type`, `entity_id`, `attribute`, `observed_value`, `observed_at`, `collection_method`, `confidence`.
- `products`: `product_id`, `product_name`, `category`, `evidence_type`, `confidence`.
- `competitors`: `competitor_id`, `platform`, `handle_or_name`, `profile_url`, `observed_at`, `confidence`.
- `videos`: `video_id`, `competitor_id`, `video_url`, `observed_at`, `evidence_type`, `confidence`.
- `findings`: `finding_id`, `finding_text`, `evidence_type`, `confidence`, `created_at`, `status`.
- `hypotheses`: `hypothesis_id`, `hypothesis`, `basis_finding_ids`, `target_audience`, `proposed_test`, `success_metric`, `required_data`, `status`.
- `audit_findings`: all eight fields.

Set enums for evidence, confidence, access status, finding status (`draft`, `audited`, `accepted`, `rejected`), hypothesis status (`unverified`, `testing`, `supported`, `rejected`), and audit result (`pass`, `warning`, `fail`). Define foreign keys for `observations.source_id -> sources.source_id`, `products.commission_source_id -> sources.source_id`, `videos.competitor_id -> competitors.competitor_id`; list fields such as `source_ids` and `observation_ids` as JSON-encoded arrays in CSV.

- [ ] **Step 4: Implement shared I/O helpers**

Implement the interfaces above with these behaviors:

- Resolve `root` to an absolute `Path` without changing the current working directory.
- Reject a missing or malformed `field-definitions.json` with a `ValueError` that names the path and missing key.
- Create parent directories before writes.
- Use `newline=""` for CSV files.
- Never write secrets or read environment variables containing credentials.
- Preserve empty strings as empty strings in CSV; do not convert missing values to fabricated numbers.

- [ ] **Step 5: Create policy documents and templates**

`research-policy.md` must define direct/calculated/estimate/hypothesis, confidence levels, provenance minimums, the no-sales-inference rule, raw immutability and audit gate.

`source-policy.md` must define the source priority order from the spec, `accessible`/`partial`/`blocked`/`not_verified`, permitted collection methods (`exa_search`, `web_fetch`, `browser`, `manual`, `api` only when authorized), and what to do when a page is blocked.

Each JSON record template must be a valid JSON object with `"_template": true`, all canonical fields present, empty strings or `null` only where a field is optional, and a `_note` explaining that the file is not research data. Do not include real product names, prices, URLs, handles, metrics or claims. Markdown templates must contain headings and explicit placeholders such as `Chưa có dữ liệu được xác minh`, not invented findings.

- [ ] **Step 6: Run the tests and inspect the generated schema**

Run:

```bash
.venv/bin/python -m unittest tests.test_research_io -v
.venv/bin/python -m json.tool config/field-definitions.json >/dev/null
for file in templates/*.json; do .venv/bin/python -m json.tool "$file" >/dev/null; done
```

Expected: all tests PASS and all JSON files parse successfully.

---

### Task 3: Implement workspace initialization and schema validation

**Files:**
- Create: `scripts/init_research.py`
- Create: `scripts/validate_records.py`
- Create: `tests/test_init_research.py`
- Create: `tests/test_validate_records.py`

**Interfaces:**
- `scripts.init_research.initialize_workspace(root: Path, force: bool = False) -> list[Path]` creates directories and empty CSVs from the canonical schema. With `force=False`, it raises `FileExistsError` rather than overwriting a non-empty existing CSV or database.
- CLI: `scripts/init_research.py --root PATH [--force]`; default root is `.`. `--force` may only create missing files or rewrite files that contain only the exact generated header; it must never delete records.
- `scripts.validate_records.validate_workspace(root: Path) -> list[dict]` returns issue dictionaries with `table`, `record_id`, `rule`, `severity`, `message`.
- CLI: `scripts/validate_records.py --root PATH [--output PATH] [--fail-on-warning]`; JSON output is a list of issues plus summary counts; exit 0 for no errors, 1 for validation errors, 2 for invocation/file errors.

- [ ] **Step 1: Write failing initialization tests**

Use `tempfile.TemporaryDirectory()` and assert:

```python
def test_initialize_creates_expected_directories_and_headers(self):
    created = initialize_workspace(root)
    self.assertTrue((root / "data/raw").is_dir())
    self.assertTrue((root / "data/processed").is_dir())
    self.assertEqual(read_header(root / "data/processed/sources.csv"), EXPECTED_TABLES["sources"])
    self.assertEqual(len(created), 8)

def test_initialize_never_overwrites_existing_records(self):
    initialize_workspace(root)
    path = root / "data/processed/sources.csv"
    path.write_text(path.read_text(encoding="utf-8") + "source-1,https://example.com,Title,,,,,,,,\n", encoding="utf-8")
    with self.assertRaises(FileExistsError):
        initialize_workspace(root)
    self.assertIn("source-1", path.read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run initialization tests to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_init_research -v
```

Expected: FAIL because `initialize_workspace` does not exist.

- [ ] **Step 3: Implement initialization**

Create directories `data/raw`, `data/processed`, and `reports`; create `.gitkeep` only if absent; write one header row for each of the eight tables. Create `data/research.sqlite` only in the SQLite task, not here. Use exclusive creation (`open(..., "x")`) or an equivalent existence check so a non-empty file is never overwritten. Print a summary listing created and skipped paths; do not print file contents.

- [ ] **Step 4: Run initialization tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_init_research -v
```

Expected: PASS.

- [ ] **Step 5: Write failing validation tests**

Create fixtures in temporary directories with one valid source/observation pair and test these exact failures:

```python
def test_valid_records_have_no_issues(self):
    write_valid_fixture(root)
    self.assertEqual(validate_workspace(root), [])

def test_missing_absolute_url_is_an_error(self):
    record = valid_source(url="not-a-url")
    write_sources(root, [record])
    issues = validate_workspace(root)
    self.assertIssue(issues, table="sources", rule="url_absolute", severity="error")

def test_missing_source_reference_is_an_error(self):
    write_observations(root, [valid_observation(source_id="missing")])
    issues = validate_workspace(root)
    self.assertIssue(issues, table="observations", rule="foreign_key", severity="error")

def test_calculated_without_method_is_an_error(self):
    write_findings(root, [valid_finding(evidence_type="calculated", calculation_method="")])
    issues = validate_workspace(root)
    self.assertIssue(issues, table="findings", rule="calculation_method", severity="error")

def test_estimate_without_limitations_is_an_error(self):
    write_products(root, [valid_product(evidence_type="estimate", limitations="")])
    issues = validate_workspace(root)
    self.assertIssue(issues, table="products", rule="estimate_limitations", severity="error")

def test_hypothesis_is_not_verified(self):
    write_findings(root, [valid_finding(evidence_type="hypothesis", status="accepted")])
    issues = validate_workspace(root)
    self.assertIssue(issues, table="findings", rule="hypothesis_status", severity="error")
```

Also test invalid enum, missing `observed_at` for a video metric, missing currency when `price_value` is present, invalid ISO timestamp, duplicate ID within a table, and duplicate URL within sources as a warning rather than silent deletion.

- [ ] **Step 6: Run validation tests to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_validate_records -v
```

Expected: FAIL because validation functions do not exist.

- [ ] **Step 7: Implement record validation**

Implement validation in this order:

1. Load definitions and read each known CSV; report missing file/header mismatch as invocation/data errors.
2. For each row, require schema-required fields and produce one issue per violated rule.
3. Validate IDs are non-empty, dates use `datetime.fromisoformat` after accepting a terminal `Z`, and source URLs use `urllib.parse.urlparse` with `http`/`https` scheme and non-empty netloc.
4. Validate all enum values from config.
5. Build ID sets before cross-reference checks; report missing foreign keys.
6. Parse JSON-array fields (`source_ids`, `observation_ids`, `basis_finding_ids`) and report malformed arrays.
7. Enforce evidence rules: calculated requires `calculation_method`; estimate requires `limitations`; hypothesis findings must have status `draft` or `rejected`, never `audited`/`accepted`.
8. Enforce product currency when `price_value` is non-empty and commission source when `commission_value` is non-empty.
9. Enforce `observed_at` for videos whenever any observed metric is non-empty.
10. Report duplicate IDs as errors and duplicate source URLs as warnings; never modify files.

Use stable issue ordering by table, row number, rule. Return plain dictionaries so the CLI can serialize them without a custom package.

- [ ] **Step 8: Run all validation tests and CLI smoke tests**

Run:

```bash
.venv/bin/python -m unittest tests.test_init_research tests.test_validate_records -v
rm -rf /tmp/tiktok-research-validation-smoke
.venv/bin/python scripts/init_research.py --root /tmp/tiktok-research-validation-smoke
.venv/bin/python scripts/validate_records.py --root /tmp/tiktok-research-validation-smoke --output /tmp/tiktok-research-validation-smoke/report.json
.venv/bin/python -m json.tool /tmp/tiktok-research-validation-smoke/report.json >/dev/null
```

Expected: initialization succeeds, empty workspace validation exits 0, and report summary has zero records/issues.

---

### Task 4: Implement duplicate detection as a non-destructive audit operation

**Files:**
- Create: `scripts/deduplicate_sources.py`
- Create: `tests/test_deduplicate_sources.py`

**Interfaces:**
- `scripts.deduplicate_sources.find_source_duplicates(records: list[dict[str, str]]) -> list[dict]` returns groups with `kind` (`id` or `url`), `value`, and `record_ids`.
- `scripts.deduplicate_sources.audit_duplicates(root: Path) -> dict` reads `sources.csv` and returns `{"duplicates": [...], "summary": {...}}`.
- CLI: `scripts/deduplicate_sources.py --root PATH [--output PATH]`; default output is stdout JSON, optional output writes JSON and never changes source CSV.

- [ ] **Step 1: Write the failing duplicate tests**

Test exact behavior:

```python
def test_duplicate_ids_are_reported(self):
    result = find_source_duplicates([
        {"source_id": "s1", "url": "https://one.example"},
        {"source_id": "s1", "url": "https://two.example"},
    ])
    self.assertEqual(result[0]["kind"], "id")
    self.assertEqual(result[0]["record_ids"], ["s1", "s1"])

def test_duplicate_urls_are_reported_without_normalizing_away_evidence(self):
    result = find_source_duplicates([
        {"source_id": "s1", "url": "https://example.com/a"},
        {"source_id": "s2", "url": "https://example.com/a"},
    ])
    self.assertEqual(result[0]["kind"], "url")
    self.assertEqual(result[0]["record_ids"], ["s1", "s2"])


def test_audit_does_not_modify_csv(self):
    before = sources_csv.read_text(encoding="utf-8")
    audit_duplicates(root)
    self.assertEqual(sources_csv.read_text(encoding="utf-8"), before)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_deduplicate_sources -v
```

Expected: FAIL because the duplicate functions do not exist.

- [ ] **Step 3: Implement duplicate detection**

Group non-empty IDs and exact URL strings. Do not silently strip query strings, redirect URLs, or delete rows; exact canonicalization can be added later only as a separately documented rule. Sort duplicate groups by `kind`, `value`, then record IDs. Include counts for duplicate groups and affected records. Return an empty report for a missing/empty sources CSV after initialization.

- [ ] **Step 4: Run tests and CLI check**

Run:

```bash
.venv/bin/python -m unittest tests.test_deduplicate_sources -v
.venv/bin/python scripts/deduplicate_sources.py --root . --output /tmp/source-duplicates.json
.venv/bin/python -m json.tool /tmp/source-duplicates.json >/dev/null
```

Expected: PASS; current empty project data produces a zero-duplicate report and leaves `data/processed/sources.csv` unchanged.

---

### Task 5: Build a reproducible SQLite index from processed CSV data

**Files:**
- Create: `scripts/build_sqlite_index.py`
- Create: `tests/test_build_sqlite_index.py`

**Interfaces:**
- `scripts.build_sqlite_index.build_index(root: Path, database: Path | None = None) -> Path` creates/replaces the SQLite database from processed CSVs and returns the database path.
- CLI: `scripts/build_sqlite_index.py --root PATH [--database PATH]`; default database is `data/research.sqlite`.
- Database tables use the eight canonical table names and canonical columns as `TEXT`, with `row_number INTEGER` metadata only if needed; no data is inferred or aggregated during indexing.

- [ ] **Step 1: Write failing SQLite tests**

Use a temporary root with initialized CSVs and write one valid source and observation. Assert:

```python
def test_build_index_creates_all_tables_and_rows(self):
    database = build_index(root)
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue(set(EXPECTED_TABLES).issubset(tables))
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0], 1)
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM observations").fetchone()[0], 1)

def test_rebuild_removes_stale_rows(self):
    build_index(root)
    remove_source_row_from_csv(root)
    build_index(root)
    with sqlite3.connect(root / "data/research.sqlite") as connection:
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0], 0)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_build_sqlite_index -v
```

Expected: FAIL because `build_index` does not exist.

- [ ] **Step 3: Implement transactional rebuild**

Create the parent directory, open SQLite, enable foreign keys, and use one transaction. For each canonical table, create a table with quoted column identifiers and `TEXT` columns; define primary key on the configured ID field where SQLite-compatible. Delete/recreate table contents from processed CSVs, insert values exactly as strings, and commit only after all tables load successfully. On any parse/insert error, roll back and preserve the previous database file if possible by building a temporary sibling database and atomically replacing the target after successful commit. Do not calculate metrics, merge duplicate records, or edit CSVs.

- [ ] **Step 4: Run SQLite tests and integrity checks**

Run:

```bash
.venv/bin/python -m unittest tests.test_build_sqlite_index -v
.venv/bin/python scripts/build_sqlite_index.py --root .
.venv/bin/python -c 'import sqlite3; c=sqlite3.connect("data/research.sqlite"); print(c.execute("PRAGMA integrity_check").fetchone()[0]); c.close()'
```

Expected: tests PASS and integrity check prints `ok`.

---

### Task 6: Export a truthful Markdown research summary

**Files:**
- Create: `scripts/export_research_summary.py`
- Create: `tests/test_export_research_summary.py`
- Modify: `README.md` — document exact export command after implementation.

**Interfaces:**
- `scripts.export_research_summary.export_summary(root: Path, output: Path, title: str, accessed_at: str | None = None) -> Path` reads processed records, validation output if available, and source metadata to render a Markdown report.
- CLI: `scripts/export_research_summary.py --root PATH --output PATH --title TEXT [--accessed-at ISO_TIMESTAMP]`.
- The exporter must not invent findings; it can only render rows and explicit status sections.

- [ ] **Step 1: Write failing export tests**

Test empty and mixed evidence cases:

```python
def test_empty_workspace_states_that_no_verified_data_exists(self):
    output = export_summary(root, root / "reports/empty.md", "Test report")
    text = output.read_text(encoding="utf-8")
    self.assertIn("Chưa có dữ liệu được xác minh", text)
    self.assertIn("Phạm vi và phương pháp", text)
    self.assertIn("Giới hạn", text)

def test_hypotheses_are_separate_from_verified_findings(self):
    write_finding(root, evidence_type="direct_source", status="audited")
    write_finding(root, evidence_type="hypothesis", status="draft")
    output = export_summary(root, root / "reports/mixed.md", "Test report")
    text = output.read_text(encoding="utf-8")
    self.assertIn("Phát hiện có bằng chứng", text)
    self.assertIn("Giả thuyết chưa xác minh", text)
    self.assertNotIn("hypothesis text", verified_section(text))
```

Also test that a blocked source is rendered under limitations, a product with blank price is not shown with a numeric price, and observed video metrics are labeled with observation time.

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_export_research_summary -v
```

Expected: FAIL because the exporter does not exist.

- [ ] **Step 3: Implement deterministic Markdown export**

Render these headings in this order:

1. `# <title>`
2. `## Tóm tắt phạm vi và phương pháp`
3. `## Nguồn thông tin đã sử dụng`
4. `## Phát hiện có bằng chứng`
5. `## Sản phẩm và nhóm sản phẩm`
6. `## Dữ liệu video/kênh công khai`
7. `## Giả thuyết chưa xác minh`
8. `## Dữ liệu cần thu thập tiếp`
9. `## Giới hạn và rủi ro`
10. `## Kiểm toán dữ liệu`

Use tables only for fields with actual values. Include source URL, accessed time, published time when present, collection method, confidence, evidence type and limitations. For empty datasets, write `Chưa có dữ liệu được xác minh` in the relevant section. Never turn hypotheses into facts and never infer sales/profit from metrics. Sort records by ID for deterministic output and escape Markdown pipe/newline characters in cells.

- [ ] **Step 4: Run export tests and smoke export**

Run:

```bash
.venv/bin/python -m unittest tests.test_export_research_summary -v
.venv/bin/python scripts/export_research_summary.py --root . --output reports/initial-system-smoke.md --title "TikTok Affiliate Research System Smoke Report"
```

Expected: tests PASS and the smoke report explicitly says no verified research data exists. This smoke report is a system check, not the final smart-home market report.

---

### Task 7: Create reusable Claude Code Skills and research Agents

**Files:**
- Create: `.claude/skills/market-research/SKILL.md`
- Create: `.claude/skills/product-research/SKILL.md`
- Create: `.claude/skills/competitor-analysis/SKILL.md`
- Create: `.claude/skills/content-strategy/SKILL.md`
- Create: `.claude/skills/research-audit/SKILL.md`
- Create: `.claude/agents/market-analyst.md`
- Create: `.claude/agents/product-researcher.md`
- Create: `.claude/agents/competitor-researcher.md`
- Create: `.claude/agents/research-auditor.md`
- Create: `tests/test_claude_assets.py`

**Interfaces:**
- Every `SKILL.md` starts with YAML frontmatter containing non-empty `name` and `description`, followed by reusable instructions and output format.
- Every agent file starts with frontmatter containing non-empty `name` and `description`; body includes `Nhiệm vụ`, `Phạm vi`, `Công cụ được phép`, `Giới hạn`, `Định dạng đầu ra`.
- Skills and agents must use the same evidence vocabulary and schema field names as `config/field-definitions.json`.
- Agents must explicitly report `not_available` when a required web/browser/API tool is unavailable.

- [ ] **Step 1: Write failing asset tests**

Test every expected file exists, frontmatter parses enough to contain `name:` and `description:`, and every body contains the required safety phrases:

```python
REQUIRED_SAFETY = (
    "Không bịa",
    "không suy ra doanh số",
    "nguồn",
    "confidence",
    "limitations",
)
REQUIRED_AGENT_SECTIONS = (
    "Nhiệm vụ", "Phạm vi", "Công cụ được phép", "Giới hạn", "Định dạng đầu ra"
)
```

Also assert that no asset instructs an agent to bypass login, CAPTCHA, anti-bot, or access private data. Check the skills have their exact names: `market-research`, `product-research`, `competitor-analysis`, `content-strategy`, `research-audit`.

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_claude_assets -v
```

Expected: FAIL because the files do not exist.

- [ ] **Step 3: Write the five Skills**

Each Skill must include:

- frontmatter `name` and `description`;
- when to use and when not to use;
- required user inputs: market, geography, category, target audience, date range and research question;
- source collection rules and evidence types;
- a step-by-step workflow;
- explicit distinction between observed data, calculated values, estimates and hypotheses;
- a reusable output contract using fields `finding`, `source_url`, `accessed_at`, `published_at`, `observed_data`, `collection_method`, `confidence`, `limitations`;
- a “Thiếu dữ liệu” section instead of fabricated values;
- a safety note for public-only access.

Specific content:

- `market-research`: demand problems, category signals, competition and market evidence; no market size without a reliable source.
- `product-research`: product problem/benefits, price date, commission source, Affiliate eligibility and content potential; leave price/commission blank when unverified.
- `competitor-analysis`: public channel/video URL, observed hook/story/product presentation/CTA/disclosure and timestamped public metrics; explicitly prohibits sales/profit inference.
- `content-strategy`: persona, content pillars, formats, hypotheses, test matrix and success metrics; every hypothesis references supporting finding IDs.
- `research-audit`: source reachability, date, duplicate, provenance, evidence type, confidence, limitations, unsupported claims and final pass/warning/fail.

- [ ] **Step 4: Write the four Agents**

Each agent file must specify permitted tools conservatively:

- `market-analyst`: may use read-only project files and configured public web search/fetch if available; does not assume Playwright or TikTok API.
- `product-researcher`: may use public sources and user-provided URLs; commercial fields require direct source and observation date.
- `competitor-researcher`: may inspect public pages only when reachable; records `not_available` rather than bypassing access controls.
- `research-auditor`: reads outputs and source metadata, may run local validation scripts, does not rewrite raw evidence or invent corrections.

Each output contract must return structured sections for `sources`, `observations`, `findings`, `hypotheses`, `limitations`, and `tool_status`, with stable IDs or an explicit `proposed_id` to be assigned by the scripts. The auditor additionally returns `audit_findings` and an overall status.

- [ ] **Step 5: Run asset tests and frontmatter inspection**

Run:

```bash
.venv/bin/python -m unittest tests.test_claude_assets -v
for file in .claude/skills/*/SKILL.md .claude/agents/*.md; do printf '%s: ' "$file"; grep -E '^(name|description):' "$file" | wc -l; done
```

Expected: all tests PASS; every file has both required frontmatter keys and no prohibited access language.

---

### Task 8: Add end-to-end verification and operational documentation

**Files:**
- Modify: `README.md`
- Create: `tests/test_end_to_end.py`
- Create: `reports/.gitkeep` if absent
- Create: `data/raw/.gitkeep` and `data/processed/.gitkeep` if absent

**Interfaces:**
- The end-to-end test runs each script through Python function interfaces in a temporary workspace and asserts the sequence `init -> write fixture -> validate -> duplicate audit -> SQLite -> export`.
- No end-to-end test calls external web services, browser, TikTok, Exa, or a paid API.

- [ ] **Step 1: Write the failing end-to-end test**

Create a test that:

1. initializes a temp root;
2. writes one synthetic-but-explicitly-test-only source/product/observation/finding/hypothesis fixture with URLs under `https://example.com`;
3. validates successfully;
4. runs duplicate audit and expects zero duplicate groups;
5. builds SQLite and checks source/product/finding rows;
6. exports Markdown and checks source URL, evidence labels, limitations and separate hypothesis heading.

The fixture must be created inside the test and never committed to `data/`; mark it with a local variable comment `TEST_FIXTURE_ONLY`.

- [ ] **Step 2: Run the end-to-end test to verify failure**

Run:

```bash
.venv/bin/python -m unittest tests.test_end_to_end -v
```

Expected: FAIL until earlier script interfaces are available or the assertions reveal mismatches.

- [ ] **Step 3: Implement only compatibility fixes**

Fix mismatched function signatures, CLI defaults, CSV headers, JSON encoding or Markdown section names found by the test. Do not broaden scope, add a dependency, change evidence rules, or add market facts to make the test pass.

- [ ] **Step 4: Run the complete local suite**

Run:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/init_research.py --root .
.venv/bin/python scripts/validate_records.py --root . --output /tmp/tiktok-research-validation.json
.venv/bin/python scripts/deduplicate_sources.py --root . --output /tmp/tiktok-research-duplicates.json
.venv/bin/python scripts/build_sqlite_index.py --root .
.venv/bin/python scripts/export_research_summary.py --root . --output reports/initial-system-smoke.md --title "TikTok Affiliate Research System Smoke Report"
```

Expected: all tests PASS; the current empty project validates with zero errors; SQLite integrity is `ok`; smoke report states that no verified research data exists.

- [ ] **Step 5: Update README with final runbook**

Document the complete runbook in Vietnamese, including:

```bash
python3 -m venv .venv
.venv/bin/python scripts/init_research.py --root .
.venv/bin/python scripts/validate_records.py --root . --output reports/validation.json
.venv/bin/python scripts/deduplicate_sources.py --root . --output reports/duplicates.json
.venv/bin/python scripts/build_sqlite_index.py --root .
.venv/bin/python scripts/export_research_summary.py --root . --output reports/<date>-<topic>.md --title "..."
.venv/bin/python -m unittest discover -s tests -v
```

Explain that the generated validation/duplicate JSON files are audit artifacts, that raw data remains unchanged, and that a report with no reachable TikTok data must say so.

---

### Task 9: Run the first public-source pilot research and audited report

**Files:**
- Create: `data/raw/<date>-smart-home-source-captures/` only for legally storable public source material.
- Create/update: `data/processed/sources.csv`, `observations.csv`, `products.csv`, `competitors.csv`, `videos.csv`, `findings.csv`, `hypotheses.csv`, `audit_findings.csv` using the scripts and schema.
- Create: `reports/YYYY-MM-DD-smart-home-tiktok-affiliate.md`
- Create: `reports/YYYY-MM-DD-smart-home-tiktok-affiliate-audit.md`

**Interfaces:**
- The pilot consumes only public, reachable sources from Exa/Web Fetch/Playwright or URLs explicitly supplied by the user.
- It produces records conforming to the canonical schema; all source access times use ISO 8601 UTC.
- The final report must contain the ten requested video ideas, but each idea must be labeled as a content hypothesis and linked to findings or marked as requiring validation.

- [ ] **Step 1: Define the research brief before searching**

Write a brief in the report draft containing:

- geography: Vietnam;
- market: TikTok Affiliate/TikTok Shop public ecosystem;
- category: smart home appliances;
- target audience assumptions explicitly labeled as assumptions;
- research date and access method;
- questions: customer problems, supported product groups, public competitor content patterns, observable commercial information, risks and missing data.

- [ ] **Step 2: Collect official and public sources without bypassing controls**

Prioritize official TikTok Shop/TikTok Developer documentation, public marketplace pages, authoritative industry or legal sources, and reachable public creator/video pages. For each source, immediately record URL, title, publisher, type, access time, publication date if stated, method and access status. If a source is blocked or requires login, record `blocked`/`partial` and do not retry around the control.

- [ ] **Step 3: Extract observations before writing findings**

Record exact observable facts and excerpts. For products, only record price/currency/commission when the source explicitly states them. For videos, record only public metrics seen at `observed_at`; do not calculate sales, revenue or profit. For each source-derived statement, attach `source_id` and, where applicable, an observation ID.

- [ ] **Step 4: Run local validation and duplicate checks**

Run:

```bash
.venv/bin/python scripts/validate_records.py --root . --output reports/YYYY-MM-DD-smart-home-validation.json --fail-on-warning
.venv/bin/python scripts/deduplicate_sources.py --root . --output reports/YYYY-MM-DD-smart-home-duplicates.json
```

Fix data-entry issues by editing processed records or source metadata; never fix them by weakening validation rules or fabricating missing fields.

- [ ] **Step 5: Run the research auditor after independent research is complete**

Use `research-auditor` to inspect the collected records. It must return pass/warning/fail for provenance, dates, duplicates, evidence type, confidence, limitations and unsupported claims. Save the audit report. Do not call the pilot complete while an unaddressed `fail` remains in a claim presented as verified.

- [ ] **Step 6: Build index and export the report**

Run:

```bash
.venv/bin/python scripts/build_sqlite_index.py --root .
.venv/bin/python scripts/export_research_summary.py --root . --output reports/YYYY-MM-DD-smart-home-tiktok-affiliate.md --title "Nghiên cứu TikTok Affiliate Việt Nam — Đồ gia dụng thông minh"
```

Extend the generated report manually only with sourced sections needed by the brief: comparison table, competitor analysis, ten labeled content hypotheses, unverified hypotheses, data still needed and next steps. Keep generated facts and authored recommendations visibly separate.

- [ ] **Step 7: Verify pilot acceptance criteria**

Confirm the report includes:

1. scope and method;
2. all sources used;
3. customer problems and needs with evidence status;
4. supported product/group list;
5. price/benefit/competition/video-potential comparison without invented values;
6. competitor video analysis or explicit “no accessible data” statement;
7. exactly ten video ideas, each a hypothesis/test;
8. unverified hypotheses;
9. data to collect next;
10. next research step.

Run the complete local suite again. Report any inaccessible TikTok/API data plainly rather than treating the public-source pilot as complete coverage.

---

## Execution Order and Gates

1. Complete Task 1 and Task 2 before any research data is collected.
2. Complete Task 3 and Task 4 before accepting any processed records.
3. Complete Task 5 and Task 6 before using the system for a report.
4. Complete Task 7 before invoking custom Skills/Agents in a real workflow.
5. Complete Task 8 before pilot research.
6. Run Task 9 only after all local tests pass and the public-source access boundary is understood.
7. If external access, API approval, OAuth, package installation, account action or paid service becomes necessary, stop and ask the user before proceeding.

## Plan Self-Review

- **Spec coverage:** Goals and success criteria are implemented in Tasks 1–9; schema/provenance in Task 2; validation rules in Task 3; non-destructive duplicates in Task 4; rebuildable SQLite in Task 5; truthful report output in Task 6; Skills/Agents in Task 7; end-to-end verification in Task 8; pilot report and audit in Task 9; Python virtual environment and safety constraints are repeated globally and tested in Task 1.
- **No placeholders:** Every task defines files, interfaces, failure-first tests, exact commands, expected outcomes and implementation behavior. The only placeholders are runtime report paths such as `<date>` and are command arguments intentionally supplied by the operator, not unfinished implementation instructions.
- **Type consistency:** Shared functions are defined in Task 2 and consumed by Tasks 3–6; table names and fields come from the same schema; CLI flags are repeated consistently in README and tasks.
- **Review focus coverage:** Empty templates are tested in Task 2; provenance/evidence validation in Task 3; calculated/estimate/hypothesis separation in Tasks 3 and 6; duplicates in Task 4; blocked/not-available public sources in Tasks 7–9.
- **Repository state:** The project is not a Git repository, so the plan deliberately contains no commit steps and does not instruct an executor to initialize Git.
