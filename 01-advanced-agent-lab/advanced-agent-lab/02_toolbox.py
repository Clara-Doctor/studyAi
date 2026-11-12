"""
第 2 课：给 Agent 一个像样的工具箱 —— 零基础注释版
运行：python 02_toolbox.py

本课新语法（详见《Python语法急救包.md》）：
- Path / 文件读写（急救包 §11）
- 字典当"分发表"用（§4）
- try/except 错误处理（§10）
- 一次返回两个值（元组）
"""
import anthropic
from pathlib import Path

# __file__ = 本文件自己的位置；.resolve().parent = 它所在的文件夹。
# 所有文件操作都锚定在这个目录，不依赖你从哪里启动程序。
BASE_DIR = Path(__file__).resolve().parent

client = anthropic.Anthropic()   # 连接 AI 模型的"电话线"（同第 1 课）
MODEL = "claude-opus-4-8"

TOOLS = [
    # 工具定义的格式和第 1 课完全一样：name + description + input_schema
    # 加新工具 = 在这里加一段 + 下面写一个同名函数 + 登记到 TOOL_HANDLERS 表
    {
        "name": "list_files",
        "description": "列出某个子目录下的所有文件名。",
        "input_schema": {
            "type": "object",
            "properties": {"folder": {"type": "string", "description": "子目录名，如 docs"}},
            "required": ["folder"],
        },
    },
    {
        "name": "read_file",
        "description": "读取指定路径的文本文件，返回完整内容。",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "文件路径，如 docs/auth.md"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "把文本内容写入指定路径（覆盖已有内容，目录不存在会自动创建）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "目标文件路径"},
                "content": {"type": "string", "description": "要写入的完整内容"},
            },
            "required": ["path", "content"],
        },
    },
]


# ---------- 三个工具的真正实现 ----------
def tool_list_files(folder: str) -> str:
    folder_path = BASE_DIR / folder            # 用 / 拼路径：BASE_DIR/docs
    if not folder_path.is_dir():               # is_dir()：这个路径是文件夹吗
        return f"错误：目录 {folder} 不存在"    # 出错就返回错误文本（不崩程序）
    # 这一行是"遍历+筛选"：对文件夹里每一项 p，只要它是文件，就取它的名字，
    # sorted() 把名字排好序，"\n".join() 用换行符把所有名字拼成一段文字
    names = sorted(p.name for p in folder_path.iterdir() if p.is_file())
    return "\n".join(names) if names else "（空目录）"


def tool_read_file(path: str) -> str:
    file_path = BASE_DIR / path
    if not file_path.is_file():                # is_file()：这个路径是文件吗
        return f"错误：文件 {path} 不存在"
    return file_path.read_text(encoding="utf-8")   # 一次性读出全部文字


def tool_write_file(path: str, content: str) -> str:
    file_path = BASE_DIR / path
    # mkdir：创建文件夹。parents=True 连父文件夹一起建；exist_ok=True 已存在也不报错
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"已写入 {path}（{len(content)} 字符）"


# ---------- 工具分发表：名字 -> 函数 ----------
# 这是本课最重要的新写法！字典的"值"也可以是函数。
# 好处：执行工具时不用写一长串 if/elif，查表即可。
TOOL_HANDLERS = {
    "list_files": tool_list_files,
    "read_file": tool_read_file,
    "write_file": tool_write_file,
}


def execute_tool(name: str, args: dict):
    """执行工具，永远返回 (结果文本, 是否为错误) 两个值。
    Python 允许一次返回多个值，调用时用两个变量接住：
        result, is_error = execute_tool(...)
    """
    handler = TOOL_HANDLERS.get(name)
    # ↑ .get("名字")：查字典。和 msg["名字"] 的区别——
    #   查不到时 .get 返回 None（不报错），msg[...] 会直接崩
    if handler is None:
        return f"错误：未知工具 {name}", True
    try:
        # **args：把参数字典拆开变成 参数=值 的形式。
        # args={"path":"docs/a.md"} -> 相当于调用 tool_read_file(path="docs/a.md")
        # 好处：不用关心每个工具要几个参数，字典里有什么就传什么
        return handler(**args), False
    except Exception as e:
        # 模型传错参数、文件权限问题等任何意外，都转成错误文本告诉模型，
        # 让它自己调整策略 —— 这是 Agent "打不死"的关键
        return f"错误：工具执行失败 - {e}", True


# ---------- Agent 循环（和第 1 课相同，只是结果里多了 is_error） ----------
TASK = (
    "看看 docs/ 目录里有哪些文件，阅读它们，然后创建 docs/summary.md："
    "每个模块一节，写清楚该模块负责什么、1~2 条关键规则。"
    "写完后再在最终回复里给我一句话概览。"
)

messages = [{"role": "user", "content": TASK}]   # 对话历史，从任务开始
response = None
turn = 0
while True:
    turn += 1
    print(f"\n===== 第 {turn} 轮 =====")
    response = client.messages.create(
        model=MODEL, max_tokens=16000, tools=TOOLS, messages=messages
    )
    print(f"stop_reason = {response.stop_reason}")
    if response.stop_reason == "end_turn":       # 模型说做完了 -> 出循环
        break

    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result, is_error = execute_tool(block.name, block.input)
            # 三元表达式：'错误' if 条件 else '成功' —— 条件成立取前值
            print(f"[工具] {block.name}({block.input}) -> {'错误' if is_error else '成功'}")
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": is_error,        # ← 新增：明确告诉模型"这是失败"
                }
            )
    messages.append({"role": "user", "content": tool_results})

print("\n===== 最终回答 =====")
for block in response.content:
    if block.type == "text":
        print(block.text)

print(f"\n共 {turn} 轮。打开 docs/summary.md 看看 Agent 写了什么。")
