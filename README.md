# Hệ Thống Gợi Ý Từ Tự Động (Autocomplete System) Sử Dụng Cấu Trúc Dữ Liệu Trie

Dự án đồ án môn **Cấu trúc Dữ liệu và Giải thuật**. Ứng dụng mô phỏng tính năng gợi ý từ khóa thời gian thực (tương tự Google Autocomplete) với bộ dữ liệu từ điển lớn và sắp xếp theo trọng số tần suất sử dụng.

---

## 1. Giới thiệu tổng quan
- **Cấu trúc dữ liệu chính:** Cây tiền tố (Trie - Prefix Tree).
- **Thuật toán sắp xếp gợi ý:** Duyệt cây con (DFS) kết hợp sắp xếp theo trọng số tần suất (Weight-based ranking theo luật Zipf).
- **Hiệu năng:** Độ phức tạp tìm kiếm theo tiền tố $O(L)$ với $L$ là độ dài tiền tố nhập vào, đảm bảo thời gian phản hồi cực nhanh ($< 0.1$ ms) trên bộ dữ liệu $30,000$ từ vựng.

---

## 2. Cấu trúc thư mục dự án
```text
autocomplete-trie/
├── words.txt      # Bộ từ điển gồm 30,000 từ chuẩn hóa kèm trọng số tần suất
├── main.py        # Mã nguồn Cấu trúc Trie và Giao diện GUI Tkinter
├── README.md      # Tài liệu hướng dẫn cài đặt và báo cáo đồ án
└── demo.png       # Ảnh chụp giao diện thực tế
```

---

## 3. Hướng dẫn cài đặt & Chạy ứng dụng

### Yêu cầu môi trường
- Python 3.8 trở lên.
- Sử dụng các thư viện chuẩn tích hợp sẵn trong Python (`tkinter`, `time`, `os`). Không yêu cầu cài đặt thêm thư viện ngoài (`pip install`).

### Các bước thực thi
1. Clone hoặc tải project về máy cá nhân:
   ```bash
   git clone <link_repo_cua_ban>
   cd autocomplete-trie
   ```
2. Khởi chạy ứng dụng:
   ```bash
   python main.py
   ```

---

## 4. Kịch bản Demo khi bảo vệ
1. **Khởi chạy ứng dụng:** Màn hình console thông báo nạp $30,000$ từ vựng vào bộ nhớ RAM trong chưa tới $0.5$ giây.
2. **Gõ tiền tố ngắn:** Gõ ký tự `a` $ightarrow$ Hệ thống lập tức hiển thị Top 10 từ có tần suất cao nhất bắt đầu bằng chữ `a`.
3. **Gõ tiền tố dài:** Gõ tiếp `ap` $ightarrow$ Danh sách lập tức tự động thu hẹp lại theo thời gian thực mà không bị trễ hay giật lag.
4. **Đánh giá hiệu năng:** Nhìn vào chỉ số "Thời gian truy vấn" ở góc trên bảng kết quả: Tốc độ xử lý chỉ mất trung bình **$0.01 - 0.05$ ms**, chứng minh sự tối ưu vượt trội của cấu trúc dữ liệu Trie so với tìm kiếm tuyến tính trên mảng/danh sách.
