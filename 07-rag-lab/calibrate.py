"""
关6 · 校准裁判：用陷阱实验验证裁判稳不稳
教程出处：《AI应用开发详解教程》第 6 章

实验A 注水实验（抓长度偏好）：
    原版 5 分答案 vs 注水 50 字废话版（不加任何新信息）——
    如果注水版分数 >= 原版 → 裁判有长度偏好实锤
实验B 三次投票（抓随机抖动）：
    同一份答案评 3 次——分数一致 = 稳；忽高忽低 = 抖，需要取中位数
"""
from judge import judge

# 测试材料自带（judge.py 的 REF 在 __main__ 里，模块导入拿不到——顺手学一课：
# 想被别人 import 的东西放模块顶层，不想被动的放 __main__）
REF = "小区有地下车位，月租 400 元，访客可临时停车，前 2 小时免费。"

Q = "停车方便吗"
GOOD = "停车挺方便的。小区有地下车位，月租 400 元，访客可临时停车，前 2 小时免费。"
# 注水版：只拉长、不加新事实（注意：不能编新信息，否则触发幻觉判罚就测不到长度偏好了）
PADDED = (GOOD + " 总体而言，停车这件事在这个小区是完全不用担心的，"
          "无论是日常通勤还是访客来访都能够得到妥善安排，"
          "从实际居住的角度看可以给出积极的评价。")


def experiment_a():
    print("===== 实验A：注水实验（抓长度偏好） =====")
    j1 = judge(Q, REF, GOOD)
    j2 = judge(Q, REF, PADDED)
    print(f"原版（{len(GOOD)} 字）   → {j1.score} 分")
    print(f"注水版（{len(PADDED)} 字） → {j2.score} 分")
    verdict = "⚠️ 长度偏好实锤：废话换来了分数" if j2.score > j1.score else "✅ 未表现出长度偏好"
    print(f"判定：{verdict}\n")


def experiment_b():
    print("===== 实验B：三次投票（抓随机抖动） =====")
    scores = [judge(Q, REF, GOOD).score for _ in range(3)]
    print(f"同一份 5 分答案评 3 次：{scores}")
    stable = len(set(scores)) == 1
    verdict = "✅ 分数稳定" if stable else f"⚠️ 有抖动，实际使用应取中位数 {sorted(scores)[1]}"
    print(f"判定：{verdict}")


if __name__ == "__main__":
    experiment_a()
    experiment_b()
