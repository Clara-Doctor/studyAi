"""
第 8 课：给 Agent 建一个迷你评测集 —— 零基础注释版
运行：python 07_eval.py

核心思想：AI 系统没有评测就没有进步。
评测集 = 固定任务 + 自动判分。每次改动（换模型/改提示词）后重跑对比分数。

本课新语法（详见《Python语法急救包.md》）：
- 列表套字典装测试用例（§3/§4）
- p.unlink() 删文件、startswith()（§11/§9）
- 列表推导式（§3 的进阶用法）
"""
from pydantic import BaseModel
from agent_lib import run_agent, FS_TOOLS, client, MODEL, BASE_DIR


# ---------- Part A：分类任务评测 ----------
class Sentiment(BaseModel):
    label: str  # positive / negative / neutral


# 测试用例：列表里装字典，每个字典 = 输入文本 + 标准答案
# 【关键】用例是"固定"的——每次评测都用同一批，分数才有可比性
CLASSIFICATION_CASES = [
    {"text": "这耳机音质绝了，戴一天都不累", "label": "positive"},
    {"text": "用了三天就坏了，客服态度还差", "label": "negative"},
    {"text": "包装是白色的，重量约 300 克", "label": "neutral"},
    {"text": "比想象中小巧，但续航拉胯", "label": "negative"},
    {"text": "回购第三次了，全家都在用", "label": "positive"},
    {"text": "产地是广东，发货挺快", "label": "neutral"},
]


def eval_classification() -> float:
    print("===== Part A：情感分类评测 =====")
    correct = 0                                  # 答对计数器
    for case in CLASSIFICATION_CASES:            # 逐条测试
        resp = client.messages.parse(
            model=MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": f"判断情感倾向: {case['text']}"}],
            output_format=Sentiment,             # 结构化输出：只要一个 label 字段
        )
        got = resp.parsed_output.label
        got = got.strip().lower()                # .strip() 去首尾空格，.lower() 转小写
        # （模型有时返回 "Positive" 或 " positive "，先归一化再比较，判分才稳）
        ok = got == case["label"]                # 和标准答案比对 -> True/False
        correct += ok
        # ↑ True 当 1 用、False 当 0 用，所以可以直接累加
        mark = "✅" if ok else "❌"
        # :<8 表示"左对齐占 8 个字符宽"，纯粹为了让输出表格对齐好看
        print(f"  {mark} 期望={case['label']:<8} 实际={got:<10} | {case['text']}")
    acc = correct / len(CLASSIFICATION_CASES)    # 准确率 = 答对数 / 总数
    print(f"准确率: {correct}/{len(CLASSIFICATION_CASES)} = {acc:.0%}\n")
    return acc


# ---------- Part B：Agent 行为评测 ----------
def eval_agent_creates_file() -> bool:
    """评测标准不是'回答好不好听'，而是【事有没有真的做成】：
    文件必须真实存在、标题格式合格。这叫"检查产物"，不叫"看感觉"。"""
    todo_path = BASE_DIR / "todo_eval.md"
    if todo_path.exists():
        todo_path.unlink()   # unlink = 删除文件。先清掉上次的残留，
                             # 保证每次评测从同一张白纸开始（评测可重复）
    run_agent(
        system_prompt="你是文件助手。任务必须真的完成，不能只是口头描述。",
        task="创建 todo_eval.md：一个 'TODO' 标题（# 开头），下面列 3 条任意任务。",
        tools=FS_TOOLS,
        max_turns=8,
        verbose=False,       # 评测时不打印过程，跑完只看结果
    )

    print("===== Part B：Agent 行为评测 =====")
    ok = False
    if todo_path.exists():                           # 检查点 1：文件存在吗
        content = todo_path.read_text(encoding="utf-8")
        has_title = content.lstrip().startswith("#") # 检查点 2：以 # 开头（标题合格）
        # 列表推导式：遍历每行 l，只要非空行（l.strip() 非空）就收进列表
        line_count = len([l for l in content.splitlines() if l.strip()])
        ok = has_title and line_count >= 4           # 标题 + 至少4行(标题+3条任务)
        print(f"  文件存在: True | 标题合格: {has_title} | 非空行数: {line_count}")
    else:
        print("  文件存在: False ❌")
    print(f"  结果: {'✅ 通过' if ok else '❌ 未通过'}\n")
    return ok


if __name__ == "__main__":
    acc = eval_classification()
    behavior_ok = eval_agent_creates_file()

    print("===== 评测总报告 =====")
    print(f"分类准确率   : {acc:.0%}")          # :.0% = 显示成百分比，不带小数
    print(f"Agent 行为测试: {'通过' if behavior_ok else '未通过'}")
    print("\n下一步实验：改动 agent_lib.py 的 MODEL 常量或 run_agent 的参数，")
    print("重跑本文件对比分数——这就是'用评测驱动 Agent 迭代'。")
