# File: run.py
# File khởi chạy liên kết hệ thống (Không can thiệp vào bất kỳ file nào trong 4 file gốc)

import time
import tkinter as tk
import main
from autocomplete import AutocompleteSystem


class TrieGUIAdapter(AutocompleteSystem):
    """
    Adapter chuyển tiếp các lệnh từ main.py sang AutocompleteSystem:
    - Ánh xạ thuộc tính total_words -> len(self)
    - Ánh xạ hàm search_prefix(prefix, top_k) -> suggest_fast_cache() hoặc suggest()
    """
    def __init__(self, enable_node_cache: bool = True, cache_k: int = 10):
        super().__init__(enable_node_cache=enable_node_cache, cache_k=cache_k)

    @property
    def total_words(self) -> int:
        return len(self)

    def search_prefix(self, prefix: str, top_k: int = 10):
        if self.enable_node_cache:
            return self.suggest_fast_cache(prefix, top_k)
        return self.suggest(prefix, top_k)


if __name__ == "__main__":
    # Khởi tạo lõi Autocomplete của Khang với cơ chế Cache tăng tốc
    trie = TrieGUIAdapter(enable_node_cache=True, cache_k=10)

    dataset_file = "words.txt"
    print(f"[*] Đang nạp dữ liệu từ {dataset_file} vào AutocompleteSystem...")
    start_t = time.perf_counter()
    count = main.load_dataset(dataset_file, trie)
    print(f"[OK] Đã nạp thành công {count:,} từ vựng ({time.perf_counter() - start_t:.3f}s).")

    # Chạy giao diện Tkinter từ main.py nhưng vận hành bằng thuật toán của trie.py & autocomplete.py
    root = tk.Tk()
    app = main.AutocompleteGUI(root, trie)
    root.mainloop()