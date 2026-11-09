# Autocomplete bằng cây Trie

Báo cáo cuối kì môn **Cấu trúc dữ liệu và giải thuật**, đề tài 2: hệ thống tự động hoàn thành từ khóa (Autocomplete) xây dựng trên cây Trie, viết bằng Python.

Khi người dùng gõ một tiền tố, hệ thống tìm các từ bắt đầu bằng tiền tố đó và gợi ý những từ có trọng số (độ phổ biến) cao nhất.

## Mục lục

- [Thành viên và phần việc](#thành-viên-và-phần-việc)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Cách chạy](#cách-chạy)
- [Giao diện hàm chung](#giao-diện-hàm-chung)
- [Ví dụ sử dụng Trie](#ví-dụ-sử-dụng-trie)
- [Quy ước chuẩn hóa](#quy-ước-chuẩn-hóa)
- [Độ phức tạp](#độ-phức-tạp)
- [Quy trình làm việc với Git](#quy-trình-làm-việc-với-git)
- [Tiến độ](#tiến-độ)

## Thành viên và phần việc

| Thành viên | Phần việc | File |
| --- | --- | --- |
| Hiếu (nhóm trưởng) | Lõi Trie: insert, search, startsWith, unit test, chương lý thuyết | `trie.py`, `test_trie.py` |
| Khang | Gợi ý top-N theo trọng số (suggest) | `autocomplete.py` |
| Tài | Chuẩn bị dữ liệu, giao diện, demo | `main.py`, `data/` |
| Hiền | Benchmark, tổng hợp báo cáo | `benchmark.py`, `docs/` |

## Cấu trúc thư mục

```
autocomplete-trie/
├── trie.py            # Lõi cây Trie (TrieNode, Trie)
├── test_trie.py       # Unit test cho trie.py
├── autocomplete.py    # suggest(prefix, N) dựa trên Trie
├── main.py            # Giao diện và demo
├── benchmark.py       # Đo thời gian chạy
├── data/
│   └── words.txt      # Bộ từ điển kèm trọng số
├── docs/              # Báo cáo, hình ảnh, kết quả benchmark
├── .gitignore
└── README.md
```

Một số file vẫn đang được các thành viên hoàn thiện, xem mục [Tiến độ](#tiến-độ).

## Cách chạy

Yêu cầu: đã cài Python 3. Chỉ dùng thư viện chuẩn, không cần cài thêm gói nào.

```bash
git clone <link-repo>
cd autocomplete-trie
```

Chạy bộ kiểm thử của lõi Trie:

```bash
python -m unittest -v test_trie
```

Kết quả đúng là `Ran 46 tests ... OK`. Nếu đã cài pytest thì có thể chạy `pytest -v test_trie.py`.

Chạy demo nhanh của lõi Trie:

```bash
python trie.py
```

Chạy ứng dụng demo và benchmark: Tài và Hiền bổ sung lệnh tại đây khi hoàn thành.

## Giao diện hàm chung

Cả nhóm dùng chung các hàm sau để code song song mà không vướng nhau.

| Hàm | Mô tả |
| --- | --- |
| `insert(word, weight=1)` | Thêm từ cùng trọng số. Nếu từ đã có thì cộng dồn trọng số. |
| `search(word)` | Trả về `True` nếu từ được lưu đầy đủ trong cây, ngược lại `False`. |
| `get_weight(word)` | Trả về trọng số của từ, hoặc `None` nếu từ không tồn tại. |
| `startsWith(prefix)` | Trả về **node cuối** của tiền tố, hoặc `None` nếu không có từ nào bắt đầu bằng tiền tố đó. |
| `suggest(prefix, N)` | Trả về tối đa N gợi ý có trọng số cao nhất (`autocomplete.py`). |

Mỗi node (`TrieNode`) gồm ba thuộc tính:

- `children`: dict ánh xạ ký tự sang node con.
- `isEnd`: `True` nếu đường đi từ gốc tới node này là một từ hoàn chỉnh.
- `weight`: trọng số của từ, chỉ có ý nghĩa khi `isEnd` là `True`.

`startsWith` trả về node chứ không chỉ `True`/`False` để `suggest` có thể duyệt thẳng cây con bắt đầu từ node đó.

## Ví dụ sử dụng Trie

```python
from trie import Trie

t = Trie()
t.insert("app", 5)
t.insert("apple", 9)
t.insert("apple", 1)        # từ đã có: trọng số cộng dồn thành 10
t.insert("Hà Nội", 7)

t.search("apple")           # True
t.search("appl")            # False (chỉ là tiền tố, chưa phải từ)
t.get_weight("apple")       # 10
t.search("HÀ NỘI")          # True (không phân biệt hoa thường)

node = t.startsWith("app")  # node cuối của "app"
sorted(node.children)       # ['l']
node.isEnd                  # True, vì "app" cũng là một từ
t.startsWith("xyz")         # None
```

## Quy ước chuẩn hóa

Mọi chuỗi đi vào `insert`, `search` và `startsWith` đều được chuẩn hóa ngay trong `trie.py`, các module khác không cần tự xử lý:

- **Unicode NFC:** chữ như "ế" dù gõ dạng tổ hợp hay dạng rời đều thành cùng một chuỗi.
- **Chữ thường:** "Hà Nội" và "hà nội" là cùng một từ.
- **Khoảng trắng:** với từ thì cắt khoảng trắng hai đầu. Với tiền tố thì giữ khoảng trắng cuối, vì `"xin "` khác `"xin"`.
- **Ký tự đặc biệt** (`+`, `-`, `'`, số, dấu cách ở giữa...) được giữ nguyên.
- **Dấu tiếng Việt** là ký tự riêng: `ăn`, `ân`, `an` là ba từ khác nhau, `đ` khác `d`.

Các trường hợp biên:

- `insert("")` báo `ValueError`. `search("")` trả về `False`. `startsWith("")` trả về node gốc.
- Đầu vào không phải chuỗi báo `TypeError`.
- Trọng số phải là số hữu hạn và không âm, nếu không báo `ValueError`.

## Độ phức tạp

Gọi L là độ dài chuỗi đầu vào:

- `insert`, `search`, `startsWith`: **O(L)** thời gian, không phụ thuộc số từ đang lưu.
- Bộ nhớ: tối đa bằng tổng số ký tự của các từ đã chèn, thực tế ít hơn nhiều nhờ các từ dùng chung tiền tố.

Phân tích đầy đủ và số liệu thực nghiệm nằm trong báo cáo (thư mục `docs/`).

## Quy trình làm việc với Git

1. Mỗi người làm trên nhánh riêng, đặt tên dạng `ten/viec` (ví dụ `khang/autocomplete`).
2. Trước mỗi buổi làm: `git pull origin main`.
3. Commit nhỏ, thường xuyên, mô tả ngắn gọn.
4. Xong phần việc thì đẩy nhánh lên và mở Pull Request.
5. Nhóm trưởng xem lại, chạy test rồi gộp vào `main`.

Quy tắc chung:

- Không push trực tiếp lên `main`.
- Mỗi người chỉ sửa file của mình. Cần sửa file người khác thì nhắn họ.
- Chạy test của mình trước khi mở Pull Request.

## Tiến độ

- [x] Lõi Trie (`trie.py`)
- [x] Unit test (`test_trie.py`, 46 ca)
- [x] Chương cơ sở lý thuyết về Trie
- [ ] Gợi ý top-N theo trọng số (`autocomplete.py`)
- [ ] Bộ dữ liệu và giao diện demo (`data/`, `main.py`)
- [ ] Benchmark (`benchmark.py`)
- [ ] Ghép báo cáo hoàn chỉnh (`docs/`)
