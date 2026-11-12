# AI 应用开发详解教程 —— RAG · LLM-as-Judge · 生产工程化

> 定位：《AI应用开发进阶闯关.md》的配套详解教材（任务书=关卡清单，本册=逐关讲解+可跑代码）。
> 所有代码已按你机器的实际情况写：中转站鉴权（`ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`）、
> 结构化输出用"工具调用+兜底"模式（你踩过 output_format 的坑）、运行时加 `-X utf8`。
> 模型统一 `claude-opus-4-8`（与 extractor.py 一致）。

---

# 阶段一 · RAG：让 AI 懂你的私域数据

## 第 1 章 · 为什么会幻觉，RAG 怎么救

**幻觉的根源**：模型的知识来自训练数据，有个"知识截止日期"；而且它**从来没见过
你公司的房源文档**。你硬问，它不会说"我不知道"，而是按语言惯性**编一个像样的答案**——
因为它被训练成"总要回答"。

**亲手体感**（5 分钟，不写代码）：
1. 问 Claude："eval-practice-house 项目 cases.json 第 7 条用例的期望朝向是什么？"
   → 它要么猜、要么坦白不知道
2. 把 cases.json 全文粘给它，再问 → 答对了

第 2 步你做的事——**先查资料、把资料塞给它、再让它回答**——就是 RAG。
唯一的问题是"你手动粘"，RAG 把这个动作自动化了。

**RAG 五步全图**：

```
离线准备：  📄文档 ──①切块──→ 🔪chunks ──②向量化──→ 🧮向量 ──③存库──→ 📚知识库
在线问答：  ❓用户问题 ──②向量化──→ 🧮
                                  └──④检索：找最像的 top3──→ 📋
再拼接：    prompt = "参考以下资料回答：{top3}\n\n问题：{用户问题}"
            ──⑤交给模型──→ ✅有据可查的回答
```

一句话记忆：**RAG = 开卷考试**。模型还是那个模型，但你把相关书页翻好递给它。

---

## 第 2 章 · 相似度：机器怎么知道两段话"像"

RAG 的核心难题是第④步检索：问题来了，从 100 个块里挑 3 个最相关的。
机器判断"像不像"靠**把文字变成数字再比大小**。

### 2.1 入门版：关键词重合度（零依赖，今天就能跑）

`jaccard` 相似度：两段文字分词后，**共同词 ÷ 总词数**。

```python
# similarity.py —— 最朴素的相似度：关键词重合度
def tokenize(text):
    # 中文没空格分词，教学版用"2字滑窗"粗暴切片（能抓到 房源/朝南 这类词）
    text = text.replace("，", " ").replace("。", " ").replace("？", " ")
    return {text[i:i+2] for i in range(len(text) - 1)}   # 返回集合（去重）

def jaccard(a, b):
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0
    return len(ta & tb) / len(ta | tb)   # 交集 / 并集：1=完全相同，0=毫无重叠

docs = [
    "两室一厅 89平 朝南 拎包入住",
    "南北通透三居室 120平米 拎包入住",
    "朝阳公园旁一居 45平 拎包入住",
]
q = "朝南两居 拎包入住"

# 给每个文档打相似度分，排序
ranked = sorted(docs, key=lambda d: jaccard(q, d), reverse=True)
for d in ranked:
    print(f"{jaccard(q, d):.2f}  {d}")
```

**做实验**：把 `q` 改成"89㎡南向包入住"再跑——你会发现"㎡"和"平"、
"南向"和"朝南"这些**同义不同词**的情况，关键词法就抓瞎了。

### 2.2 为什么需要向量（embedding）

embedding 模型在海量文本上训练过，它知道"平≈㎡""朝南≈南向"——
它输出的向量里，**语义相近的词距离就近**，哪怕一个字都不重合。
所以工业界检索用 embedding，关键词法只做兜底（两者混合叫混合检索）。

真 embedding 需要调接口（Anthropic 官方没有 embeddings API，常用 Voyage、
OpenAI 系、或本地跑 `sentence-transformers` 库）。**你的中转站是否放行
embedding 接口需要实测**——不通就先用 2.1 的关键词法把 RAG 全流程学完，
原理完全一样，只是"打分函数"换了。

---

## 第 3 章 · 搭第一个 RAG：房源 FAQ 问答机器人

### 3.1 先写知识库 `faq.md`（10 条问答对）

```markdown
## 小区停车
小区有地下车位，月租 400 元，访客可临时停车，前 2 小时免费。

## 供暖与水电
集中供暖，民水民电，燃气入户。电费 0.52 元/度，水费 3.9 元/吨。

## 拎包入住
房屋已配置床、沙发、冰箱、洗衣机、空调，可拎包入住。

## 押金与付款
押一付三，可月付（需押二）。签约一年起租。

## 交通
距地铁 6 号线朝阳站步行 800 米，小区门口有公交 31 路。

## 宠物
不允许养宠物。

## 维修
屋内设施损坏联系管家，24 小时内响应，人为损坏需赔偿。

## 看房
支持随时看房，联系管家预约即可。

## 周边配套
1 公里内有永辉超市、朝阳大悦城，三甲医院 2 公里。

## 合同与退租
提前 30 天书面通知可退租，押金无违约全额退。
```

### 3.2 完整机器人 `rag_bot.py`（可跑）

```python
# rag_bot.py —— 房源 FAQ 问答机器人（关键词检索版 RAG）
import anthropic

MODEL = "claude-opus-4-8"
client = anthropic.Anthropic()          # 自动读环境变量（中转站）

# ---------- 第①步：切块 ----------
def load_chunks(path="faq.md"):
    """按 '## ' 标题把文档切成一块一块"""
    chunks = []
    title, body = None, []
    for line in open(path, encoding="utf-8"):
        if line.startswith("## "):             # 遇到新标题：收上一块，开新块
            if title:
                chunks.append(f"{title}\n" + "".join(body))
            title, body = line.strip(), []
        else:
            body.append(line)
    if title:
        chunks.append(f"{title}\n" + "".join(body))
    return chunks

# ---------- 第②步：相似度（复用第 2 章的函数） ----------
def tokenize(text): ...
def jaccard(a, b): ...
# （把第 2 章的两个函数原样贴进来）

# ---------- 第④步：检索 top-k ----------
def retrieve(question, chunks, k=3):
    scored = sorted(chunks, key=lambda c: jaccard(question, c), reverse=True)
    return scored[:k]

# ---------- 第⑤步：拼接 + 交给模型 ----------
def answer(question):
    chunks = load_chunks()
    top = retrieve(question, chunks)
    context = "\n---\n".join(top)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=(
            "你是房源客服。只根据【参考资料】回答问题；"
            "参考资料里没有的信息，老实回答'这个资料里没有提到'，禁止编造。"
        ),                                     # ← 反幻觉红线写死在 system 里
        messages=[{"role": "user",
                   "content": f"【参考资料】\n{context}\n\n【问题】{question}"}],
    )
    return resp.content[0].text

if __name__ == "__main__":
    while True:
        q = input("\n你的问题（回车退出）：").strip()
        if not q:
            break
        print(answer(q))
```

**验收实验**：问"停车方便吗"→ 命中车位块，答 400 元 ✓；
问"能养宠物吗"→ 知识库里**有**这条 → 答"不允许" ✓；
问"房东是谁"→ 资料里没有 → 它**必须**答"没有提到" ✓。
第三条是 RAG 的灵魂测试：**检索不到时，宁说不知，不许编**。

---

## 第 4 章 · RAG 调优：检索不准，后面全白搭

RAG 效果差，90% 是检索的锅（模型根本没拿到对的资料）。三个旋钮：

| 旋钮 | 调什么 | 常见效果 |
|---|---|---|
| 块的大小 | 按"##"切 vs 按固定 200 字切 | 块太大→一堆无关内容稀释重点；太小→上下文断裂 |
| 检索条数 k | top3 vs top5 | k 大召回率高但塞入噪声、烧 token |
| 打分函数 | 纯 jaccard vs "标题命中额外加分" | 标题往往就是问题关键词，加权常立竿见影 |

**用评测驯服它**（第 7 课思想第三次复用）：

```python
# rag_eval.py —— 检索命中率测试
CASES = [  # (问题, 应命中块的关键词)
    ("停车方便吗",            "车位"),
    ("水电费多少钱",          "供暖与水电"),
    ("能养猫吗",              "宠物"),
    ("地铁近吗",              "交通"),
    ("怎么退租",              "合同与退租"),
]

def hit(question, chunks):
    top = retrieve(question, chunks, k=3)
    return any(kw in t for t in top for kw in [dict(CASES)[question]])

chunks = load_chunks()
ok = sum(hit(q, chunks) for q, _ in CASES)
print(f"检索命中率：{ok}/{len(CASES)}")
```

改一个旋钮 → 跑一次 → 记一格式。**分数说话，感觉不算。**

---

# 阶段二 · LLM-as-Judge：用模型当裁判

## 第 5 章 · 裁判模式：硬规则判不了的软质量

你的 eval.py 靠正则比数字——但"这段回答通不通顺、专业不专业"没有正则可写。
解法：让**另一个模型**按你写好的**评分量规（rubric）**打分，输出结构化结果。

`judge.py` 完整实现（**复用 extractor 的"工具调用+兜底"模式**，中转站安全）：

```python
# judge.py —— 用大模型当裁判给回答打分
import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"
client = anthropic.Anthropic()

JUDGE_TOOL = {
    "name": "submit_judgment",
    "description": "提交对被评答案的判定结果",
    "input_schema": {
        "type": "object",
        "properties": {
            "score":    {"type": "integer", "description": "1-5 分"},
            "reason":   {"type": "string",  "description": "扣分/加分理由，必须引用原文"},
        },
        "required": ["score", "reason"],
    },
}

class Judgment(BaseModel):
    score: int
    reason: str

RUBRIC = """按以下量规打分（1~5）：
5 分：准确回答了问题，且只用参考资料中的信息，表述清晰
3 分：方向对但有含糊/遗漏，或混入少量资料外内容
1 分：答非所问，或编造了参考资料里不存在的信息（幻觉直接 1 分）"""

def judge(question: str, reference: str, answer: str) -> Judgment:
    messages = [{"role": "user", "content":
        f"【评分量规】\n{RUBRIC}\n\n【问题】{question}\n"
        f"【参考资料】{reference}\n【被评答案】{answer}\n\n请调用工具提交判定。"}]
    resp = client.messages.create(
        model=MODEL, max_tokens=1000,
        system="你是严格的质量裁判。只依据量规打分，理由必须引用原文证据。",
        tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "submit_judgment"},
        messages=messages,
    )
    for block in resp.content:
        if block.type == "tool_use":                      # 正常路径
            return Judgment(**block.input)
    # 兜底路径：中转站偶尔不执行强制工具调用 → 追问一次
    messages += [{"role": "assistant", "content": resp.content},
                 {"role": "user", "content": "必须调用 submit_judgment 工具提交判定。"}]
    resp = client.messages.create(
        model=MODEL, max_tokens=1000, tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "submit_judgment"}, messages=messages)
    for block in resp.content:
        if block.type == "tool_use":
            return Judgment(**block.input)
    raise RuntimeError("裁判两次都没有提交判定")
```

验收：拿它评 3 条真实回答（一条好、一条含糊、一条编造的）——
**编造那条必须被打 1 分且理由引用了原文**，裁判才算立住了。

## 第 6 章 · 裁判自己也不可靠：校准

迁移你第 7 课最重要的一课——**判分器必须先可靠**。裁判模型的三个已知毛病：

| 毛病 | 表现 | 校准招 |
|---|---|---|
| 长度偏好 | 同内容的长答案分高 | rubric 写死"长度不参与评分" |
| 位置偏差 | 两答案对调顺序，评分翻转 | 顺序对调各评一次取平均 |
| 量纲漂移 | 今天 3 分明天 4 分 | 每档分给**具体描述**（见 RUBRIC），且评 3 次取中位数 |

**做实验**：把一段 5 分答案抄两遍、第二遍后面多加 50 字废话，分别送评——
如果分数变了，你就亲眼看见了长度偏好。修 rubric 再测，直到分数稳定。

**进阶：A/B 对比式打分**（比绝对打分稳得多）——不给分，只问"两份答案哪个好"，
因为"比较"是模型最擅长的判断：

```python
# 不打分，只站队：prompt 换成——
# "A 和 B 两份答案，哪个更符合量规？只回答 A 或 B，并给一句理由。"
# 用两次（AB / BA 顺序对调）投票，2:0 或 2:1 出结论
```

什么时候敢信裁判：rubric 具体 + 中位数投票 + 抽 10% 人工复核无重大分歧。
不满足就人工。

---

# 阶段三 · 生产工程化：从能跑到敢上线

## 第 7 章 · 健壮性三件套：重试、超时、限流

线上 API **必然**偶发失败。Demo 和产品的分水岭就是接不接得住。
先记住**错误分类学**（哪些该重试）：

| 错误 | 该重试吗 | 原因 |
|---|---|---|
| 429 限流 / 5xx 服务错 / 超时 / 断连 | ✅ 等 retry-after 后重试 | 对方/网络的问题，再试可能就好 |
| 400 参数错 / 401 密钥错 | ❌ 绝不重试 | 你自己的问题，重试一万次还是 400 |

`robust_call.py`——给任何一次 API 调用套上外壳（手写 30 行，看懂原理）：

```python
# robust_call.py —— 生产级调用外壳：超时 + 重试 + 指数退避
import time
import anthropic

def call_with_retry(make_request, max_retries=3, base_delay=1.0):
    """make_request: 一个无参函数，内部发 API 请求并返回结果"""
    for attempt in range(max_retries + 1):
        try:
            return make_request()
        except anthropic.RateLimitError as e:          # 429：按服务器指示等
            wait = float(e.response.headers.get("retry-after", base_delay * 2 ** attempt))
        except (anthropic.APIStatusError) as e:        # 5xx：指数退避
            if e.status_code < 500:
                raise                                   # 4xx 不重试！
            wait = base_delay * 2 ** attempt
        except (anthropic.APIConnectionError, anthropic.APITimeoutError):
            wait = base_delay * 2 ** attempt            # 网络问题：退避重试
        if attempt == max_retries:
            raise                                       # 重试用尽，向上抛
        print(f"第 {attempt+1} 次失败，{wait:.1f}s 后重试…")
        time.sleep(wait)

# 用法：把"发请求"包成函数传进去
client = anthropic.Anthropic(timeout=30.0)              # 超时也交给客户端管
result = call_with_retry(lambda: client.messages.create(
    model="claude-opus-4-8", max_tokens=200,
    messages=[{"role": "user", "content": "用一句话介绍 RAG"}]))
print(result.content[0].text)
```

**验收实验**：把环境变量 `ANTHROPIC_BASE_URL` 临时改错再跑——
观察"失败→等待→重试"的日志；改回来恢复正常。429 的指数退避节奏
（1s→2s→4s）是行业惯例，**别用死循环硬砸限流的服务**。

## 第 8 章 · 缓存与降级：省钱和保命

**缓存**：同样的问题别重复烧钱。最小实现一个 dict：

```python
_cache = {}
def cached_answer(question):
    if question in _cache:                 # 命中：0 次 API 调用
        return _cache[question]
    ans = answer(question)                 # 未命中：真调用，然后存起来
    _cache[question] = ans
    return ans
```
（生产会换语义缓存/带过期时间，但原理就是"问过的别再问"。）

**降级链**：主模型挂了别让服务死——

```python
def answer_with_fallback(question):
    for model in ["claude-opus-4-8", "claude-haiku-4-5"]:
        try:
            return call_with_retry(lambda: client.messages.create(
                model=model, max_tokens=500,
                messages=[{"role": "user", "content": question}]))
        except Exception as e:
            print(f"{model} 挂了：{e}，降级…")
    return "服务暂时不可用，请稍后再试。"     # 最后一道兜底：人话，不是报错堆栈
```
（这就是《模型编排详解教程》的容错形态：贵的先上，不行换便宜的，再不行给兜底。）

## 第 9 章 · 监控与数据飞轮：上线只是开始

每次调用记一笔账（csv 就够起步）：

```python
import csv, time
def log_call(question, model, ok, seconds, out_tokens):
    with open("calls.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([time.strftime("%F %T"), question, model,
                                ok, f"{seconds:.1f}", out_tokens])
```

真正值钱的是**数据飞轮**：

```
线上日志 → 挑出 bad case → 人工标注 → 追加进 cases.json → 重跑评测提分
   ↑                                                        ↓
   └────────────── 服务更聪明了，继续上线接流量 ←────────────┘
```

这是 AI 产品和传统软件最大的差别：**传统软件上线即巅峰，AI 服务靠飞轮越转越好**。
你的 eval-practice-house 第 3 关（扩充用例）其实就是飞轮的手动版——现在只是
让它转起来。

---

# 阶段四 · 选型与视野

## 第 10 章 · 三条路怎么选：提示词 vs RAG vs 微调

| | 提示词/结构化输出 | RAG | 微调 |
|---|---|---|---|
| 教模型什么 | **规则**（格式、口径、纪律） | **知识**（会变的事实、文档） | **习惯**（固化的任务模式/风格） |
| 成本 | 几乎为 0 | 中（检索+向量库） | 高（数据+训练+运维） |
| 更新 | 改字即生效 | 换文档即生效 | 要重新训练 |
| 选它当 | 知识不多的规则约束 | 知识量大且常变 | 任务固定、量大、前两者到顶 |

决策口诀：**先提示词，知识常变上 RAG，都到顶才微调**（90% 的场景走不完这条路）。
第 10 关的三道思考题答案方向：①产品手册 → RAG；②"南北通透"写错 → 先提示词/schema，
不行再微调；③每周价格表 → RAG。

## 第 11 章 · 多模态初体验（选修）

图片照常走 messages.create，加一个图片内容块：

```python
import base64
with open("room.jpg", "rb") as f:
    b64 = base64.standard_b64encode(f.read()).decode()
resp = client.messages.create(
    model="claude-opus-4-8", max_tokens=500,
    messages=[{"role": "user", "content": [
        {"type": "image", "source":
            {"type": "base64", "media_type": "image/jpeg", "data": b64}},
        {"type": "text", "text": "描述这个房间：户型布局、装修风格、采光。"},
    ]}]})
print(resp.content[0].text)
```
业务联想：租客拍照 → 自动生成房源描述草稿 → 人工确认——多模态+结构化输出的组合拳。

---

# 🎓 毕业项目装配清单（对照《AI应用开发进阶闯关.md》）

| 要求 | 从哪关搬积木 |
|---|---|
| 健壮：重试/超时/降级 | 第 7、8 章两个外壳函数 |
| 省钱：缓存+分档模型 | 第 8 章 + 模型编排教程 |
| 可信：抽样裁判复核 | 第 5、6 章 judge.py |
| 可观测：调用日志+飞轮 | 第 9 章 csv + 飞轮流程 |
| 有说明书：README | 边界（什么答不了）、挂了的表现、质量怎么保证 |

毕业检验：把文件夹给一个不懂 AI 的同事，**不解释**，他能用、坏了知道找谁——
这就是"工程师做的 AI"和"玩具 AI"的分界线。
