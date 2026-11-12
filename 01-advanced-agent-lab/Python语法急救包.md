# Python 语法急救包（专为看懂本课程代码）

> 用法：看代码时遇到看不懂的写法，按"关键字"来这里查。
> 只讲课程里真正用到的，10 分钟能读完。

---

## 1. 变量：给值起个名字

```python
MODEL = "claude-opus-4-8"   # 把右边的值存进左边的名字里
turn = 0                    # 数字不用引号；文字（字符串）要引号
```

## 2. f-string：把变量塞进字符串

字符串前面加 `f`，里面用 `{}` 挖坑，运行时把变量的值填进去：

```python
turn = 3
print(f"第 {turn} 轮")        # 输出：第 3 轮
print(f"共 {turn*2} 次")      # {} 里可以放算式
print(f"名字是 {MODEL}")
print(f"{acc:.0%}")           # :.0% = 显示成百分比且不带小数，如 83%
result[:80]                   # 只取字符串前 80 个字符（切片）
```

## 3. 列表 list（方括号）—— 有序的装箱子

```python
tools = ["read", "write"]     # 用方括号装一串东西
tools.append("delete")        # 往末尾追加一个（课程里不断往 messages 追加历史）
tools[0]                      # 取第 1 个（计数从 0 开始！）
len(tools)                    # 数有几个
a + b                         # 两个列表可以相加（拼接）
for x in tools: print(x)      # 逐个取出处理
```

## 4. 字典 dict（花括号）—— 带"标签"的储物柜

课程里**到处都是**字典：每条消息、每个工具定义、每个工具结果。

```python
msg = {"role": "user", "content": "你好"}
#       ↑键      ↑值        ↑键        ↑值

msg["role"]                   # 取出 "role" 标签里的值 -> "user"
msg["content"] = "新内容"      # 修改
```

## 5. 函数 def：把一段代码打包起名字

```python
def execute_tool(name: str, args: dict) -> str:
    #  ↑函数名   ↑参数1  ↑参数2        ↑"-> str"表示返回字符串（只是说明书）
    if name == "read_file":
        return "读了文件"        # return = 交回结果，函数到此结束
    return "未知工具"            # 没进 if 就走这里

result = execute_tool("read_file", {"path": "a.md"})
# 调用：把值按顺序传进去，返回值存进 result
```

- `**args`（两个星号）：把字典拆开变成"参数=值"的形式传给函数。
  `handler(**{"path": "a.md"})` 等价于 `handler(path="a.md")`

## 6. if / elif / else 和判断

```python
if stop_reason == "end_turn":   # == 是"相等吗"（一个 = 是赋值，别搞混）
    break                        # break = 立刻跳出循环
elif x > 10:
    ...
else:
    ...
```

真值判断：`if system_prompt:` 表示"system_prompt 非空/非 None 就成立"。

## 7. while / for 循环

```python
while True:          # 无限循环，必须靠 break 出去（Agent 的发动机）
    ...

for block in response.content:   # 逐个遍历列表里的元素
    ...

for turn in range(1, 4):         # turn 依次是 1, 2, 3（注意：不含 4）
    ...
```

## 8. import 与第三方库

```python
import anthropic                 # 引入库（库 = 别人写好的工具箱）
client = anthropic.Anthropic()   # 用"库.名字"访问里面的东西
```

装第三方库的命令：`pip install 库名`（课程已装好 anthropic）。

## 9. 类与对象：只需要看懂两种用法

**用法一：调用方法**。`变量.动作()` —— 点号表示"这个东西自带的动作"：

```python
messages.append(x)        # 列表自带的"追加"动作
text.strip()              # 去掉首尾空白
text.lower()              # 转小写
path.exists()             # 路径存在吗
```

**用法二：定义模板**（课程 4、6、8 课出现，照抄即可，不用深究）：

```python
class Verdict(BaseModel):       # 定义一个"数据模板"，继承自 BaseModel（pydantic 库）
    verdict: str                # 这个模板的数据里有个 verdict 字段，是字符串
    issues: list[str]           # 还有个 issues 字段，是字符串列表
# 之后模型返回的内容会自动变成这个模板的实例，可以直接 v.verdict 取值
```

## 10. 异常处理 try / except / raise

```python
try:
    危险操作()                    # 尝试执行，如果报错……
except ToolError as e:            # ……就到这里接住，程序不会崩
    return str(e)                 # e 是错误对象，str(e) 是错误信息
```

```python
raise ToolError("文件不存在")     # 主动"扔出一个错误"，给上层接住
```

## 11. 文件与路径 pathlib

```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
#   __file__      = 当前 py 文件自己的路径
#   .resolve()    = 转成绝对路径（去掉 ../ 之类的花招）
#   .parent       = 它所在的文件夹

p = BASE_DIR / "docs" / "auth.md"  # 用 / 拼接路径（跨 Windows/Mac 通用）
p.is_file()                        # 是文件吗
p.read_text(encoding="utf-8")      # 读整个文件（utf-8 保证中文不乱码）
p.write_text("内容", encoding="utf-8")  # 写文件
p.parent.mkdir(parents=True, exist_ok=True)  # 创建文件夹（已存在也不报错）
p.unlink()                         # 删除文件
```

## 12. 类型提示：纯说明书，不影响运行

```python
def run_agent(system_prompt: str | None, max_turns: int = 12) -> str:
#                        ↑可以是字符串或None    ↑默认值12，调用时不传就用12
```

## 13. 两个固定套路（看懂即可）

**套路一：`if __name__ == "__main__":`**
意思是"只有直接运行本文件时才执行下面的代码；被别人 import 时不执行"。固定写法，背下来。

**套路二：`with open(...) as f:` / `with client.messages.stream(...) as f:`**
`with` = "这个资源用完帮我自动收拾干净"（自动关文件/断开连接）。固定搭配。

## 14. 常见报错速查

| 报错 | 人话 | 怎么办 |
|---|---|---|
| `NameError: name 'x' is not defined` | 用了没定义的变量 | 检查拼写、是否漏了赋值 |
| `KeyError: 'path'` | 字典里没这个键 | 检查 `args["path"]` 的键名 |
| `TypeError: ... argument` | 参数类型/数量不对 | 对照函数定义检查 |
| `FileNotFoundError` | 文件路径不对 | 打印 `args["path"]` 看看到底传了啥 |
| `IndentationError` | 缩进不对（Python 靠缩进分层） | 同一层代码对齐，用 4 个空格 |
| API 401 | 密钥不对/没设 | 检查 `ANTHROPIC_AUTH_TOKEN` |
| API 429 | 请求太快 | 等几秒重试 |
| API 400 | 请求格式错 | 常见：messages 没回填 assistant 回复 |

## 15. 课程核心数据结构（背下这三张图）

**一条消息**（对话历史里的每个元素）：
```python
{"role": "user" 或 "assistant", "content": "文字" 或 [一堆块]}
```

**一个工具定义**：
```python
{"name": 名字, "description": 说明, "input_schema": {参数说明书}}
```

**一个工具结果**：
```python
{"type": "tool_result", "tool_use_id": 取餐号, "content": 结果文本, "is_error": 是否出错}
```
