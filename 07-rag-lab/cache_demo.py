"""
关8 · 缓存与降级链：省钱和保命
教程出处：《AI应用开发详解教程》第 8 章

效果1 缓存：同样的问题第二次来，0 次 API 调用（省钱）
效果2 降级：主模型挂了 → 自动切备用模型 → 还不行给兜底文案（保命）
"""
import anthropic

CALLS = {"n": 0}          # API 调用计数器（证明缓存生效用）
CACHE = {}                # 缓存：问题 → 答案


def ask(question, model="claude-opus-4-8", base_url=None):
    """发一次真实 API 调用（base_url 可注入坏地址，用来模拟"模型挂了"）"""
    CALLS["n"] += 1
    client = (anthropic.Anthropic(timeout=30.0, base_url=base_url)
              if base_url else anthropic.Anthropic(timeout=30.0))
    resp = client.messages.create(
        model=model, max_tokens=1000,      # 给思考块留余量——预算太小正文没出生就被截断
        messages=[{"role": "user", "content": question}])
    texts = [b.text for b in resp.content if b.type == "text"]
    return texts[0] if texts else "(无文字返回：可能被 max_tokens 截断)"


def ask_cached(question):
    """带缓存的提问：命中缓存 = 0 次 API 调用"""
    if question in CACHE:
        print(f"[缓存命中] 本次 0 次 API 调用（累计 {CALLS['n']} 次）")
        return CACHE[question]
    ans = ask(question)
    CACHE[question] = ans
    print(f"[缓存未命中→已存] 累计 {CALLS['n']} 次 API 调用")
    return ans


def ask_with_fallback(question):
    """降级链：主模型(opus) → 备用模型(haiku) → 兜底文案"""
    try:
        # 演示：故意把主模型指向不存在的地址，模拟"贵模型挂了"
        return ask(question, "claude-opus-4-8", base_url="https://invalid.example")
    except Exception as e:
        print(f"[降级] 主模型挂了（{type(e).__name__}），自动切 haiku…")
    try:
        return ask(question, "claude-haiku-4-5")
    except Exception as e:
        print(f"[降级] haiku 也挂了（{type(e).__name__}）")
    return "服务暂时不可用，请稍后再试。"      # 最后一道：给人话，不给堆栈


if __name__ == "__main__":
    print("===== 效果1：缓存（省钱） =====")
    q = "押金怎么付？"
    print(f"第1次问「{q}」→", ask_cached(q)[:40], "…")
    print(f"第2次问「{q}」→", ask_cached(q)[:40], "…")
    print(f"两次提问累计 API 调用：{CALLS['n']} 次（=1，第二次走缓存）")

    print("\n===== 效果2：降级链（保命） =====")
    print("回答 →", ask_with_fallback("交通方便吗？")[:60], "…")
