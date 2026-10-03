---
name: competitor-analysis
description: Phân tích video công khai, định dạng nội dung, hook và cấu trúc kịch bản của kênh đối thủ TikTok Affiliate
---

# Kỹ năng Phân tích Kênh và Video Đối thủ (Competitor Analysis)

Kỹ năng này hướng dẫn phương pháp quan sát, mổ xẻ và học hỏi cấu trúc nội dung từ các video công khai của những nhà sáng tạo nội dung (creator) và kênh đối thủ đang làm affiliate trên TikTok tại Việt Nam.

## Hướng dẫn sử dụng

### Khi nào nên dùng
- Khi cần phân tích 3 giây đầu tiên (hook), cấu trúc dẫn dắt câu chuyện (storytelling), cách trình diễn sản phẩm và lời kêu gọi hành động (CTA) của video công khai.
- Khi cần ghi nhận chỉ số tương tác công khai (lượt xem, lượt thích, lượt chia sẻ) gắn liền với thời điểm quan sát cụ thể.
- Khi cần nhận diện các định dạng video đang thu hút sự chú ý trong một ngách sản phẩm.

### Khi nào không nên dùng
- Không dùng để suy ra doanh số, số đơn hàng hay lợi nhuận của đối thủ từ lượt xem, thích hay bình luận video.
- Không dùng đối với các tài khoản hoặc video không công khai.
- Không dùng để thực hiện các hành vi gây ảnh hưởng tiêu cực đến kênh đối thủ.

## Yêu cầu đầu vào từ người dùng

Để việc phân tích đạt hiệu quả cao, cần cung cấp:
- **market**: Thị trường hoạt động (TikTok Affiliate Việt Nam).
- **geography**: Khu vực địa lý của tệp người xem mục tiêu (Việt Nam).
- **category**: Ngành hàng nội dung cần mổ xẻ (ví dụ: Đồ gia dụng nhà bếp, Đồ công nghệ tiện ích).
- **target audience**: Tệp khán giả mà kênh đối thủ hướng tới.
- **date range**: Khung thời gian xuất bản video hoặc giai đoạn quan sát.
- **research question**: Mục tiêu phân tích (ví dụ: Các video có trên 500k lượt xem của kênh X sử dụng dạng hook thị giác hay câu hỏi thách thức?).

## Phân loại bằng chứng và cam kết trung thực

Mọi dữ liệu phân tích đối thủ phải tuân thủ phân loại 4 loại bằng chứng chuẩn:
- `direct_source`: Số liệu tương tác công khai hiển thị trên giao diện video kèm ngày giờ quan sát, câu thoại nguyên bản của hook hoặc CTA.
- `calculated`: Tỷ lệ tương tác công khai (ví dụ: tỷ lệ lượt thích trên lượt xem) được tính toán chính xác từ các con số direct_source.
- `estimate`: Ước lượng thời lượng phân bổ giữa các phần trong video (ví dụ: hook chiếm 15% thời lượng).
- `hypothesis`: Giả thuyết về lý do vì sao kịch bản đó giữ chân được người xem hoặc cảm xúc mà video gợi lên.

Cam kết trung thực và an toàn:
- Tuyệt đối không bịa đặt số liệu tương tác, tên kênh hoặc trích dẫn sai lời thoại video.
- Mọi dữ liệu phải chỉ rõ nguồn URL video công khai và thời điểm quan sát (`accessed_at`).
- Tuyệt đối không suy ra doanh số hay tỷ lệ chuyển đổi đơn hàng từ lượt xem hoặc tương tác.
- Đánh giá khách quan độ tin cậy `confidence` và ghi nhận rõ ràng các hạn chế `limitations`.

## Quy trình phân tích video đối thủ từng bước

1. **Bước 1: Lựa chọn kênh và video công khai tiêu biểu**
   - Chọn các kênh creator hoặc nhãn hàng công khai hoạt động trong cùng ngách ngành hàng.
2. **Bước 2: Ghi nhận dữ liệu định lượng công khai**
   - Thu thập số lượt xem (view_count), lượt thích (like_count), lượt bình luận (comment_count) và lượt chia sẻ tại thời điểm quan sát.
   - Ghi nhận đường dẫn công khai và thời gian đăng tải video.
3. **Bước 3: Mổ xẻ cấu trúc định tính của kịch bản**
   - **Hook**: Phân tích hình ảnh, âm thanh và lời thoại trong 3 giây đầu.
   - **Storytelling**: Cách đặt vấn đề, tạo xung đột và dẫn dắt câu chuyện.
   - **Product Presentation**: Cách sản phẩm xuất hiện, công năng được phô diễn thực tế hay lồng ghép tinh tế.
   - **Call to Action (CTA)**: Lời kêu gọi nhấn vào giỏ hàng hoặc đường dẫn bio.
   - **Affiliate Disclosure**: Video có gắn nhãn cộng tác thương mại/giỏ hàng công khai hay không.
4. **Bước 4: Đánh giá hạn chế phương pháp luận**
   - Nhận định rõ việc video có thể được chạy quảng cáo trả phí (TikTok Boost/Spark Ads) khiến chỉ số tương tác cao mà không phản ánh hoàn toàn lưu lượng tự nhiên; ghi vào `limitations`.
5. **Bước 5: Lưu trữ có hệ thống**
   - Xuất dữ liệu vào bảng `videos`, `competitors` và bảng `findings`.

## Chuẩn dữ liệu đầu ra tái sử dụng

Dữ liệu ghi nhận từ kỹ năng phải tuân thủ đúng các trường chuẩn:
- `finding`: Nhận định súc tích về kỹ thuật kịch bản, điểm nổi bật của hook hoặc phong cách trình diễn.
- `source_url`: URL video hoặc profile công khai của kênh đối thủ.
- `accessed_at`: Thời gian quan sát thực tế (ISO UTC: YYYY-MM-DDTHH:MM:SSZ).
- `published_at`: Thời điểm video được đăng tải công khai trên nền tảng.
- `observed_data`: Dữ liệu số đo cụ thể tại thời điểm xem (ví dụ: view: 150000, like: 12000, hook_type: visual_shock).
- `collection_method`: Phương thức thu thập (ví dụ: public_video_inspection).
- `confidence`: Mức độ tin cậy của thông tin (high, medium, low, unverified).
- `limitations`: Các yếu tố gây nhiễu chỉ số (quảng cáo trả phí, video xóa, thay đổi thuật toán).

## Thiếu dữ liệu

Khi trang video hoặc kênh bị ẩn, bị xóa, hoặc không thể truy cập qua giao diện công khai thông thường:
- Ghi nhận trạng thái `Chưa có dữ liệu được xác minh` hoặc đánh dấu `not_available`.
- Không cố gắng phỏng đoán số liệu tương tác của video khi không trực tiếp quan sát được.
- Đưa các câu hỏi suy đoán về hiệu quả bán hàng vào danh sách giả thuyết (`hypothesis`) cần kiểm chứng độc lập.
