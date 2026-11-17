"""
关4 · 检索命中率评测：给 RAG 的第④步装尺子
教程出处：《AI应用开发详解教程》第 4 章

测试对 = (用户问题, 正确答案应该命中哪一块的关键词)
命中率 = 命中的问题数 / 总问题数——这就是检索器的"分数"
"""
from similarity import tokenize, jaccard
from rag_bot import load_chunks

CASES = [
    ("停车方便吗", "车位"),
    ("水电费多少钱", "供暖与水电"),
    ("能养猫吗", "宠物"),
    ("地铁近吗", "交通"),
    ("怎么退租", "合同与退租"),
]


def retrieve_tuned(question, chunks, k=3, title_bonus=0.0):
    """带旋钮的检索：k = 取几块；title_bonus = 问题关键词命中标题时的额外加分"""
    def score(chunk):
        s = jaccard(question, chunk)
        if title_bonus:
            title = chunk.split("\n")[0]                       # 第一行是标题
            windows = [question[i:i + 2] for i in range(len(question) - 1)]
            if any(w and w in title for w in windows):
                s += title_bonus                               # 问题关键词戳中标题 → 加分
        return s
    scored = sorted(chunks, key=score, reverse=True)
    return scored[:k]


def run(label, k, title_bonus, synonyms=None):
    """synonyms：同义词词典——检索前先把问题里的词"翻译"成知识库用的词（查询扩展）"""
    chunks = load_chunks()
    hits = 0
    details = []
    for q, expect_kw in CASES:
        q_expanded = q + " " + " ".join(v for kk, v in (synonyms or {}).items() if kk in q)
        top = retrieve_tuned(q_expanded, chunks, k=k, title_bonus=title_bonus)
        ok = any(expect_kw in t for t in top)
        hits += ok
        details.append(f"  {'✓' if ok else '✗'} {q}（应含：{expect_kw}）")
    print(f"\n【{label}】命中率 {hits}/{len(CASES)}")
    print("\n".join(details))
    return hits


if __name__ == "__main__":
    run("旋钮0 基线 (k=3, 无加分)", k=3, title_bonus=0)
    run("旋钮1 检索条数 (k=5)", k=5, title_bonus=0)
    run("旋钮2 标题加权 (k=3, +0.1)", k=3, title_bonus=0.1)
    run("旋钮3 同义词扩展 (k=3, 猫→宠物)", k=3, title_bonus=0,
        synonyms={"猫": "宠物"})
