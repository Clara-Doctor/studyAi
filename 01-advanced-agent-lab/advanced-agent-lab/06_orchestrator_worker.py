"""
第 7 课：指挥官-工人（Orchestrator-Worker）多智能体 —— 零基础注释版
运行：python 06_orchestrator_worker.py

本课的核心技巧只有一个：把"派子智能体"本身注册成一个工具（delegate）。
这正是 Claude Code 里 Agent 工具的原理！

本课新语法（详见《Python语法急救包.md》）：
- 列表相加拼接：FS_TOOLS + [DELEGATE_TOOL]（§3）
- tool_executor 参数：第 3 课留的"插槽"，这里用上了
"""
# 只从 agent_lib 拿需要的四样东西
from agent_lib import run_agent, FS_TOOLS, execute_tool

EXPLORER_SYSTEM = (
    "你是一名高效的调研员。用工具读取指定文件，输出要点列表（每条一行）。"
    "只回答被问的问题，不写废话。"
)
# ↑ "工人"的身份设定。每个子智能体都带着这套设定出生

DELEGATE_TOOL = {
    # 给"主 Agent（指挥官）"看的工具说明。
    # 对主 Agent 来说，delegate 和 read_file 没有区别——都是可点名的工具。
    # 它不知道的是：这个工具的返回值背后，是一个完整的子 Agent 跑了几十轮！
    "name": "delegate",
    "description": (
        "把一个独立的调研子任务交给子智能体执行。"
        "子智能体有文件读取工具，但看不到本对话，"
        "所以任务描述必须自包含（写清楚要读哪个文件、回答什么问题）。"
        "它会返回最终结论文本。"
    ),
    # ↑ description 里必须写清楚"子智能体看不到本对话"——
    #   这是在教主 Agent：派活时要把话说明白（任务自包含）
    "input_schema": {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "完整、自包含的子任务描述"}
        },
        "required": ["task"],
    },
}


def delegate(task: str) -> str:
    """每次委派 = 调用 run_agent() 全新启动一个子 Agent。

    关键认知 1（上下文隔离）：子 Agent 看不到主对话，
    它的唯一信息来源就是 task 这段文字 —— 所以任务描述必须自包含。
    关键认知 2（结论回传）：它内部跑的几十轮读文件过程全部丢弃，
    只有最终结论这个字符串返回给主 Agent。主 Agent 的上下文始终干净。
    """
    print(f"\n>>> 派出子智能体：{task[:60]}...")
    result = run_agent(EXPLORER_SYSTEM, task, tools=FS_TOOLS, max_turns=10, verbose=False)
    #                                          ↑ verbose=False：子 Agent 干活过程不刷屏
    print(f"<<< 子智能体已返回（结论 {len(result)} 字符）")
    return result


def main_executor(name: str, args: dict):
    """主 Agent 专用的工具执行器（第 3 课留的 tool_executor 插槽）。
    规则：名字叫 delegate 的我自己处理，其余的转交给默认文件工具。"""
    if name == "delegate":
        return delegate(args["task"]), False    # 返回(结论, 不是错误)
    return execute_tool(name, args)             # list_files / read_file / write_file


ORCHESTRATOR_SYSTEM = (
    "你是工程团队的协调员。你的工作是拆解任务、派出子智能体、汇总结论。"
    "不要自己直接读大文件——那是子智能体的活。"
    "可以同时在一条消息里发出多个 delegate 调用来并行调研。"
)
# ↑ 最后一句是在"教"主 Agent 并行：
#   API 允许模型一次回复里发多个工具调用，我们的循环天然支持（逐个执行再一起回传）


TASK = (
    "docs/ 目录下有几份模块文档。请派出子智能体分别调研每份文档的："
    "模块职责 + 它最重要的一条规则。全部返回后，"
    "把汇总写成 docs/report.md，并在最终回复里给出 3 行以内的摘要。"
)


def main():
    print("===== 指挥官（主 Agent）开始工作 =====")
    final = run_agent(
        ORCHESTRATOR_SYSTEM,
        TASK,
        tools=FS_TOOLS + [DELEGATE_TOOL],   # 列表相加：3 个文件工具 + delegate = 4 个
        max_turns=15,
        verbose=True,
        tool_executor=main_executor,        # ★ 插上自定义执行器，delegate 生效
    )
    print("\n===== 指挥官的最终汇报 =====")
    print(final)
    print("\n打开 docs/report.md 看看汇总结果。")
    print("思考题：主 Agent 的上下文里只有 3 段结论，而 3 个子智能体各自")
    print("       读了完整文档——如果只有 1 个 Agent 自己读，它的窗口会怎样？")


if __name__ == "__main__":
    main()
