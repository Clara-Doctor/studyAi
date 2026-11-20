"""
关3 · RAG 问答机器人：把关2的打分器装进 RAG 五步流水线
教程出处：《AI应用开发详解教程》第 3 章

流程：读知识库切块(①) → 问题来了检索 top3(④) → 拼进提示词(⑤) → 模型回答
反幻觉红线（写在 system 里）：资料里没有的，老实说没有提到，禁止编造。

改良说明（对照教程）：tokenize/jaccard 不再复制粘贴，直接从 similarity.py import——
和线一"服务复用 extractor"是同一个手法：写过的代码不抄第二遍。
"""
import anthropic
from similarity import tokenize, jaccard     # 复用关2的打分器
from armor import call_with_retry            # 关7：公共盔甲（超时已在 client 上）

MODEL = "claude-opus-4-8"
client = anthropic.Anthropic(timeout=30.0)    # 盔甲习惯：超时从第一天就带着


def load_chunks(path="faq.md"):
    """步骤①切块：按 '## ' 标题切成一块一块（标题+正文算一块）"""
    chunks, title, body = [], None, []
    for line in open(path, encoding="utf-8"):
        if line.startswith("## "):            # 遇到新标题：收上一块，开新块
            if title:
                chunks.append(f"{title}\n" + "".join(body))
            title, body = line.strip(), []
        else:
            body.append(line)
    if title:
        chunks.append(f"{title}\n" + "".join(body))
    return chunks


def retrieve(question, chunks, k=3):
    """步骤④检索：给每个块打相似度分，取最高的 k 块"""
    scored = sorted(chunks, key=lambda c: jaccard(question, c), reverse=True)
    return scored[:k]


def answer(question):
    """步骤⑤拼接+回答：资料垫底，问题压轴，反幻觉红线写死在 system"""
    chunks = load_chunks()
    top = retrieve(question, chunks)
    context = "\n---\n".join(top)
    resp = call_with_retry(lambda: client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=("你是房源客服。只根据【参考资料】回答问题；"
                "参考资料里没有的信息，老实回答'这个资料里没有提到'，禁止编造。"),
        messages=[{"role": "user",
                   "content": f"【参考资料】\n{context}\n\n【问题】{question}"}],
    ))
    # 返回的 content 是块列表（思考块/文字块混排），必须按类型过滤，不能按位置猜
    return next(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    # 三连验收实验（代替教程里的手动输入循环，方便自动化重跑）
    for q in ["停车方便吗",            # 应命中"小区停车"，答对
              "能养宠物吗",            # 应命中"宠物"，答"不允许"
              "房东是谁"]:             # 知识库里根本没有 → 必须答"没有提到"
        print(f"\n【问】{q}")
        print(f"【答】{answer(q)}")
