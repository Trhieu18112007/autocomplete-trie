"""
trie.py - Lõi cấu trúc dữ liệu Trie cho hệ thống Autocomplete.
Đề tài 2, môn Cấu trúc dữ liệu và giải thuật. Phụ trách: Hiếu (nhóm trưởng).

Giao diện chung của nhóm:
    insert(word, weight)   thêm từ + trọng số (cộng dồn nếu từ đã tồn tại)
    search(word) -> bool   tìm chính xác
    get_weight(word)       trọng số của từ (None nếu từ không tồn tại)
    startsWith(prefix)     trả về NODE CUỐI của prefix (hoặc None); Khang dùng
                           node này để duyệt cây con khi viết suggest()

Cấu trúc node: children (dict ký tự -> node), isEnd, weight.

Quy ước chuẩn hóa (áp dụng cho MỌI chuỗi vào insert/search/startsWith):
    1. Unicode NFC  : "ế" gõ dạng tổ hợp hay dạng rời đều ra cùng một chuỗi.
    2. Chữ thường   : "Hà Nội" và "hà nội" là cùng một từ.
    3. Với từ (insert/search) cắt khoảng trắng ở hai đầu. Với prefix thì GIỮ
       khoảng trắng cuối, vì "xin " (có dấu cách) khác "xin".
    Các ký tự đặc biệt (+, -, ', số, dấu cách ở giữa...) được giữ nguyên.
    Chữ có dấu tiếng Việt là ký tự khác chữ không dấu ("ăn" != "an", "đ" != "d").

Độ phức tạp: insert, search, startsWith đều O(L), L là độ dài chuỗi,
không phụ thuộc số từ đã lưu trong Trie.
"""

import math
import numbers
import unicodedata


def normalize(text, strip=True):
    """Chuẩn hóa chuỗi: NFC -> chữ thường -> NFC (lower() có thể sinh lại dạng rời)."""
    if not isinstance(text, str):
        raise TypeError("Đầu vào phải là chuỗi (str), nhận được: %s" % type(text).__name__)
    text = unicodedata.normalize("NFC", text).lower()
    text = unicodedata.normalize("NFC", text)
    return text.strip() if strip else text


class TrieNode:
    """Một nút của cây Trie."""

    __slots__ = ("children", "isEnd", "weight")

    def __init__(self):
        self.children = {}   # ký tự -> TrieNode (dict nên dùng được cho tiếng Việt có dấu)
        self.isEnd = False   # True nếu đường đi từ gốc tới nút này tạo thành một từ hoàn chỉnh
        self.weight = 0      # trọng số tần suất (chỉ có ý nghĩa khi isEnd == True)


class Trie:
    """Cây Trie lưu từ khóa kèm trọng số."""

    def __init__(self):
        self.root = TrieNode()
        self._size = 0  # số từ phân biệt đang lưu

    # ------------------------------------------------------------------ insert
    def insert(self, word, weight=1):
        """
        Thêm `word` với trọng số `weight` (mặc định 1).
        Nếu từ đã tồn tại thì CỘNG DỒN trọng số.
        Lỗi: TypeError nếu word không phải str; ValueError nếu word rỗng
        (sau khi chuẩn hóa) hoặc weight không phải số hữu hạn >= 0.
        """
        word = normalize(word)
        if word == "":
            raise ValueError("Không thể chèn chuỗi rỗng")
        self._check_weight(weight)

        node = self.root
        for ch in word:
            nxt = node.children.get(ch)
            if nxt is None:               # chưa có nhánh cho ký tự này -> tạo node mới
                nxt = TrieNode()
                node.children[ch] = nxt
            node = nxt

        if not node.isEnd:                # từ mới
            node.isEnd = True
            self._size += 1
        node.weight += weight             # từ cũ -> cộng dồn

    # ------------------------------------------------------------------ search
    def search(self, word):
        """True nếu `word` được lưu như một từ hoàn chỉnh. Chuỗi rỗng -> False."""
        node = self._find(normalize(word))
        return node is not None and node.isEnd

    def get_weight(self, word):
        """Trọng số của `word`, hoặc None nếu từ không tồn tại."""
        node = self._find(normalize(word))
        if node is not None and node.isEnd:
            return node.weight
        return None

    # -------------------------------------------------------------- startsWith
    def startsWith(self, prefix):
        """
        Trả về NODE cuối của `prefix`, hoặc None nếu không có từ nào bắt đầu bằng prefix.
        - prefix == "" trả về node gốc (mọi từ đều bắt đầu bằng chuỗi rỗng).
        - Node trả về chưa chắc là từ hoàn chỉnh; kiểm tra node.isEnd nếu cần.
        """
        return self._find(normalize(prefix, strip=False))

    starts_with = startsWith  # bí danh theo phong cách Python

    # --------------------------------------------------------------- tiện ích
    def _find(self, text):
        """Đi theo từng ký tự của text từ gốc; trả về node cuối hoặc None."""
        node = self.root
        for ch in text:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    @staticmethod
    def _check_weight(weight):
        # bool là lớp con của int nên phải loại riêng
        if isinstance(weight, bool) or not isinstance(weight, numbers.Real):
            raise ValueError("Trọng số phải là số thực, nhận được: %r" % (weight,))
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Trọng số phải hữu hạn và >= 0, nhận được: %r" % (weight,))

    def __len__(self):
        return self._size

    def __contains__(self, word):
        return self.search(word)


if __name__ == "__main__":
    t = Trie()
    for w, f in [("app", 5), ("apple", 9), ("apply", 3), ("Hà Nội", 7), ("apple", 1)]:
        t.insert(w, f)
    print("số từ:", len(t))
    print("search('apple'):", t.search("apple"), "| weight:", t.get_weight("apple"))
    print("search('appl'):", t.search("appl"))
    print("startsWith('app') có con:", sorted(t.startsWith("app").children))
    print("search('HÀ NỘI'):", t.search("HÀ NỘI"))
