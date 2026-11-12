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
        if g is None and w is None:
            return True      # 描述没提、模型也没提 = 双双正确（"不知道"=="不知道"）
        if g is None or w is None:
            return False     # 一边有一边没有 = 错（该提没提，或不该编却编了）
        return abs(g - w) < 0.01
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
        api_failed = False
        try:
            got = extract_listing(case["text"])
        except Exception:
            time.sleep(2)                     # 失败等 2 秒重试一次
            try:
                got = extract_listing(case["text"])
            except Exception as e:
                api_fail += 1                 # 仍失败：该条 5 字段全记错，但不中断
                api_failed = True
                print(f"  [{i}] API 错误，记 0 分：{e}")
                got = Listing()               # 全 None 的空答题卡

        answer = case["answer"]
        for f in FIELDS:
            g, w = getattr(got, f), answer.get(f)
            # API 挂掉的用例整条记错（防止"全 None 恰好匹配全缺失答案"白捡分）
            ok = field_ok(f, g, w) and not api_failed
            total += 1
            per_field[f][1] += 1
            if ok:
                correct += 1
                per_field[f][0] += 1
            else:
                wrong_list.append((f, g, w, case["text"]))
        print(f"  [{i}/{len(cases)}] 完成")

    # ---------- 报告 1：总体准确率（第 7 课：一个数看全局） ----------
    print("\n===== 报告 1：总体字段准确率 =====")
    print(f"  {correct}/{total} = {correct / total:.0%}")

    # ---------- 报告 2：分项准确率（定位最弱字段，决定第 2 关先修谁） ----------
    print("\n===== 报告 2：分项准确率 =====")
    for f in FIELDS:
        hit, n = per_field[f]
        bar = "█" * round(hit / n * 20)       # 简易进度条，纯装饰
        print(f"  {FIELD_NAMES[f]}: {hit}/{n} = {hit / n:.0%}  {bar}")

    # ---------- 报告 3：错题清单（第 1 关的"病历"，逐条读它） ----------
    print("\n===== 报告 3：错题清单 =====")
    if not wrong_list:
        print("  （全对，没有错题）")
    for f, g, w, text in wrong_list:
        print(f"  [{FIELD_NAMES[f]}] 期望={w!r} 实际={g!r} | {text[:30]}")
    if api_fail:
        print(f"\n  ⚠ 有 {api_fail} 条用例因 API 错误记 0 分，建议重跑一次")


if __name__ == "__main__":
    main()
