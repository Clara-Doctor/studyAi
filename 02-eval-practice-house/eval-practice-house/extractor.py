"""
评测闯关项目：房源信息提取器（被评测的"产品"）
本文件不直接运行，由 eval.py 导入使用。

【重要】v1 的提示词是【故意写得模糊】的，所以它只有 60 分左右。
第 2 关你的任务：只改下面 SYSTEM_PROMPT 这一个字符串，把分数提到 95% 以上。
埋了哪些坑、每关怎么玩，见 MISSIONS.md 和 SPEC.md 的埋坑清单。

【实现说明】为什么用"工具调用"而不是第 7 课的 output_format？
output_format 是较新的 API，部分模型中转站不支持（会返回普通文字导致解析失败）；
而工具调用是第 1-3 课的核心 API，到处都支持。效果一样：都是逼模型按固定结构作答。
"""
import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()     # 自动读取环境变量（ANTHROPIC_API_KEY 或 AUTH_TOKEN/BASE_URL）
MODEL = "claude-opus-4-8"          # 与课程用同一个模型，分数才有可比性

# ★★★ 第 2 关你唯一允许修改的地方 ★★★
# 故意只写一句模糊的话：没说格式约定、没说单位、没说缩写换算、
# 没说朝向只能取哪些值、也没说"没提到就返回 null"——五个坑全埋在这一句话里。
SYSTEM_PROMPT = "你是房源信息提取助手。从房源描述中提取户型、面积、租金、朝向、车位情况。"

# 给模型看的"答题卡"（工具定义，格式同第 2 课）。
# 注意：description 刻意写得和 SYSTEM_PROMPT 一样模糊——不能在这里偷偷把坑填了！
LISTING_TOOL = {
    "name": "extract_listing",
    "description": "从房源描述中提取户型、面积、租金、朝向、车位情况。",
    "input_schema": {
        "type": "object",
        "properties": {
            "layout": {"type": "string", "description": "户型"},
            "area": {"type": "number", "description": "面积"},
            "price": {"type": "number", "description": "月租"},
            "orientation": {"type": "string", "description": "朝向"},
            "parking": {"type": "boolean", "description": "车位"},
        },
    },
}


class Listing(BaseModel):
    """提取结果的"答题卡"（pydantic 模型，第 7 课 Part A 同款思路）。
    模型交回的字典会在这里做类型校验；缺了的字段自动补 None。
    注意一个隐藏知识点：schema 里 area/price 声明为 number，
    模型就算想返回"89平米"也做不到，只能返回 89——
    【结构（schema）也是一种提示词工程】，MISSIONS.md 第 2 关思考题会问你这点。"""

    layout: str | None = None        # 户型，约定格式 "N室N厅"（阿拉伯数字）
    area: float | None = None        # 面积（平方米），纯数字
    price: float | None = None       # 月租（元），纯数字
    orientation: str | None = None   # 朝向，只允许：东/南/西/北/南北
    parking: bool | None = None      # 车位：true 有 / false 没有 / null 没提到


def _create(messages):
    """发一次"强制用工具作答"的请求。tool_choice 声明模型必须调 extract_listing。"""
    return client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=[LISTING_TOOL],
        tool_choice={"type": "tool", "name": "extract_listing"},
    )


def extract_listing(text: str) -> Listing:
    """把一段房源描述变成 Listing 对象。eval.py 每条用例调它一次。"""
    messages = [{"role": "user", "content": f"房源描述：{text}"}]
    response = _create(messages)

    # 兜底：个别情况（比如描述里啥都没提）模型会直接用文字回答、不调工具
    # （部分中转站也不严格执行 tool_choice）。追问一次，要求它用工具提交。
    if not any(b.type == "tool_use" for b in response.content):
        # 只回放 text/tool_use 块，thinking 块不能原样发回（接口会拒绝）
        messages.append({"role": "assistant",
                         "content": [b for b in response.content if b.type in ("text", "tool_use")]})
        messages.append({"role": "user",
                         "content": "请必须调用 extract_listing 工具提交你的提取结果。"})
        response = _create(messages)

    for block in response.content:
        if block.type == "tool_use":
            return Listing(**block.input)   # pydantic 在这里当"答题卡"校验
    raise RuntimeError("模型没有返回工具调用")   # 追问过仍不调才到这里（评测会记 API 错误）
