---
name: market-research
description: Nghiên cứu nhu cầu thị trường và hành vi tiêu dùng TikTok Affiliate Việt Nam từ nguồn công khai xác minh
---

# Kỹ năng Nghiên cứu Thị trường (Market Research)

Kỹ năng này hướng dẫn quy trình nghiên cứu nhu cầu khách hàng, xu hướng tiêu dùng và bài toán thị trường cho ngành hàng TikTok Affiliate tại Việt Nam từ các nguồn dữ liệu công khai, minh bạch.

## Hướng dẫn sử dụng

### Khi nào nên dùng
- Khi cần khảo sát nhu cầu, nỗi đau (pain points) và hành vi của người tiêu dùng trong một ngành hàng cụ thể.
- Khi cần thu thập các báo cáo thị trường công khai, bài viết nghiên cứu uy tín và dữ liệu thống kê chính thức.
- Khi cần xác định các tín hiệu nhu cầu thực tế trước khi lựa chọn sản phẩm affiliate.

### Khi nào không nên dùng
- Không dùng để đoán mò quy mô thị trường khi không có nguồn xác minh.
- Không dùng để thu thập thông tin cá nhân hoặc dữ liệu riêng tư.
- Không dùng khi chưa xác định được câu hỏi nghiên cứu cụ thể.

## Yêu cầu đầu vào từ người dùng

Trước khi bắt đầu nghiên cứu, cần xác định rõ các thông tin đầu vào sau:
- **market**: Thị trường mục tiêu (mặc định: TikTok Shop Affiliate Việt Nam).
- **geography**: Phạm vi địa lý (ví dụ: Toàn quốc, thành thị, nông thôn tại Việt Nam).
- **category**: Ngành hàng nghiên cứu (ví dụ: Gia dụng thông minh, Chăm sóc sắc đẹp, Thời trang).
- **target audience**: Chân dung tệp khách hàng mục tiêu (độ tuổi, giới tính, lối sống, thói quen).
- **date range**: Khoảng thời gian thu thập dữ liệu (ví dụ: Q3-Q4/2026, 12 tháng gần nhất).
- **research question**: Câu hỏi nghiên cứu cụ thể cần giải quyết (ví dụ: Nhu cầu sử dụng nồi chiên không dầu của người độc thân tại đô thị).

## Phân loại bằng chứng và nguyên tắc trung thực

Mọi thông tin ghi nhận phải được phân loại rõ ràng theo một trong 4 loại bằng chứng chuẩn:
1. `direct_source`: Dữ liệu trích dẫn nguyên văn từ tài liệu, báo cáo hoặc trang web công khai có nguồn gốc rõ ràng.
2. `calculated`: Dữ liệu được tính toán từ các số liệu direct_source thông qua công thức toán học minh bạch.
3. `estimate`: Dữ liệu ước tính hợp lý dựa trên phương pháp luận cụ thể kèm giả định rõ ràng.
4. `hypothesis`: Ý kiến, giả thuyết hoặc suy đoán sơ bộ cần được kiểm chứng thêm.

Nguyên tắc bắt buộc:
- Tuyệt đối không bịa đặt số liệu, không phát minh thông tin khảo sát hoặc báo cáo không có thật.
- Ghi nhận đầy đủ nguồn gốc, thời điểm truy cập và đường dẫn minh bạch.
- Tuyệt đối không suy ra doanh số hoặc lợi nhuận từ lượt xem, lượt thích hoặc bình luận video.
- Mọi đánh giá phải gắn liền với mức độ tin cậy `confidence` (high, medium, low, unverified) và ghi rõ các giới hạn `limitations`.

## Quy trình nghiên cứu từng bước

1. **Bước 1: Xác định phạm vi và câu hỏi nghiên cứu**
   - Làm rõ market, geography, category, target audience, date range và research question.
2. **Bước 2: Tìm kiếm và xác thực nguồn công khai**
   - Thu thập báo cáo từ các hiệp hội thương mại, cơ quan nghiên cứu thị trường, hoặc bài phân tích báo chí uy tín.
   - Ghi lại URL công khai, ngày phát hành và ngày truy cập.
3. **Bước 3: Trích xuất quan sát và phân loại bằng chứng**
   - Tách biệt rõ ràng giữa dữ liệu quan sát trực tiếp (`direct_source`) và các phân tích suy luận (`calculated`, `estimate`, `hypothesis`).
4. **Bước 4: Đánh giá độ tin cậy và hạn chế**
   - Đánh giá mức độ đại diện của mẫu khảo sát, phương pháp thống kê và ghi nhận `limitations`.
5. **Bước 5: Lập hồ sơ phát hiện chuẩn**
   - Xuất dữ liệu theo đúng cấu trúc đầu ra chuẩn để tích hợp vào hệ thống lưu trữ.

## Chuẩn dữ liệu đầu ra tái sử dụng

Mỗi phát hiện nghiên cứu thị trường phải cung cấp đầy đủ các trường thông tin chuẩn:
- `finding`: Nội dung phát hiện cô đọng, khách quan, mô tả đúng bản chất dữ liệu.
- `source_url`: Liên kết nguồn công khai nơi thông tin được xuất bản.
- `accessed_at`: Thời gian truy cập nguồn dữ liệu (định dạng ISO UTC: YYYY-MM-DDTHH:MM:SSZ).
- `published_at`: Thời gian xuất bản của nguồn (nếu có, để trống nếu không rõ).
- `observed_data`: Dữ liệu thực tế quan sát được (trích dẫn nguyên bản hoặc số liệu đo đạc).
- `collection_method`: Phương pháp thu thập dữ liệu (ví dụ: public_web_search, official_report).
- `confidence`: Mức độ tin cậy của thông tin (high, medium, low, unverified).
- `limitations`: Các giới hạn phương pháp luận, sai số hoặc rủi ro về độ chính xác.

## Thiếu dữ liệu

Khi không tìm thấy dữ liệu xác minh công khai cho bất kỳ chỉ số hoặc câu hỏi nghiên cứu nào:
- Ghi nhận trạng thái rõ ràng là `Chưa có dữ liệu được xác minh` hoặc để trống trường thông tin tương ứng.
- Tuyệt đối không tự suy diễn số liệu thị trường để lấp đầy báo cáo.
- Đưa các câu hỏi chưa được giải đáp vào danh mục câu hỏi tồn đọng hoặc giả thuyết (`hypothesis`) cần kiểm chứng tiếp trong các chu kỳ nghiên cứu sau.
