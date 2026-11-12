# Skills 深度教程 —— 从"预设提示词"到"AI 的操作手册"

> 定位：《ClaudeCode深度用法与结对开发闯关.md》第 20 关配套教材，从初步认识到高阶认识。
> 狠活：**本教程全程用你机器上的真实技能文件讲解**——你自己写的 `commit`、
> 以及 superpowers 技能库（12+ 个技能），路径都给全，随时可以打开对照。

---

# 第一部分 · 初步认识

## 第 0 章 · Skill 到底是什么（一句话 + 三兄弟对比）

**Skill = 一个文件夹 + 一份带触发条件的操作手册（SKILL.md）。**

先和它的两个近亲划清界限——三个东西都是"给 AI 的文字"，但加载方式完全不同：

| | CLAUDE.md | 自定义命令（第 8 关） | Skill（本关） |
|---|---|---|---|
| 是什么 | 项目常驻记忆 | 一段预设提示词 | 带触发条件的操作手册 |
| 加载方式 | **每次会话全文塞进上下文** | 手动输 `/命令` 才进 | **只有一句话常驻，正文按需加载** |
| 谁触发 | 自动 | 你 | **AI 自己**（读到任务匹配就掏出来） |
| 类比 | 工位上贴的制度牌，抬头就见 | 你递给 AI 的任务单 | 图书馆里的专业手册，**要用才翻** |

你环境里的真实三层样本（对应三种安装位置）：

```
C:\Users\Administrator\.claude\skills\commit\        ← 你自己写的（用户级）
C:\Users\Administrator\.claude\skills\harmonyos-development\   ← 鸿蒙开发（用户级）
C:\Users\Administrator\.claude\plugins\...\superpowers\skills\ ← 插件装的整套（12+个）
```

---

## 第 1 章 · 解剖真实样本：你的 commit skill

打开 `C:\Users\Administrator\.claude\skills\commit\SKILL.md`，结构就两块：

```markdown
---                                    ← 前置元数据（YAML frontmatter）
name: commit                           ← 技能名（/commit 也是这个名字）
description: 读取 Git 暂存区代码差异，自动生成……使用时说"提交"…   ← ★给AI看的"什么时候用我"
allowed-tools: Bash, Read              ← 这个技能被允许用的工具（权限收口）
version: 1.0.0
---

# Commit Skill                         ← 正文（触发后才被 AI 读的"菜谱"）
## 任务指令
1. 获取暂存区差异（git diff --staged）……
2. 分析变更类型（feat/fix/docs……）
3. 生成提交信息（格式模板……）
```

两个角色要分清：

- **description 是写给 AI 挑选用的**——AI 每次接到任务时扫一遍所有技能的
  description，判断"这活该不该掏这本手册"
- **正文是触发后的执行菜谱**——分步指令、格式模板、示例，AI 照着做

---

## 第 2 章 · description 是灵魂：AI 靠它决定"翻不翻这本手册"

机制一句话：**AI 不会读所有技能的全文，它只读 description 做匹配。**
所以 description 写得好坏 = 技能会不会被用起来。

写法公式：**「Use when <具体触发场景>」+「一句话说做什么」**

```
❌ 坏："关于 Git 的问题"                     ← 太泛，啥都像，AI 无所适从
✅ 好："当用户要求生成 Git 提交信息时使用（说'提交'即可触发）；
      读取暂存区差异并按 Conventional Commits 规范生成提交说明"
```

那"AI 忘了用"怎么办？superpowers 用一个**元技能**管纪律——`using-superpowers`：
> "只要有 1% 的可能某个技能适用，就必须先调用它。"

它在每次会话开始时被注入，相当于给 AI 立了条铁规矩：**宁可错掏手册，不许裸奔干活**。
这就是为什么你每次看到我说"Using [skill] to ..."——制度在起作用。

---

# 第二部分 · 深入高阶

## 第 3 章 · 高阶一：渐进披露（progressive disclosure）——上下文经济学

Skill 相对 CLAUDE.md 的本质优势，全在**三层加载**机制上：

```
第 1 层：description          永远常驻上下文     ~50 token × N 个技能
第 2 层：SKILL.md 正文        触发时才加载       通常 1~3K token
第 3 层：附属文件             正文点名才读       不限，想多大就多大
        （references/ 脚本/ 模板/）
```

算一笔账你就懂了：假如你有 20 个技能，若像 CLAUDE.md 那样全文常驻，
上下文直接爆掉；但 Skill 只常驻 20 句 description（约 1000 token），
**技能库可以无限大，常驻成本恒定小**——需要哪本翻哪本。

**实证就在你机器上**：`systematic-debugging`（系统化调试）一个技能，
附属文件有 7 个（`root-cause-tracing.md`、`defense-in-depth.md`……）。
平时它们一个 token 都不占你的上下文；只有 AI 真在调 bug、翻开手册、
正文让它读某份深入资料时，那份资料才进上下文。

> 🔑 一句话总结：**CLAUDE.md 回答"AI 永远该知道什么"；
> Skill 解决"AI 需要时才知道什么"。**

---

## 第 4 章 · 高阶二：技能文件夹里能装什么（四种形态）

按"SKILL.md 之外还装什么"分四档，全是真实样本：

| 形态 | 装什么 | 真实样本（superpowers 里） |
|---|---|---|
| 纯指令型 | 只有 SKILL.md | 你的 `commit`；`verification-before-completion` |
| 带参考型 | `references/*.md` 深入资料 | `systematic-debugging/`（7 份调试方法论） |
| 带脚本型 | `scripts/*.sh` 自动化脚本 | `brainstorming/`（起本地服务器的脚本） |
| 带提示词模板型 | 复用提示词文件 | `subagent-driven-development/`（给子代理的 implementer-prompt.md） |

高阶心得：**SKILL.md 本身要短**——它是"菜谱目录 + 核心步骤"，深入细节全部
外置到附属文件，正文里写"深入时读 references/xxx.md"即可。这样
单次触发也只加载真正需要的部分。

---

## 第 5 章 · 高阶三：技能互相调用 = 方法论组合拳

SKILL.md 正文里可以**指示 AI 去启用另一个技能**，于是技能能串成流水线。
superpowers 的开发流程链就是活例子：

```
brainstorming（想清楚要什么） → writing-plans（写计划文档）
   → executing-plans（按计划执行） → requesting-code-review（交付前审查）
```

**你亲历过这条链**：当时建 `eval-practice-house` 项目，我走的就是
brainstorming → SPEC → writing-plans → executing-plans——每个环节
各是一本被触发翻开的"手册"。技能组合 = 把团队 SOP（标准作业流程）
沉淀给 AI。

---

## 第 6 章 · 四件套终极对比（本关验收要求）

| | 自定义命令 | Skill | MCP | 子代理 |
|---|---|---|---|---|
| 本质 | 一段预设提示词 | 按需加载的操作手册 | 外接工具/数据 | 隔离上下文的临时工 |
| 触发 | 你手动 `/命令` | **AI 自动匹配** | AI 按需调用工具 | AI 或你派活 |
| 常驻成本 | 0（不触发不占） | 极小（一句 description） | 工具列表 | 派活时的开销 |
| 沉淀的是 | 固定话术 | **方法论/知识** | **能力**（连外部系统） | 并行/隔离 |
| 适合 | "每次都这么问" | "每次都这么做" | "接外部世界" | "大范围/独立小任务" |

记忆口诀：**命令存话术，Skill 存方法论，MCP 给手，子代理分身。**

---

# 第三部分 · 动手实战

## 第 7 章 · 实战：把你的评测方法论写成 skill（第 20 关动手）

目标：把你在 eval-practice-house 闯关攒的方法论，变成任何项目都能复用的手册。
建 `D:\studyAi\.claude\skills\eval-methodology\SKILL.md`（项目级，放 studyAi 根）：

```markdown
---
name: eval-methodology
description: 当用户想评测/打分任何 AI 功能（提取器、分类器、Agent）时使用。
  覆盖：建基线、写测试用例、设计判分器、迭代提示词、回归测试。
---

# 评测方法论（来自房源提取器闯关的实战沉淀）

## 铁律
1. 判分器永远不许动，考卷只能加不能减——标尺先立稳，再谈提分
2. 没把握的字段标 null，禁止编造（幻觉防线要在 schema 层面立住）
3. 一次只改一处，改完立刻重跑——控制变量才能归因

## 流程
1. **建基线**：先跑分记录，逐字段找最弱项（不要凭感觉判断哪里有问题）
2. **分项归因**：盯分项报告+错题清单，每条错题对应一条缺失的提示词规则
3. **手术**：只改提示词，按错题清单逐条修，改一条跑一次
4. **稳定性**：连跑 2 次达标才算真稳（模型有随机性）
5. **回归**：追加自写新用例（只加不改），确认分数不塌

深入时读：D:\studyAi\eval-practice-house\MISSIONS.md（完整闯关版）
```

**验证方式**（关键一步）：重开会话，说"我想给我的地址提取功能打个分"——
观察 AI 会不会自己触发这个技能、按你的方法论开工。触发了 = 学费没白交。

---

## 🎮 闯关任务（3 关）

### 第 1 关 · 实物考察
读两份真实文件：你的 `commit\SKILL.md` 和 superpowers 的
`systematic-debugging\SKILL.md`。
**验收**：说出三层加载（description / 正文 / 附属文件）在这两个技能上
分别怎么体现的；`systematic-debugging` 的 7 个附属文件平时占多少上下文？

### 第 2 关 · 写第一个 skill
按第 7 章建 `eval-methodology`，新会话验证触发。
**验收**：AI 能自己按"基线→分项→手术→稳定→回归"的顺序开工。

### 第 3 关 · 高阶改造
给技能加一个 `references/` 子文件夹（比如把"null 纪律详解"移进去），
正文只留一句"涉及 null 语义时读 references/null.md"。
**验收**：能算清这波改造省了多少常驻/触发的 token。

---

## 速查

| 要点 | 内容 |
|---|---|
| 最小结构 | 文件夹/SKILL.md（frontmatter: name + description） |
| 安装位置 | `~/.claude/skills/`（用户级）、`项目/.claude/skills/`（项目级）、插件 |
| description 公式 | Use when <具体场景> + 一句话做什么 |
| 加载 | 三层渐进披露：常驻一句话 → 正文按需 → 附属文件再按需 |
| 组合 | 正文可指示调用其他技能，串成方法论流水线 |
| 和近亲的区别 | 命令存话术，Skill 存方法论，MCP 给手，子代理分身 |
