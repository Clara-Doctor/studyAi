# 房源信息提取器 · 评测闯关项目 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `d:\studyAi\eval-practice-house\` 建一个闯关式评测练习项目：故意 60 分的房源提取器 + 自动判分器 + 三关任务书，让学习者亲历"评测驱动开发"循环。

**Architecture:** 三个可运行文件各管一摊：`extractor.py`（被评测的产品：pydantic 模型 + 单次结构化输出调用）、`cases.json`（18 条固定用例=标尺）、`eval.py`（归一化 + 字段级判分 + 三种报告）。两个纯文档：`README.md`、`MISSIONS.md`。`eval.py` 导入 `extractor.py`，避免两处定义模型。

**Tech Stack:** Python 3.12、anthropic SDK 1.4.0（`client.messages.parse` 结构化输出，与课程 07_eval.py 同款）、pydantic 2.13.5。

**Spec:** `d:\studyAi\eval-practice-house\SPEC.md`（本计划逐条实现它，字段规则、埋坑清单、关卡验收都以 SPEC 为准）

## Global Constraints

- 项目目录：`d:\studyAi\eval-practice-house\`，所有命令在此目录下执行
- **不是 git 仓库（SPEC §6 决定不建）→ 每个任务以"运行验证"收尾，没有 commit 步骤**
- 所有代码/文档为**零基础中文注释**风格（与 advanced-agent-lab 课程一致）
- `MODEL = "claude-opus-4-8"`、`max_tokens=1000`、`client.messages.parse(..., output_format=Listing)` —— 与课程 07_eval.py 同款写法
- 依赖 `ANTHROPIC_API_KEY` 环境变量；Task 1、3 的验证不需要它（离线），Task 2、5 需要
- `cases.json` 一经 Task 1 写定即为标尺；**只有 Task 5 基线严重越界时允许微调**（见 Task 5 调整规则），其余任务一律不动
- 价格不收中文数字（"三千二"），只收 "3.2k" 型缩写（SPEC §2）
- 判分器不替模型圆错：如 "3.2k" 归一化出 3.2 ≠ 3200，就让它挂、进错题清单（修坑是第 2 关的事）

---

### Task 1: cases.json —— 18 条固定用例

**Files:**
- Create: `d:\studyAi\eval-practice-house\cases.json`

**Interfaces:**
- Consumes: 无（纯数据）
- Produces: 18 个 `{"text": str, "answer": {layout, area, price, orientation, parking}}` 用例。answer 全部按 SPEC §1 归一化约定标注（layout="N室N厅" 阿拉伯数字；area/price 纯数字；orientation ∈ 东/南/西/北/南北/null；parking ∈ true/false/null）。Task 3 的判分器和 Task 5 的基线验证都依赖这些**确切的键名与格式**。

- [ ] **Step 1: 写入 cases.json（完整内容如下）**

覆盖矩阵：干净写法 4 条（1-4）、中文数字户型 4 条（5-8）、面积单位变体 3 条（9-11）、价格缩写 2 条（12-13）、朝向变体 2 条（14-15）、字段缺失 3 条（16-18，含 1 条全缺失极端用例）。

```json
[
  {"text": "阳光花园小区，2室1厅，面积95平米，月租4500元，朝南，带地下车位",
   "answer": {"layout": "2室1厅", "area": 95, "price": 4500, "orientation": "南", "parking": true}},
  {"text": "翡翠湾 3室2厅，120平米，租金6800元每月，朝南北，无车位",
   "answer": {"layout": "3室2厅", "area": 120, "price": 6800, "orientation": "南北", "parking": false}},
  {"text": "学府雅苑 1室1厅 45平 朝西 月租2300元",
   "answer": {"layout": "1室1厅", "area": 45, "price": 2300, "orientation": "西", "parking": null}},
  {"text": "江景房 2室2厅 面积110平米 朝东 租金5200元/月 地面停车场可用",
   "answer": {"layout": "2室2厅", "area": 110, "price": 5200, "orientation": "东", "parking": true}},
  {"text": "老小区两室一厅，78平米，出租3200元一个月，朝南",
   "answer": {"layout": "2室1厅", "area": 78, "price": 3200, "orientation": "南", "parking": null}},
  {"text": "梧桐苑三室两厅，精装修，145平，租金9000元/月，南北通透，楼下有停车位",
   "answer": {"layout": "3室2厅", "area": 145, "price": 9000, "orientation": "南北", "parking": true}},
  {"text": "小两房一厅出租，面积58平米，月租2600，房子朝北",
   "answer": {"layout": "2室1厅", "area": 58, "price": 2600, "orientation": "北", "parking": null}},
  {"text": "四室二厅大平层，210平，租金12800元/月，朝南带车位",
   "answer": {"layout": "4室2厅", "area": 210, "price": 12800, "orientation": "南", "parking": true}},
  {"text": "云顶公寓 88㎡ 一室一厅 月租2900元 朝东",
   "answer": {"layout": "1室1厅", "area": 88, "price": 2900, "orientation": "东", "parking": null}},
  {"text": "金桂华庭2室1厅，65㎡，2200元/月，朝西，可以停车",
   "answer": {"layout": "2室1厅", "area": 65, "price": 2200, "orientation": "西", "parking": true}},
  {"text": "顶楼复式视野好，5室3厅，面积200平，租金15000元每月，朝南",
   "answer": {"layout": "5室3厅", "area": 200, "price": 15000, "orientation": "南", "parking": null}},
  {"text": "地铁口两室一厅，75平，租金3.2k，朝南",
   "answer": {"layout": "2室1厅", "area": 75, "price": 3200, "orientation": "南", "parking": null}},
  {"text": "公寓开间1室0厅，35㎡，4.5k一个月，朝北，无停车位",
   "answer": {"layout": "1室0厅", "area": 35, "price": 4500, "orientation": "北", "parking": false}},
  {"text": "南北通透户型，3室1厅，95平米，租3600元每月，小区车位充足",
   "answer": {"layout": "3室1厅", "area": 95, "price": 3600, "orientation": "南北", "parking": true}},
  {"text": "单间朝南向，1室1厅，50平，2400元月租",
   "answer": {"layout": "1室1厅", "area": 50, "price": 2400, "orientation": "南", "parking": null}},
  {"text": "急租！2室1厅 90平 3500元，拎包入住",
   "answer": {"layout": "2室1厅", "area": 90, "price": 3500, "orientation": null, "parking": null}},
  {"text": "百子湾小区 一室一厅 朝南 带固定车位",
   "answer": {"layout": "1室1厅", "area": null, "price": null, "orientation": "南", "parking": true}},
  {"text": "小区绿化特别好，物业负责任，周边配套齐全，随时看房",
   "answer": {"layout": null, "area": null, "price": null, "orientation": null, "parking": null}}
]
```

- [ ] **Step 2: 离线验证（不需要 API key）**

```bash
cd /d/studyAi/eval-practice-house && python -c "
import json
cases = json.load(open('cases.json', encoding='utf-8'))
assert len(cases) == 18, f'应为18条，实际{len(cases)}'
for c in cases:
    assert set(c) == {'text', 'answer'}, c
    a = c['answer']
    assert set(a) == {'layout', 'area', 'price', 'orientation', 'parking'}, c
    assert a['orientation'] in (None, '东', '南', '西', '北', '南北'), c
    assert a['parking'] in (None, True, False), c
    assert a['layout'] is None or all(ch.isdigit() or ch in '室厅' for ch in a['layout']), c
print('cases.json OK：18 条用例全部合规')
"
```

Expected: `cases.json OK：18 条用例全部合规`

---

### Task 2: extractor.py —— 被评测的产品（v1 埋坑版）

**Files:**
- Create: `d:\studyAi\eval-practice-house\extractor.py`

**Interfaces:**
- Consumes: `ANTHROPIC_API_KEY` 环境变量、anthropic SDK
- Produces: `class Listing(BaseModel)`（5 个字段，键名与 cases.json 的 answer 完全一致）和 `extract_listing(text: str) -> Listing`。Task 3 只 import 这两个名字。

- [ ] **Step 1: 写入 extractor.py（完整内容如下）**

```python
"""
评测闯关项目：房源信息提取器（被评测的"产品"）
本文件不直接运行，由 eval.py 导入使用。

【重要】v1 的提示词是【故意写得模糊】的，所以它只有 60 分左右。
第 2 关你的任务：只改下面 SYSTEM_PROMPT 这一个字符串，把分数提到 95% 以上。
埋了哪些坑、每关怎么玩，见 MISSIONS.md 和 SPEC.md 的埋坑清单。
"""
import anthropic
from pydantic import BaseModel

client = anthropic.Anthropic()     # 自动读取环境变量 ANTHROPIC_API_KEY（同课程 agent_lib.py）
MODEL = "claude-opus-4-8"          # 与课程用同一个模型，分数才有可比性

# ★★★ 第 2 关你唯一允许修改的地方 ★★★
# 故意只写一句模糊的话：没说格式约定、没说单位、没说缩写换算、
# 没说朝向只能取哪些值、也没说"没提到就返回 null"——五个坑全埋在这一句话里。
SYSTEM_PROMPT = "你是房源信息提取助手。从房源描述中提取户型、面积、租金、朝向、车位情况。"


class Listing(BaseModel):
    """提取结果的"答题卡"：强制模型按这 5 个字段输出（第 7 课 Part A 同款）。
    注意一个隐藏知识点：类型约束本身就在帮模型——area/price 声明为数字，
    模型就算想返回"89平米"也做不到，只能返回 89。
    【结构（schema）也是一种提示词工程】，MISSIONS.md 第 2 关思考题会问你这点。"""

    layout: str | None = None        # 户型，约定格式 "N室N厅"（阿拉伯数字）
    area: float | None = None        # 面积（平方米），纯数字
    price: float | None = None       # 月租（元），纯数字
    orientation: str | None = None   # 朝向，只允许：东/南/西/北/南北
    parking: bool | None = None      # 车位：true 有 / false 没有 / null 没提到


def extract_listing(text: str) -> Listing:
    """把一段房源描述变成 Listing 对象。eval.py 每条用例调它一次。"""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,            # 有身份设定就传（同课程 agent_lib 的 kwargs 写法）
        messages=[{"role": "user", "content": f"房源描述：{text}"}],
        output_format=Listing,           # 结构化输出：答案必须长成 Listing 的样子
    )
    return response.parsed_output
```

- [ ] **Step 2: 离线验证（不调 API）**

```bash
cd /d/studyAi/eval-practice-house && python -c "
from extractor import Listing, extract_listing, SYSTEM_PROMPT
m = Listing()
assert m.layout is None and m.parking is None
assert Listing(layout='2室1厅', area=89.0, price=3200.0, orientation='南', parking=True).area == 89.0
assert '房源信息提取' in SYSTEM_PROMPT
print('extractor.py 离线检查 OK')
"
```

Expected: `extractor.py 离线检查 OK`

- [ ] **Step 3: 单条冒烟测试（1 次 API 调用，验证 parse + system 参数可用）**

```bash
cd /d/studyAi/eval-practice-house && python -c "
from extractor import extract_listing
r = extract_listing('阳光花园小区，2室1厅，面积95平米，月租4500元，朝南，带地下车位')
print(type(r).__name__, '|', r.layout, r.area, r.price, r.orientation, r.parking)
"
```

Expected: 打印 `Listing | 2室1厅 95.0 4500.0 南 True`（字段值允许微小出入——v1 本来就不保证对；关键是**不抛异常**且返回 Listing 对象）。
若 `system=` 参数报错（SDK 不认）：把 `system=SYSTEM_PROMPT` 一行删掉，改为把提示词并进用户消息：`"content": SYSTEM_PROMPT + "\\n房源描述：" + text`，重跑本步。

---

### Task 3: eval.py —— 自动判分器

**Files:**
- Create: `d:\studyAi\eval-practice-house\eval.py`

**Interfaces:**
- Consumes: `extractor.extract_listing`、`extractor.Listing`（Task 2）；`cases.json`（Task 1）
- Produces: `normalize_layout(v)`、`normalize_number(v)`、`normalize_orientation(v)`、`field_ok(field, got, want) -> bool`、`main()`。Task 5 直接 `python eval.py` 运行。

- [ ] **Step 1: 写入 eval.py（完整内容如下）**

```python
"""
评测闯关项目：自动判分器（第 7 课"固定任务 + 自动判分"的完整版）
运行：python eval.py

它做三件事：
1. 逐条读 cases.json，调 extractor.extract_listing 拿模型答案
2. 把模型答案【归一化】成和标准答案相同的格式，再逐字段比对
   （第 7 课教过：判分器自己必须稳定，先归一化再比，否则测的是噪声）
3. 输出三种报告：总体准确率 / 分项准确率 / 错题清单
"""
import json
import re
import time
from pathlib import Path

from extractor import extract_listing, Listing

BASE_DIR = Path(__file__).resolve().parent
FIELDS = ["layout", "area", "price", "orientation", "parking"]
FIELD_NAMES = {"layout": "户型", "area": "面积", "price": "月租",
               "orientation": "朝向", "parking": "车位"}

# ---------- 归一化：把模型的各种写法"洗"成和标准答案一样的格式 ----------
_CN_NUM = {"零": "0", "一": "1", "二": "2", "两": "2", "三": "3", "四": "4",
           "五": "5", "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"}


def _to_arabic(s: str) -> str:
    """中文数字转阿拉伯数字，逐字替换（用例里数字都 ≤5，够用就好）。"""
    for cn, digit in _CN_NUM.items():
        s = s.replace(cn, digit)
    return s


def normalize_layout(v):
    """'两室一厅'/'2房1厅'/'2室1厅' -> 统一成 '2室1厅'。
    洗不出来就原样返回（必然判错，进错题清单——错得看得见）。"""
    if v is None:
        return None
    s = _to_arabic(str(v))
    m = re.search(r"(\d+)\s*[室房]\s*(\d*)\s*厅", s)
    if not m:
        return str(v).strip()
    halls = m.group(2) if m.group(2) else "0"   # 只写"2室"没提厅 -> 按 0 厅算
    return f"{m.group(1)}室{halls}厅"


def normalize_number(v):
    """从 '89平米'/'95' 里抠出数字。注意：'3.2k' 抠出来是 3.2，
    和标准答案 3200 对不上——这个坑判分器【不替它圆】，要靠第 2 关改提示词修。"""
    if v is None or isinstance(v, bool):   # bool 是 int 的子类，先排除
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"\d+(?:\.\d+)?", str(v))
    return float(m.group()) if m else None


def normalize_orientation(v):
    """朝向只做去空格；枚举约束（只许 东/南/西/北/南北）是提示词的活。"""
    return None if v is None else str(v).strip()


def field_ok(field: str, got, want) -> bool:
    """单个字段判分：先归一化再比对。want 是标准答案（本身已合规）。"""
    if field in ("area", "price"):
        g, w = normalize_number(got), normalize_number(want)
        return g is not None and w is not None and abs(g - w) < 0.01
    if field == "layout":
        return normalize_layout(got) == normalize_layout(want)
    if field == "orientation":
        return normalize_orientation(got) == normalize_orientation(want)
    return got == want                      # parking：bool/null 直接比


def main():
    cases = json.loads((BASE_DIR / "cases.json").read_text(encoding="utf-8"))
    total, correct, api_fail = 0, 0, 0
    per_field = {f: [0, 0] for f in FIELDS}   # 字段 -> [对的个数, 总个数]
    wrong_list = []                            # 错题清单：(字段, 实际, 期望, 用例文本)

    print(f"===== 房源提取评测：共 {len(cases)} 条用例 =====")
    for i, case in enumerate(cases, 1):
        try:
            got = extract_listing(case["text"])
        except Exception:
            time.sleep(2)                     # 失败等 2 秒重试一次
            try:
                got = extract_listing(case["text"])
            except Exception as e:
                api_fail += 1                 # 仍失败：该条 5 字段全记错，但不中断
                print(f"  [{i}] API 错误，记 0 分：{e}")
                got = Listing()               # 全 None 的空答题卡

        answer = case["answer"]
        for f in FIELDS:
            g, w = getattr(got, f), answer.get(f)
            ok = field_ok(f, g, w)
            total += 1
            per_field[f][1] += 1
            if ok:
                correct += 1
                per_field[f][0] += 1
            else:
                wrong_list.append((f, g, w, case["text"]))
        print(f"  [{i}/{len(cases)}] 完成")

    # ---------- 报告 1：总体准确率（第 7 课：一个数看全局） ----------
    print("\\n===== 报告 1：总体字段准确率 =====")
    print(f"  {correct}/{total} = {correct / total:.0%}")

    # ---------- 报告 2：分项准确率（定位最弱字段，决定第 2 关先修谁） ----------
    print("\\n===== 报告 2：分项准确率 =====")
    for f in FIELDS:
        hit, n = per_field[f]
        bar = "█" * round(hit / n * 20)       # 简易进度条，纯装饰
        print(f"  {FIELD_NAMES[f]}: {hit}/{n} = {hit / n:.0%}  {bar}")

    # ---------- 报告 3：错题清单（第 1 关的"病历"，逐条读它） ----------
    print("\\n===== 报告 3：错题清单 =====")
    if not wrong_list:
        print("  （全对，没有错题）")
    for f, g, w, text in wrong_list:
        print(f"  [{FIELD_NAMES[f]}] 期望={w!r} 实际={g!r} | {text[:30]}")
    if api_fail:
        print(f"\\n  ⚠ 有 {api_fail} 条用例因 API 错误记 0 分，建议重跑一次")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 离线验证归一化与判分逻辑（不调 API，不用 key）**

```bash
cd /d/studyAi/eval-practice-house && python -c "
from eval import normalize_layout, normalize_number, field_ok
assert normalize_layout('两室一厅') == '2室1厅'
assert normalize_layout('2房1厅') == '2室1厅'
assert normalize_layout('2室1厅') == '2室1厅'
assert normalize_layout(None) is None
assert normalize_number('89平米') == 89.0
assert normalize_number(95) == 95.0
assert normalize_number('3.2k') == 3.2      # 注意：3.2 != 3200，判错是【正确行为】
assert normalize_number(None) is None
assert field_ok('layout', '两室一厅', '2室1厅') is True
assert field_ok('area', '89平米', 89) is True
assert field_ok('price', 3.2, 3200) is False
assert field_ok('parking', None, None) is True
assert field_ok('parking', True, None) is False
assert field_ok('orientation', ' 南 ', '南') is True
print('eval.py 离线检查 OK')
"
```

Expected: `eval.py 离线检查 OK`

---

### Task 4: README.md + MISSIONS.md —— 项目说明与三关任务书

**Files:**
- Create: `d:\studyAi\eval-practice-house\README.md`
- Create: `d:\studyAi\eval-practice-house\MISSIONS.md`

**Interfaces:**
- Consumes: Task 1-3 的文件名与运行命令（`python eval.py`）
- Produces: 学习者入口文档；MISSIONS.md 的关卡规则与 SPEC §5 一致（第 2 关只准改 SYSTEM_PROMPT；第 3 关只准追加用例）

- [ ] **Step 1: 写入 README.md（完整内容如下）**

```markdown
# 房源信息提取器 · 评测闯关练习

一句话：这里有一个**故意只考 60 分**的 AI 房源信息提取器。
你的任务不是给它加功能，而是用**评测循环**把它修到 95 分以上——
亲身体验课程第 7 课教的"评测驱动开发"。

## 和课程的关系

第 7 课你见过了评测的两个零件：固定用例 + 自动判分。本项目把它们
放大成一个完整的开发循环：**基线 → 改进 → 重跑对比 → 扩充回归**。
将来你做任何 AI 项目，第一步都应该是先搭出这两个零件。

## 文件说明

| 文件 | 是什么 | 你可以改吗 |
|---|---|---|
| `extractor.py` | 被评测的提取器（产品本体） | 第 2 关只许改 `SYSTEM_PROMPT` |
| `cases.json` | 18 条固定用例（考卷） | 第 1、2 关不许动；第 3 关只许追加 |
| `eval.py` | 自动判分器（标尺） | 永远不许动（改标尺=作弊） |
| `MISSIONS.md` | 三关任务书 | ← 从这里开始 |
| `SPEC.md` | 项目设计文档 | 看不懂设计时来查 |

## 环境准备

1. 需要 `ANTHROPIC_API_KEY` 环境变量（与 advanced-agent-lab 课程共用）
2. 依赖已装好：`anthropic`、`pydantic`（Python 3.12）
3. 成本：跑一次评测 ≈ 18 次小调用，随便跑，不用心疼

## 快速开始

```bash
cd eval-practice-house
python eval.py     # 跑第一次评测——这就是你的"基线分数"
```

然后打开 `MISSIONS.md`，开始闯关。
```

- [ ] **Step 2: 写入 MISSIONS.md（完整内容如下）**

````markdown
# 三关任务书

> 玩法总纲：**判分器永远不许动，考卷只能加不能减。你唯一的武器是提示词。**
> 每改一版提示词就重跑 `python eval.py`，用分数说话。

---

## 第 1 关 · 建立基线（只看，不改）

**目标**：搞清楚 v1 到底错在哪。

1. 跑 `python eval.py`，把总体准确率记在下面：______
2. 盯着「报告 2：分项准确率」，找出最弱的两个字段
3. 逐条读「报告 3：错题清单」，给 5 个字段各写一句"它为什么错"：

   - 户型 layout：______
   - 面积 area：______
   - 月租 price：______
   - 朝向 orientation：______
   - 车位 parking：______

**验收**：5 句话都能落到实处（如"模型返回'两室一厅'但约定是'2室1厅'"）。
**提示**：错题清单就是第 2 关的施工图——每一条错题都对应提示词里缺的一句话。

---

## 第 2 关 · 提示词手术（本项目的核心）

**目标**：只改 `extractor.py` 里的 `SYSTEM_PROMPT` 一个字符串，
连跑 **2 次**都达到 **总体准确率 ≥ 95%**（跑 2 次是因为模型有随机性，
分数稳定才算真稳——这也是评测观念的一部分）。

**规则（铁律）**：
- 只准改 `SYSTEM_PROMPT`，`extractor.py` 其他部分、`eval.py`、`cases.json` 一个字都不许动
- 不许删掉或绕过判分逻辑

**施工建议**（按第 1 关错题清单逐条修，常见手段）：
- 格式约定：明确"户型输出为 N室N厅，用阿拉伯数字"
- 单位规则："面积和价格只要数字，不要单位"
- 换算规则："3.2k 这类写法换算成 3200"
- 枚举约束："朝向只能取：东/南/西/北/南北"
- null 规则："描述里没提到的字段一律返回 null，禁止编造"
- few-shot：在提示词里给 1-2 个输入输出示例（课程第 4 课的思路）

**思考题**（做完再答，写在文件末尾你自己加的笔记区）：
1. `Listing` 模型把 area/price 声明成数字类型，模型想返回"89平米"也做不到
   ——这算不算一种"提示词工程"？它和写在 SYSTEM_PROMPT 里的规则有何不同？
2. 你加的哪条规则带来的涨分最多？怎么证明是你的改动带来的？（提示：控制变量，
   一次只改一条规则，改完就跑）
3. parking 字段在基线挂的错，本质是什么 AI 风险？（提示：模型"不知道"的时候
   做了什么）

---

## 第 3 关 · 扩充用例 + 回归（评测集是活的）

**目标**：把你自己的 2-4 条新房源描述加进考卷，并保证分数不塌。

1. 找/写 2-4 条新描述（真实风格最佳：口语化、有噪声、有字段缺失）
2. **人工标注标准答案**（按 cases.json 现有格式；拿不准的字段标注时就想清楚
   "标准答案是什么"——这个纠结本身就是在学习标尺）
3. **只追加，不改旧用例**，存盘后重跑 `python eval.py`
4. 若新用例挂了：回第 2 关继续修提示词，直到总用例 ≥20 条且 ≥95%

**验收**：cases.json ≥20 条；重跑 2 次都 ≥95%；在本文件末尾记录一条
"bad case → 加用例 → 修复"的完整经过。

**思考题**：为什么加新用例前必须先人工标注答案，而不是"模型说啥就是啥"？
（提示：如果标尺抄模型的答案，评测还测得出模型错吗？）

---

## 通关之后

把 `extractor.py` 的 SYSTEM_PROMPT 和第 2 关的迭代过程对比读一遍，
你就拥有了面试/实战都能讲的答案："你怎么保证一个 AI 功能的质量？"
````

- [ ] **Step 3: 验证**

```bash
cd /d/studyAi/eval-practice-house && ls && python -c "print(open('README.md', encoding='utf-8').read().count('eval.py'), open('MISSIONS.md', encoding='utf-8').read().count('95'))"
```

Expected: 列出 7 个文件（5 主文件 + SPEC.md + docs 目录），README 引用 eval.py、MISSIONS 含 "95" 阈值（>0）。

---

### Task 5: 端到端基线验证（最终验收）

**Files:**
- 无新增；运行并观察 `eval.py`（若需微调：只允许动 `extractor.py` 的 `SYSTEM_PROMPT`，或按下面调整规则动 `cases.json`）

**Interfaces:**
- Consumes: Task 1-4 全部产物 + `ANTHROPIC_API_KEY`
- Produces: SPEC §8 的验收结论：端到端跑通、三种报告齐全、基线落在 55%~75%

- [ ] **Step 1: 确认 key 存在**

```bash
python -c "import os; assert os.environ.get('ANTHROPIC_API_KEY'), '缺少 ANTHROPIC_API_KEY'; print('key OK')"
```

- [ ] **Step 2: 跑完整评测**

```bash
cd /d/studyAi/eval-practice-house && python eval.py
```

Expected: 逐条 `[i/18] 完成`（或个别 API 错误行）；随后报告 1/2/3 齐全；无 Python 异常栈。

- [ ] **Step 3: 检查基线分数区间（SPEC §8）**

- **55%~75%** → 通过，记录分数与分项明细，任务完成
- **>75%** → v1 太强：把 `SYSTEM_PROMPT` 改得更简略（删掉任何超出"提取户型、面积、租金、朝向、车位"之外的措辞），重跑；仍 >75% 则把 1-2 条"干净用例"的文本改得更口语化（如 "4500元"→"4500块"），**并在 SPEC.md §2 下追加一行改动记录**
- **<55%** → 大概率不是埋坑问题而是工程问题：先看报告 3 是不是大面积 API 错误/格式解析失败（回 Task 2 Step 3 排查），确认是真实提取错误再考虑放宽（通常不需要）

- [ ] **Step 4: 汇报**

向学习者报告：基线分数、分项最弱字段、以及"现在可以打开 MISSIONS.md 开始第 1 关了"。

---

## Self-Review 记录

- **Spec 覆盖**：SPEC §1 字段规则→Task 1/2/3；§2 用例矩阵→Task 1；§3 判分与报告→Task 3；§4 埋坑→Task 2 + Task 5 Step 3；§5 关卡→Task 4；§6 非目标→未引入越界物；§7 环境→Global Constraints；§8 验收→Task 5。无缺口。
- **占位符扫描**：所有代码/文档均为完整内容，无 TBD/TODO/“适当处理”。
- **类型一致性**：`Listing` 五字段名与 cases.json 的 answer 键、eval.py 的 `FIELDS` 列表三处一致；`extract_listing(text) -> Listing` 签名在 Task 2 定义、Task 3/5 使用一致；normalize_* 名称在 Task 3 内部自洽。
