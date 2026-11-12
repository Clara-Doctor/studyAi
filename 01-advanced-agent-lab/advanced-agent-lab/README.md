# 高阶实战实验室（Advanced Agent Lab）

配套教程见：`D:\studyAi\高阶实战教程.md`（先读它！）

**零 Python 基础？** 所有课件都已是零基础逐行中文注释版；看不懂的语法去查
`D:\studyAi\Python语法急救包.md`（变量/字典/函数/循环/报错速查，10 分钟读完）。

## 一次性环境准备

```bash
# 1. 确认 Python 版本 >= 3.10
python --version

# 2. 安装依赖（在本目录执行）
pip install -r requirements.txt

# 3. 设置 API key（在 console.anthropic.com 创建，注意 API 与 Claude Code 订阅是分开计费的）
#    PowerShell（永久生效，之后重开终端）：
#    setx ANTHROPIC_API_KEY "sk-ant-你的key"
#    或 Git Bash（仅当前窗口有效）：
#    export ANTHROPIC_API_KEY "sk-ant-你的key"
```

## 课程文件（按顺序跑）

| 文件 | 对应教程 | 内容 |
|---|---|---|
| `01_minimal_agent.py` | 第 1 课 | 最小可运行 Agent，亲眼看循环 |
| `02_toolbox.py` | 第 2 课 | 多工具 + 工具分发表 |
| `agent_lib.py` | 第 3 课 | 把 Agent 封装成可复用小框架（后续课的依赖） |
| `04_streaming_structured.py` | 第 4 课 | 流式输出 + 结构化输出 |
| `05_generator_critic.py` | 第 6 课 | 双 Agent 对抗：生成者 vs 评审者 |
| `06_orchestrator_worker.py` | 第 7 课 | 指挥官-工人多智能体（delegate 工具模式） |
| `07_eval.py` | 第 8 课 | 迷你评测集 |

```bash
python 01_minimal_agent.py
```

## 费用说明

每课运行一次约消耗 1~10 万 token。用默认模型 `claude-opus-4-8`
（$5 / $25 每百万 token）大约每课 $0.1~$1。想做对照实验可以改代码里的
`MODEL` 常量换模型——对比不同模型的表现本身就是很好的练习。

## 安全提示

`agent_lib.py` 中的文件工具被限制在本目录内（防路径穿越），这是生产级
Agent 的基本安全实践，教程第 3 课会讲为什么。
