"""
第 3 课的产物：agent_lib.py —— 可复用的迷你 Agent 框架（零基础注释版）
运行：python agent_lib.py（会跑一个自测）

本课新语法（详见《Python语法急救包.md》）：
- class 类与自定义异常（§9、§10）
- 类型提示、默认参数（§12）
- if __name__ == "__main__"（§13）
- 以后所有课都 from agent_lib import ... 复用本文件
"""
import anthropic
from pathlib import Path

client = anthropic.Anthropic()
MODEL = "claude-opus-4-8"
BASE_DIR = Path(__file__).resolve().parent


class ToolError(Exception):
    """自定义错误类型。
    class X(Exception) 表示：造一个新错误类型，继承 Python 自带的 Exception。
    为什么要自定义？——为了把"业务上的错误"（如文件不存在）
    和"程序 bug"区分开：前者要礼貌地告诉模型，后者才是真故障。
    """


def _resolve(path: str) -> Path:
    """把模型给的路径解析并锁定在本目录内 —— 安全防护核心！

    【为什么必须防】模型输出的内容是不可信的！
    如果它传来 "../../重要文件"，直接 open() 就会越权读写。
    攻击者也可以诱导模型传恶意路径（路径穿越攻击）。

    下面三行做的事：
    1. BASE_DIR / path        拼出完整路径
    2. .resolve()             化成最简绝对路径（../ 花招会被解开）
    3. 检查它是否还在 BASE_DIR 里，不在就主动抛错
    """
    p = (BASE_DIR / path).resolve()
    # p.parents = p 的所有上级文件夹；判断 BASE_DIR 是否在其中
    if not (p == BASE_DIR or BASE_DIR in p.parents):
        raise ToolError(f"路径越界：只允许访问 {BASE_DIR} 下的文件")
        # raise = 主动扔出一个错误，交给上层 try/except 接住
    return p


# ---------- 内置文件工具（和第 2 课相同，多了 _resolve 防护） ----------
def _list_files(folder: str) -> str:
    # 函数名前的下划线是约定：表示"内部函数，外部别直接用"
    folder_path = _resolve(folder)
    if not folder_path.is_dir():
        raise ToolError(f"目录 {folder} 不存在")   # 用"抛错"代替"返回错误文本"
    names = sorted(p.name for p in folder_path.iterdir() if p.is_file())
    return "\n".join(names) if names else "（空目录）"


def _read_file(path: str) -> str:
    p = _resolve(path)                    # 先过安检
    if not p.is_file():
        raise ToolError(f"文件 {path} 不存在")
    return p.read_text(encoding="utf-8")


def _write_file(path: str, content: str) -> str:
    p = _resolve(path)                    # 写文件同样要过安检！
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"已写入 {path}（{len(content)} 字符）"


# 工具定义列表（给模型看的"菜单"），格式同第 1、2 课
FS_TOOLS = [
    {
        "name": "list_files",
        "description": "列出某个子目录下的所有文件名。",
        "input_schema": {
            "type": "object",
            "properties": {"folder": {"type": "string", "description": "子目录名"}},
            "required": ["folder"],
        },
    },
    {
        "name": "read_file",
        "description": "读取指定路径的文本文件，返回完整内容。",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "文件路径"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "把文本内容写入指定路径（覆盖写入，目录不存在会自动创建）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "目标文件路径"},
                "content": {"type": "string", "description": "完整内容"},
            },
            "required": ["path", "content"],
        },
    },
]

_TOOL_HANDLERS = {
    "list_files": _list_files,
    "read_file": _read_file,
    "write_file": _write_file,
}


def execute_tool(name: str, args: dict):
    """默认工具执行器：查表 -> 执行 -> 出错接住。
    永远返回 (结果文本, 是否为错误) 两个值。"""
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return f"错误：未知工具 {name}", True
    try:
        return handler(**args), False          # **args：字典拆成 参数=值（见急救包 §5）
    except ToolError as e:                     # 业务错误（文件不存在等）
        return str(e), True
    except Exception as e:                     # 其他任何意外，也不崩，告诉模型
        return f"错误：工具内部异常 - {e}", True


def get_text(response) -> str:
    """从模型的回复里提取文字部分（回复里可能有文字块和工具调用块混在一起）。"""
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""                                  # 一个文字块都没有就返回空串


def run_agent(
    system_prompt: str | None,   # 身份设定；str | None = 可以是字符串，也可以不传(None)
    task: str,                   # 用户任务
    tools=None,                  # 工具列表；=None 表示"不传就用默认的文件工具"
    max_turns: int = 12,         # 循环上限，防死循环；默认 12
    verbose: bool = True,        # 要不要打印过程
    tool_executor=None,          # 自定义工具执行器；第 7 课用它挂 delegate 工具
) -> str:
    """核心 Agent 循环 —— 整个框架就这一个函数。

    和第 1 课手写的循环一模一样，只是包成了函数、加了保护。
    返回值：模型最终的文字回答。
    """
    tools = tools if tools is not None else FS_TOOLS
    # ↑ "A if 条件 else B" 三元表达式：tools 传了就用传的，没传就用默认
    executor = tool_executor or execute_tool
    # ↑ "or" 技巧：tool_executor 有值就用它，是 None 就用默认执行器

    messages = [{"role": "user", "content": task}]

    response = None
    for turn in range(1, max_turns + 1):        # 最多循环 max_turns 次（1 到 max_turns）
        # 用字典装参数，是因为 system 可有可无，这样能"按需"添加
        kwargs = dict(model=MODEL, max_tokens=16000, tools=tools, messages=messages)
        if system_prompt:                        # 有身份设定才加这个参数
            kwargs["system"] = system_prompt
        response = client.messages.create(**kwargs)   # **kwargs 同样是"拆字典传参"

        if verbose:                              # verbose=True 才打印（调试开关）
            print(f"  [第 {turn} 轮] stop_reason={response.stop_reason}")

        if response.stop_reason == "end_turn":   # 正常完成
            return get_text(response)
        if response.stop_reason == "refusal":    # 模型因安全原因拒绝
            return "(模型拒绝了该请求)"
        if response.stop_reason == "max_tokens": # 输出被长度截断
            print("  [警告] 输出被 max_tokens 截断，考虑调大它")

        # —— 模型想用工具：回填历史 + 执行 + 喂回结果（同第 1 课） ——
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if verbose:
                    print(f"  [工具] {block.name}")
                result, is_error = executor(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                        "is_error": is_error,
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    # for 循环自然跑完（没被 return 打断）= 轮数用尽，强制结束
    print(f"  [警告] 达到 max_turns={max_turns} 上限，强制结束")
    return get_text(response) if response else ""


# ---------- 自测 ----------
# 固定写法：只有直接运行本文件（python agent_lib.py）时才执行下面；
# 被其他文件 import 时不会执行（第 5、6、7 课都是 import 本文件）
if __name__ == "__main__":
    print("== agent_lib 自测：让 Agent 写一个文件再读回来 ==")
    answer = run_agent(
        system_prompt="你是一个文件管理助手，操作简洁，完成后只回复一行确认。",
        task="创建 test_hello.txt，内容为三行：hello、agent、lib。然后读回来确认，最后告诉我文件有几行。",
        verbose=True,
    )
    print("\nAgent 的回答：", answer)
