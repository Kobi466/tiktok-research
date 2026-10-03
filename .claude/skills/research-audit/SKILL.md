---
name: research-audit
description: Kiểm toán tính trung thực, tính hợp lệ của nguồn và phân loại bằng chứng trong toàn bộ dữ liệu nghiên cứu
---

# Kỹ năng Kiểm toán Nghiên cứu (Research Audit)

Kỹ năng này hướng dẫn quy trình kiểm định chất lượng, rà soát tính hợp lệ của nguồn gốc dữ liệu, kiểm tra tính toàn vẹn của các liên kết và đảm bảo hệ thống nghiên cứu TikTok Affiliate tuân thủ nghiêm ngặt các tiêu chuẩn khoa học và đạo đức dữ liệu.

## Hướng dẫn sử dụng

### Khi nào nên dùng
- Khi cần kiểm tra chéo các nguồn dữ liệu trước khi xuất bản báo cáo nghiên cứu chính thức.
- Khi cần phát hiện các khẳng định thiếu căn cứ, các trường hợp suy diễn doanh số trái phép từ lượt xem/tương tác.
- Khi cần rà soát tính trùng lặp của nguồn tin và kiểm tra sự nhất quán giữa các bảng dữ liệu.

### Khi nào không nên dùng
- Không dùng để tự động sửa chữa hoặc bóp méo dữ liệu gốc của nhà nghiên cứu.
- Không dùng để hợp thức hóa các phát hiện không có nguồn gốc kiểm chứng.
- Không dùng thay thế cho việc xác thực nguồn tại thực địa khi có nghi vấn gian lận.

## Yêu cầu đầu vào từ người dùng

Trước khi thực hiện kiểm toán dữ liệu, cần chuẩn bị:
- **market**: Không gian dữ liệu thị trường cần kiểm toán (TikTok Affiliate Việt Nam).
- **geography**: Phạm vi địa lý của các kết quả nghiên cứu.
- **category**: Nhóm ngành hàng mà dữ liệu đang phản ánh.
- **target audience**: Tệp đối tượng khách hàng trong hồ sơ nghiên cứu.
- **date range**: Khoảng thời gian thu thập dữ liệu cần rà soát kiểm toán.
- **research question**: Trọng tâm kiểm toán (ví dụ: Toàn bộ bảng giá sản phẩm và tỷ lệ hoa hồng có nguồn gốc direct_source hợp lệ không?).

## Phân loại bằng chứng và nguyên tắc kiểm toán độc lập

Kiểm toán viên rà soát việc sử dụng 4 loại bằng chứng chuẩn:
- `direct_source`: Có URL xác thực, có ngày giờ truy cập, dữ liệu trích dẫn đúng nguyên văn, không thêm bớt.
- `calculated`: Có công thức tính rõ ràng từ số liệu gốc, không có lỗi số học hoặc logic.
- `estimate`: Có phương pháp luận ước tính hợp lý và nêu rõ các biến giả định.
- `hypothesis`: Được tách riêng vào khu vực giả thuyết, không bị đánh đồng với kết quả thực tế.

Nguyên tắc an toàn và kiểm toán nghiêm ngặt:
- Tuyệt đối không bịa đặt biên bản kiểm toán hoặc che giấu các sai sót dữ liệu.
- Kiểm tra tính xác thực của nguồn trích dẫn và thời gian truy cập.
- Bắt buộc gắn cảnh báo nếu phát hiện hành vi không suy ra doanh số mà lại ước tính doanh thu tùy tiện từ lượt xem video.
- Đánh giá mức độ tin cậy `confidence` của từng bằng chứng và báo cáo đầy đủ các rủi ro `limitations`.

## Quy trình kiểm toán nghiên cứu từng bước

1. **Bước 1: Rà soát tính khả dụng và hợp lệ của nguồn**
   - Kiểm tra định dạng URL (phải bắt đầu bằng http:// hoặc https://), tên miền công khai hợp lệ.
   - Kiểm tra tính đầy đủ của trường `accessed_at` và `source_id`.
2. **Bước 2: Kiểm tra tính toàn vẹn của mã định danh và tính trùng lặp**
   - Kiểm tra định dạng chuẩn: `SRC-`, `OBS-`, `PRD-`, `CMP-`, `VID-`, `FND-`, `HYP-`, `AUD-`.
   - Chạy script kiểm tra trùng lặp để phát hiện các URL bị thu thập lặp lại.
3. **Bước 3: Phân định ranh giới giữa sự thật và giả thuyết**
   - Đảm bảo các phát hiện chưa được kiểm chứng không xuất hiện trong danh mục phát hiện có bằng chứng (`findings`).
   - Đảm bảo các sản phẩm không có giá xác minh không bị gán giá trị số 0 hoặc số ảo.
4. **Bước 4: Tổng hợp phát hiện kiểm toán và phân loại mức độ nghiêm trọng**
   - Phân loại lỗi theo các mức: thông tin (`info`), cảnh báo (`warning`), nghiêm trọng (`fail` hoặc `error`).
5. **Bước 5: Đưa ra kết luận kiểm toán tổng thể**
   - Đưa ra kết luận tổng thể theo 3 mức độ: `pass` (đạt chuẩn), `warning` (cần bổ sung thông tin), hoặc `fail` (không đạt chuẩn, cần thu thập lại dữ liệu).

## Chuẩn dữ liệu đầu ra tái sử dụng

Mỗi bản ghi kiểm toán phải có cấu trúc chuẩn:
- `finding`: Nội dung phát hiện kiểm toán, nêu rõ vấn đề hoặc sự sai lệch phát hiện được.
- `source_url`: URL của nguồn bị kiểm toán hoặc mã bản ghi liên quan (ví dụ: SRC-001, PRD-002).
- `accessed_at`: Thời gian thực hiện kiểm toán (ISO UTC: YYYY-MM-DDTHH:MM:SSZ).
- `published_at`: Thời điểm phát hành của tài liệu liên quan (nếu có).
- `observed_data`: Dữ liệu sai lệch quan sát được (ví dụ: URL không truy cập được, thiếu trường ngày giờ).
- `collection_method`: Phương pháp kiểm toán (ví dụ: automated_schema_check, cross_reference_verification).
- `confidence`: Mức độ chắc chắn của kết luận kiểm toán (high, medium, low, unverified).
- `limitations`: Các hạn chế kỹ thuật trong quá trình kiểm toán.

## Thiếu dữ liệu

Nếu hồ sơ nghiên cứu thiếu nguồn kiểm chứng độc lập hoặc thông tin không thể xác minh:
- Ghi nhận trạng thái là `Chưa có dữ liệu được xác minh`.
- Đánh dấu trạng thái kiểm toán là `warning` hoặc `fail` tùy thuộc vào tầm quan trọng của trường dữ liệu thiếu.
- Bắt buộc yêu cầu người nghiên cứu thu thập bổ sung bằng chứng trước khi xuất bản báo cáo chính thức.
