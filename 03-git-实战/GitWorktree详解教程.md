# Git Worktree 详解教程 —— 平行工作室完全指南

> 定位：《Git从零到实战闯关.md》的进阶续篇，也是《ClaudeCode深度用法与结对开发闯关.md》
> 第 21 关（多 Agent 并行工厂）的配套教材。
> 前提：学过分支（Git 教程第 6 章）——知道 `git switch -c`、`git merge` 是什么。
> 环境：Windows + Git Bash，全部命令在项目文件夹里执行。

---

## 第 0 章 · 为什么需要 worktree —— 先看三个痛点

你已经知道：**分支 = 平行世界**。但有个隐藏限制一直没说破——

> **一个文件夹同一时刻只能站在一个分支上。** 切分支 = 全文件夹的文件瞬间换成那个分支的样子。

于是遇到这些场景就难受了：

| 痛点 | 具体场景 | 老办法的下场 |
|---|---|---|
| ① 半成品被打断 | A 功能改一半，急着切去修 bug | 只能 stash 塞抽屉（忘了 pop 就抓瞎） |
| ② 要同时跑两个版本 | 两个提示词方案各跑一遍 eval 对比 | 切来切去，跑完 A 的环境切到 B 就没了 |
| ③ 多个 AI 并行干活 | 派两个 Claude Code 同时写不同功能 | 同一个文件夹必打架——都往一张书桌上堆文件 |

**笨办法**：把项目文件夹复制两份（`项目-方案A`、`项目-方案B`）。
代价：磁盘双倍、两边历史**不共享**（A 里 commit 的东西 B 看不见）、想合并只能手动搬文件。

**正解**：`git worktree`——一个仓库开多间"工作室"，每间各站一个分支，
**共用同一个 `.git` 档案柜**。历史互通、磁盘只存一份快照、合并走正规 `merge`。

---

## 第 1 章 · 一张图看懂 worktree

```
D:\studyAi\eval-practice-house\   ← 主工作室：站在 main
D:\studyAi\eph-taskA\             ← 工作室A：站在 taskA 分支
D:\studyAi\eph-taskB\             ← 工作室B：站在 taskB 分支
        │
        └─────── 三间工作室共用同一个 .git（在主工作室文件夹里）───────┘

共享的（档案柜里的东西）：全部快照历史、全部分支、配置、远程地址
各自独立的（书桌上的东西）：工作区文件、当前站在哪个分支、未提交的改动
```

两个正式术语（见到不慌）：

- **主工作区**：你 `git init` / `git clone` 出来的那个原始文件夹
- **链接工作区**：用 `git worktree add` 开出来的其他文件夹

理解核心就一句话：**worktree 把"文件夹 ↔ 分支"的绑定从一对一变成一对多。**
文件夹多了几间，档案柜始终只有一个。

> 💡 技术细节（好奇再看）：`git worktree add` 会在 `.git/worktrees/` 下
> 建一个"分店登记簿"，记录每间工作室的路径和所在分支——所以档案柜永远知道
> 谁站在哪，也不会让你把同一个分支站两次（见第 2 章）。

---

## 第 2 章 · 四件套命令（就这么多）

```bash
# ① 开新工作室 + 顺便建新分支（90% 的场景用它）
git worktree add ../eph-taskA -b taskA
#               └路径(建议放项目旁边)  └新分支名

# ② 用【已有分支】开工作室（比如把远程的 feature 拉下来本地看）
git worktree add ../eph-hotfix hotfix-fix

# ③ 查看所有工作室（哪些文件夹、各站哪个分支）
git worktree list

# ④ 拆除工作室（活干完、合并完就拆，别留垃圾）
git worktree remove ../eph-taskA
```

三条使用须知：

1. **路径放项目旁边（`../xxx`），别建在项目文件夹里面**。
   建在里面虽然能跑，但工作室文件夹会出现在 `git status` 里，容易被误提交，纯添乱。
2. **同一个分支不能同时被两间工作室站着**——你 `add` 时 Git 会直接拒绝：
   `fatal: 'taskA' is already checked out at ...`。这是保护不是坑：两个工人站同一分支等于没分开。
3. **remove 时工作室里有未提交的改动，Git 会拒绝**（防止你误删工作）。
   确定真不要了才 `git worktree remove --force ../eph-taskA`——加 force 前深呼吸。

---

## 第 3 章 · 完整生命周期（跟着敲一遍就懂了）

场景：给 `eval-practice-house` 同时开发两个互不相关的功能。

```bash
# ⓪ 回到主工作室，确认 main 干净（军规：动手前先 commit）
cd /d/studyAi/eval-practice-house
git status                    # 必须是 working tree clean

# ① 开两间工作室
git worktree add ../eph-taskA -b taskA    # 功能A：写 reports.py
git worktree add ../eph-taskB -b taskB    # 功能B：补 README
git worktree list                          # 三行：主 + 两间新工作室
```

`list` 输出长这样（读懂它）：

```
D:/studyAi/eval-practice-house  a1b2c3d [main]
D:/studyAi/eph-taskA            a1b2c3d [taskA]     ← 新工作室，起点=main 最新快照
D:/studyAi/eph-taskB            a1b2c3d [taskB]
```

```bash
# ② 进任意一间，像平常一样干活（add/commit 流程完全一样，只是发生在这间屋里）
cd ../eph-taskA
echo "report 功能" > reports.py
git add . && git commit -m "新增 reports.py 初版"

# ③ 见证"档案柜共享"：回到主工作室，能直接看到 taskA 的快照！
cd ../eval-practice-house
git log --oneline --graph --all    # taskA 的提交就在图里
                                   # 而你自己的 main 一个文件都没被动过

# 💡 不爱看命令行图？IDEA 内置的 Git Log 看的是同一个档案柜：
#    底部 Git 工具窗（Alt+9）→ Log 页签 → 勾选 All branches，
#    全部分支的分叉合流图形化展示，点任意提交可看 diff。
#    （GitLens 是 VS Code 的插件，干的是同一件事，IDEA 用不上。）

# ④ 验收 + 合并（在主工作室做）
git diff main..taskA               # 审查 A 干的活
git merge taskA                    # 快进合并，reports.py 出现在主工作室
git merge taskB

# ⑤ 拆除 + 清理分支
git worktree remove ../eph-taskA
git worktree remove ../eph-taskB
git branch -d taskA taskB
```

体会一下最爽的点：**全程主工作室安静躺在 main 上，一行代码没被踩过**——
这就是"敢让 AI/自己乱试"的物理隔离。

---

## 第 4 章 · 配合 Claude Code：多 AI 并行工厂（第 21 关实操手册）

worktree 的杀手级用法：**每间工作室开一个终端，各启动一个 Claude Code，同时干活。**

```bash
# 终端1
cd /d/studyAi/eph-taskA && claude
# 终端2
cd /d/studyAi/eph-taskB && claude
```

给每个工人的**提示词模板**（三个要素：任务 + 边界 + 交付方式）：

```
实现 <功能描述>。
规则：只准改 <文件范围>，其他文件一个字不动。
完成后：git add + git commit（message 写清做了什么），不要 push。
```

**指挥官（你）的完整节拍**：

1. 拆任务 → 确认两间工作室的任务**文件范围不重叠**（铁律！都改同一文件 = merge 冲突）
2. 放工 → 两边自己去 commit
3. 验收 → 每间必跑 `git diff main..taskX` 亲自过目（不盲信 AI）
4. 合并 → 主工作室里 `git merge taskA` → `git merge taskB`
5. 拆除 → `git worktree remove` → `git branch -d`

冲突了怎么办？照 Git 教程 6.4 的四步手解（看冲突块 → 手改 → add → commit）。

三个提醒：

- **每个 Claude Code 会话是独立的**：各自的权限弹窗、各自的上下文，互不知晓对方存在——
  协调工作全靠你拆任务时划清地盘
- **多会话 = 多份 token 消耗**：并行是用钱换时间，小任务别开工厂
- **先跑通单人版再开工厂**：先在一个分支上让 AI 自己 commit 跑顺（ClaudeCode 闯关第 4、15 关），
  再上并行

### 4.1 不想开多个终端？三种替代

| 方式 | 形态 | 适合 |
|---|---|---|
| A. 一个会话里派子代理 ⭐ | 只开一个 Claude Code 窗口，动嘴指挥 | 日常首选 |
| B. IDE 插件代替终端 | 每间工作室用 IDEA/VS Code 开成项目窗口，侧边栏面板打字 | 想要全 GUI |
| C. 无头模式脚本化 | 一个脚本后台同时起 N 个 `claude -p`，结果落盘 | 无人值守（见第 16 关） |

方式 A 的提示词示范（主会话 = 总指挥，子代理 = 工人）：

```
建两个 worktree：../eph-taskA -b taskA 和 ../eph-taskB -b taskB。
然后派两个子代理并行干活：
- 子代理A 在 ../eph-taskA 里：写 reports.py（只准碰这个文件）
- 子代理B 在 ../eph-taskB 里：补 README 使用说明（只准碰 README）
各自完成后自己 git add + commit，都完成后向我汇报。
```

实话实说：方式 A 的所有工作都汇在一个会话里——**token 集中烧、看不到
实时干活过程**；多窗口的好处恰是各算各的账、可以分别盯着。小活用 A，
重活开多终端。铁律不因方式而变：worktree 隔离 + 文件范围不重叠 +
你亲自 diff 验收后再 merge。

---

## 第 5 章 · worktree vs 老朋友们（什么时候用什么）

| 需求 | 用什么 | 为什么 |
|---|---|---|
| 改一半被打断，一会儿就回来 | `git stash` | 秒级操作，杀鸡别用牛刀 |
| 单个功能，做完再干下一个 | 普通分支 + switch | 一个人的串行世界，最简单 |
| 同时**看/跑/改**两个版本；多 AI 并行 | **worktree** | 唯一能让多个分支同时"活着"的办法 |
| 想给别人一份独立仓库 / 两边历史独立 | `git clone` | 只有需要历史隔离时才值得付双倍磁盘 |

反过来说，**这些情况别用 worktree**：

- 就一个小改动——开工作室的仪式感比改动本身还贵
- 两个任务会碰同一批文件——注定 merge 冲突，并行是假并行（先串行干完 A 再干 B）

---

## 第 6 章 · 翻车急救

| 状况 | 解药 |
|---|---|
| 手滑直接删了工作室文件夹（没走 remove） | `git worktree prune` 清掉失效登记；分支和历史毫发无损 |
| 工作室里改了一半，全不要了 | `git worktree remove --force ../路径`（真不要了才加 force） |
| 想切的分支提示 already checked out | 它被某间工作室占着——先 remove 那间，或 `git worktree list` 查明 |
| 工作室不小心建在了项目文件夹里面 | 没提交过东西就直接 `remove`，重开到 `../` |
| 忘了哪间工作室是干嘛的 | `git worktree list` + 各自 `git log --oneline -3` 看最近提交 |

---

## 第 7 章 · 速查表

| 命令 | 作用 |
|---|---|
| `git worktree add ../路径 -b 新分支` | 开工作室 + 建分支（主力） |
| `git worktree add ../路径 已有分支` | 用已有分支开工作室 |
| `git worktree list` | 查看所有工作室 |
| `git worktree remove ../路径` | 拆工作室（有未提交改动会拒绝） |
| `git worktree remove --force ../路径` | 强拆（丢弃未提交改动） |
| `git worktree prune` | 清理失效工作室记录 |
| （工作室里）`git add / commit` | 和平常一模一样 |
| （主工作室）`git diff main..分支` → `git merge 分支` | 验收 → 合并 |

---

## 🎮 闯关任务（3 关）

### 第 1 关 · 第一间工作室
在 eval-practice-house：开 `../eph-lab -b lab` → 进去建个 `lab.txt` 并 commit →
回主工作室 `git log --oneline --graph --all` 找到这条快照 → `git merge lab` →
确认主工作室里出现了 lab.txt → 拆除 + 删分支。
**验收**：能指着 `worktree list` 的输出说出每一行是什么。

### 第 2 关 · 两间并行（手动版工厂）
同时开两间：A 补 README 的"安装"章节，B 补"使用示例"章节（文件范围错开）。
各自 commit 后依次 merge 回 main。
**验收**：两个 README 章节都出现在主工作室，且全程没碰过 stash。

### 第 3 关 · 真·多 AI 工厂（选修，对应 ClaudeCode 第 21 关）
开两间工作室 + 两个终端 + 两个 claude，派两个互不重叠的真实任务
（提示词用第 4 章模板），你只做验收和合并。
**验收**：复盘一句话——哪一步 AI 想偏了/越界了，你在哪一步拦住的。

---

## 通关之后

你已经拥有完整的"并行开发"能力栈：分支（隔离历史）→ stash（临时腾桌）→
worktree（多桌同时开工）→ merge（验收收货）。配合 Claude Code，
"一个指挥官 + 多个 AI 工人"的工厂就是这四块积木搭起来的——
剩下的熟练度，只能在真实项目里练。
