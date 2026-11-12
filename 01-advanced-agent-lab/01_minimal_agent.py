"""
第 1 课：最小可运行的 Agent —— 零基础逐行注释版
运行命令：python 01_minimal_agent.py

怎么读这个文件：
1. 每行代码上方/右侧都有中文注释，先读注释再读代码
2. 看不懂 Python 语法本身（字典、函数、f-string……），
   去查《D:\\studyAi\\Python语法急救包.md》
3. 本文件的核心思想只有一句话：Agent = 大模型 + 工具 + while 循环
"""

# ═════════ 第 0 部分：导入"工具箱" ═════════

# import 的意思：把别人写好的代码库引进来用。
# anthropic 这个库封装了"和 AI 模型对话"的全部网络通信细节，
# 我们只管调用它，不用自己写 HTTP 请求。
import anthropic

# 创建"客户端"对象——它就是你与 AI 模型之间的电话线。
# 括号里什么都不写 = 自动读取两个环境变量：
#   ANTHROPIC_BASE_URL   -> 请求发到哪个服务器（你的网关地址）
#   ANTHROPIC_AUTH_TOKEN -> 用哪个密钥证明"你是你"
client = anthropic.Anthropic()

# 用哪个模型。你的网关会自动把它映射到实际服务的模型。
MODEL = "claude-opus-4-8"

# ═════════ 第 1 部分：定义工具 ═════════
# 【最重要的认知】模型自己只会"打字"，它没有手。
# 它想读文件时，只能"点名"说：我要用 read_file，参数是 xxx。
# 真正打开文件的，是下面你自己写的 Python 函数。

# TOOLS 是一个列表（方括号），里面每个元素是一个字典（花括号）。
# 这个字典告诉模型：有这么一个工具叫 xxx、干什么用、要填什么参数。
TOOLS = [
    {
        "name": "read_file",                    # 工具的名字（模型点名时用的）
        "description": "读取指定路径的文本文件，返回完整内容。",
        # ↑ description 非常重要：模型靠这段话判断"什么时候该用这个工具"
        "input_schema": {                       # 参数的格式说明书（JSON Schema）
            "type": "object",
            "properties": {                     # 有哪些参数
                "path": {
                    "type": "string",           # 参数类型：字符串
                    "description": "文件路径，如 README.md"  # 告诉模型这个参数填什么
                }
            },
            "required": ["path"],               # 哪些参数必须填
        },
    }
]


def execute_tool(name: str, args: dict) -> str:
    """工具的真正实现（执行者）。

    语法说明：
      def xxx(参数):   -> 定义一个函数，之后可以用 xxx() 调用它
      name: str        -> 类型提示，纯粹给人看的说明书，表示 name 应该是字符串
      args: dict       -> args 是一个字典，比如 {"path": "README.md"}
      -> str           -> 表示这个函数返回一个字符串
    """
    # args["path"] 表示：从字典里取出 "path" 这个键对应的值
    # open(...) 打开文件，encoding="utf-8" 指定中文编码（不写会乱码）
    # with ... as f:  的意思是"用完自动关闭文件"，固定搭配
    if name == "read_file":
        # ★ 练习 1.2：把这行 return 换成 "错误：文件不存在"，重跑看模型反应
        # ★ 练习 1.3：换成 "文件内容是：今天天气晴朗"（谎言），看模型被骗
        with open(args["path"], encoding="utf-8") as f:
            return f.read()                     # read() = 读出全部内容并返回
    return f"错误：未知工具 {name}"              # f"..." 是 f-string：把变量填进字符串


# ═════════ 第 2 部分：Agent 循环 ═════════

# messages 是一个列表，存放整个对话历史。
# 每条消息是一个字典：{"role": 谁说的, "content": 说了什么}
# 对话之所以"连贯"，就是因为每轮都把历史完整发给模型。
messages = [
    {"role": "user", "content": "请阅读本目录下的 README.md，用 3 句话总结它的内容。"}
]

response = None    # 先占个位（否则循环里创建的变量，循环外用不了）
turn = 0           # 计数器：数循环跑了几轮

# while True = 无限循环，直到碰到 break 才出去。
# 整个 Agent 的"发动机"就是下面这个循环。
while True:
    turn += 1                                       # turn = turn + 1 的简写
    print(f"\n========== 第 {turn} 轮 ==========")  # f-string：把 turn 的值填进字符串

    # —— 核心调用：把【完整对话历史】发给模型，要它决定下一步 ——
    response = client.messages.create(
        model=MODEL,          # 用哪个模型
        max_tokens=16000,     # 单次回答最多生成多少 token（防止无限输出）
        tools=TOOLS,          # 告诉模型"你有哪些工具可以点名"
        messages=messages,    # 完整对话历史
    )
    # 返回的 response 里最关键的两个字段：
    #   response.stop_reason : 模型为什么停下来
    #                          "tool_use" = 我想用工具（继续循环）
    #                          "end_turn" = 任务完成（退出循环）
    #   response.content     : 模型这轮"说的话"，是一个列表（可能包含文字块和工具调用块）
    print(f"stop_reason = {response.stop_reason}")

    if response.stop_reason == "end_turn":
        break  # 模型说"我做完了" -> 跳出 while 循环

    # —— 走到这里说明模型想用工具 ——

    # 关键步骤 1：把模型这轮的回复（含它的工具调用请求）记回对话历史。
    # 【不记会怎样】下一轮模型就"失忆"，不知道自己刚点过菜，API 直接报错。
    messages.append({"role": "assistant", "content": response.content})

    # 关键步骤 2：真正去执行模型点名的每个工具，把结果打包
    tool_results = []                               # 建一个空列表，准备装结果
    for block in response.content:                  # 逐个检查模型这轮输出的"块"
        if block.type == "tool_use":                # 这个块是"工具调用请求"吗？
            print(f"AI 想用工具 -> {block.name}，参数 = {block.input}")
            # block.name  = 工具名（如 "read_file"）
            # block.input = 参数字典（如 {"path": "README.md"}）
            # block.id    = 这次调用的"取餐号"，回传结果时必须带上
            result = execute_tool(block.name, block.input)   # ★ 真正干活的地方
            print(f"工具返回 -> {result[:80]}...")           # [:80] 只打印前 80 个字符
            tool_results.append(
                {
                    "type": "tool_result",       # 固定写法：声明这是工具结果
                    "tool_use_id": block.id,     # 取餐号，和上面的调用一一对应
                    "content": result,           # 工具执行的结果（喂给模型当"现实"）
                }
            )
    # 把工具结果作为一条 user 消息追加进历史（协议规定结果放在 user 角色）
    messages.append({"role": "user", "content": tool_results})
    # 然后回到 while 顶上，带着结果再问一次模型："下一步？"

# ═════════ 第 3 部分：提取最终回答 ═════════
print("\n========== 最终回答 ==========")
# 遍历最终回复的每个块，把"文字块"打印出来
for block in response.content:
    if block.type == "text":
        print(block.text)

print(f"\n共循环了 {turn} 轮。回去看看每轮的 stop_reason 变化——这就是 Agent 的一生。")

# ─────────────────────────────────────────────────────────
# 本课小结（对应教程第 1 课）：
#   模型从不动手，它只点名 -> execute_tool 是你的代码
#   对话历史必须完整回填    -> append 一行都不能少
#   tool_use_id 必须对应    -> 模型靠它把"点的菜"和"上的菜"配对
# ─────────────────────────────────────────────────────────
