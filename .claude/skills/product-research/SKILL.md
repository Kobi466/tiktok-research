---
name: product-research
description: Đánh giá tiềm năng sản phẩm, bài toán thương mại và điều kiện làm affiliate trên TikTok Shop Việt Nam
---

# Kỹ năng Nghiên cứu Sản phẩm (Product Research)

Kỹ năng này hướng dẫn quy trình phát hiện, thẩm định chất lượng và đánh giá tiềm năng thương mại của các sản phẩm phục vụ chiến dịch TikTok Affiliate tại Việt Nam từ các nguồn công khai có thể kiểm chứng.

## Hướng dẫn sử dụng

### Khi nào nên dùng
- Khi cần thẩm định một sản phẩm cụ thể về tính giải quyết vấn đề, lợi ích nổi bật và tiềm năng trình diễn trên video ngắn.
- Khi cần kiểm tra giá bán niêm yết công khai, chính sách hoa hồng affiliate chính thức từ các sàn thương mại điện tử hoặc mạng lưới tiếp thị liên kết.
- Khi cần đánh giá mức độ phù hợp của sản phẩm với thị hiếu người dùng TikTok tại Việt Nam.

### Khi nào không nên dùng
- Không dùng để tự suy đoán mức hoa hồng hoặc giá bán khi chưa có thông tin xác thực từ nhà bán hàng hoặc sàn.
- Không dùng để suy đoán số lượng đã bán từ số lượng video hoặc tương tác mạng xã hội.
- Không dùng để thực hiện các hành vi mua hàng tự động hay can thiệp trái phép vào hệ thống phân phối.

## Yêu cầu đầu vào từ người dùng

Trước khi triển khai nghiên cứu sản phẩm, cần làm rõ:
- **market**: Thị trường mục tiêu (TikTok Shop Affiliate Việt Nam).
- **geography**: Khu vực phân phối địa lý (Việt Nam, giao hàng toàn quốc hoặc khu vực cụ thể).
- **category**: Ngành hàng sản phẩm (ví dụ: Điện gia dụng thông minh, Đồ chơi giáo dục, Mỹ phẩm).
- **target audience**: Đối tượng người mua và người dùng cuối mà sản phẩm hướng tới.
- **date range**: Thời gian tiến hành thẩm định và thu thập dữ liệu giá/hoa hồng.
- **research question**: Mục tiêu nghiên cứu (ví dụ: Sản phẩm robot hút bụi phân khúc 3-5 triệu có tỷ lệ hoa hồng cạnh tranh và góc quay hấp dẫn không?).

## Phân loại bằng chứng và nguyên tắc an toàn dữ liệu

Mọi phát hiện về sản phẩm cần được dán nhãn theo đúng 4 nhóm bằng chứng chuẩn:
- `direct_source`: Giá bán, tỷ lệ hoa hồng hoặc thông số kỹ thuật được trích xuất trực tiếp từ trang sản phẩm công khai hoặc thông cáo chính thức của nhà cung cấp.
- `calculated`: Tỷ suất lợi nhuận ước tính hoặc mức hoa hồng tuyệt đối được tính toán minh bạch từ giá và phần trăm hoa hồng direct_source.
- `estimate`: Ước tính chi phí vận chuyển, chi phí bao bì dựa trên thông số kích thước và trọng lượng sản phẩm.
- `hypothesis`: Giả thuyết về góc nhìn trình diễn sản phẩm (demo video) hoặc nhóm khách hàng tiềm năng.

Nguyên tắc an toàn bắt buộc:
- Tuyệt đối không bịa đặt tên sản phẩm, mã SKU, giá tiền hay điều khoản hoa hồng.
- Ghi rõ nguồn trích dẫn kèm ngày giờ truy cập.
- Tuyệt đối không suy ra doanh số thực tế từ lượt xem hay lượt thích video liên quan.
- Mỗi bản ghi sản phẩm phải có mức độ tin cậy `confidence` rõ ràng và công khai các điểm `limitations`.

## Quy trình thẩm định sản phẩm từng bước

1. **Bước 1: Thu thập thông tin sản phẩm công khai**
   - Xác định tên chính xác, mã SKU, thương hiệu, nhà sản xuất và liên kết sản phẩm công khai.
2. **Bước 2: Thẩm định công năng và tính phù hợp video**
   - Xác định bài toán cốt lõi mà sản phẩm giải quyết và các tính năng có thể quay cận cảnh, thử nghiệm trực quan (visual hook).
3. **Bước 3: Thu thập dữ liệu thương mại có kiểm chứng**
   - Kiểm tra giá bán niêm yết (kèm đơn vị tiền tệ VND).
   - Kiểm tra tỷ lệ hoa hồng niêm yết công khai trên TikTok Shop Affiliate hoặc nền tảng tiếp thị.
   - Nếu không có nguồn công khai xác minh, để trống trường giá hoặc hoa hồng.
4. **Bước 4: Đánh giá hạn chế và rủi ro thương mại**
   - Xem xét các phản hồi tiêu cực công khai, chính sách bảo hành, giấy phép công bố và ghi nhận `limitations`.
5. **Bước 5: Chuẩn hóa hồ sơ phát hiện**
   - Xuất dữ liệu theo đúng định dạng chuẩn để nhập vào bảng `products` hoặc `findings`.

## Chuẩn dữ liệu đầu ra tái sử dụng

Dữ liệu đầu ra của mỗi phát hiện sản phẩm phải bao gồm các trường chuẩn:
- `finding`: Tóm tắt đánh giá sản phẩm, điểm mạnh, điểm yếu và tính khả thi.
- `source_url`: URL trang sản phẩm hoặc tài liệu chính thức được tham chiếu.
- `accessed_at`: Thời điểm kiểm tra thông tin (ISO UTC: YYYY-MM-DDTHH:MM:SSZ).
- `published_at`: Thời điểm cập nhật giá/chính sách của nhà bán hàng (nếu có).
- `observed_data`: Dữ liệu quan sát thực tế (thông số, giá, hoa hồng nguyên bản).
- `collection_method`: Phương thức thu thập (ví dụ: public_shop_page_inspection).
- `confidence`: Đánh giá mức độ tin cậy (high, medium, low, unverified).
- `limitations`: Các hạn chế về nguồn tin, thời hạn áp dụng của giá khuyến mãi.

## Thiếu dữ liệu

Trong trường hợp không tìm thấy nguồn xác minh công khai cho giá bán hoặc tỷ lệ hoa hồng:
- Bắt buộc để trống trường dữ liệu hoặc ghi rõ `Chưa có dữ liệu được xác minh`.
- Không điền giá số `0` hoặc ước lượng mức hoa hồng tùy tiện.
- Đánh dấu trạng thái kiểm toán là chưa xác minh và chuyển các giả định doanh thu vào danh sách giả thuyết (`hypothesis`).
