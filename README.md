# Nghiên cứu tiếp thị liên kết TikTok

## Mục tiêu

Workspace này dùng để thực hiện nghiên cứu có thể kiểm chứng về nội dung và cơ hội tiếp thị liên kết trên TikTok bằng dữ liệu công khai. Mục tiêu của giai đoạn khởi tạo là tạo một ranh giới an toàn, tái lập được, tôn trọng quyền riêng tư và giúp người mới chạy các bước kiểm tra trước khi viết ứng dụng hoặc thu thập dữ liệu.

Mọi kết luận phải phân biệt rõ dữ kiện quan sát được với phép tính, ước tính và giả thuyết. Phạm vi mặc định là dữ liệu công khai; không dùng workspace này để truy cập trái phép, vượt giới hạn dịch vụ hoặc suy đoán thông tin kinh doanh riêng tư.

## Bố cục workspace

```text
.
├── .gitignore                 # Các tệp cục bộ và dữ liệu nhạy cảm không được theo dõi
├── README.md                  # Hướng dẫn vận hành và quy tắc nghiên cứu
├── .venv/                     # Môi trường Python cục bộ, không đưa vào Git
├── data/
│   ├── raw/                   # Dữ liệu nguồn; raw/private/ không được sử dụng để chia sẻ
│   ├── processed/             # Dữ liệu đã chuẩn hóa hoặc tính toán
│   └── exports/               # Các bản xuất phục vụ xem xét
├── evidence/                  # Bằng chứng và liên kết nguồn khi được bổ sung
├── reports/                   # Báo cáo nghiên cứu khi được bổ sung
├── src/                       # Mã ứng dụng khi được bổ sung
└── tests/
    ├── __init__.py
    └── test_project_layout.py # Kiểm tra ranh giới bố cục tối thiểu
```

Chỉ tạo thư mục hoặc tệp dữ liệu theo yêu cầu của từng nhiệm vụ. Không đặt khóa, cookie, token, mật khẩu, danh sách khách hàng hoặc dữ liệu cá nhân vào workspace.

## Thiết lập virtualenv

Không cài gói bên ngoài trong bước khởi tạo. Từ thư mục gốc dự án, chạy đúng các lệnh sau:

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/python --version
```

Các lệnh kiểm tra chính dùng `.venv/bin/python` để tránh nhầm với Python hệ thống. Có thể thoát môi trường bằng `deactivate`; việc thoát không xóa `.venv/`. Nếu `.venv/` đã tồn tại, không cần tạo lại.

## Khởi tạo

1. Mở terminal tại thư mục gốc của workspace.
2. Xác nhận Python hệ thống bằng `python3 --version`.
3. Tạo môi trường bằng `python3 -m venv .venv` nếu môi trường chưa có.
4. Kích hoạt bằng `source .venv/bin/activate` và xác nhận bằng `.venv/bin/python --version`.
5. Không chạy `pip install`, `npm install` hoặc trình cài đặt bên ngoài trong giai đoạn này.
6. Chạy bộ kiểm tra bố cục trước khi thêm mã mới.

Kiểm tra thư viện chuẩn mà không thay đổi môi trường:

```bash
.venv/bin/python -c 'import csv, json, sqlite3, urllib.request, hashlib, datetime, argparse, unittest; print("standard library ready")'
```

## Sổ tay vận hành hoàn chỉnh (Operational Runbook)

Toàn bộ quy trình nghiên cứu được thực thi thông qua các công cụ chuẩn sử dụng Python tiêu chuẩn, chạy trực tiếp trong môi trường `.venv`:

```bash
# 1. Tạo môi trường ảo Python (nếu chưa có)
python3 -m venv .venv

# 2. Khởi tạo cấu trúc thư mục nghiên cứu và 8 bảng CSV chuẩn hóa rỗng
.venv/bin/python scripts/init_research.py --root .

# 3. Xác thực tính hợp lệ của toàn bộ bản ghi theo schema chuẩn
.venv/bin/python scripts/validate_records.py --root . --output reports/validation.json

# 4. Kiểm toán và rà soát nguồn trùng lặp (không làm thay đổi dữ liệu gốc)
.venv/bin/python scripts/deduplicate_sources.py --root . --output reports/duplicates.json

# 5. Xây dựng lại chỉ mục SQLite để phục vụ truy vấn cục bộ
.venv/bin/python scripts/build_sqlite_index.py --root .

# 6. Xuất báo cáo tổng kết nghiên cứu Markdown trung thực
.venv/bin/python scripts/export_research_summary.py --root . --output reports/YYYY-MM-DD-topic.md --title "Tiêu đề Báo cáo Nghiên cứu"

# 7. Chạy toàn bộ bộ kiểm thử tự động của hệ thống
.venv/bin/python -m unittest discover -s tests -v
```

### Ý nghĩa của các tệp báo cáo kiểm toán (Audit Artifacts)

- `reports/validation.json`: Là bằng chứng kiểm định chất lượng dữ liệu, ghi lại các lỗi thiếu trường bắt buộc, sai định dạng enum, vi phạm quy tắc ngày giờ hoặc lỗi logic bằng chứng.
- `reports/duplicates.json`: Là báo cáo kiểm toán độc lập về các nhóm nguồn bị trùng URL hoặc mã định danh.
- **Bảo toàn dữ liệu gốc:** Các script kiểm toán và rà soát trùng lặp là các công cụ kiểm tra không can thiệp (read-only audit). Chúng tuyệt đối KHÔNG tự động xóa bỏ hoặc thay đổi nội dung dữ liệu trong `data/raw/` hay `data/processed/`.
- **Nguyên tắc báo cáo trung thực:** Khi hệ thống chưa có dữ liệu công khai được xác minh từ TikTok hoặc các nguồn khảo sát, báo cáo xuất ra sẽ hiển thị rõ ràng thông báo `Chưa có dữ liệu được xác minh` cho từng phần tương ứng. Tuyệt đối không tự suy diễn số liệu, không gán giá trị 0đ cho sản phẩm chưa xác minh giá, và không suy đoán doanh số từ lượt xem video.

## Chi tiết các công cụ dòng lệnh (CLI Scripts)

### Chi tiết lệnh xuất báo cáo (`export_research_summary.py`)

Lệnh xuất tài liệu Markdown trung thực từ 8 bảng chuẩn hóa trong `data/processed/`:

- `--root`: Đường dẫn thư mục gốc workspace (mặc định: `.`).
- `--output`: Đường dẫn tệp Markdown xuất ra (bắt buộc).
- `--title`: Tiêu đề báo cáo (bắt buộc).
- `--accessed-at`: Dấu thời gian ISO 8601 tùy chọn (mặc định: thời gian UTC hiện tại).
- Mã thoát (exit code): `0` khi xuất thành công; `2` khi tham số không hợp lệ hoặc lỗi tệp/thư mục.

Ví dụ xuất báo cáo kiểm thử hệ thống:

```bash
.venv/bin/python scripts/export_research_summary.py --root . --output reports/initial-system-smoke.md --title "TikTok Affiliate Research System Smoke Report"
```

Nếu công cụ chưa được triển khai, chỉ chạy các bài kiểm tra bố cục ở trên và ghi rõ trạng thái `chưa triển khai`; không tạo dữ liệu giả để làm cho lệnh thành công. Mỗi lần validate hoặc audit phải giữ lại nguồn, thời điểm truy cập, thao tác biến đổi và cảnh báo liên quan.

## Loại bằng chứng

Mỗi nhận định trong ghi chú hoặc báo cáo phải có một loại bằng chứng. Dùng đúng nhãn tiếng Anh dưới đây để có thể lọc và kiểm tra nhất quán:

- `direct_source`: thông tin được đọc trực tiếp từ nguồn công khai có thể dẫn lại, kèm URL hoặc mã nhận diện và thời điểm truy cập.
- `calculated`: giá trị được tính từ các trường hoặc nguồn đã ghi rõ; phải nêu công thức, đầu vào và quy tắc làm tròn.
- `estimate`: xấp xỉ dựa trên giả định hoặc mẫu chưa đầy đủ; phải nêu khoảng, giả định và giới hạn, không trình bày như sự thật.
- `hypothesis`: diễn giải cần kiểm chứng thêm; phải nêu cách kiểm chứng hoặc bằng chứng có thể bác bỏ nó.

Không nâng cấp `estimate` hoặc `hypothesis` thành `direct_source` chỉ vì kết quả có vẻ hợp lý. Nếu một câu có nhiều loại bằng chứng, hãy tách câu hoặc gắn từng phần bằng nhãn riêng.

## Giới hạn công cụ: chỉ dữ liệu công khai

Chỉ sử dụng các trang, API, tài liệu, video, hồ sơ và số liệu mà người dùng có thể truy cập công khai theo điều khoản hiện hành. Công cụ phải tôn trọng robots.txt, điều khoản dịch vụ, giới hạn tốc độ, giới hạn truy cập và yêu cầu xóa dữ liệu. Ưu tiên API hoặc giao diện chính thức nếu có.

Không dùng đăng nhập của người khác, cookie phiên, endpoint nội bộ, kỹ thuật vượt CAPTCHA, proxy né giới hạn, thu thập hàng loạt gây quá tải, hoặc bất kỳ cách nào để mở khóa dữ liệu riêng tư. Không cố suy ra danh tính, vị trí, doanh thu, biên lợi nhuận hay thông tin không được công bố của một cá nhân hoặc doanh nghiệp. Khi nguồn không công khai hoặc không thể kiểm chứng, ghi nhận là không có dữ liệu thay vì tìm cách vượt rào.

## Không suy ra doanh số

**Không suy ra doanh số.** Lượt xem, lượt thích, bình luận, người theo dõi, giá niêm yết, hoa hồng được quảng cáo hoặc tín hiệu tương tác không phải là bằng chứng cho doanh số thực tế. Không chuyển các chỉ số đó thành doanh thu, đơn hàng, chuyển đổi hay lợi nhuận nếu không có nguồn công khai trực tiếp và phù hợp.

Có thể tính một chỉ số mô tả khi công thức và đầu vào được công bố, nhưng phải gắn nhãn `calculated` hoặc `estimate`, nêu rõ đó không phải doanh số, và không dùng nó để khẳng định hiệu quả tài chính. Nếu không thể phân biệt, bỏ nhận định hoặc ghi `unknown`.

## Không lưu thông tin xác thực

Không lưu API key, access token, refresh token, mật khẩu, cookie, khóa riêng, tệp `.env`, dữ liệu thanh toán hoặc thông tin đăng nhập trong Git hay trong workspace. Các thư mục và mẫu nhạy cảm đã được loại trừ trong `.gitignore`, nhưng mỗi người vẫn phải kiểm tra trước khi chia sẻ hoặc xuất tệp.

Nếu một công cụ cần xác thực, dùng cơ chế quản lý bí mật được phê duyệt ở ngoài repository và biến môi trường chỉ trong phiên chạy. Không ghi giá trị bí mật vào log, báo cáo, notebook, URL, tên tệp, thông báo lỗi hoặc bản export. Khi phát hiện bí mật đã lộ, dừng chia sẻ, thu hồi hoặc xoay vòng thông tin đó theo quy trình của nhà cung cấp và chỉ ghi lại mã tham chiếu không nhạy cảm.

## Quy trình nghiên cứu 11 bước

1. **Xác định câu hỏi:** viết câu hỏi, phạm vi, đối tượng, khu vực, khoảng thời gian và tiêu chí thành công; tách câu hỏi mô tả khỏi câu hỏi tài chính.
2. **Kiểm tra quyền truy cập:** liệt kê các nguồn công khai hợp lệ, điều khoản, giới hạn tốc độ và phương thức truy cập được phép; loại bỏ nguồn yêu cầu vượt rào.
3. **Lập kế hoạch bằng chứng:** định nghĩa trường dữ liệu, loại bằng chứng (`direct_source`, `calculated`, `estimate`, `hypothesis`) và tiêu chí để bác bỏ nhận định.
4. **Ghi nhận nguồn:** lưu URL hoặc mã nguồn, tiêu đề, tác giả nếu có, thời điểm truy cập, phạm vi hiển thị và nội dung cần trích dẫn; không lưu thông tin xác thực.
5. **Thu thập tối thiểu:** lấy đúng dữ liệu công khai cần thiết, tôn trọng tốc độ và giới hạn; không thu thập dữ liệu cá nhân hoặc dữ liệu riêng tư ngoài phạm vi.
6. **Bảo toàn bản gốc:** lưu dấu vết tệp, checksum khi phù hợp, timestamp và phiên bản công cụ; đánh dấu dữ liệu chưa xác minh và không chỉnh sửa bản raw để che giấu thay đổi.
7. **Làm sạch có kiểm soát:** chuẩn hóa định dạng, loại trùng theo quy tắc đã viết, xử lý thiếu dữ liệu và ghi nhật ký mọi biến đổi; không tự điền giá trị làm thay đổi ý nghĩa.
8. **Kiểm tra chất lượng:** chạy `validate`, kiểm tra nguồn bằng `audit`, xem xét mẫu, phát hiện sai lệch và ghi các giới hạn hoặc xung đột giữa nguồn.
9. **Tính toán minh bạch:** chạy phép tính đã định nghĩa, lưu công thức và đầu vào, gắn nhãn `calculated` hoặc `estimate`; tuyệt đối không suy ra doanh số từ tín hiệu tương tác.
10. **Tổng hợp và phản biện:** lập chỉ mục dữ liệu đã duyệt, nêu nhận định cùng bằng chứng, phân biệt giả thuyết, kiểm tra cách diễn giải thay thế và cho phép tái lập kết quả.
11. **Xuất và lưu trữ:** chạy `export` chỉ với dữ liệu đã kiểm tra, loại bỏ bí mật và dữ liệu nhạy cảm, ghi phiên bản và ngày xuất, rồi lưu báo cáo cùng danh sách nguồn và các câu hỏi còn bỏ ngỏ.

Mỗi bước có thể dừng quy trình nếu nguồn không còn công khai, dữ liệu không đủ để kiểm chứng hoặc có nguy cơ vi phạm quyền riêng tư. Khi đó báo cáo trạng thái và lý do dừng thay vì lấp đầy khoảng trống bằng phỏng đoán.

## Kiểm tra nhanh trước khi chia sẻ

- Đã chạy test bằng Python hệ thống và `.venv/bin/python` chưa?
- Mọi nguồn đều công khai, được phép truy cập và có thời điểm ghi nhận chưa?
- Mỗi nhận định đã có loại bằng chứng và giới hạn chưa?
- Có câu nào vi phạm nguyên tắc **Không suy ra doanh số** không?
- Có khóa, token, cookie, mật khẩu hoặc dữ liệu cá nhân trong tệp xuất không?
- Bản export có thể truy nguyên về dữ liệu gốc và công thức không?
