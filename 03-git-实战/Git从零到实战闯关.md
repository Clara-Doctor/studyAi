# Git 从零到实战 · 详细教程 + 闯关

> 定位：零基础 Git 教程，重点服务**AI 结对开发**场景（让 Claude Code 改代码之前，你得先会兜底）。
> 呼应：《ClaudeCode深度用法与结对开发闯关.md》第 14 关（Git 是 AI 的后悔药）。
> 环境：Windows + Git Bash（你已经有了——能跑 `git --version` 就行）。
> 建议：先通读第 0~2 章（概念），然后边闯关边查后面的章节。

---

## 第 0 章 · 为什么必须有 Git（5 分钟看懂）

先看没有 Git 的世界有多惨：

```
简历_最终版.docx
简历_最终版2.docx
简历_真最终版.docx
简历_打死不改版.docx     ← 你想回到"最终版2"，但已经分不清哪个是哪个了
```

写代码时更惨：
- 昨天代码还能跑，今天改崩了，**想回到昨天，回不去**
- 想试两种写法，只能复制整个文件夹：`项目-方案A`、`项目-方案B`
- 电脑硬盘坏了 = 几个月心血没了

Git 一口气解决三件事：

| 痛点 | Git 的答案 | 关键命令 |
|---|---|---|
| 改崩了想回退 | **存档系统**（像游戏存档点） | `commit` / `reset` |
| 想同时试两个方案 | **分支**（平行世界） | `branch` / `merge` |
| 怕电脑坏 / 要协作 | **远程仓库**（云端备份） | `push` / `pull` |

一句话记住 Git：**它给项目的每个重要时刻拍快照，你随时可以翻看、回退、分叉任何一张快照。**

---

## 第 1 章 · 安装与初次配置（一次性）

```bash
# 检查装没装（Git Bash 自带）
git --version

# 告诉 Git 你是谁——每次存档都会记下作者名和邮箱（一次性配置）
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"

# 检查配置结果
git config --list
```

> 💡 `--global` 表示"这台电脑所有项目通用"。名字邮箱随便填也行（本地练习不上传的话），
> 但建议认真填——以后推 GitHub 时这就是你的署名。

---

## 第 2 章 · 核心世界观：三个区域（本章最重要）

用**网购收快递**来类比。Git 管理文件有三个区域：

```
┌─────────────┐   git add    ┌─────────────┐  git commit  ┌─────────────┐
│   工作区     │ ──────────→ │   暂存区     │ ──────────→  │   仓库       │
│ (你的书桌)   │   挑出要存的  │ (购物车)     │  封箱存档     │ (档案柜)     │
└─────────────┘              └─────────────┘              └─────────────┘
   你正在改的文件                这次想存哪几个？               永久快照，永不变
```

- **工作区**：你眼睛看到的文件，随便改，改坏了天也不会塌
- **暂存区**：购物车——工作区改了 5 个文件，但这次只想存档其中 2 个，就把那 2 个"加进购物车"
- **仓库**：`commit` 时拍下的**永久快照**，每一张快照有唯一编号，永远可回溯

还有两个高频术语：

- **HEAD** = "你现在站在哪张快照上"（指针，通常指向最新快照）
- **commit（提交）** = 一次存档动作 = 一张快照 = 一个后悔药存档点，**随便打，不花钱**

> 🔑 新手最大的心结："存太多次会不会把项目搞乱？"
> 不会。快照是叠加的，不覆盖旧的；存 1000 次也只是档案柜里多 1000 个贴了标签的盒子。
> **存档永远不嫌多，就像游戏里见到存档点就该存。**

---

## 第 3 章 · 基本功：存档循环

### 3.1 开工：把文件夹变成 Git 仓库

```bash
cd /d/studyAi/eval-practice-house   # 进入任意项目文件夹
git init                             ← 一行命令，当前文件夹变成 Git 仓库
```

`git init` 做的事：在文件夹里建一个隐藏的 `.git/` 子文件夹——**整个档案柜都在这里**。
（不要手贱去改 `.git/` 里的东西；想让 Git 不再管这个项目，删掉它即可。）

### 3.2 每天的循环：改 → 看 → 加 → 存

这 4 条命令是 Git 的"呼吸"，占了日常使用的 90%：

```bash
# ① 改完代码后，先看状态（WHO 动了什么？）
git status

# ② 看具体改了哪几行（可选但强烈建议）
git diff

# ③ 把要存档的文件加进购物车
git add extractor.py        # 加指定文件
git add .                   # 加当前目录全部改动（最常用）

# ④ 封箱存档，-m 后面是这次存档的说明
git commit -m "修复判分器双 null 误判问题"

# 偷懒组合技（熟练后再用）：
git commit -am "说明"   # 自动 add 所有【改过的老文件】再 commit
                        # ⚠️ 帮不了全新文件（Untracked）——陌生人必须显式点名
```

> 💡 新手建议前期老老实实 add、commit 分两步敲，每步跑一次 `git status`
> 看三区变化——肌肉记忆就是这么练的。（IDEA 用户：Commit 窗口勾选文件
> 就是在替你做 add，见文末对照表。）

### 3.3 读懂 git status（它会告诉你下一步干什么）

```
On branch main

Changes to be committed:          ← 已在购物车，commit 后就会存档
        modified:   eval.py

Changes not staged for commit:    ← 改了但还没 add（还在书桌上）
        modified:   extractor.py

Untracked files:                  ← 全新文件，Git 还不认识它
        notes.md
```

`git status` 是**永远可以说"我不知道该干嘛"时万能的第一反应**——它总是告诉你答案。

### 3.4 git diff：找不同

```bash
git diff               # 书桌 vs 购物车：我改了什么还没 add？
git diff --staged      # 购物车 vs 上一张快照：我 add 了什么？
```

输出读法：`-` 开头的红色行 = 删掉的，`+` 开头的绿色行 = 新增的。

### 3.5 git log：翻档案柜

```bash
git log                 # 完整历史（按 q 退出）
git log --oneline       # 一行一条，最常用
git log --oneline --graph --all    # 带分支图，分支多时用
```

每条记录长这样：

```
a1b2c3d (HEAD -> main) 修复判分器双 null 误判问题
e4f5g6h 建立基线：跑通第一版评测
```

- 黄色乱码 `a1b2c3d` = 快照编号（哈希），**写前 7 位就能代表整张快照**
- `HEAD -> main` = 你现在站在这张快照上，它在 main 分支的最新处

### 3.6 Commit message 怎么写

一句话说清"这次为什么存档"。坏例子 vs 好例子：

```
❌ git commit -m "修改"
❌ git commit -m "asdff"
✅ git commit -m "SYSTEM_PROMPT 增加朝向枚举约束，修 10 条朝向错题"
```

> 🔧 动手：在任意文件夹 `git init` → 随便建个文件 → 完整走一遍
> status → add → status（观察变化！）→ commit → log。

### ⚠️ 澄清一个最经典的误解："commit 只对 add 过的文件生效"

不对。**commit 拍的是全家福——快照里永远包含项目所有老文件，一个不缺。**
add 决定的只是：照片里这个文件用**新样子**（add 过）还是**沿用旧样子**（没 add）。

```
快照1 = { a=v1, b=v1 }
改了 a 但没 add 就 commit：
快照2 = { a=v1 ←沿用旧样子！, b=v1 }   ← a 和 b 都在照片里
```

（只有**从没 commit 过的新文件**才进不了照片——那就是 Untracked 状态。）

亲手验证：`echo v1 > a.txt && git add a.txt && git commit -m "v1"` →
`echo v2 > a.txt`（不 add）→ `git commit -m "试试"`（照样成功）→
`git show HEAD`：快照里 a.txt 是 v1（旧样子），而书桌上的 v2 改动还在。

---

## 第 4 章 · .gitignore：存档前先排除垃圾

有些文件**永远不该进档案柜**：密码、临时文件、别人能生成的产物。

在项目根目录建一个名为 `.gitignore` 的文本文件（没有扩展名）：

```gitignore
# Python 项目的典型 .gitignore
__pycache__/        # Python 自动生成的缓存
*.pyc
.env                # 密钥文件！绝对不能提交
reports/            # 程序生成的输出目录

# 通用
*.log
.DS_Store
```

规则很简单：一行一条，`*` 是通配符，`/` 结尾表示文件夹。
（`.gitignore` 自己要提交进仓库——它是给所有人看的规矩。）

> ⚠️ **AI 时代特别注意**：Claude Code 会读项目里所有文件。把 `.env`（API 密钥）
> 写进 `.gitignore` 既是防止泄露到 GitHub，也是给 AI 划禁区。

---

## 第 5 章 · 后悔药全集（本章背下来 = 终身受益）

按"你现在卡在哪一步"对号入座。**先跑 `git status` 确认自己的位置，再选药。**

### 5.1 文件改坏了，还没 add → 丢弃书桌上的改动

```bash
git restore extractor.py      # 把这个文件恢复到上一张快照的样子
```

> 💡 为什么没 add 也能恢复？因为每次 commit 存的是**整个项目的完整快照**，
> 档案柜里本来就躺着每个老文件的上一版完整复印件——restore 只是复印一份盖掉书桌上的。
> **前提：这文件得在上次快照里存在过**（`Changes not staged` 状态）。全新文件
> （`Untracked` 状态）档案柜里没有复印件，restore 管不了，改没了就是真没了。
>
> ⚠️ 这也是唯一一条**找不回来**的后悔药（丢弃的是"还没存档过的改动"），
> 按回车前三思。不确定就先 `git stash`（见 5.5）。

### 5.2 add 错了，还没 commit → 拿出购物车

```bash
git restore --staged extractor.py   # 撤销 add，文件改动本身还在书桌上
```

### 5.3 commit 完想反悔 → 三种 reset

`git reset` = 把 HEAD 指针往回拨。三种模式，**区别在"旧快照之后干的活留不留"**：

```bash
git reset --soft HEAD~1    # 撤销 commit，改动退回【购物车】（想改改说明再存）
git reset --mixed HEAD~1   # 撤销 commit + 撤销 add，改动退回【书桌】(默认模式)
git reset --hard HEAD~1    # 撤销 commit + add + 书桌改动，【彻底回到上一张快照】
```

- `HEAD~1` = 上一张快照（`HEAD~2` = 上上张，也可以直接写编号 `git reset --hard a1b2c3d`）
- 记忆法：**soft 留最多，hard 全扔掉**

> ⚠️ `reset --hard` 会真删工作区文件。**已经 push 到远程的提交不要用 reset**（见 5.4）。

### 5.4 已经推送到远程，想撤销 → revert（安全版）

```bash
git revert a1b2c3d    # 生成一张"反着做"的新快照，抵消指定快照的效果
```

**类比：会计红字冲销。** 账本已经给别人看过了，记错一笔怎么办？
不撕页重写（那别人手里的旧账本就对不上了），而是**补一行红字："第 3 笔作废，冲回"**。
revert 就是自动帮你补这笔红字——把指定快照的改动精确地反着做一遍，
生成一张新快照。历史里谁也没消失（`git log` 能看到"写错的 + 冲销它的"两条），
但最终代码恢复正确。

```
快照A: 写错价格（已 push）
git revert A   →   快照C: 把 A 的改动反着做一遍，效果抵消
历史：A → C，只是追加了 C，原有历史一个字没动
```

reset 是"穿越回去改历史"，revert 是"历史不动，补一张抵消快照"。
**历史已经公开（push 过）就用 revert**：你本地和远程、和同事手里的历史
从此永远一致。而 reset 会把快照从历史里抹掉——同事再 pull 时发现
"我这里有快照 A，你那边怎么没有"，两边历史对不上，协作直接乱套。

> 💡 一句话：**快照没出过门（没 push）→ reset 随便穿越；
> 快照已出门（push 过）→ 只能 revert 补红字。**

### 5.5 改到一半被打断，还不想存档 → stash（先塞抽屉）

**它解决什么麻烦**：你在改 `extractor.py`，改到一半——乱的、跑不起来、
根本不配存档。突然要去修个急 bug（得切分支）。
书桌上摊着烂摊子，怎么切？stash 给三区模型加第四个地点：**抽屉**。

```bash
git stash        # 把书桌上所有改动打包塞进抽屉，书桌瞬间恢复干净
                 #（= 最近一张快照的样子；改动没丢，躺在抽屉里）
# ... 去干急活：切分支、修 bug、commit ...
git stash pop    # 干完回来，把抽屉那包倒回书桌，半成品原样回来
git stash list   # 看抽屉里塞了几包（stash@{0} 是最新一包）
```

生活版：作业写到一半被喊吃饭——作业不算写完，但桌子得腾出来 →
半页作业夹进抽屉，擦干净桌子；吃完饭抽出来接着写。

**stash vs commit 的本质区别**（最容易糊的地方）：

| | commit | stash |
|---|---|---|
| 是什么 | 正式快照 | 临时一包 |
| 进历史吗 | ✅ `git log` 看得到 | ❌ `git log` 看不到 |
| 适合 | 干完的、完整的活 | 干一半的、见不得人的活 |

口诀：**切走之前，书桌必须清空——成品 commit 存档，半成品 stash 塞抽屉。**
（为什么 add 不行？add 只是把改动从书桌挪进购物车——**购物车里也算未存档改动**，
切分支照样被带走/被拦。真正清空书桌的只有两个动作：commit 或 stash。）
⚠️ stash 不进历史，塞久了容易忘——塞了就尽快 pop。

### 5.6 终极保险：reflog（Git 的黑匣子）

误操作把 commit"删"了？只要 commit 过，**90 天内都能救回来**：

```bash
git reflog                  # 列出 HEAD 的所有移动记录（包括你 reset 掉的）
# 找到想回去的那条，比如 a1b2c3d
git reset --hard a1b2c3d    # 瞬间回去
```

> 💡 为什么 Git 删不干净？第 2 章说过：快照只叠加不覆盖。reset 只是"把指针拨走"，
> 快照本体还在档案柜深处躺着，reflog 就是它的寻物启事。

### 5.7 一张表总结

| 我现在的状态 | 用药 |
|---|---|
| 改崩了，没 add，想扔掉改动 | `git restore 文件名` |
| add 错文件 | `git restore --staged 文件名` |
| commit 信息写错了，还没 push | `git commit --amend -m "新信息"`（改最近一张） |
| 想撤最近一次 commit 重新整理 | `git reset --soft HEAD~1` |
| 彻底回到过去某张快照 | `git reset --hard 编号` |
| 已经 push 过，要撤销 | `git revert 编号` |
| 改一半要临时切走 | `git stash` → 干活 → `git stash pop` |
| 好像把什么都搞没了 | 深呼吸 → `git reflog` |

---

## 第 6 章 · 分支：平行世界

### 6.1 是什么

分支 = 从某张快照分岔出去的**平行世界**。互相独立改动，谁也不影响谁：

```
                 ┌── 方案A实验 (feature-a) ──改改改──┐
a ── b ── c ────┤                                    ├── 合并
                 └── 方案B实验 (feature-b) ──改改改──┘
        ↑
      main（主线，永远保持"能跑"状态）
```

**AI 时代的核心用法**：让 Claude Code 在分支上实验——成了就合并，砸了就删分支，
main 主线从头到尾没被污染。这就是"敢让 AI 乱试"的底气。

> 📚 想让多个分支**同时活着**（多 AI 并行、同时跑两个方案）？那是进阶篇的事：
> 见《GitWorktree详解教程.md》。

### 6.2 基本操作

```bash
git branch                       # 列出所有分支（* 标出你所在的）
git switch -c feature-orient     # 创建并进入新分支 feature-orient
git switch main                  # 切回主线
git branch -d feature-orient     # 删掉已合并的分支（-D 强删未合并的）
```

> 💡 老教程里是 `git checkout -c` / `git checkout main`——同一个功能，
> `switch` 是新命令、语义更清晰，用哪个都行。

在分支上照常干活：改 → `add` → `commit`（流程和第 3 章一模一样，只是存进了平行世界）。

### 6.3 合并：把分支的成果带回家

```bash
git switch main          # ① 先站到"接受合并"的一方
git merge feature-orient # ② 把 feature-orient 的改动合并进来
```

最理想的情况叫 **fast-forward**：主线在分岔后没动过，直接把指针快进到分支头部，无任何冲突。

### 6.4 冲突：两个人改了同一处（必经历一次才懂）

如果 main 和分支**改了同一个文件的同一处**，merge 时会停下报错：

```
<<<<<<< HEAD
orientation 只能取：东/南/西/北/南北        ← main（当前分支）的版本
=======
orientation 统一转换为小写                   ← feature-orient 分支的版本
>>>>>>> feature-orient
```

解决四步（Git 不敢替你做决定，**人工裁决**）：

```bash
# ① 打开冲突文件，找到 <<<<<<< 到 >>>>>>> 的冲突块
# ② 手工编辑：留下正确版本（或融合两者），删掉 <<<<<<<、=======、>>>>>>> 标记行
# ③ 标记"我解决完了"
git add 冲突文件
# ④ 完成合并
git commit
```

中途后悔想放弃合并：`git merge --abort`，一切回到 merge 之前。

---

## 第 7 章 · 远程仓库：云端备份与协作

### 7.1 概念

- **远程仓库（remote）**：放在 GitHub / Gitee 等服务器上的仓库副本
- **origin**：远程仓库的默认代号（就是个名字，约定俗成）
- `push` = 本地 → 云端（上传新快照）；`pull` = 云端 → 本地（下载新快照）

```
你的电脑（本地仓库） ──push──→ GitHub（origin）
你的电脑（本地仓库） ←──pull── GitHub（origin）
```

### 7.2 GitHub 建仓 + 首次推送（走一遍）

1. 注册/登录 github.com → 右上角 **+** → **New repository**
2. 起名（如 `eval-practice-house`），**不要**勾选 README（本地已有），Create
3. 回到 Git Bash，按 GitHub 页面提示执行：

```bash
git remote add origin https://github.com/你的用户名/eval-practice-house.git
git push -u origin main
```

- 第一次 push 会弹认证：浏览器登录 GitHub 授权即可（Windows 凭据管理器会记住）
- `-u` 只在第一次需要：建立"本地 main ↔ 远程 main"的绑定，以后直接 `git push`

### 7.3 日常三件套与克隆

```bash
git push              # 上传
git pull              # 下载并合并（= fetch + merge）
git fetch             # 只下载不合并——先看看远程更新了啥再决定
git clone https://github.com/用户名/仓库.git   # 把别人的仓库完整复制到本地（含全部历史）
```

> `fetch` vs `pull`：pull 是"快递直接拆箱上架"，fetch 是"快递先放门口，看看是什么再拆"。
> 多人协作时先 fetch 看一眼更稳。

---

## 第 8 章 · 团队协作流程（30 秒概念版）

单人 + AI 开发其实用不到多人协作，但面试和入职第一周会问，记这个模型：

1. `main` 分支永远保持能跑、能上线
2. 每个新功能开一个 feature 分支：`git switch -c feature-xxx`
3. 在分支上开发、存档、push
4. 发起 **Pull Request（PR）**：在 GitHub 上"请求把我的分支合进 main"，队友审查代码、讨论、通过后合并
5. 合并后删除 feature 分支

PR 的本质：**合并之前强制过一道"人审代码"的关卡**——AI 时代这一步反而更重要了。

---

## 第 9 章 · AI 时代的 Git 军规 ⭐（本教程的最终目的）

你正在用 Claude Code 这类"一秒改十个文件"的工具，Git 的用法重心变了：

| # | 军规 | 为什么 |
|---|---|---|
| 1 | **让 AI 动手前，先 commit** | 存好档再让 AI 乱来；改崩了一句 `git reset --hard` 回到改造前 |
| 2 | **AI 说做完了，先 `git diff` 亲自过目** | diff 是最小单位的"审查"：AI 到底改了哪几行，一目了然 |
| 3 | **实验开分支，验证通过再合并** | 两个提示词方案 → 两条分支各跑一遍 eval → 好的那个 merge 回 main |
| 4 | **一个 commit = 一件完整的小事** | 方便定位"哪次改动引入了 bug"，也方便 revert |
| 5 | **push 到远程才算备份** | 本地 commit 只防"改崩"，push 才防"硬盘崩" |

对应实战：《ClaudeCode深度用法与结对开发闯关.md》第 14 关 + 毕业项目全流程。

---

## 第 10 章 · 翻车急救决策表

``我出事了，现在怎么办''：

- **我不敢动了，先保命** → `git stash`（把现场封起来， 世界恢复干净）
- **AI 刚改完，我想全部退回改动前** → `git reset --hard`（前提：改之前 commit 过！军规 1）
- **只想要某一个文件回到过去** → `git restore 文件名`
- **我 commit 了不该 commit 的东西**（如密码）→ `git reset --soft HEAD~1` → 修好 .gitignore → 重新 add/commit
- **我 reset --hard 扔多了** → `git reflog` → `git reset --hard 编号`
- **merge 冲突看不懂** → `git merge --abort` 逃跑，喝口水再来
- **分支删错了** → `git reflog` 找到编号 → `git branch 分支名 编号` 复活
- **push 被拒（remote 报错）** → 先 `git pull` 再 `git push`

---

## 第 11 章 · 命令速查表

| 分类 | 命令 | 作用 |
|---|---|---|
| 配置 | `git config --global user.name "x"` | 设置署名（一次） |
| 开仓 | `git init` / `git clone 地址` | 新建仓库 / 复制远程仓库 |
| 日常 | `git status` | 看状态（万能第一步） |
| 日常 | `git add 文件` / `git add .` | 加进购物车 |
| 日常 | `git commit -m "说明"` | 存档 |
| 查看 | `git diff` / `git diff --staged` | 书桌 vs 购物车 / 购物车 vs 快照 |
| 查看 | `git log --oneline --graph --all` | 历史 + 分支图 |
| 后悔 | `git restore 文件` | 丢弃书桌改动 |
| 后悔 | `git restore --staged 文件` | 撤销 add |
| 后悔 | `git reset --soft/mixed/hard HEAD~1` | 撤销 commit（留购物车/留书桌/全扔） |
| 后悔 | `git revert 编号` | 用新快照抵消旧快照（push 后用这个） |
| 后悔 | `git stash` / `git stash pop` | 塞抽屉 / 倒回来 |
| 保命 | `git reflog` | 黑匣子，救回一切 commit 过的东西 |
| 分支 | `git branch` / `git switch -c 名` / `git switch main` | 查看 / 新建进入 / 切换 |
| 分支 | `git merge 分支名` | 合并（冲突手改后 add + commit） |
| 分支 | `git branch -d 名` | 删分支 |
| 远程 | `git remote add origin 地址` | 绑定远程（一次） |
| 远程 | `git push -u origin main`（首次）/ `git push` | 上传 |
| 远程 | `git pull` / `git fetch` | 下载合并 / 只下载 |

---

## 附 · IDEA 用户对照表

> 在 IDEA 里"从没操作过 add"？因为 IDEA 把 add+commit 合并成了一步：
> **Commit 窗口里勾选文件的动作就是 add**，点按钮时它自动替你执行。
> IDEA 只是遥控器，底层干活的从来都是同一个 Git。

| 你在 IDEA 里做的 | 底层命令 |
|---|---|
| Commit 窗口勾选部分文件 | `git add 勾选的文件` |
| 点 Commit 按钮 | `git commit`（没勾的文件在快照里沿用旧样子） |
| 文件右键 Rollback | `git restore 文件` |
| Show Diff | `git diff` |
| Shelve / Unshelve | 类似 `git stash` / `git stash pop` |
| Git → New Branch / Checkout | `git branch` / `git switch` |
| Git → Annotate（行尾看作者） | `git blame` |

（想和命令行完全一致：Settings → Version Control → 勾 "Enable staging area"，
但默认不开更顺手。）

---

## 🎮 闯关任务（6 关，全部在 `eval-practice-house` 上实操）

### 第 1 关 · 建仓
`cd` 进项目 → `git init` → 建好 `.gitignore`（至少排除 `__pycache__/` 和 `.env`）→
首次 commit。
**验收**：`git log` 能看到第一条记录。

### 第 2 关 · 存档循环体感
随便改一个文件，**每一步都跑 `git status`**：改完看一次 → `add` 后看一次 →
`commit` 后再看一次。用 `git diff` 和 `git diff --staged` 各看一次。
**验收**：能用购物车类比说出三个区域各自的文件长什么样。

### 第 3 关 · 后悔药全都试一遍（在测试文件上）
建 `test.txt`：① 改坏它 → `restore` 救回；② `add` 后撤销 add；
③ commit 后 `reset --soft HEAD~1` 再重新 commit；④ 改一半 `stash` 再 `pop`。
**验收**：能背出"改崩了没 add"和"commit 完想反悔"各用什么命令。

### 第 4 关 · 分支 A/B 实验 ⭐
`git switch -c experiment` → 让 Claude Code 在这个分支上改一版 SYSTEM_PROMPT →
自己跑 `python -X utf8 eval.py` → 分数好：`git switch main` + `merge`；
分数差：`git switch main` + `git branch -D experiment`。
**验收**：亲身体验"AI 乱试零风险"——main 全程没被动过。

### 第 5 关 · 手工制造并解决一次冲突
开两个分支各改 `README.md` 的**同一行**，merge 制造冲突，手改解决。
**验收**：看到 `<<<<<<<` 不再心慌，知道四步流程。

### 第 6 关 · 推上 GitHub（选修，需注册账号）
按第 7 章走完整流程：建远程仓 → 绑 origin → push。
**验收**：刷新 GitHub 网页能看到你的代码；从此硬盘坏了也不怕。

---

## 通关之后

你已具备"敢让 AI 大刀阔斧改代码"的安全网。下一步把军规融入习惯：
**每次开 Claude Code 干活，第一反应是 `git status`，动手前 `commit`，干完看 `diff`。**
这三连做满一周，Git 就长在你手上了。
