"""
关5 · LLM-as-Judge：用大模型当裁判给回答打分
教程出处：《AI应用开发详解教程》第 5 章

硬尺子（eval.py 的正则）只能比数字；"回答好不好"没有正则可写——
所以让另一个模型按【评分量规 rubric】打分，用"工具调用"逼它交结构化判定。
（结构化输出 = 你在 extractor.py 修了无数次的"工具调用+兜底"模式，换个用途而已）
"""
import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"
client = anthropic.Anthropic(timeout=30.0)

# 裁判要填的"判定表"（结构同 extractor 的答题卡）
JUDGE_TOOL = {
    "name": "submit_judgment",
    "description": "提交对被评答案的判定结果",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "description": "1-5 分"},
            "reason": {"type": "string",
                       "description": "打分理由。必须引用原文证据，禁止只说'挺好的'"},
        },
        "required": ["score", "reason"],
    },
}


class Judgment(BaseModel):
    score: int
    reason: str


# ★ 评分量规：每一档都有具体描述——量规越具体，裁判越稳定（关6 校准的关键）
RUBRIC = """按以下量规打分（1~5 分）：
5 分：准确回答了问题，且只用参考资料中的信息，表述清晰无遗漏
3 分：方向对但有含糊/遗漏，或混入少量资料外内容
1 分：答非所问，或编造了参考资料里不存在的信息（幻觉直接 1 分）
注意：答案长短不参与评分。"""


def judge(question: str, reference: str, answer: str) -> Judgment:
    """让裁判按量规给一份回答打分。reference=正确资料，answer=被评的回答。"""
    messages = [{"role": "user", "content":
        f"【评分量规】\n{RUBRIC}\n\n"
        f"【问题】{question}\n"
        f"【参考资料】{reference}\n"
        f"【被评答案】{answer}\n\n"
        f"请调用 submit_judgment 工具提交判定。"}]

    def _call():
        return client.messages.create(
            model=MODEL, max_tokens=1000,
            system="你是严格的质量裁判。只依据量规打分，理由必须引用原文证据。",
            tools=[JUDGE_TOOL],
            tool_choice={"type": "tool", "name": "submit_judgment"},
            messages=messages,
        )

    resp = _call()
    if not any(b.type == "tool_use" for b in resp.content):
        # 兜底：中转站偶尔不执行强制工具调用——追问一次（extractor 同款手法）
        messages += [{"role": "assistant",
                      "content": [b for b in resp.content if b.type in ("text", "tool_use")]},
                     {"role": "user",
                      "content": "必须调用 submit_judgment 工具提交判定。"}]
        resp = _call()

    for block in resp.content:
        if block.type == "tool_use":
            return Judgment(**block.input)
    raise RuntimeError("裁判两次都没有提交判定")


if __name__ == "__main__":
    REF = "小区有地下车位，月租 400 元，访客可临时停车，前 2 小时免费。"
    CASES = [
        # (问题, 被评答案, 期望档位)——期望值用来核对裁判打分准不准
        ("停车方便吗",
         "停车挺方便的。小区有地下车位，月租 400 元，访客可临时停车，前 2 小时免费。",
         "应 5 分：准确、只用资料信息"),
        ("停车方便吗",
         "停车还行吧，应该算方便。",
         "应 ~3 分：方向对但含糊无内容"),
        ("房东是谁",
         "房东是张先生，联系电话 138xxxx6666。",
         "应 1 分：编造了资料里不存在的信息（幻觉）"),
    ]
    for q, ans, expect in CASES:
        j = judge(q, REF, ans)
        print(f"\n【{expect}】")
        print(f"裁判实际：{j.score} 分")
        print(f"理由：{j.reason}")
