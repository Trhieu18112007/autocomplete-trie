"""Benchmark phần Hiền: chạy trong repo có trie.py và autocomplete.py.
python -m pip install matplotlib
python benchmark.py
"""
import csv
import random
import statistics
import string
import time
from pathlib import Path
from trie import Trie
from autocomplete import AutocompleteSystem

SIZES = (10_000, 50_000, 100_000)
REPEATS = 3
QUERY_COUNT = 100
OUTPUT = Path(__file__).resolve().parent / 'docs' / 'benchmark_output'


def dataset(count):
    """Dữ liệu giả lập có prefix chung để kiểm tra autocomplete; seed cố định."""
    rng = random.Random(2026)
    words = set()
    while len(words) < count:
        group = rng.choice(('app', 'data', 'code', 'web', 'python', 'tree', 'algo', 'viet'))
        words.add(group + ''.join(rng.choices(string.ascii_lowercase, k=9)))
    return sorted(words)


def elapsed_ms(action):
    samples = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        action()
        samples.append((time.perf_counter() - t0) * 1000)
    return statistics.median(samples)


def linear_suggest(pairs, prefix, n=5):
    matches = ((w, weight) for w, weight in pairs if w.startswith(prefix))
    return sorted(matches, key=lambda x: (-x[1], x[0]))[:n]


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    words_all = dataset(max(SIZES))
    rows = []
    for count in SIZES:
        words = words_all[:count]
        pairs = [(word, (i * 37) % 101 + 1) for i, word in enumerate(words)]
        # Insert: mỗi lần đo xây dựng một cây mới, không cộng dồn trọng số giữa các lần.
        insert_ms = elapsed_ms(lambda: build(Trie, pairs))
        system_insert_ms = elapsed_ms(lambda: build(AutocompleteSystem, pairs))
        cache_insert_ms = elapsed_ms(lambda: build(lambda: AutocompleteSystem(enable_node_cache=True, cache_k=10), pairs))
        trie = build(Trie, pairs)
        ac = build(AutocompleteSystem, pairs)
        cached = build(lambda: AutocompleteSystem(enable_node_cache=True, cache_k=10), pairs)
        rng = random.Random(42)
        present = rng.sample(words, QUERY_COUNT // 2)
        absent = ['notfound_' + str(i) for i in range(QUERY_COUNT // 2)]
        queries = present + absent
        rng.shuffle(queries)
        prefixes = [word[:3] for word in rng.sample(words, QUERY_COUNT)]
        # Đối chiếu tính đúng đắn trước khi đo.
        assert all(trie.search(w) == (w in words) for w in queries)
        for prefix in prefixes[:15]:
            expected = linear_suggest(pairs, prefix, 5)
            assert ac.suggest(prefix, 5) == expected, 'Sai kết quả suggest DFS'
            assert cached.suggest_fast_cache(prefix, 5) == expected, 'Sai kết quả cache'
        tests = [
            ('insert_trie', insert_ms, count),
            ('insert_autocomplete', system_insert_ms, count),
            ('insert_cache', cache_insert_ms, count),
            ('search_trie', elapsed_ms(lambda: [trie.search(w) for w in queries]), len(queries)),
            ('search_linear', elapsed_ms(lambda: [w in words for w in queries]), len(queries)),
            ('suggest_dfs', elapsed_ms(lambda: [ac.suggest(p, 5) for p in prefixes]), len(prefixes)),
            ('suggest_cache', elapsed_ms(lambda: [cached.suggest_fast_cache(p, 5) for p in prefixes]), len(prefixes)),
            ('suggest_linear', elapsed_ms(lambda: [linear_suggest(pairs, p, 5) for p in prefixes]), len(prefixes)),
        ]
        for op, total, ops in tests:
            rows.append({'words': count, 'operation': op, 'total_ms': round(total, 5),
                         'operations': ops, 'avg_ms': round(total / ops, 8)})
        print(f'Đã hoàn thành {count:,} từ; kiểm tra kết quả: OK')
    with (OUTPUT / 'benchmark_results.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('Đã lưu CSV. Cài matplotlib để xuất biểu đồ.')
        return
    for title, ops in [('insert', ['insert_trie', 'insert_autocomplete', 'insert_cache']),
                       ('search', ['search_trie', 'search_linear']),
                       ('suggest', ['suggest_dfs', 'suggest_cache', 'suggest_linear'])]:
        fig, ax = plt.subplots(figsize=(8, 5))
        for op in ops:
            values = [next(r['avg_ms'] for r in rows if r['words'] == n and r['operation'] == op) for n in SIZES]
            ax.plot([str(n) for n in SIZES], values, marker='o', label=op)
        ax.set(title=f'Benchmark {title}', xlabel='Số từ', ylabel='Thời gian trung bình / thao tác (ms)')
        ax.legend()
        ax.grid(alpha=.25)
        fig.tight_layout()
        fig.savefig(OUTPUT / f'{title}_comparison.png', dpi=170)
        plt.close(fig)
    print('Kết quả tại:', OUTPUT)


def build(factory, pairs):
    obj = factory()
    for word, weight in pairs:
        result = obj.insert(word, weight)
        if result is False:
            raise RuntimeError('Không thể chèn: ' + word)
    return obj


if __name__ == '__main__':
    run()
