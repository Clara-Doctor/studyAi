"""
第 6 课：双 Agent 对抗 —— 生成者 vs 评审者（零基础注释版）
运行：python 05_generator_critic.py

本课新语法（详见《Python语法急救包.md》）：
- range(1, 4) 循环（§7）
- "\\n".join(列表)（§3/§11）
- 复用 agent_lib（第 3 课的框架）
"""
from pydantic import BaseModel
# from agent_lib import ...：把第 3 课写的框架文件里这些东西引进来用
from agent_lib import run_agent, FS_TOOLS, client, MODEL, BASE_DIR

WORKSPACE = "workspace5"  # 生成者的工作目录（相对 lab 根目录，写文件时自动创建）

GEN_SYSTEM = (
    "你是一名严谨的 Python 工程师。只做任务要求的事，代码完整可运行，"
    "带类型注解和简短 docstring。写完文件后在最终回复中说明你写了什么。"
)
# ↑ 这个字符串是"生成者 Agent"的身份设定（system prompt）。
#   多个圆括号字符串挨着写 = 自动拼接成一段（Python 的小技巧）

CRITIC_SYSTEM = (
    "你是一名极其挑剔的代码评审员。只关心正确性："
    "边界条件、异常处理、是否严格符合规格。不要评论代码风格。"
)
# ↑ 评审者是【另一个 Agent】：不同的身份设定 = 不同的"人格"。
#   多智能体的"分工"，很大程度就是不同的 system prompt


class Verdict(BaseModel):
    """评审结论的数据模板（同第 4 课的用法）。
    为什么必须结构化？——主程序要用代码判断 v.verdict == "pass" 来决定走向，
    总不能让程序去读"我觉得还行吧"这种自然语言。"""
    verdict: str       # "pass" 或 "revise"
    issues: list[str]  # 打回原因清单；pass 时为空列表 []


def critique(code: str, spec: str) -> Verdict:
    """评审者：运行在【全新上下文】——
    只喂给它规格和代码，它完全不知道代码是怎么写出来的。
    没有'我为什么要这么写'的立场，才挑得出真毛病。"""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4000,
        system=CRITIC_SYSTEM,               # 评审者的身份
        messages=[
            {
                "role": "user",
                "content": (
                    f"功能规格：\n{spec}\n\n"
                    f"待评审代码：\n```python\n{code}\n```\n\n"
                    "对照规格逐条检查。全部满足则 verdict=pass；"
                    "否则 verdict=revise，并在 issues 里列出每个具体问题。"
                ),
            }
        ],
        output_format=Verdict,              # 结论必须是结构化的
    )
    return response.parsed_output           # 返回 Verdict 对象，调用方直接用


def main():
    spec = (
        "实现函数 median(nums: list[float]) -> float：\n"
        "1. 空列表抛 ValueError，消息为 'empty list'\n"
        "2. 奇数个元素：返回排序后的中间值\n"
        "3. 偶数个元素：返回中间两个数的平均值\n"
        "4. 文件底部写 if __name__ == '__main__' 的自测代码，覆盖上述 3 种情况"
    )
    # ↑ spec 是"功能规格"：生成者照它写代码，评审者照它挑毛病。双方共同的裁判标准

    feedback = ""                           # 评审打回意见，一开始为空
    for round_no in range(1, 4):            # 最多对抗 3 轮：round_no = 1, 2, 3
        print(f"\n========== 第 {round_no} 轮：生成者干活 ==========")
        if feedback:                        # feedback 非空 = 上一轮被打回了
            task = (
                f"你上一版的代码被评审打回，问题清单：\n{feedback}\n\n"
                f"请修订 {WORKSPACE}/math_utils.py，严格满足全部规格：\n{spec}"
            )
        else:                               # 第一轮：正常布置任务
            task = f"在 {WORKSPACE}/math_utils.py 中实现以下规格：\n{spec}"

        # 生成者 Agent 开工：run_agent 是第 3 课框架里的主循环。
        # 注意：每次调用都是全新的一次对话（上一轮的对话不会带进去，
        # 我们只把"打回意见"写进任务文字里传给它）
        run_agent(GEN_SYSTEM, task, tools=FS_TOOLS, max_turns=10, verbose=True)

        # 生成者写的文件读出来（它有 write_file 工具，文件真实存在于磁盘上）
        code_path = BASE_DIR / WORKSPACE / "math_utils.py"
        code = code_path.read_text(encoding="utf-8")

        print(f"\n---------- 第 {round_no} 轮：评审者检查 ----------")
        v = critique(code, spec)            # 评审者登场（全新上下文）
        print(f"verdict = {v.verdict}")
        for issue in v.issues:
            print(f"  - {issue}")

        if v.verdict == "pass":             # 用代码判断走向——结构化的价值！
            print(f"\n✅ 第 {round_no} 轮通过评审！成品在 {code_path}")
            return                          # 整个 main() 结束
        # 没通过：把问题列表拼成一段文字（每条前面加"- "，用换行连接），
        # 下一轮生成时塞进任务里
        feedback = "\n".join(f"- {i}" for i in v.issues)

    # 3 轮都没过，走到这里。正确的产品设计：升级给人，而不是无限吵下去
    print("\n⚠️ 3 轮对抗后仍未通过。真实系统中，此时应该把问题升级给人类，而不是硬扛。")


if __name__ == "__main__":
    main()
