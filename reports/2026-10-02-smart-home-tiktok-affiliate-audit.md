# Biên bản Kiểm toán Nghiên cứu: Thị trường TikTok Affiliate Đồ gia dụng thông minh tại Việt Nam

- **Hồ sơ kiểm toán:** `reports/2026-10-02-smart-home-tiktok-affiliate-audit.md`
- **Thời điểm kiểm toán:** 2026-10-02T18:45:00Z
- **Vai trò thực hiện:** Kiểm toán viên Nghiên cứu độc lập (Research Auditor)
- **Đối tượng kiểm toán:** Toàn bộ dữ liệu thô tại `data/raw/2026-10-02-smart-home-source-captures/`, 8 bảng dữ liệu chuẩn tại `data/processed/`, chỉ mục SQLite `data/research.sqlite` và báo cáo tổng hợp `reports/2026-10-02-smart-home-tiktok-affiliate.md`.

---

## 1. Kết luận kiểm toán tổng thể

- **Kết quả chung (Audit Verdict):** **PASS**
- **Trạng thái tuân thủ:**
  - Không phát hiện bất kỳ trường hợp nào suy đoán doanh số, doanh thu hay GMV từ lượt xem video, lượt thích hoặc bình luận.
  - Phân tách triệt để giữa dữ kiện có bằng chứng (`direct_source`, `calculated`, `estimate`) và các ý tưởng video dạng giả thuyết (`hypothesis`).
  - Toàn bộ giá niêm yết và hoa hồng chưa xác minh được giữ nguyên trạng thái trống, hiển thị trung thực là `Chưa có giá xác minh` và `-`, không bịa đặt số liệu hoặc gán giá trị `0 VND`.
  - Toàn bộ 8 bảng dữ liệu chuẩn vượt qua kiểm tra cấu trúc với **0 lỗi (errors)** và **0 cảnh báo (warnings)** khi chạy với cờ `--fail-on-warning`.
  - Kiểm toán trùng lặp ghi nhận **0 nhóm nguồn trùng lặp (duplicate groups)** trên toàn bộ tập dữ liệu.

---

## 2. Phạm vi và phương pháp kiểm toán

Kiểm toán viên đã tiến hành rà soát theo nguyên tắc kiểm toán chỉ đọc (read-only), không chỉnh sửa đè dữ liệu gốc:
1. **Kiểm tra tính toàn vẹn và khả năng truy cập của nguồn:** Đối soát 8 tệp ghi chép thô tại `data/raw/2026-10-02-smart-home-source-captures/` với các bản ghi trong `sources.csv`. Xác minh URL tuyệt đối (`http`/`https`), trạng thái truy cập (`accessible`), thời điểm truy cập (`accessed_at`) và mã băm nội dung (`content_hash`).
2. **Kiểm tra quy chuẩn cấu trúc và quan hệ khóa:** Sử dụng script kiểm tra `scripts/validate_records.py` đối chiếu 8 bảng dữ liệu với lược đồ gốc `config/field-definitions.json`. Xác minh các liên kết khóa ngoại (`source_id`, `competitor_id`, `commission_source_id`) và mảng JSON tham chiếu (`source_ids`, `observation_ids`, `basis_finding_ids`).
3. **Kiểm toán trùng lặp:** Thực thi `scripts/deduplicate_sources.py` để quét trùng lặp cả về mã định danh (`source_id`) và địa chỉ liên kết (`url`).
4. **Kiểm toán chỉ mục truy vấn SQLite:** Kiểm tra tính toàn vẹn của tệp cơ sở dữ liệu `data/research.sqlite` sau khi xây dựng lại thông qua `PRAGMA integrity_check` và đối soát số lượng dòng trên 8 bảng.
5. **Kiểm toán tính trung thực trong báo cáo Markdown:** Rà soát tệp `reports/2026-10-02-smart-home-tiktok-affiliate.md` theo 10 tiêu đề bắt buộc, đảm bảo các giả thuyết không bị đưa vào phần phát hiện có bằng chứng và các chỉ số video đều gắn kèm mốc thời gian `observed_at`.

---

## 3. Chi tiết kết quả kiểm tra từng cấu phần

### 3.1. Bảng dữ liệu nguồn (sources) và quan sát (observations)
- **Số lượng nguồn:** 8 nguồn dữ liệu công khai hợp lệ từ các đơn vị phân tích thị trường uy tín (Metric Analytics, Metric.vn), chuyên gia tiếp thị liên kết (Mobivision, Allymatic), cộng đồng đánh giá thiết bị (VnReview) và kênh đánh giá độc lập (Tech Z Official, Vật Vờ Studio).
- **Trạng thái truy cập:** 8/8 nguồn đạt trạng thái `accessible`, phương pháp thu thập hoàn toàn công khai, không xâm phạm rào cản kỹ thuật hay yêu cầu xác thực riêng tư.
- **Số lượng quan sát:** 12 bản ghi quan sát có trích lục bằng chứng nguyên bản (`evidence_excerpt`), liên kết đúng mã nguồn cha và gắn nhãn độ tin cậy `high`.

### 3.2. Bảng sản phẩm (products) và tính trung thực thương mại
- **Số lượng sản phẩm:** 5 sản phẩm thuộc ngành hàng đồ gia dụng thông minh tại Việt Nam.
- **Kiểm toán giá bán:**
  - `PRD-001` (Ecovacs Deebot T80 Max Omni): Giá xác minh 15.900.000 VND (nguồn SRC-005).
  - `PRD-002` (Xiaomi Robot Vacuum 5 Pro): Giá xác minh 20.000.000 VND (nguồn SRC-006).
  - `PRD-003` (Tủ lạnh Aqua Multi Door 515L): Giá xác minh 24.800.000 VND (nguồn SRC-007).
  - `PRD-004` (Nồi chiên không dầu Bear): Để trống giá do chưa có con số xác minh chính thức từ hãng; báo cáo xuất hiện đúng chuỗi `Chưa có giá xác minh`.
  - `PRD-005` (Robot Roborock Qrevo Edge 2 Flow): Để trống giá; báo cáo xuất hiện đúng chuỗi `Chưa có giá xác minh`.
  - **Không có sản phẩm nào bị gán số 0 hoặc số bịa đặt.**
- **Kiểm toán hoa hồng:** Toàn bộ 5 sản phẩm đều để trống tỷ lệ hoa hồng do các nguồn công khai chưa công bố bảng chia hoa hồng chính thức của từng SKU trên Seller Center. Hệ thống tuân thủ nghiêm ngặt quy tắc không suy đoán tỷ lệ phần trăm hoa hồng.

### 3.3. Bảng đối thủ (competitors) và video công khai (videos)
- **Đối thủ quan sát:** 4 đơn vị/nhà sáng tạo nội dung công khai (Tech Z Official, VnReview, Andy Huỳnh - Vật Vờ Studio, Mobivision).
- **Video công khai:** 3 video đánh giá thực tế.
- **Ranh giới an toàn:** Tất cả các trường chỉ số (`views_observed`, `likes_observed`, `comments_observed`) đều được kiểm tra đi kèm mốc thời gian quan sát cụ thể (`observed_at: 2026-10-02T15:00:00Z`). Không có bất kỳ kết luận nào suy diễn doanh thu của nhà bán từ các chỉ số này.

### 3.4. Bảng phát hiện có bằng chứng (findings)
- **Số lượng phát hiện:** 8 phát hiện có bằng chứng.
- **Phân loại bằng chứng:**
  - `direct_source`: 7 phát hiện (FND-001, FND-002, FND-004, FND-005, FND-006, FND-007, FND-008).
  - `calculated`: 1 phát hiện (FND-003) có nêu rõ phương pháp tính toán: `Cộng thị phần doanh số nhóm Đồ gia dụng nhà bếp (35.6%) và Thiết bị gia dụng nhỏ (32.1%) từ báo cáo Metric Analytics: 35.6% + 32.1% = 67.7%`.
  - Toàn bộ đều ở trạng thái `audited` hoặc `accepted`.

### 3.5. Bảng giả thuyết nghiên cứu (hypotheses)
- **Số lượng giả thuyết:** Đúng 10 ý tưởng video được cấu trúc hóa thành giả thuyết khoa học có thể kiểm chứng (HYP-001 đến HYP-010).
- **Tính đầy đủ:** Mỗi giả thuyết đều xác định rõ đối tượng mục tiêu (`target_audience`), kịch bản thử nghiệm đối chứng (`proposed_test`), chỉ số thành công định lượng (`success_metric`), dữ liệu cần thu thập (`required_data`) và các giới hạn kỹ thuật (`limitations`).
- **Phân tách dữ liệu:** Tất cả đều ở trạng thái `unverified` và được xếp riêng vào Mục 7 của báo cáo tổng hợp.

### 3.6. Bảng kiểm toán nội bộ (audit_findings)
- **Số lượng bản ghi kiểm toán:** 5 bản ghi kiểm toán chuẩn (AUD-001 đến AUD-005) bao quát các quy tắc: khả năng tiếp cận nguồn, tính nhất quán giá/tiền tệ, nguyên tắc không suy diễn doanh số từ mạng xã hội, nguồn gốc hoa hồng tiếp thị và phân tách giả thuyết.

---

## 4. Báo cáo cấu trúc JSON theo hợp đồng Research Auditor

```json
{
  "tool_status": {
    "validation_script": "available",
    "deduplication_script": "available",
    "sqlite_builder": "available",
    "summary_exporter": "available"
  },
  "audit_status": "pass",
  "audit_findings": [
    {
      "audit_id": "AUD-001",
      "severity": "info",
      "target_id": "SRC-001",
      "message": "Nguồn phân tích thị trường Metric Analytics hợp lệ, truy cập công khai và có thời gian truy cập đầy đủ."
    },
    {
      "audit_id": "AUD-002",
      "severity": "info",
      "target_id": "PRD-004",
      "message": "Sản phẩm chưa có giá xác minh được để trống giá và tiền tệ, hiển thị trung thực là 'Chưa có giá xác minh', không bịa đặt số liệu."
    },
    {
      "audit_id": "AUD-003",
      "severity": "info",
      "target_id": "VID-001",
      "message": "Chỉ số tương tác video công khai được định danh rõ mốc thời gian observed_at, không suy diễn doanh số thương mại."
    },
    {
      "audit_id": "AUD-004",
      "severity": "info",
      "target_id": "PRD-001",
      "message": "Tỷ lệ hoa hồng chưa có nguồn đối soát được để trống trung thực, không tự tiện suy đoán."
    },
    {
      "audit_id": "AUD-005",
      "severity": "info",
      "target_id": "HYP-001",
      "message": "10 ý tưởng video được phân loại là giả thuyết chưa xác minh (unverified) và phân tách hoàn toàn khỏi các phát hiện thực tế."
    }
  ],
  "sources": [
    {"source_id": "SRC-001", "status": "valid"},
    {"source_id": "SRC-002", "status": "valid"},
    {"source_id": "SRC-003", "status": "valid"},
    {"source_id": "SRC-004", "status": "valid"},
    {"source_id": "SRC-005", "status": "valid"},
    {"source_id": "SRC-006", "status": "valid"},
    {"source_id": "SRC-007", "status": "valid"},
    {"source_id": "SRC-008", "status": "valid"}
  ],
  "observations": [
    {"observation_id": "OBS-001", "provenance_checked": true},
    {"observation_id": "OBS-002", "provenance_checked": true},
    {"observation_id": "OBS-003", "provenance_checked": true},
    {"observation_id": "OBS-004", "provenance_checked": true},
    {"observation_id": "OBS-005", "provenance_checked": true},
    {"observation_id": "OBS-006", "provenance_checked": true},
    {"observation_id": "OBS-007", "provenance_checked": true},
    {"observation_id": "OBS-008", "provenance_checked": true},
    {"observation_id": "OBS-009", "provenance_checked": true},
    {"observation_id": "OBS-010", "provenance_checked": true},
    {"observation_id": "OBS-011", "provenance_checked": true},
    {"observation_id": "OBS-012", "provenance_checked": true}
  ],
  "findings": [
    {"finding_id": "FND-001", "evidence_type": "direct_source", "audit_verdict": "verified"},
    {"finding_id": "FND-002", "evidence_type": "direct_source", "audit_verdict": "verified"},
    {"finding_id": "FND-003", "evidence_type": "calculated", "audit_verdict": "verified"},
    {"finding_id": "FND-004", "evidence_type": "direct_source", "audit_verdict": "verified"},
    {"finding_id": "FND-005", "evidence_type": "direct_source", "audit_verdict": "verified"},
    {"finding_id": "FND-006", "evidence_type": "direct_source", "audit_verdict": "verified"},
    {"finding_id": "FND-007", "evidence_type": "direct_source", "audit_verdict": "verified"},
    {"finding_id": "FND-008", "evidence_type": "direct_source", "audit_verdict": "verified"}
  ],
  "hypotheses": [
    {"hypothesis_id": "HYP-001", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-002", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-003", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-004", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-005", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-006", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-007", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-008", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-009", "status": "properly_segregated"},
    {"hypothesis_id": "HYP-010", "status": "properly_segregated"}
  ],
  "limitations": [
    "Biên bản kiểm toán căn cứ trên dữ liệu tĩnh thu thập ngày 2026-10-02.",
    "Chỉ số video công khai chỉ phản ánh trạng thái tại thời điểm quan sát cụ thể (observed_at).",
    "Tỷ lệ hoa hồng thực tế cần kiểm chứng thêm từ TikTok Shop Seller Center của từng nhà phân phối khi triển khai chiến dịch chính thức."
  ]
}
```

---

## 5. Khuyến nghị cho các chu kỳ nghiên cứu tiếp theo

1. **Theo dõi chính sách hoa hồng động:** Định kỳ 30 ngày một lần kiểm tra tỷ lệ hoa hồng Shop Ads và Standard Commission trên các gian hàng Mall đồ gia dụng để cập nhật FND-006.
2. **Đối chứng thử nghiệm nội dung:** Khi triển khai các video theo giả thuyết HYP-001 đến HYP-010, cần lưu trữ báo cáo retention rate từ TikTok Creator Studio vào `data/raw/` trước khi chuyển trạng thái giả thuyết sang `supported` hoặc `rejected`.
3. **Mở rộng nguồn dữ liệu giá niêm yết:** Thu thập giá thực tế của các dòng nồi chiên không dầu và robot tầm trung qua các phiên bán hàng chính hãng để hoàn thiện trường `price_value` cho PRD-004 và PRD-005.
