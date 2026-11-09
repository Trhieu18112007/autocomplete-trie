# File: autocomplete.py
# Người phụ trách: Khang
# Kết nối và kế thừa trực tiếp từ trie.py (giữ nguyên file gốc của Hiếu)

import heapq
from typing import List, Tuple
from trie import Trie, TrieNode, normalize


class _HeapCandidate:
    """
    Đối tượng trung gian đưa vào Min-Heap kích thước N.
    Quy tắc ưu tiên:
    1. Trọng số (weight) lớn hơn -> ưu tiên hơn.
    2. Hòa trọng số -> từ đứng trước theo bảng chữ cái (word nhỏ hơn) ưu tiên hơn.
    """
    __slots__ = ("word", "weight")

    def __init__(self, word: str, weight: int):
        self.word = word
        self.weight = weight

    def __lt__(self, other: "_HeapCandidate") -> bool:
        if self.weight != other.weight:
            return self.weight < other.weight
        return self.word > other.word


class _CachedTrieNode(TrieNode):
    """
    Kế thừa TrieNode và mở rộng __slots__ để lưu top_k cache
    mà không cần can thiệp hay chỉnh sửa file trie.py gốc.
    """
    __slots__ = ("top_k",)

    def __init__(self):
        super().__init__()
        self.top_k = []


class AutocompleteSystem(Trie):
    """
    Hệ thống gợi ý từ khóa kế thừa lõi Trie của Hiếu.
    Bổ sung: suggest(prefix, N), cập nhật trọng số khi chọn từ, và Top-K Cache tại mỗi node.
    """

    # Liên kết với hàm normalize của trie.py để giải quyết triệt để lỗi thiếu normalize_text
    normalize_text = staticmethod(normalize)

    def __init__(self, enable_node_cache: bool = False, cache_k: int = 10):
        super().__init__()
        # Thay thế nút gốc bằng nút hỗ trợ cache nếu tính năng được bật
        if enable_node_cache:
            self.root = _CachedTrieNode()
        self.enable_node_cache = enable_node_cache
        self.cache_k = cache_k
        # Từ điển dự phòng lưu cache trong trường hợp gặp TrieNode thông thường
        self._fallback_cache = {}

    def insert(self, word: str, weight: int = 1) -> bool:
        """
        Thêm từ và cập nhật cache Top-K (nếu enable_node_cache=True).
        Trả về True nếu chèn thành công, False nếu đầu vào không hợp lệ.
        """
        try:
            clean_word = self.normalize_text(word)
            self._check_weight(weight)
        except (TypeError, ValueError):
            return False

        if clean_word == "":
            return False

        node = self.root
        path_nodes = [node]

        for char in clean_word:
            if char not in node.children:
                # Tạo node mới có hỗ trợ cache nếu chế độ cache đang bật
                node.children[char] = _CachedTrieNode() if self.enable_node_cache else TrieNode()
            node = node.children[char]
            path_nodes.append(node)

        # Cập nhật trạng thái từ và đồng bộ biến _size của Trie
        if not node.isEnd:
            node.isEnd = True
            self._size += 1
            node.weight = weight
        else:
            node.weight += weight

        if self.enable_node_cache:
            final_weight = node.weight
            for p_node in path_nodes:
                self._update_node_top_k(p_node, clean_word, final_weight)

        return True

    def _update_node_top_k(self, node: TrieNode, word: str, weight: int) -> None:
        """Cập nhật danh sách top-K gợi ý lưu sẵn ngay tại node."""
        if hasattr(node, "top_k"):
            cache_list = node.top_k
        else:
            cache_list = self._fallback_cache.get(node, [])

        cache_list = [(w, wt) for w, wt in cache_list if w != word]
        cache_list.append((word, weight))
        cache_list.sort(key=lambda item: (-item[1], item[0]))
        if len(cache_list) > self.cache_k:
            cache_list.pop()

        if hasattr(node, "top_k"):
            node.top_k = cache_list
        else:
            self._fallback_cache[node] = cache_list

    def suggest(self, prefix: str, N: int = 5) -> List[Tuple[str, int]]:
        """
        Trả về danh sách tối đa N từ khóa phù hợp nhất dạng [(word, weight), ...].
        - Bước 1: Dùng startsWith(prefix) từ trie.py để tìm đến node cuối của prefix.
        - Bước 2: Duyệt DFS toàn bộ cây con để thu thập từ hoàn chỉnh.
        - Bước 3: Dùng Min-Heap kích thước N (heapq) để lọc Top-N.
        """
        if N <= 0 or not isinstance(prefix, str):
            return []

        # Giữ nguyên khoảng trắng cuối theo đúng quy ước chuẩn hóa prefix của trie.py
        clean_prefix = normalize(prefix, strip=False)
        if clean_prefix == "":
            return []

        prefix_node = self.startsWith(clean_prefix)
        if prefix_node is None:
            return []

        min_heap: List[_HeapCandidate] = []

        def dfs(curr_node: TrieNode, path_chars: List[str]) -> None:
            if curr_node.isEnd:
                candidate = _HeapCandidate("".join(path_chars), curr_node.weight)
                if len(min_heap) < N:
                    heapq.heappush(min_heap, candidate)
                elif min_heap[0] < candidate:
                    heapq.heapreplace(min_heap, candidate)

            for char, next_node in curr_node.children.items():
                path_chars.append(char)
                dfs(next_node, path_chars)
                path_chars.pop()

        dfs(prefix_node, list(clean_prefix))

        # Trích xuất từ heap và sắp xếp giảm dần theo độ ưu tiên
        top_candidates = sorted(min_heap, reverse=True)
        return [(item.word, item.weight) for item in top_candidates]

    def suggest_fast_cache(self, prefix: str, N: int = 5) -> List[Tuple[str, int]]:
        """Phần nâng cao: Truy vấn tức thì từ danh sách top-K đã lưu sẵn."""
        if not self.enable_node_cache or N > self.cache_k:
            return self.suggest(prefix, N)
        if N <= 0 or not isinstance(prefix, str):
            return []

        clean_prefix = normalize(prefix, strip=False)
        prefix_node = self.startsWith(clean_prefix)
        if prefix_node is None:
            return []

        cached_data = getattr(prefix_node, "top_k", None)
        if cached_data is None:
            cached_data = self._fallback_cache.get(prefix_node, [])

        return cached_data[:N]

    def record_user_selection(self, selected_word: str, bonus_weight: int = 1) -> bool:
        """Cập nhật trọng số khi người dùng chọn một gợi ý (tăng tần suất xuất hiện)."""
        if not self.search(selected_word):
            return False
        return self.insert(selected_word, bonus_weight)


if __name__ == "__main__":
    # Chạy thử nghiệm tích hợp trực tiếp
    ac = AutocompleteSystem(enable_node_cache=True, cache_k=5)
    ac.insert("cấu trúc dữ liệu", 10)
    ac.insert("cấu trúc giải thuật", 8)
    ac.insert("cây trie", 15)
    ac.insert("cây avl", 12)

    print(f"Tổng số từ: {len(ac)}")
    print("Suggest DFS 'cây':", ac.suggest("cây", N=2))
    print("Suggest Fast Cache 'cây':", ac.suggest_fast_cache("cây", N=2))