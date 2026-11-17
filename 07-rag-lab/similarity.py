"""
关2 · 相似度实验：最朴素的"找相似"打分器（jaccard 关键词重合度）
教程出处：《AI应用开发详解教程》第 2.1 节

jaccard 相似度 = 两个集合的交集 / 并集。
1 = 完全一样，0 = 毫无重叠。
这就是 RAG 第④步"检索"的心脏——先从最笨的版本开始，才能理解为什么后面要 embedding。
"""
import sys


def tokenize(text):
    """把一段话切成"片段集合"。
    中文没有空格分词，教学版用 2 字滑窗粗暴切片：
    "朝南两居" → {"朝南", "南两", "两居"}——能抓到大部分词，也会混进噪声。"""
    for ch in "，。？！、 ":                 # 先丢掉标点和空格
        text = text.replace(ch, "")
    return {text[i:i + 2] for i in range(len(text) - 1)}


def jaccard(a, b):
    """相似度打分：交集/并集。"""
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0
    return len(ta & tb) / len(ta | tb)


if __name__ == "__main__":
    # 知识库里的三条房源描述（RAG 的"块"）
    docs = [
        "两室一厅 89平 朝南 拎包入住",
        "南北通透三居室 120平米 拎包入住",
        "朝阳公园旁一居 45平 拎包入住",
    ]
    # 实验改良：问题从命令行传入，不传就用默认值——方便做对照组实验
    q = sys.argv[1] if len(sys.argv) > 1 else "朝南两居 拎包入住"
    print(f"问题：{q}\n")

    ranked = sorted(docs, key=lambda d: jaccard(q, d), reverse=True)
    for d in ranked:
        print(f"  相似度 {jaccard(q, d):.2f}  |  {d}")
