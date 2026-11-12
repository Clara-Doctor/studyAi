# Agent SDK：从教学版到生产版 · 实操教程

> 定位：《ClaudeCode深度用法与结对开发闯关.md》第 18 关的配套教材。
> 一句话目标：你在 `advanced-agent-lab/agent_lib.py` 里**手写**的那套 Agent 零件，
> 官方有一个**生产版**全部做好了——包名叫 `claude-agent-sdk`。本教程带你装上、跑通、玩明白。
> 环境：Windows + Git Bash + Python 3.12（你的机器全满足）。

---

## 第 0 章 · 先对号入座：你写过的每个零件，SDK 里叫什么

你在课程里手写的（教学版） → SDK 里的（生产版）：

| 你手写的（agent_lib.py） | 它干的事 | Agent SDK 里的对应物 |
|---|---|---|
| `run_agent()` 的 while 循环 | 反复调模型直到不再用工具 | **SDK 内置**——你调一次 `query()`，循环它自己跑 |
| `SYSTEM_PROMPT` 参数 | 告诉模型它是谁 | `system_prompt` 选项 |
| `tools` 字典 + `TOOL_HANDLERS` | 定义工具并执行 | **内置工具**（读/写/改文件、Bash、搜索…开箱即用）+ `@tool` 自定义 |
| `max_turns=12` | 防止无限循环 | `max_turns` 选项（一模一样的名字） |
| （教学版没有的） | 权限控制 | `permission_mode`——哪些操作要你批准 |
| （教学版没有的） | 多轮会话/记忆 | `ClaudeSDKClient`——自动记住上文 |
| （教学版没有的） | 成本上限 | `max_budget_usd`——烧钱超限自动停 |

> 💡 教学版的价值 = **你亲眼看见循环怎么转**（第 3 课 §3.1）。
> 生产版的价值 = **同样的循环 + 权限 + 会话 + 内置工具，你 10 行代码就能驱动**。
> 两者都懂，面试讲"你了解 Agent 原理吗"和"你怎么工程化落地"就都有了。

---

## 第 1 章 · 安装（一次性，5 分钟）

```bash
pip install claude-agent-sdk
```

就这一条。事实核对（2026-10 实查）：

- ✅ 需要 Python 3.10+（你是 3.12）
- ✅ **不需要** Node.js，也**不需要**另装 Claude Code CLI——包自带
- ✅ **你的中转站鉴权直接生效**：你环境里的 `ANTHROPIC_BASE_URL` +
  `ANTHROPIC_AUTH_TOKEN` 会被 SDK 原样传给它内部启动的进程，不用改任何代码
- ⚠️ 中转站如果报 `400 Extra inputs are not permitted`，先设
  `export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` 再跑（关掉实验性字段）
- 建议顺手设 `export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`（少些不必要联网）

---

## 第 2 章 · Hello World（第一个文件）

建 `D:\studyAi\my-sdk-lab\hello.py`：

```python
# hello.py —— Agent SDK 第一步：让一个生产版 Agent 跟你说话
import asyncio                                  # SDK 是异步的，asyncio 用来跑异步代码
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    # query() = 喊一个 Agent 干活，返回的是一串"消息流"
    async for message in query(
        prompt="你好，你是谁？用一句话回答。",
        options=ClaudeAgentOptions(permission_mode="default"),
    ):
        # 消息分两种：模型的回答（AssistantMessage）和收尾报告（ResultMessage）
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):      # 只打印文字部分
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"—— 本轮结束：{message.subtype}")

asyncio.run(main())
```

运行（记得 `-X utf8` 防 GBK 乱码）：

```bash
cd /d/studyAi/my-sdk-lab && python -X utf8 hello.py
```

> 🔍 对照教学版：在 agent_lib.py 里，"发请求 → 看要不要用工具 → 执行工具 →
> 把结果塞回去 → 再发请求"这一整段 while 循环，在 SDK 里被压成了**一次 `query()`**。
> 跑通后把 hello.py 和 agent_lib.py 摆在一起看，你会对"循环去哪了"有体感。

---

## 第 3 章 · 多轮对话：ClaudeSDKClient（会记忆的 Agent）

`query()` 每次都是**新会话**——问完就忘。要"记得上文"，用 `ClaudeSDKClient`：

```python
# chat.py —— 多轮对话：第二次提问能接住第一次的上下文
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def 打印回复(client):
    async for msg in client.receive_response():          # 收这轮的回复流
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    print(b.text)

async def main():
    async with ClaudeSDKClient() as client:              # with 块内 = 同一个会话
        await client.query("法国的首都是哪？")
        await 打印回复(client)

        await client.query("那个城市有多少人口？")        # ← 它记得"那个城市"是巴黎
        await 打印回复(client)

asyncio.run(main())
```

对照教学版：你在第 7 课见过"Agent 无状态、历史要自己存 messages 列表"——
SDK 用 Client 把这件事也替你做了。

---

## 第 4 章 · 常用选项速查（ClaudeAgentOptions）

| 选项 | 干什么 | 教学版对照 |
|---|---|---|
| `system_prompt="..."` | 设定 Agent 人设/规则 | SYSTEM_PROMPT |
| `allowed_tools=["Read","Edit","Bash"]` | **放行**哪些工具（不设=默认全放开） | tools 字典 |
| `disallowed_tools=["Bash"]` | 反向拉黑：禁止用什么 | —— |
| `permission_mode="..."` | 权限模式：`default`（危险操作要你批）/ `acceptEdits`（改文件不用批）/ `plan`（只规划不动手）/ `bypassPermissions`（全放开，⚠️危险） | —— |
| `max_turns=10` | 最多循环几轮 | max_turns |
| `max_budget_usd=1.0` | 花费超 1 美元自动停 | —— |
| `cwd="D:/studyAi"` | Agent 的活动目录（它的"书桌"） | —— |
| `model="claude-opus-4-8"` | 指定模型（与 agent_lib.py 同款） | MODEL |

一个"上锁"的例子——只准读代码、不准改：

```python
options = ClaudeAgentOptions(
    system_prompt="你是代码审查员。只读代码，任何文件都不许改。",
    allowed_tools=["Read", "Glob", "Grep"],   # 只放行读取类工具——想写也没有工具可用
    permission_mode="default",
    max_turns=8,
    cwd=r"D:\studyAi\eval-practice-house",
)
```

> 🔑 这就是教学版完全没有的第三层防线：**工具层面**的权限
> （第 1 层提示词约束、第 2 层 permission_mode 批准弹窗、第 3 层 allowed_tools 白名单）。

---

## 第 5 章 · 自定义工具：@tool 装饰器（你的 TOOL_HANDLERS 的生产版）

把你自己写的 Python 函数变成 Agent 能调的工具：

```python
# my_tools.py —— 自定义工具：算数器
import asyncio
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, query

# @tool(名字, 描述, 参数schema) —— 描述写给模型看，它靠这个判断"什么时候该用这工具"
@tool("add", "两数相加", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    # ⚠️ 必须是 async 函数，参数固定收一个 dict，返回也是固定格式
    return {"content": [{"type": "text", "text": str(args["a"] + args["b"])}]}

# 把工具打包成一个"工具箱"（内部跑一个迷你 MCP server——第 11 关你装过的东西！）
calc = create_sdk_mcp_server(name="calculator", tools=[add])

async def main():
    async for msg in query(
        prompt="用工具计算 3.5 + 4.2",
        options=ClaudeAgentOptions(
            mcp_servers={"calc": calc},                 # 挂载工具箱
            allowed_tools=["mcp__calc__add"],           # 放行，命名规则：mcp__服务器名__工具名
        ),
    ):
        print(msg)

asyncio.run(main())
```

对照教学版：你在课程里写的 `TOOL_HANDLERS = {"工具名": 函数}` 干的就是这件事，
只是 SDK 用装饰器把"函数 → 工具定义（schema）"的转换也自动化了。

---

## 第 6 章 · Windows 上的坑（实查过的）

| 坑 | 症状 | 解法 |
|---|---|---|
| 中文乱码 | 控制台输出乱码 | 照旧 `python -X utf8 文件.py` |
| 不要手动设 `cli_path` 指向 `claude.cmd` | `CLIConnectionError: Refusing to execute batch script` | 什么都不设——SDK 用包内置的执行文件，绕开这个坑 |
| 超长 system_prompt | Windows 命令行长度上限报错 | 改用文件：`system_prompt={"type": "file", "path": "prompt.txt"}` |
| .env 文件 | SDK **不会**自动读 .env | 要么系统环境变量，要么自己用 dotenv 先加载 |

---

## 🎮 闯关任务（3 关）

### 第 1 关 · 跑通 Hello World
按第 1、2 章装好、跑通 `hello.py`。
**验收**：屏幕上出现模型的回答和"本轮结束"字样；能说出 `query()` 里藏着
agent_lib.py 的哪段代码（while 循环）。

### 第 2 关 · 记忆体 + 工具
改 `chat.py` 连问三轮互相有关系的问题；再给 `my_tools.py` 加一个自定义工具
（比如 `read_listing`：读一个 txt 文件返回内容——就是房源描述），让 Agent
"用工具读 D:\studyAi\eval-practice-house\cases.json 并总结前 3 条"。
**验收**：多轮对话接得上文；Agent 真的调了你的工具（返回里能看到调用痕迹）。

### 第 3 关 · 对比实验：教学版 vs 生产版 ⭐
同一个任务——"读 advanced-agent-lab 文件夹并总结每个文件讲什么"——分别用
`agent_lib.py`（教学版）和 SDK（生产版，`allowed_tools=["Read","Glob","Grep"]`）跑一遍。
**验收**：写 3 句对比——哪个更省代码？哪个更能看清原理？各自适合什么场景？

---

## 通关之后

你就打通了整个知识闭环：**API 调用（第 1 课）→ 工具循环（第 3 课）→ 多智能体
（第 6 课）→ 评测（第 7 课）→ Claude Code（工作流）→ Agent SDK（把 Claude Code
变成你项目里的库）**。从"会调用模型"到"能在业务层落地一个生产级 Agent"，
这条路你已经走完了。剩下的深度（hooks、子代理配置、会话持久化）等真实需求来了再查
官方文档：`code.claude.com/docs/en/agent-sdk`。
