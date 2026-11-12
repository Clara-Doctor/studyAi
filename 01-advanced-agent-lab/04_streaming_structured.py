"""
第 4 课：流式输出 + 结构化输出 —— 零基础注释版
运行：python 04_streaming_structured.py

本课新语法（详见《Python语法急救包.md》）：
- with 语句（§13）
- class X(BaseModel) 数据模板（§9）
- parsed_output：模型回答直接变成 Python 对象
"""
import anthropic
from pydantic import BaseModel     # pydantic：定义"数据模板"的库

client = anthropic.Anthropic()
MODEL = "claude-opus-4-8"


def demo_streaming():
    print("===== Demo 1：流式输出（边生成边打印）=====")
    # client.messages.stream(...)  流式请求：内容一点一点到达，不用等全部生成完
    # with ... as stream:          with 语句 = 结束后自动收拾干净（断开连接）
    with client.messages.stream(
        model=MODEL,
        max_tokens=2000,
        messages=[
            {"role": "user", "content": "用 5 个要点解释：为什么 Agent 循环要有轮数上限？"}
        ],
    ) as stream:
        # stream.text_stream：每次循环吐出一小段新文字
        # print(..., end="", flush=True)：end="" 表示不换行（接着打）；
        #   flush=True 表示立刻显示（不等缓冲区攒够）
        for text in stream.text_stream:
            print(text, end="", flush=True)
        # 流结束后仍能拿到"完整消息对象"，和普通请求的 response 一样用
        final = stream.get_final_message()
    print(f"\n\n(流式完成，output_tokens = {final.usage.output_tokens})")
    # ↑ final.usage.output_tokens = 这轮生成消耗的 token 数（计费看这里）


# ---------- Demo 2：结构化输出 ----------
class CodeReview(BaseModel):
    """用 Pydantic 定义"你想要的回答长什么样"。
    这几行是数据模板：告诉 SDK"我要一个对象，里面有
    has_bug(布尔)、severity(字符串)、issues(字符串列表) 三个字段"。
    SDK 会自动把它转成格式要求发给模型，模型返回后自动校验。
    之后你就能用 代码.字段 的方式取值，不用解析文字！"""
    has_bug: bool                     # True / False
    severity: str                     # "low" / "medium" / "high"
    issues: list[str]                 # 字符串组成的列表


def demo_structured():
    print("\n===== Demo 2：结构化输出（回答变成可编程对象）=====")
    buggy_code = '''def average(nums):
    return sum(nums) / len(nums)'''
    # ↑ 三引号字符串：可以跨多行，常用来装代码块

    response = client.messages.parse(
        # ↑ 注意：不再是 .create，而是 .parse —— 专为结构化输出准备的入口
        model=MODEL,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": f"评审这段代码，找出所有 bug：\n```python\n{buggy_code}\n```",
                # ↑ \n 是换行符；``` 是 Markdown 的代码块标记
            }
        ],
        output_format=CodeReview,     # 告诉它"按这个模板返回"
    )
    review = response.parsed_output   # 拿到的直接是 CodeReview 对象！

    # 关键区别：以前要从一段话里"抠"信息（脆弱）；
    # 现在直接用 .字段名 取值（稳），还能写 if 判断 —— 程序可以"消费"AI 结果了
    print(f"有 bug 吗 : {review.has_bug}")
    print(f"严重程度  : {review.severity}")
    for issue in review.issues:       # issues 是列表，逐条打印
        print(f"  - {issue}")

    if review.has_bug and review.severity == "high":
        # and = 两边都成立才进；这里演示"程序根据 AI 结论自动行动"
        print("-> 条件命中：真实系统里这里可以自动建高优工单 / 打回重写")


if __name__ == "__main__":
    demo_streaming()
    demo_structured()
