"""
test_trie.py - Unit test cho trie.py (insert / search / startsWith / xử lý biên).
Chạy:  python -m unittest -v test_trie     hoặc     pytest -v test_trie.py
"""

import random
import string
import unicodedata
import unittest

from trie import Trie, TrieNode, normalize


class TestInsertSearch(unittest.TestCase):
    def setUp(self):
        self.t = Trie()

    def test_empty_trie(self):
        self.assertEqual(len(self.t), 0)
        self.assertFalse(self.t.search("a"))
        self.assertEqual(self.t.root.children, {})

    def test_insert_then_search(self):
        self.t.insert("apple", 5)
        self.assertTrue(self.t.search("apple"))
        self.assertEqual(len(self.t), 1)

    def test_search_missing_word(self):
        self.t.insert("apple", 5)
        self.assertFalse(self.t.search("banana"))

    def test_prefix_is_not_a_word(self):
        self.t.insert("apple", 5)
        self.assertFalse(self.t.search("app"))
        self.assertFalse(self.t.search("appl"))

    def test_longer_than_stored_word(self):
        self.t.insert("app", 5)
        self.assertFalse(self.t.search("apple"))

    def test_word_and_its_prefix_both_stored(self):
        self.t.insert("app", 2)
        self.t.insert("apple", 7)
        self.assertTrue(self.t.search("app"))
        self.assertTrue(self.t.search("apple"))
        self.assertEqual(self.t.get_weight("app"), 2)
        self.assertEqual(self.t.get_weight("apple"), 7)
        self.assertEqual(len(self.t), 2)

    def test_insert_prefix_after_longer_word(self):
        self.t.insert("apple", 7)
        self.assertFalse(self.t.search("app"))
        self.t.insert("app", 1)
        self.assertTrue(self.t.search("app"))

    def test_single_character_word(self):
        self.t.insert("a", 3)
        self.assertTrue(self.t.search("a"))
        self.assertFalse(self.t.search("b"))

    def test_shared_prefix_shares_nodes(self):
        self.t.insert("car", 1)
        self.t.insert("cart", 1)
        self.t.insert("cat", 1)
        c = self.t.root.children["c"]
        a = c.children["a"]
        self.assertEqual(set(a.children), {"r", "t"})
        self.assertEqual(len(self.t), 3)

    def test_default_weight_is_one(self):
        self.t.insert("hello")
        self.assertEqual(self.t.get_weight("hello"), 1)

    def test_weight_accumulates_on_duplicate(self):
        self.t.insert("apple", 5)
        self.t.insert("apple", 3)
        self.assertEqual(self.t.get_weight("apple"), 8)
        self.assertEqual(len(self.t), 1)      # không đếm trùng

    def test_float_and_zero_weight(self):
        self.t.insert("a", 0)
        self.t.insert("b", 2.5)
        self.assertTrue(self.t.search("a"))
        self.assertEqual(self.t.get_weight("a"), 0)
        self.assertAlmostEqual(self.t.get_weight("b"), 2.5)

    def test_get_weight_missing_returns_none(self):
        self.t.insert("apple", 5)
        self.assertIsNone(self.t.get_weight("app"))
        self.assertIsNone(self.t.get_weight("zzz"))

    def test_contains_operator(self):
        self.t.insert("apple")
        self.assertIn("apple", self.t)
        self.assertNotIn("app", self.t)


class TestStartsWith(unittest.TestCase):
    def setUp(self):
        self.t = Trie()
        for w, f in [("app", 2), ("apple", 7), ("apply", 3), ("banana", 4)]:
            self.t.insert(w, f)

    def test_returns_node(self):
        node = self.t.startsWith("app")
        self.assertIsInstance(node, TrieNode)
        self.assertEqual(set(node.children), {"l"})

    def test_node_of_complete_word(self):
        node = self.t.startsWith("app")
        self.assertTrue(node.isEnd)
        self.assertEqual(node.weight, 2)

    def test_node_of_pure_prefix_is_not_end(self):
        node = self.t.startsWith("appl")
        self.assertIsNotNone(node)
        self.assertFalse(node.isEnd)

    def test_nonexistent_prefix(self):
        self.assertIsNone(self.t.startsWith("xyz"))
        self.assertIsNone(self.t.startsWith("applex"))

    def test_empty_prefix_returns_root(self):
        self.assertIs(self.t.startsWith(""), self.t.root)

    def test_prefix_on_empty_trie(self):
        self.assertIsNone(Trie().startsWith("a"))

    def test_subtree_can_be_traversed(self):
        """Giả lập việc Khang duyệt cây con từ node của prefix."""
        found = []

        def dfs(node, path):
            if node.isEnd:
                found.append(path)
            for ch in sorted(node.children):
                dfs(node.children[ch], path + ch)

        dfs(self.t.startsWith("app"), "app")
        self.assertEqual(found, ["app", "apple", "apply"])

    def test_starts_with_alias(self):
        self.assertIs(self.t.starts_with("app"), self.t.startsWith("app"))

    def test_prefix_is_normalized(self):
        self.assertIs(self.t.startsWith("APP"), self.t.startsWith("app"))


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.t = Trie()

    # --- chuỗi rỗng
    def test_insert_empty_raises(self):
        with self.assertRaises(ValueError):
            self.t.insert("")

    def test_insert_whitespace_only_raises(self):
        with self.assertRaises(ValueError):
            self.t.insert("   \t\n")

    def test_search_empty_is_false(self):
        self.t.insert("a")
        self.assertFalse(self.t.search(""))
        self.assertFalse(self.t.search("   "))

    def test_failed_insert_leaves_trie_unchanged(self):
        with self.assertRaises(ValueError):
            self.t.insert("", 5)
        with self.assertRaises(ValueError):
            self.t.insert("abc", -1)
        self.assertEqual(len(self.t), 0)
        self.assertEqual(self.t.root.children, {})   # không tạo node thừa

    # --- chữ hoa / thường
    def test_case_insensitive(self):
        self.t.insert("Apple", 2)
        self.assertTrue(self.t.search("apple"))
        self.assertTrue(self.t.search("APPLE"))
        self.assertTrue(self.t.search("aPpLe"))

    def test_case_variants_merge_weight(self):
        self.t.insert("Apple", 2)
        self.t.insert("APPLE", 3)
        self.assertEqual(self.t.get_weight("apple"), 5)
        self.assertEqual(len(self.t), 1)

    # --- khoảng trắng
    def test_word_edges_are_stripped(self):
        self.t.insert("  hello  ", 1)
        self.assertTrue(self.t.search("hello"))
        self.assertTrue(self.t.search("  hello"))

    def test_inner_space_is_kept(self):
        self.t.insert("new york", 4)
        self.assertTrue(self.t.search("new york"))
        self.assertFalse(self.t.search("newyork"))

    def test_trailing_space_in_prefix_is_kept(self):
        self.t.insert("new york", 4)
        self.t.insert("newark", 2)
        node = self.t.startsWith("new ")
        self.assertIsNotNone(node)
        self.assertEqual(set(node.children), {"y"})   # chỉ "new york", không có "newark"

    # --- ký tự đặc biệt
    def test_special_characters(self):
        for w in ["c++", "c#", "don't", "e-mail", "a.b", "100%", "x_y", "hello!", "a/b", "tab\tinside"]:
            self.t.insert(w, 1)
        for w in ["c++", "c#", "don't", "e-mail", "a.b", "100%", "x_y", "hello!", "a/b", "tab\tinside"]:
            self.assertTrue(self.t.search(w), w)
        self.assertFalse(self.t.search("c"))
        self.assertFalse(self.t.search("e mail"))

    def test_digits_and_symbols_only(self):
        self.t.insert("12345", 1)
        self.t.insert("@#$", 1)
        self.assertTrue(self.t.search("12345"))
        self.assertTrue(self.t.search("@#$"))

    def test_emoji_and_non_latin(self):
        self.t.insert("cà phê ☕", 1)
        self.t.insert("日本語", 1)
        self.t.insert("привет", 1)
        self.assertTrue(self.t.search("cà phê ☕"))
        self.assertTrue(self.t.search("日本語"))
        self.assertTrue(self.t.search("ПРИВЕТ"))

    # --- tiếng Việt
    def test_vietnamese_basic(self):
        self.t.insert("xin chào", 10)
        self.t.insert("việt nam", 8)
        self.assertTrue(self.t.search("xin chào"))
        self.assertTrue(self.t.search("việt nam"))

    def test_vietnamese_uppercase(self):
        self.t.insert("Hà Nội", 5)
        self.assertTrue(self.t.search("hà nội"))
        self.assertTrue(self.t.search("HÀ NỘI"))

    def test_vietnamese_nfc_vs_nfd(self):
        composed = unicodedata.normalize("NFC", "tiếng việt")
        decomposed = unicodedata.normalize("NFD", "tiếng việt")
        self.assertNotEqual(composed, decomposed)        # đảm bảo hai dạng thực sự khác nhau
        self.t.insert(decomposed, 3)                     # chèn bằng dạng rời
        self.assertTrue(self.t.search(composed))         # tìm bằng dạng tổ hợp
        self.assertTrue(self.t.search(decomposed))
        self.t.insert(composed, 2)                       # chèn lại bằng dạng tổ hợp
        self.assertEqual(len(self.t), 1)                 # vẫn là một từ duy nhất
        self.assertEqual(self.t.get_weight("tiếng việt"), 5)

    def test_vietnamese_prefix_nfd(self):
        self.t.insert("tiếng", 1)
        node = self.t.startsWith(unicodedata.normalize("NFD", "tiế"))
        self.assertIsNotNone(node)

    def test_diacritics_are_distinct(self):
        self.t.insert("an", 1)
        self.t.insert("ăn", 1)
        self.t.insert("ân", 1)
        self.t.insert("da", 1)
        self.t.insert("đa", 1)
        self.assertEqual(len(self.t), 5)
        self.assertFalse(self.t.search("ần"))
        self.assertNotEqual(self.t.get_weight("đa"), None)
        self.assertEqual(set(self.t.root.children), {"a", "ă", "â", "d", "đ"})

    def test_d_stroke_lowercase(self):
        self.t.insert("Đà Nẵng", 6)
        self.assertTrue(self.t.search("đà nẵng"))

    # --- kiểu dữ liệu sai
    def test_non_string_raises_type_error(self):
        for bad in [None, 123, 1.5, ["a"], b"abc"]:
            with self.assertRaises(TypeError):
                self.t.insert(bad)
            with self.assertRaises(TypeError):
                self.t.search(bad)
            with self.assertRaises(TypeError):
                self.t.startsWith(bad)

    def test_invalid_weight_raises(self):
        for bad in [-1, -0.1, float("nan"), float("inf"), "5", None, True]:
            with self.assertRaises(ValueError):
                self.t.insert("abc", bad)
        self.assertFalse(self.t.search("abc"))

    # --- normalize()
    def test_normalize_function(self):
        self.assertEqual(normalize("  HÀ  "), "hà")
        self.assertEqual(normalize("  HÀ  ", strip=False), "  hà  ")
        self.assertEqual(normalize("e\u0301"), "\u00e9")     # e + dấu sắc rời -> é


class TestScale(unittest.TestCase):
    def test_many_words_against_reference_set(self):
        rng = random.Random(2026)
        ref = {}
        t = Trie()
        for _ in range(20000):
            w = "".join(rng.choice("abcdeăâđ") for _ in range(rng.randint(1, 8)))
            f = rng.randint(1, 100)
            t.insert(w, f)
            ref[w] = ref.get(w, 0) + f
        self.assertEqual(len(t), len(ref))
        for w, f in ref.items():
            self.assertTrue(t.search(w))
            self.assertEqual(t.get_weight(w), f)
        for _ in range(2000):                 # từ không có trong tập tham chiếu
            w = "".join(rng.choice(string.ascii_uppercase) for _ in range(rng.randint(9, 12)))
            self.assertFalse(t.search(w))

    def test_very_long_word(self):
        word = "a" * 10000
        t = Trie()
        t.insert(word, 1)
        self.assertTrue(t.search(word))
        self.assertFalse(t.search(word + "a"))
        self.assertFalse(t.search(word[:-1]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
