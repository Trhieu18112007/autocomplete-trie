"""
ĐỒ ÁN CẤU TRÚC DỮ LIỆU & GIẢI THUẬT
Chủ đề: Hệ thống Auto-complete (Gợi ý từ) thời gian thực sử dụng Trie và Trọng số tần suất.
"""

import os
import time
import tkinter as tk
from tkinter import ttk

# ==================== 1. CẤU TRÚC DỮ LIỆU TRIE ====================
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.weight = 0

class AutocompleteTrie:
    def __init__(self):
        self.root = TrieNode()
        self.total_words = 0

    def insert(self, word: str, weight: int):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.weight = weight
        self.total_words += 1

    def _dfs(self, node: TrieNode, prefix: str, results: list):
        if node.is_end_of_word:
            results.append((prefix, node.weight))
        for char, next_node in node.children.items():
            self._dfs(next_node, prefix + char, results)

    def search_prefix(self, prefix: str, top_k: int = 10):
        node = self.root
        prefix = prefix.lower()
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        all_matches = []
        self._dfs(node, prefix, all_matches)
        # Sắp xếp theo trọng số tần suất giảm dần
        all_matches.sort(key=lambda x: x[1], reverse=True)
        return all_matches[:top_k]

# ==================== 2. ĐỌC & LÀM SẠCH DỮ LIỆU ====================
def load_dataset(filepath: str, trie: AutocompleteTrie):
    if not os.path.exists(filepath):
        print(f"[CẢNH BÁO] Không tìm thấy file {filepath}!")
        return 0

    seen = set()
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue
            parts = line.split(",", 1)
            word = parts[0].strip().lower()
            try:
                freq = int(parts[1].strip())
            except ValueError:
                freq = 1

            if word.isalpha() and word not in seen:
                seen.add(word)
                trie.insert(word, freq)
                count += 1
    return count

# ==================== 3. GIAO DIỆN NGƯỜI DÙNG (GUI) ====================
class AutocompleteGUI:
    def __init__(self, root, trie: AutocompleteTrie):
        self.root = root
        self.trie = trie
        self.root.title("DSA Demo: Autocomplete Trie Search Engine")
        self.root.geometry("560x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f4f6f9")

        # Header
        title_frame = tk.Frame(root, bg="#1e3a8a", pady=15)
        title_frame.pack(fill="x")

        tk.Label(
            title_frame,
            text="HỆ THỐNG GỢI Ý TỪ THỜI GIAN THỰC (TRIE)",
            font=("Segoe UI", 13, "bold"),
            fg="#ffffff",
            bg="#1e3a8a"
        ).pack()

        tk.Label(
            title_frame,
            text=f"Quy mô từ điển: {self.trie.total_words:,} từ vựng",
            font=("Segoe UI", 9),
            fg="#93c5fd",
            bg="#1e3a8a"
        ).pack(pady=2)

        # Search Box Container
        search_box = tk.Frame(root, bg="#f4f6f9", padx=25, pady=15)
        search_box.pack(fill="x")

        tk.Label(
            search_box,
            text="Nhập tiền tố tìm kiếm (Prefix):",
            font=("Segoe UI", 10, "bold"),
            fg="#1f2937",
            bg="#f4f6f9"
        ).pack(anchor="w", pady=(0, 5))

        self.input_var = tk.StringVar()
        self.input_var.trace_add("write", self.on_text_change)

        self.entry = tk.Entry(
            search_box,
            textvariable=self.input_var,
            font=("Consolas", 13),
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightcolor="#2563eb"
        )
        self.entry.pack(fill="x", ipady=6)
        self.entry.focus()

        # Stats Bar
        self.stats_lbl = tk.Label(
            root,
            text="Thời gian truy vấn: 0.0000 ms | Kết quả: 0 từ",
            font=("Consolas", 9, "bold"),
            fg="#059669",
            bg="#f4f6f9"
        )
        self.stats_lbl.pack(anchor="w", padx=25, pady=(0, 5))

        # Result Table (Treeview)
        table_frame = tk.Frame(root, bg="#ffffff", padx=25)
        table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e5e7eb")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)

        columns = ("rank", "word", "weight")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("rank", text="Hạng")
        self.tree.heading("word", text="Từ vựng gợi ý (Autocomplete)")
        self.tree.heading("weight", text="Tần suất (Trọng số)")

        self.tree.column("rank", width=55, anchor="center")
        self.tree.column("word", width=290, anchor="w")
        self.tree.column("weight", width=140, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_text_change(self, *args):
        prefix = self.input_var.get().strip()
        self.tree.delete(*self.tree.get_children())

        if not prefix:
            self.stats_lbl.config(text="Thời gian truy vấn: 0.0000 ms | Kết quả: 0 từ", fg="#6b7280")
            return

        t_start = time.perf_counter()
        matches = self.trie.search_prefix(prefix, top_k=10)
        t_elapsed = (time.perf_counter() - t_start) * 1000

        self.stats_lbl.config(
            text=f"Thời gian truy vấn: {t_elapsed:.4f} ms | Tìm thấy: {len(matches)} gợi ý",
            fg="#059669"
        )

        for i, (word, weight) in enumerate(matches, start=1):
            self.tree.insert("", "end", values=(f"#{i}", word, f"{weight:,}"))

    def on_select(self, event):
        selected = self.tree.focus()
        if selected:
            vals = self.tree.item(selected, "values")
            if vals:
                self.input_var.set(vals[1])
                self.entry.icursor(tk.END)

if __name__ == "__main__":
    trie = AutocompleteTrie()
    dataset_file = "words.txt"
    print(f"[*] Đang nạp dữ liệu từ {dataset_file}...")
    start_t = time.perf_counter()
    count = load_dataset(dataset_file, trie)
    print(f"[OK] Đã nạp thành công {count:,} từ vựng vào Trie ({time.perf_counter() - start_t:.3f}s).")

    root = tk.Tk()
    app = AutocompleteGUI(root, trie)
    root.mainloop()
