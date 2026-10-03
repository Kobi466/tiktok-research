# Chính sách nguồn

## Thứ tự ưu tiên nguồn

Ưu tiên nguồn trực tiếp, chính thức và có thể truy xuất từ đối tượng được nghiên cứu. Tiếp theo là nguồn công bố uy tín có ngày xuất bản hoặc ngữ cảnh rõ ràng. Kết quả tìm kiếm, bản xem trước và nguồn tổng hợp chỉ dùng để định hướng hoặc làm bằng chứng khi nội dung liên quan có thể được ghi nhận chính xác cùng giới hạn.

## Trạng thái truy cập

- `accessible`: Nội dung liên quan có thể truy cập và ghi nhận đầy đủ ở phạm vi cần thiết.
- `partial`: Chỉ truy cập hoặc ghi nhận được một phần nội dung liên quan.
- `blocked`: Không thể truy cập nội dung cần thiết vì chặn truy cập, đăng nhập, giới hạn kỹ thuật hoặc điều kiện tương tự.
- `not_verified`: Chưa xác minh được khả năng truy cập hoặc nội dung của nguồn.

## Phương thức được phép

Chỉ được dùng các phương thức sau: `exa_search`, `web_fetch`, `browser`, `manual`, và `api` khi đã được ủy quyền. Phải lưu phương thức đã dùng cùng bản ghi nguồn.

## Xử lý trang bị chặn

Không được suy đoán nội dung của trang bị chặn. Lưu URL, thời điểm truy cập, trạng thái `blocked`, phương thức đã thử và giới hạn. Có thể tìm nguồn thay thế có thể truy xuất; mọi thông tin từ nguồn thay thế phải được ghi thành nguồn riêng. Không dùng thông tin xác thực, không cố vượt qua kiểm soát truy cập và không coi đoạn xem trước là bằng chứng cho nội dung không truy cập được.
