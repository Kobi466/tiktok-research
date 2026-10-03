# Thiết kế hệ thống nghiên cứu thị trường TikTok Affiliate Việt Nam

- **Ngày:** 2026-10-02
- **Trạng thái:** Đã được người dùng phê duyệt để viết spec; chờ người dùng review trước khi lập kế hoạch triển khai
- **Ngôn ngữ xử lý dữ liệu:** Python
- **Môi trường chạy:** Linux, Python virtual environment tại `./.venv`
- **Phạm vi phiên bản đầu:** Nghiên cứu nguồn công khai, lưu bằng chứng có truy nguyên, kiểm toán và xuất báo cáo Markdown

## 1. Mục tiêu và tiêu chí thành công

Hệ thống giúp một người mới có thể nghiên cứu TikTok Affiliate tại Việt Nam theo cách có thể lặp lại, kiểm tra được và không bịa dữ liệu. Hệ thống phải hỗ trợ:

1. Nghiên cứu thị trường, nhu cầu khách hàng và nhóm sản phẩm.
2. Ghi nhận sản phẩm, giá, hoa hồng và điều kiện Affiliate chỉ khi có nguồn xác minh.
3. Phân tích kênh và video công khai khi dữ liệu truy cập hợp lệ.
4. Tạo giả thuyết nội dung và đề xuất thử nghiệm, phân biệt rõ với sự kiện thực tế.
5. Lưu nguồn, thời điểm truy cập, dữ liệu quan sát, phương pháp và giới hạn.
6. Kiểm toán nguồn, bản ghi trùng, thiếu trường và kết luận vượt quá bằng chứng.
7. Xuất dữ liệu CSV/JSON/SQLite và báo cáo Markdown dễ đọc, dễ sao lưu.

Tiêu chí thành công của phiên bản đầu:

- Có thể khởi tạo một workspace nghiên cứu mới bằng script Python.
- Mọi phát hiện thực tế trong báo cáo truy nguyên được tới nguồn và quan sát.
- Dữ liệu thiếu hoặc chưa xác minh không bị tự động biến thành số liệu chắc chắn.
- Validator phát hiện tối thiểu URL thiếu, ngày không hợp lệ, confidence/evidence_type không hợp lệ, liên kết nguồn không tồn tại và bản ghi trùng rõ ràng.
- Quy trình không yêu cầu đăng nhập TikTok, cookie, CAPTCHA bypass hoặc API credential chưa được cấp quyền.
- Có thể chạy toàn bộ kiểm tra bằng Python trong `./.venv` mà không phụ thuộc package ngoài ở phiên bản đầu.

## 2. Phạm vi và ngoài phạm vi

### Trong phạm vi

- Skills Markdown trong `.claude/skills/`.
- Agent instructions Markdown trong `.claude/agents/`.
- Quy ước nghiên cứu, schema, template và validator.
- Dữ liệu công khai do Exa, trình duyệt hoặc người dùng cung cấp hợp lệ.
- Chỉ mục SQLite cục bộ được xây dựng từ dữ liệu chuẩn hóa.
- Báo cáo thử nghiệm về đồ gia dụng thông minh sau khi quy trình được kiểm tra.
- Hướng dẫn sử dụng bằng tiếng Việt.

### Ngoài phạm vi phiên bản đầu

- Tự động đăng nhập hoặc điều khiển tài khoản TikTok.
- Thu thập dữ liệu private, dữ liệu sau CAPTCHA hoặc vượt cơ chế anti-bot.
- Suy ra doanh số, lợi nhuận hoặc hoa hồng của đối thủ từ lượt xem/lượt thích.
- Tự động mua hàng, đăng video, gửi lời mời Affiliate hoặc thay đổi tài khoản.
- TikTok Research API trước khi có quyền truy cập và cấu hình riêng.
- Dashboard, biểu đồ hoặc hệ thống web UI. Nếu thêm trực quan hóa sau này, đó là một phạm vi thiết kế riêng.
- Cài package Python ngoài khi chưa có nhu cầu cụ thể và sự xác nhận của người dùng.
- Khởi tạo Git hoặc commit, trừ khi người dùng yêu cầu sau này.

## 3. Các quyết định kiến trúc

### 3.1. Markdown là giao diện điều phối

Claude Code Skills và Agents là các file Markdown có frontmatter hợp lệ. Chúng mô tả nhiệm vụ, giới hạn quyền, quy trình, điều kiện thiếu dữ liệu và định dạng đầu ra. Chúng không được giả định rằng web, trình duyệt, TikTok API hoặc công cụ trả phí luôn có sẵn; mỗi agent phải báo công cụ nào thực sự được cấp.

### 3.2. CSV/JSON/Markdown là định dạng dữ liệu chính

- JSON dùng cho record mẫu, metadata và dữ liệu lồng nhau nhỏ.
- CSV dùng cho bảng dữ liệu chuẩn hóa, dễ mở bằng spreadsheet.
- Markdown dùng cho báo cáo, phương pháp và audit narrative.
- Raw evidence được bảo toàn, không sửa trực tiếp.

SQLite là lớp chỉ mục/truy vấn cục bộ được tái tạo từ dữ liệu chuẩn hóa; không phải nguồn sự thật duy nhất. Nếu SQLite bị xóa, có thể xây dựng lại từ CSV/JSON.

### 3.3. Python virtual environment bắt buộc

Workspace dùng `./.venv`. Không cài package vào Python hệ thống. Script và kiểm tra phải chạy qua `.venv/bin/python` sau khi môi trường được tạo. Giai đoạn đầu chỉ dùng standard library (`csv`, `json`, `sqlite3`, `urllib`, `hashlib`, `datetime`, `argparse`, `unittest` nếu cần).

### 3.4. Không tạo dữ liệu giả

Các file khởi tạo chỉ chứa header, schema hoặc placeholder được đánh dấu rõ. Không tạo sản phẩm, giá, hoa hồng, lượt xem hay kết luận mẫu có vẻ như dữ liệu thực. Báo cáo phải ghi rõ khi không có dữ liệu truy cập được.

## 4. Cấu trúc workspace

```text
.claude/
├── agents/
│   ├── market-analyst.md
│   ├── product-researcher.md
│   ├── competitor-researcher.md
│   └── research-auditor.md
├── skills/
│   ├── market-research/SKILL.md
│   ├── product-research/SKILL.md
│   ├── competitor-analysis/SKILL.md
│   ├── content-strategy/SKILL.md
│   └── research-audit/SKILL.md
└── settings.local.json

config/
├── research-policy.md
├── field-definitions.json
└── source-policy.md

data/
├── raw/
│   └── .gitkeep
├── processed/
│   └── .gitkeep
└── research.sqlite

docs/superpowers/specs/
└── 2026-10-02-tiktok-affiliate-research-system-design.md

reports/
└── .gitkeep

scripts/
├── init_research.py
├── validate_records.py
├── deduplicate_sources.py
├── build_sqlite_index.py
└── export_research_summary.py

templates/
├── source-record.json
├── observation-record.json
├── product-record.json
├── video-record.json
├── finding-record.json
├── hypothesis-record.json
├── research-report.md
└── audit-report.md

.venv/
README.md
.gitignore
```

`./.venv/` là thư mục sinh ra từ lệnh `python3 -m venv .venv`, không commit và không chứa trong bản sao dữ liệu nghiên cứu.

## 5. Mô hình dữ liệu và provenance

### 5.1. Nguồn (`sources`)

Các trường tối thiểu:

- `source_id`
- `url`
- `title`
- `publisher`
- `source_type`
- `accessed_at`
- `published_at`
- `access_status`
- `collection_method`
- `content_hash`
- `limitations`
- `notes`

`published_at` có thể rỗng nếu không tìm thấy ngày công bố. `accessed_at` phải ghi thời điểm hệ thống hoặc người nghiên cứu quan sát nguồn.

### 5.2. Quan sát (`observations`)

Các trường tối thiểu:

- `observation_id`
- `source_id`
- `entity_type`
- `entity_id`
- `attribute`
- `observed_value`
- `unit`
- `observed_at`
- `published_at`
- `evidence_excerpt`
- `collection_method`
- `confidence`
- `limitations`

Observation mô tả dữ liệu nhìn thấy, không phải kết luận. Ví dụ `views_observed=12000` là quan sát tại một thời điểm; không được đổi thành doanh số.

### 5.3. Thực thể sản phẩm (`products`)

Các trường chính:

- `product_id`, `product_name`, `category`
- `seller_name`, `product_url`
- `price_value`, `currency`, `price_observed_at`
- `commission_value`, `commission_type`, `commission_source_id`
- `customer_problem`, `benefits_observed`
- `video_potential`, `competition_notes`
- `evidence_type`, `confidence`, `limitations`

Giá và hoa hồng chỉ điền khi nguồn nêu rõ. Một giá quan sát từ marketplace phải giữ ngày quan sát và không được hiểu là giá cố định theo thời gian.

### 5.4. Kênh và video (`competitors`, `videos`)

Kênh lưu platform, tên/handle công khai, profile URL, ngách, public metrics và giới hạn. Video lưu video URL, ngày đăng nếu biết, thời điểm quan sát, metrics công khai, hook, cấu trúc, cách trình bày sản phẩm, CTA và affiliate disclosure nếu quan sát được.

Metrics chỉ là dữ liệu quan sát. Không đưa trường doanh số/lợi nhuận vào schema trừ khi có nguồn trực tiếp khác và được ghi như một observation riêng.

### 5.5. Phát hiện và giả thuyết (`findings`, `hypotheses`)

`findings` liên kết `source_ids` và/hoặc `observation_ids`, có `evidence_type`, phương pháp tính nếu cần, confidence, limitations và status audit.

`hypotheses` phải chỉ rõ:

- phát hiện làm cơ sở;
- khách hàng mục tiêu;
- thử nghiệm đề xuất;
- metric thành công;
- dữ liệu còn thiếu;
- trạng thái `unverified`, `testing`, `supported` hoặc `rejected`.

## 6. Enum và quy tắc xác thực

### Evidence type

```text
direct_source
calculated
estimate
hypothesis
```

### Confidence

```text
high
medium
low
unverified
```

### Access status

```text
accessible
partial
blocked
not_verified
```

### Quy tắc bắt buộc

1. URL phải là URL tuyệt đối hợp lệ cho bản ghi nguồn.
2. `source_id` tham chiếu phải tồn tại.
3. `accessed_at` phải có khi có dữ liệu quan sát.
4. `published_at` chỉ dùng khi nguồn xác nhận hoặc ghi rõ là không xác định.
5. `evidence_type=calculated` phải có `calculation_method`.
6. `evidence_type=estimate` phải có phương pháp và giới hạn.
7. `evidence_type=hypothesis` không được xuất trong phần “kết luận đã xác minh”.
8. `confidence=high` cần nguồn trực tiếp hoặc nhiều nguồn độc lập phù hợp; validator chỉ kiểm tra điều kiện dữ liệu, không thay thế phán đoán audit.
9. Giá trị tiền phải có currency khi được điền.
10. Hoa hồng phải liên kết tới nguồn xác minh; nếu không thì để trống và ghi `unverified`/`limitations`.
11. Bản ghi trùng theo ID hoặc URL phải được báo cáo, không tự động xóa.
12. Mọi số liệu mạng xã hội phải có `observed_at`.

## 7. Luồng nghiên cứu

1. Xác định ngành hàng, thị trường, câu hỏi và khách hàng mục tiêu.
2. Lập danh sách nguồn công khai phù hợp.
3. Thu thập source record và bản sao raw hợp lệ nếu cần.
4. Trích xuất observations, giữ nguyên trích đoạn và thời điểm quan sát.
5. Chuẩn hóa sản phẩm, kênh, video và dữ liệu thị trường.
6. Tạo findings với liên kết bằng chứng.
7. Tạo hypotheses và test plan; đánh dấu phần chưa xác minh.
8. Chạy `validate_records.py` và kiểm tra trùng nguồn.
9. Agent `research-auditor` rà soát trước khi tổng hợp.
10. Xuất SQLite index và báo cáo Markdown.
11. Ghi lại dữ liệu còn thiếu và bước nghiên cứu tiếp theo.

Các nghiên cứu song song chỉ được dùng khi nhiệm vụ độc lập, ví dụ một agent nghiên cứu tài liệu thị trường và một agent lập inventory sản phẩm. Audit luôn chạy sau khi các kết quả đó hoàn tất.

## 8. Vai trò Skills và Agents

### Skills

- `market-research`: câu hỏi thị trường, nhu cầu, cạnh tranh và xu hướng có nguồn.
- `product-research`: sản phẩm, lợi ích, giá, điều kiện Affiliate và hoa hồng có xác minh.
- `competitor-analysis`: kênh/video public, hook, cấu trúc, CTA và metrics quan sát.
- `content-strategy`: giả thuyết, chân dung, format, lịch thử nghiệm; không trình bày ý tưởng như dữ liệu thị trường.
- `research-audit`: kiểm tra provenance, ngày, trùng lặp, evidence type, confidence và suy luận quá mức.

### Agents

Mỗi agent phải có nhiệm vụ, phạm vi, công cụ được phép, giới hạn quyền truy cập và output contract. Agent không được giả định Exa/Playwright/TikTok API khả dụng; phải nhận diện tool thực tế và báo `not_available` khi thiếu.

- `market-analyst`: tạo nguồn, observations và market findings.
- `product-researcher`: đối chiếu sản phẩm và ghi trường thương mại khi có nguồn.
- `competitor-researcher`: phân tích public content, không suy ra doanh số/lợi nhuận.
- `research-auditor`: chỉ kiểm tra bằng chứng và trả audit findings; không âm thầm sửa dữ liệu gốc.

## 9. Nguồn dữ liệu và giới hạn truy cập

Nguồn ưu tiên:

1. tài liệu chính thức TikTok/TikTok Shop;
2. tài liệu pháp lý hoặc tổ chức có thẩm quyền;
3. trang sản phẩm/marketplace công khai;
4. nguồn báo chí/nghiên cứu có ngày và tác giả;
5. public TikTok pages khi truy cập hợp lệ;
6. dữ liệu do người dùng cung cấp.

Exa và Playwright chỉ được dùng trong phạm vi quyền truy cập thực tế. Context7 không phải nguồn dữ liệu TikTok mặc định và chỉ dùng sau khi được xác thực nếu cần. TikTok Research API chỉ được dùng khi người dùng có quyền và cấu hình hợp lệ.

Nếu nguồn bị block, partial hoặc không truy cập được:

- ghi source record với trạng thái tương ứng;
- ghi lý do và thời điểm;
- không thay thế bằng số liệu đoán;
- đưa mục đó vào dữ liệu cần thu thập tiếp.

## 10. Xử lý lỗi và tính nhất quán

- Lỗi schema: validator trả lỗi theo record và không xuất bản record đó như finding đã audit.
- URL không truy cập: giữ source metadata, đánh dấu `blocked`/`partial` và tiếp tục với nguồn khác.
- SQLite không đồng bộ: xóa và xây dựng lại từ processed data; không sửa tay SQLite làm nguồn duy nhất.
- Dữ liệu trùng: báo `warning` hoặc `fail` tùy trường hợp; không xóa tự động.
- Thiếu ngày/nguồn: giữ bản ghi ở trạng thái chưa xác minh.
- Agent thất bại: ghi tool/error status trong nhật ký chạy; không tạo kết luận thay thế.
- Kết quả agent mâu thuẫn: giữ các observations riêng, yêu cầu audit đánh dấu xung đột và không gộp thành số duy nhất khi chưa có quy tắc.
- Công cụ web không sẵn sàng: chạy chế độ nhập dữ liệu thủ công hoặc tạo danh sách nguồn cần bổ sung sau.

## 11. Bảo mật và quyền kiểm soát

- Không lưu API key, token, mật khẩu, cookie hoặc thông tin định danh cá nhân vào project.
- Không đưa credential user-level vào báo cáo hoặc dữ liệu raw.
- `.gitignore` phải loại trừ `.venv/`, `.env*`, `credentials/`, `secrets/`, cache và dữ liệu private.
- Không tự gửi dữ liệu ra dịch vụ ngoài, không gọi API trả phí, không đăng nội dung và không thực hiện hành động tài khoản.
- Khi cần cài package, xác nhận trước với người dùng; cài trong `./.venv` và ghi rõ package/version.
- Khi cần bật TikTok API hoặc Context7 OAuth, yêu cầu người dùng thực hiện bước xác thực; không tự xử lý credential.

## 12. Kiểm thử và xác minh

### Kiểm thử tĩnh

- Kiểm tra frontmatter Skills/Agents có `name` và `description`.
- Kiểm tra tất cả đường dẫn nội bộ và template tồn tại.
- Kiểm tra README khớp lệnh chạy thực tế.
- Kiểm tra `.gitignore` loại trừ dữ liệu nhạy cảm và `.venv/`.

### Kiểm thử dữ liệu

- Record hợp lệ được chấp nhận.
- Record thiếu URL, source link, timestamp hoặc evidence type bị báo lỗi.
- Enum sai bị báo lỗi.
- `calculated` thiếu calculation method bị báo lỗi.
- Hypothesis không xuất hiện trong verified findings.
- Duplicate URL/ID được phát hiện.
- SQLite index tái tạo được từ processed CSV/JSON.

### Kiểm thử quy trình

- Nghiên cứu không có công cụ TikTok vẫn xuất báo cáo với phần giới hạn rõ ràng.
- Nghiên cứu có Exa chỉ lưu kết quả có URL và thời điểm truy cập.
- Phân tích video public chỉ dùng metrics quan sát được.
- Audit chạy sau các agent nghiên cứu và không sửa raw data.
- Chạy trong `./.venv/bin/python`, không phụ thuộc Python global.

Phiên bản đầu ưu tiên `unittest` và các script kiểm tra nhỏ từ standard library; không thêm framework test ngoài nếu chưa cần.

## 13. Kế hoạch triển khai theo giai đoạn

### Giai đoạn C — Skills và Agents

Tạo 5 `SKILL.md` và 4 agent instructions, với output contract và giới hạn công cụ.

### Giai đoạn D — Schema và validator

Tạo config, templates, script khởi tạo, validator, duplicate checker và SQLite builder. Tạo `.venv` trước khi chạy script; chưa cài package ngoài.

### Giai đoạn E — Kiểm tra hệ thống

Chạy smoke test, schema test, kiểm tra frontmatter và thử một workflow nhỏ bằng dữ liệu placeholder được đánh dấu, không phải dữ liệu thị trường.

### Giai đoạn F — Nghiên cứu thử nghiệm

Thu thập nguồn công khai về đồ gia dụng thông minh tại Việt Nam. Ghi rõ phạm vi, thời điểm và giới hạn. Chỉ đưa dữ liệu giá/hoa hồng/video nếu xác minh được.

### Giai đoạn G — Audit và báo cáo

Chạy research-auditor, sửa lỗi dữ liệu theo audit, xây SQLite index và xuất báo cáo Markdown gồm 10 ý tưởng video cùng các giả thuyết cần kiểm chứng.

### Giai đoạn H — Hướng dẫn vận hành

Bổ sung README hướng dẫn người mới chạy nghiên cứu mới, thêm nguồn, validate, audit, xuất báo cáo và cập nhật dữ liệu.

## 14. Danh sách file dự kiến

```text
README.md
.gitignore
config/research-policy.md
config/source-policy.md
config/field-definitions.json

templates/source-record.json
templates/observation-record.json
templates/product-record.json
templates/video-record.json
templates/finding-record.json
templates/hypothesis-record.json
templates/research-report.md
templates/audit-report.md

scripts/init_research.py
scripts/validate_records.py
scripts/deduplicate_sources.py
scripts/build_sqlite_index.py
scripts/export_research_summary.py

.claude/skills/market-research/SKILL.md
.claude/skills/product-research/SKILL.md
.claude/skills/competitor-analysis/SKILL.md
.claude/skills/content-strategy/SKILL.md
.claude/skills/research-audit/SKILL.md

.claude/agents/market-analyst.md
.claude/agents/product-researcher.md
.claude/agents/competitor-researcher.md
.claude/agents/research-auditor.md

data/raw/.gitkeep
data/processed/.gitkeep
reports/.gitkeep
```

`data/research.sqlite` và `.venv/` là artifact sinh ra trong quá trình triển khai, không phải file nguồn cần viết tay.

## 15. Rủi ro và cách giảm thiểu

| Rủi ro | Cách giảm thiểu |
|---|---|
| Trang TikTok không truy cập được | Lưu trạng thái block/partial; không bịa metrics; bổ sung nguồn sau |
| Giá/hoa hồng thay đổi theo thời gian | Lưu timestamp và nguồn; không coi là giá hiện tại nếu chưa kiểm tra lại |
| Agent suy luận quá mức | Evidence type, limitations, audit gate và prompt cấm suy diễn doanh số |
| Dữ liệu raw bị sửa | Raw immutable theo quy trình; processed là bản dẫn xuất |
| SQLite lệch CSV | SQLite tái tạo được; CSV/JSON là canonical interchange |
| Python global bị ảnh hưởng | Bắt buộc `./.venv/bin/python`; `.venv/` loại trừ khỏi Git |
| Credential bị đưa vào project | Không nhận credential trong file; loại trừ `.env`, secrets, credentials |
| Scope phình to | Phiên bản đầu không có dashboard, automation tài khoản hoặc paid API |

## 16. Điều kiện chuyển sang kế hoạch triển khai

Spec này được xem là sẵn sàng để review khi:

- mục tiêu, phạm vi và ngoài phạm vi rõ ràng;
- schema có provenance và trạng thái chưa xác minh;
- kiến trúc khớp với yêu cầu Python virtual environment;
- không có yêu cầu dùng TikTok/API khi chưa được cấp quyền;
- có kiểm thử, xử lý lỗi và tiêu chí hoàn tất;
- danh sách file không bao gồm việc ghi đè file hiện có.

Sau khi người dùng review và phê duyệt spec này, bước tiếp theo là tạo implementation plan chi tiết. Chỉ sau khi implementation plan được duyệt mới bắt đầu tạo Skills, Agents, schema files, `.venv` hoặc scripts.
