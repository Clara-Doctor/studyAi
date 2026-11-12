# AI 编程（AI Coding）学习路径 —— 从零基础到多智能体

> 面向 AI 编程新手的完整学习路线图，分为 **初阶（会用）→ 中阶（懂原理）→ 高阶（能构建）** 三个阶段。
> 建议总时长：初阶 1~2 周，中阶 3~4 周，高阶 1~2 个月（每天 1~2 小时）。

---

## 第 0 章：先看全景图（开始之前必读）

### 0.1 什么是 AI 编程？

AI 编程（也叫 AI Coding、Vibe Coding）就是**用大语言模型（LLM）辅助甚至主导写代码**。它不是"让 AI 替你打字"，而是你负责想清楚"要做什么、做到什么程度算对"，AI 负责搜索代码、写代码、跑测试、修 Bug。

### 0.2 AI 编程的三个层次

| 层次 | 形态 | 例子 | 你需要的技能 |
|---|---|---|---|
| **补全** | 你写代码，AI 顺便猜下一个词 | GitHub Copilot 补全 | 正常写代码 |
| **对话** | 你描述需求，AI 给出代码块 | ChatGPT/Claude 网页版 | 会提需求 |
| **智能体（Agent）** | 你给一个目标，AI 自己搜文件→改代码→跑测试→循环直到完成 | Claude Code、Cursor Agent | 会拆解任务、验证结果、管理上下文 |

**本教程的重心在第三层**，因为它包含了前面提到的所有概念：agent、tool use、MCP、skills、多智能体。

### 0.3 一张图看懂所有部件的关系

```
你（人类）
 ↓ 提出目标
┌─────────────────────────────────────────────┐
│  AI 编程工具（宿主 / Host，如 Claude Code）      │
│                                             │
│   Agent（智能体）= LLM + 工具 + 循环            │
│    ├── 内置工具：读文件、写文件、跑命令、搜索        │
│    ├── Skills（技能）：按需加载的"操作手册"        │
│    ├── Subagents（子智能体）：干活的"分身"         │
│    └── MCP：连接外部世界的"USB 接口"             │
│         ├── GitHub MCP server               │
│         ├── 数据库 MCP server                │
│         └── ...                             │
│                                             │
│   上下文窗口（Context Window）= AI 的"工作记忆"   │
└─────────────────────────────────────────────┘
```

---

# 🟢 初阶：会用 AI 写代码（1~2 周）

**目标**：能独立用 AI 编程工具完成一个小项目，理解 AI 的"脾气"。

## 1.1 理解大模型的四个基本概念

### Token（词元）
模型不是按"字"或"词"处理文本的，而是按 **token**。一个 token 大约是 0.75 个英文单词；对中文，大约 **1 个汉字 ≈ 1~2 个 token**。计费、限速、上下文长度全都以 token 计。

### 上下文窗口（Context Window）
模型一次能"看见"的文本总量上限，就像**工作记忆**。当前主流模型已有 100 万 token 以上的窗口，但要注意：
- 塞得太满，模型会"顾此失彼"（开头和结尾记得牢，中间容易忽略）；
- 对话越长，每一轮的成本和延迟越高（因为历史要全部重发）。

### Temperature（温度）
控制输出的"随机性"。低 → 稳定、可预测（适合写代码）；高 → 多样、有创意（适合头脑风暴）。编程场景通常用低温度。

### 幻觉（Hallucination）
模型会**一本正经地编造不存在的东西**：不存在的 API、不存在的函数名、编造的文档内容。这是初学者最容易踩的坑，**验证是 AI 编程的核心习惯**。

## 1.2 Prompt（提示词）基础四原则

| 原则 | 反例 ❌ | 正例 ✅ |
|---|---|---|
| 说清楚目标 | "帮我写个网站" | "用 HTML+CSS 写一个个人主页，包含头像、简介、3 个项目卡片，单页即可" |
| 给上下文 | "报错了怎么办" | "我运行 `python main.py` 报错如下（贴报错），用的 Python 3.11，代码在 main.py 里（贴代码）" |
| 给例子 | "起个好听的名字" | "给这个项目起名，风格参考：Redis、Kafka、Zapier——简短、易读、能猜到功能" |
| 分步走 | 一口气提 10 个需求 | 先让 AI 出方案 → 确认 → 再实现 → 再改 |

## 1.3 上手你的第一个工具：Claude Code

Claude Code 是一个跑在**终端**里的 AI 编程智能体（你现在用的就是它）。核心工作流只有一句口诀：

> **说需求 → 看 AI 做 → 跑起来验证 → 不对就再描述**

安装与开始：

```bash
# 1. 安装（需要 Node.js 18+）
npm install -g @anthropic-ai/claude-code

# 2. 进入你的项目目录，启动
cd 你的项目文件夹
claude
```

初阶必会的操作：
- **直接打字**描述需求，回车发送
- `Esc` 打断 AI（它跑偏时用）
- `/clear` 清空对话开始新任务（重要！换任务就清空）
- `/help` 查看所有命令

## 1.4 初阶练习项目（任选其一，全部用 AI 完成）

1. **个人主页**：单页 HTML/CSS，部署到 GitHub Pages
2. **记账 CLI**：Python 命令行记账本，数据存 JSON 文件
3. **Markdown 转换器**：把 Markdown 转成 HTML 的小工具

**验收标准**：程序能跑通、你自己能解释每一部分是干什么的。

### 初阶自测清单
- [ ] 能解释什么是 token 和上下文窗口
- [ ] 遇到 AI 编造不存在的 API 时，知道怎么验证和纠正
- [ ] 独立用 AI 完成过一个能跑的小项目
- [ ] 知道换任务要用 `/clear`，而不是一直在旧对话里堆需求

---

# 🟡 中阶：理解 AI 编程的每个"部件"（3~4 周）

**目标**：拆开"AI 编程工具"这台机器，理解每个零件的原理和用途。

## 2.1 Agent（智能体）到底是什么

**一句话定义：Agent = LLM + 工具 + 循环。**

普通对话是"一问一答"；Agent 会自动执行"思考 → 用工具 → 看结果 → 再思考"的循环，直到任务完成。这个循环叫 **Agent Loop（智能体循环）**，是所有 AI 编程工具的心脏：

```
        ┌──────────────────────────────────┐
        │  1. 模型思考：下一步该干什么？        │
        │  2. 决定调用某个工具（如"读文件"）     │
        │  3. 工具执行，结果返回给模型           │
        │  4. 模型根据结果继续思考……            │
        └────────── 循环，直到任务完成 ─────────┘
```

用 API 的术语说：模型每次响应会带一个 `stop_reason`（停止原因）：
- `end_turn`：任务完成，回答结束
- `tool_use`：模型想用工具 → 你的程序执行工具 → 把结果发回去 → 再调一次 API

**关键认知**：Agent 不是更聪明的模型，而是**模型 + 外挂的手脚**。Claude Code 里你看到 AI 自己 `Read` 文件、`Edit` 代码、跑 `Bash` 命令，就是这个循环在运转。

## 2.2 Tool Use（工具调用 / Function Calling）

工具是模型与外界交互的唯一方式。模型自己只会生成文字，"读文件""发邮件"都是通过调用**工具**完成的。

一个工具的定义包含三部分：

```json
{
  "name": "get_weather",
  "description": "获取指定城市的当前天气",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": { "type": "string", "description": "城市名" }
    },
    "required": ["location"]
  }
}
```

三个要点：
1. **description 极其重要**：模型靠它判断"什么时候该用这个工具"。写得越清楚，调用越准。
2. **输入是 JSON Schema**：模型按 schema 填参数，你的程序负责真正执行。
3. **工具结果回填对话**：执行结果以 `tool_result` 形式发回给模型，它继续思考。

Claude Code 内置的核心工具：`Read`（读文件）、`Write`（写文件）、`Edit`（精确改文件）、`Bash`（跑命令）、`Grep`（搜内容）、`Glob`（搜文件名）、`WebSearch`/`WebFetch`（上网）、`Agent`（派子智能体）。

## 2.3 Skills（技能）—— 给 AI 的"操作手册"

**Skill = 一个带说明书的知识包**，教 AI 在特定场景下怎么做某类事。

结构就是一个文件夹 + 一个 `SKILL.md`：

```
.claude/skills/pdf-report/
└── SKILL.md        ← 里面写：这个技能做什么、什么时候用、具体步骤
```

`SKILL.md` 开头是元数据（名称、描述——AI 靠描述决定要不要用它），正文是详细操作步骤。

**核心机制叫"渐进式披露"（Progressive Disclosure）**：
- 平时只占用极少量上下文（只有一行描述）
- 当任务匹配时，AI 才读取完整的 SKILL.md
- 技能里还可以引用更多文件，用到哪层读哪层

这解决了"把所有知识都塞进系统提示词"的矛盾——既想让 AI 懂很多，又不想撑爆上下文。

类比：**MCP 是给 AI 接手（能力），Skill 是给 AI 发操作手册（知识）**。两者经常配合使用。

## 2.4 MCP（Model Context Protocol）—— AI 的"USB 接口"

**问题**：每个工具（GitHub、Notion、数据库、Slack…）都有自己的 API。如果每个 AI 工具都要为每个服务单独写集成，就是 M×N 的组合爆炸。

**MCP 的解法**：定义一个开放协议。服务方实现一次 MCP server，所有支持 MCP 的 AI 工具（Claude Code、Cursor、Claude Desktop…）都能直接用。M×N 变成 M+N。

### MCP 三层架构

```
┌──────────────────────────┐
│  Host（宿主）              │  ← Claude Code / Claude Desktop
│  ┌──────────────┐        │
│  │ MCP Client   │◄──────►│  ← 宿主内部的连接器，1 个 client 管 1 个 server
│  └──────────────┘        │
└─────────┬────────────────┘
          │ 协议通信（stdio 本地进程 / HTTP 远程）
          ▼
┌──────────────────────────┐
│  MCP Server（服务器）      │  ← GitHub MCP / 数据库 MCP / 你自己写的
│  暴露：工具(tools)、        │
│  资源(resources)、提示(提示模板) │
└──────────────────────────┘
```

- **Host**：AI 应用本体（Claude Code）
- **MCP Client**：Host 里的连接管理器，每个 server 对应一个 client
- **MCP Server**：能力提供方，可以是官方的（GitHub、Notion、Slack），也可以是社区或你自己写的

### 在 Claude Code 里添加一个 MCP server

```bash
# 添加官方 GitHub MCP server（远程 HTTP 方式）
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# 查看已装的 server
claude mcp list
```

装好后，AI 的工具列表里就多了 GitHub 的工具，你可以直接说"帮我列出我仓库的最近 5 个 PR"。

### MCP vs Skills vs 内置工具（容易混淆，记住这个表）

| | 是什么 | 谁提供 | 类比 |
|---|---|---|---|
| **内置工具** | 读/写文件、跑命令等 | AI 工具自带 | 手和脚 |
| **MCP** | 外部服务的标准化接口 | 第三方服务方 / 社区 / 你自己 | USB 外设 |
| **Skills** | 按需加载的操作知识 | 你 / 官方 / 社区 | 操作手册 |

## 2.5 上下文管理与记忆

AI 编程质量的隐形天花板是**上下文管理**。核心工具：

| 手段 | 作用 | 什么时候用 |
|---|---|---|
| `/clear` | 完全清空对话 | 换新任务时（**最重要**） |
| `/compact` | 把历史压缩成摘要 | 对话太长但任务没完 |
| `CLAUDE.md` | 项目说明书，每次自动加载 | 让 AI 记住项目约定、命令、结构 |
| 子智能体 | 让探索性的大量搜索不污染主对话 | 大范围查资料时（高阶讲） |

`CLAUDE.md` 示例（放在项目根目录）：

```markdown
# 项目说明
- 这是用 FastAPI + PostgreSQL 写的后端
- 运行测试：pytest tests/
- 代码风格：遵循 ruff，行宽 100

# 约定
- 所有 API 路由前缀 /api/v1
- 错误响应统一用 {"code": int, "message": str}
```

## 2.6 Claude Code 的其他关键部件

| 部件 | 作用 | 位置 |
|---|---|---|
| **斜杠命令**（Slash Commands） | 把常用指令做成快捷方式，如 `/review` | `.claude/commands/*.md` |
| **Plan Mode**（计划模式） | 先让 AI 出实施方案，你批准了才动手 | 按 `Shift+Tab` 切换 |
| **权限系统** | 控制哪些操作 AI 可直接做、哪些要问你确认 | `.claude/settings.json` |
| **Hooks（钩子）** | 在特定时机自动执行脚本（如"每次改完文件自动跑格式化"） | `.claude/settings.json` |
| **Subagents（子智能体）** | 独立上下文的"分身"，干探索/并行任务 | `.claude/agents/*.md` |

**Plan Mode 值得单独强调**：新手最容易犯的错是直接让 AI 动手改代码，结果方向错了改一地。养成习惯——**复杂任务先切 Plan Mode，看 AI 的计划，批准后再执行**。

## 2.7 中阶练习项目

1. **给一个真实项目写 `CLAUDE.md`**：让 AI 读了它之后，能准确回答"怎么跑测试、目录结构是什么"
2. **装一个 MCP server**：装 GitHub MCP，让 AI 帮你查自己仓库的 issue 并总结
3. **写一个自定义斜杠命令**：`/commit`，让 AI 按你的格式规范生成 commit message
4. **体验一次 Plan Mode**：一个中等复杂度的需求，先计划再实现，对比不计划的差异

### 中阶自测清单
- [ ] 能向别人解释 Agent 循环是怎么转起来的
- [ ] 能说清 MCP 和 Skills 的区别（一个是能力接口，一个是知识手册）
- [ ] 项目里有自己维护的 `CLAUDE.md`
- [ ] 复杂任务习惯先用 Plan Mode
- [ ] 知道什么时候该 `/clear`

---

# 🔴 高阶：构建自己的 Agent 与多智能体（1~2 个月）

**目标**：从"使用工具"升级到"构建系统"——用 API 手写 Agent，理解并实现多智能体架构。

## 3.1 用 API 手写一个最小 Agent

跳出工具封装，直接调用 Anthropic API，你会真正理解 Agent 的本质。**整个 Agent 核心只有一个 while 循环**：

```python
import anthropic

client = anthropic.Anthropic()  # 需要设置 ANTHROPIC_API_KEY

# 1. 定义工具：模型只"点名"要用的工具，真正执行的是你的代码
tools = [{
    "name": "get_file",
    "description": "读取指定路径文件的内容",
    "input_schema": {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "文件路径"}},
        "required": ["path"],
    },
}]

def execute_tool(name, args):
    if name == "get_file":
        with open(args["path"], encoding="utf-8") as f:
            return f.read()

# 2. Agent 循环：这就是 Agent 的全部秘密
messages = [{"role": "user", "content": "帮我总结 README.md 的核心内容"}]

while True:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason == "end_turn":   # 模型说：做完了
        break

    messages.append({"role": "assistant", "content": response.content})

    # 执行模型点名的每个工具，把结果发回去
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,   # 必须对应上
                "content": result,
            })
    messages.append({"role": "user", "content": tool_results})

# 最终回答
print(next(b.text for b in response.content if b.type == "text"))
```

数一下：**一个 while 循环 + 一个工具执行函数**，就是一个完整的 Agent。Claude Code 不过是这个骨架 + 海量工程打磨。

配套认知（动手时你会遇到）：
- **SDK 的 Tool Runner**：官方 SDK 提供自动跑循环的辅助器，你只写工具函数
- **Streaming（流式）**：长输出必须流式接收，否则容易超时
- **Prompt Caching（提示缓存）**：系统提示和工具定义放前面不动，能省 ~90% 重复输入费用
- **Structured Outputs（结构化输出）**：约束模型按 JSON Schema 输出，方便程序解析

## 3.2 多智能体（Multi-Agent）系统

### 为什么要多个 Agent？三个理由

1. **上下文隔离**：一个 Agent 干大任务，几十万 token 的中间过程会把它自己的上下文塞满。子智能体去"脏活"（读 50 个文件），只把**结论**带回主对话。
2. **并行加速**：10 个文件要审查，1 个 Agent 串行要 10 轮；10 个子智能体并行，一轮搞定。
3. **专业分工**：一个负责写代码、一个专门做代码评审、一个跑测试——各自有独立的系统提示词和工具集，互不干扰。

### 核心模式：Orchestrator–Worker（指挥官–工人）

这是最重要、最常用的模式：

```
              ┌─────────────────┐
   用户需求 ──►│  主 Agent（指挥官）│  ← 只有它和你对话，持有全局上下文
              └───┬────┬────┬───┘
        派发任务   │    │    │   收回结论（不是过程！）
             ┌────▼┐ ┌─▼──┐ ┌▼───┐
             │子 A │ │子 B│ │子 C │   ← 各自独立的上下文窗口
             │查后端│ │查前端│ │跑测试│   ← 干完活就"销毁"，只留结论
             └─────┘ └────┘ └────┘
```

工作方式：
- 主 Agent 把任务**拆解**成独立子任务，每个子任务附带完整上下文说明（子 Agent 看不到主对话！）
- 子 Agent 在自己的上下文里完成工作
- **只把最终结论**返回给主 Agent，中间过程不回流

其他常见模式：

| 模式 | 结构 | 适用场景 |
|---|---|---|
| **Pipeline（流水线）** | A 的输出 → B 的输入 → C | 需求 → 实现 → 评审，线性依赖 |
| **Judge / Critic（评审者）** | 生成者 + 独立评审者对抗 | 提高质量，评审者用全新上下文挑毛病 |
| **并行扇出** | 1 个任务拆成 N 个并行子任务 | 大规模搜索/迁移/审查 |

### 多智能体的代价（什么时候不要用）

- **成本倍增**：每个子 Agent 都要重新建立上下文
- **协调开销**：拆分不当 → 返工、结论对不上
- **深度限制**：通常只允许一层委派（主 Agent 可以派子 Agent，子 Agent 不能再派）

经验法则：**单 Agent 能解决就不要多 Agent**。任务天然可并行、或主上下文被探索过程撑爆时，才上多智能体。

### 在 Claude Code 里体验多智能体

你不需要写代码就能体验——Claude Code 内置了子智能体机制。试试这样提问：

> "并行派几个子智能体，分别调研 docs/ 目录下每个模块的职责，汇总给我。"

观察它的 `Agent` 工具调用——你会看到多个子智能体并行运行，各自返回摘要。

进阶：自己定义专门的子智能体，放在 `.claude/agents/code-reviewer.md`：

```markdown
---
name: code-reviewer
description: 代码评审专家。写完重要功能后主动使用。
tools: Read, Grep, Glob, Bash
---
你是资深代码评审员。审查代码时重点关注：
1. 正确性 Bug  2. 安全问题  3. 与项目现有风格的不一致
只报告确定的问题，每条附文件和行号。
```

## 3.3 上下文工程（Context Engineering）

高阶的核心竞争力不是"会写 prompt"，而是**管理一个有限的工作记忆**：

| 技术 | 解决什么问题 |
|---|---|
| **Compaction（压缩）** | 对话快到上下文上限时，自动把早期历史摘要化 |
| **Context Editing（上下文编辑）** | 清掉过时的工具结果（老的大文件读取结果不再有用） |
| **Memory（记忆）** | 跨会话持久化——把学到的经验写进文件，下次会话再读 |
| **渐进式披露** | Skills 机制：只加载当前任务需要的知识 |
| **Prompt Caching** | 稳定内容放前 + 缓存，重复内容几乎不花钱 |

一个实用的设计原则：**上下文里只保留"会改变下一步决策的信息"**。读过的大文件、已经确认的方案细节，都应该及时清出去。

## 3.4 工程化：评测、成本与安全

做生产级 Agent 系统还要补三块：

1. **评测（Evals）**：怎么知道你的 Agent 改进没退化？建一组带标准答案的测试任务，每次改动跑一遍对比。没有评测的 Agent 优化全靠感觉。
2. **成本控制**：token 是钱。手段——模型分级（简单任务用便宜的模型）、prompt caching、控制循环轮数上限、任务预算（task budget）。
3. **安全与权限**：Agent 能跑命令、改文件、调 API，必须设防——破坏性操作要人工确认（human-in-the-loop）、工具白名单、沙箱执行不可信代码。

## 3.5 高阶练习项目（毕业设计）

按顺序做，每个都比上一个难：

1. **手写最小 Agent**：跟着 3.1 的代码，做出一个"读文件 + 总结"的 Agent，加第二个工具（列目录）
2. **给它加上循环上限**：最多 10 轮工具调用，防止死循环
3. **实现一个两 Agent 系统**：一个生成 Python 函数，一个（全新上下文）评审并打回重写，直到通过
4. **毕业项目（选一）**：
   - 写一个自定义 Claude Code subagent + skill，解决你工作中的重复任务
   - 写一个定时运行的自动化 Agent（如"每天早上检查 GitHub 仓库新 issue，分类总结发邮件"）

### 高阶自测清单
- [ ] 不查资料能手写 Agent 循环的伪代码
- [ ] 能解释多智能体的三大收益和一个最大代价
- [ ] 知道子 Agent 为什么必须自带完整上下文
- [ ] 做过一个两 Agent 协作的程序
- [ ] 能说出至少三种上下文管理技术

---

# 附录 A：概念速查表

| 概念 | 一句话解释 |
|---|---|
| **LLM** | 大语言模型，预测下一个 token 的神经网络 |
| **Token** | 模型处理文本的最小单位，计费和长度的单位 |
| **Context Window** | 模型一次能看的全部内容，即工作记忆 |
| **Prompt** | 你发给模型的一切输入 |
| **System Prompt** | 设定模型身份和规则的"幕后指令" |
| **Temperature** | 输出随机性旋钮，编程用低值 |
| **幻觉** | 模型编造不存在的事实，必须验证 |
| **Agent** | LLM + 工具 + 循环，能自主多步完成任务 |
| **Agent Loop** | 思考→调工具→看结果→再思考，直到完成 |
| **Tool Use** | 模型按 JSON Schema 点名工具，你的代码执行 |
| **MCP** | 连接外部服务的开放协议，AI 的 USB 接口 |
| **MCP Server** | 按 MCP 协议暴露能力的程序（GitHub、数据库…） |
| **Skill** | 按需加载的操作知识包（SKILL.md + 渐进披露） |
| **Subagent** | 独立上下文的子智能体，干完只回传结论 |
| **Multi-Agent** | 多个 Agent 分工协作的系统 |
| **Orchestrator-Worker** | 主 Agent 拆解分发任务、子 Agent 执行的模式 |
| **CLAUDE.md** | 项目说明书，每次会话自动加载 |
| **Hook** | 特定时机自动触发的脚本 |
| **Plan Mode** | 先出计划、批准后再动手的工作模式 |
| **Compaction** | 上下文快满时自动摘要压缩历史 |
| **Prompt Caching** | 缓存重复的输入前缀，省 ~90% 输入费用 |
| **Evals** | 用固定测试集衡量 Agent 质量的方法 |

# 附录 B：推荐学习资源

**官方文档（最权威，随版本更新）**
- Claude Code 文档：https://code.claude.com/docs
- Anthropic API 文档：https://docs.claude.com
- MCP 官方站：https://modelcontextprotocol.io
- MCP Server 目录：https://github.com/modelcontextprotocol/servers
- Anthropic 工程博客（讲 Agent 构建最佳实践）：https://www.anthropic.com/engineering

**实践建议**
1. 每学一个概念，立刻在你自己的项目里用一次——AI 编程是"手上功夫"
2. 遇到 AI 编造内容时，不要生气，把它当成练习"验证"的机会
3. 保持好奇心：AI 编程工具迭代极快，每月看看官方更新日志
