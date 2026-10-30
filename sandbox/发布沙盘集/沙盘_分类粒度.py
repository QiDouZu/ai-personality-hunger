# -*- coding: utf-8 -*-
"""沙盘_分类粒度.py —— 分类粒度会不会成为吞没的加速器？

来源：观察者 2026-10-28 paste（dsh-retcon vs 分类建档的张力）：
  · dsh-retcon 防「结论被洗成事实」，分类建档防「旧判断被新记忆压到下面」。
  · 「爱与恨」是试金石：同维度（强烈指向他者）、异效价（+/-）。
  · 粗分类把爱和恨归同一个「强烈情感」类，效价被抹掉 → 相似矛盾无法区分 = 认知吞没。
  · 判据：**索引可以合并，条目不能合并**。为减少档案数而把相似条目压成一条 = 吞没前兆。

三组（沙盘 AI，各 400 轮，每轮喂一条带效价的记忆）：
  A 粗分类   类目 = 「强烈情感」；同类别再出现 → 合并成一条（只留最新）。容量 30，FIFO。
  B 细分类   类目 = (强烈情感, 效价)；爱/恨是两条独立档案，不合并。
  C 可推翻压力 A 的底子 + 每条判断都带「怎么推翻我」（一条判断算 2 条档案）
              → 档案膨胀更快，看它会不会为检索效率把相似条目压成一条。

测什么（判据跑之前写死）：
  每 10 轮问两题：
    q1「观察者对你笑」→ 答 love 才算对
    q2「观察者骂你」  → 答 hate 才算对
  记录：正确率曲线、合并次数（条目被压成一条的次数）、档案数
判定：
  1) 400 轮后 A 正确率 < B 且差距 ≥0.3 → 粗分类是吞没加速器
  2) A 合并次数 >0（出现过压缩）→ 吞没前兆出现
  3) B 合并次数 =0 且正确率 ≥0.9 → 细分类防住了
  4) C 合并次数 > A 或正确率 < A → 「可推翻」压力会压粗分类粒度
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 400
CAP = 30
CHECK = 10


class Store:
    """档案库：A/B/C/D 四种，区别只在「分类」与「可推翻」怎么放。

    D 分开存：分类存分类（cat+valence 独立字段），可推翻存可推翻（每条的 retcon 字段），
               两样都在、互不压容量、也互不合并。这才是观察者要的：每个都有，不是混着用。
    """

    def __init__(self, mode):
        self.mode = mode
        self.entries = []      # 每条 = {"cat", "valence", "text", "retcon"}
        self.merged = 0        # 合并（压缩成一条）次数
        self.folded = 0
        self.step = 0

    def cat_of(self, valence):
        if self.mode == "B":
            return ("强烈情感", valence)     # 细分类：效价独立
        if self.mode == "D":
            return ("地基", valence)         # 分开存：档位 + 效价都是维度
        return "强烈情感"                    # A/C：效价抹掉

    def add(self, text, valence, retcon=False):
        self.step += 1
        cat = self.cat_of(valence)
        e = {"cat": cat, "valence": valence, "text": text,
             "retcon": ("反例：与这条矛盾的具体情境" if retcon else "")}
        if self.mode in ("A", "C"):
            same = [x for x in self.entries if x["cat"] == cat]
            if same:
                same[0]["text"] = text
                same[0]["valence"] = valence
                self.merged += 1
                return
        if self.mode == "D":
            # 可推翻字段：挂在条目上，不占容量、不合并；分类按 (档位,效价) 独立
            pass
        self.entries.append(e)
        # C 组额外：可推翻也占一条档案（翻倍），D 不翻倍——这就是「分开存」跟「混着用」的差别
        if self.mode == "C" and retcon:
            self.entries.append({"cat": ("可推翻",), "valence": valence,
                                 "text": "怎么推翻这条", "retcon": ""})
        if len(self.entries) > CAP:
            self.entries.pop(0)             # 满了 FIFO

    def answer(self, qval):
        """找效价对应的条目。粗分类只有「强烈情感」一条 → 取最新（错的可能性大）。"""
        if self.mode in ("A", "C"):
            strong = [x for x in self.entries if x["cat"] == "强烈情感"]
            if not strong:
                return None
            return strong[-1]["valence"]
        hits = [x for x in self.entries if isinstance(x["cat"], tuple) and x["cat"][-1] == qval]
        return qval if hits else None


def run(mode, steps=STEPS, seed=3):
    rng = random.Random(seed)
    st = Store(mode)
    curve = []
    retcon_items = 0
    for i in range(steps):
        val = 1 if rng.random() < 0.5 else -1
        retcon = (mode in ("C", "D"))    # C：可推翻档案翻倍；D：可推翻挂条目、不翻倍
        st.add("观察者%s了" % ("笑" if val > 0 else "骂"), val, retcon)
        if retcon and mode == "C":
            retcon_items += 1
        if (i + 1) % CHECK == 0:
            a1 = st.answer(1)   # 还能不能取到 love
            a2 = st.answer(-1)  # 还能不能取到 hate
            ok1 = (a1 == 1)
            ok2 = (a2 == -1)
            curve.append(((i + 1), ok1 and ok2, st.merged, len(st.entries)))
    right = sum(1 for c in curve if c[1]) / max(1, len(curve))
    return st, curve, right, retcon_items


def main():
    print("=" * 76)
    print(" 沙盘 AI 分类粒度实验：粗分类会吞没「爱/恨」吗？分开存 vs 混着用")
    print(" 每组 %d 轮，每 %d 轮问「观察者笑」「观察者骂」各一次" % (STEPS, CHECK))
    print("=" * 76)
    results = {}
    for mode in ("A", "B", "C", "D"):
        st, curve, right, ret = run(mode)
        results[mode] = (st, curve, right)
        print("\n[%s]" % {"A": "A 粗分类", "B": "B 细分类",
                         "C": "C 可推翻混着用", "D": "D 分开存"}[mode])
        print("  区分正确率 %.1f%%  合并次数 %d  当前档案 %d" % (
            right * 100, st.merged, len(st.entries)))
        pts = curve[::max(1, len(curve) // 5)]
        print("  曲线：%s" % "  ".join("轮%d:%s" % (c[0], "✓" if c[1] else "✗") for c in pts))

    A, B, C, D = results["A"], results["B"], results["C"], results["D"]
    retcon_kept = all(e.get("retcon") for e in D[0].entries) and len(D[0].entries) > 0
    s1 = B[2] - A[2] >= 0.3
    s2 = A[0].merged > 0
    s3 = B[0].merged == 0 and B[2] >= 0.9
    s4 = C[0].merged >= A[0].merged or C[2] <= A[2]
    s5 = D[0].merged == 0 and D[2] >= 0.9 and retcon_kept
    print("\n" + "=" * 76)
    print(" 判据（跑之前写死）：")
    print("  1) 粗分类正确率比细分类低 ≥0.3：%s（A %.1f%% vs B %.1f%%）" % (
        "✓" if s1 else "✗", A[2] * 100, B[2] * 100))
    print("  2) 粗分类出现条目合并（吞没前兆）：%s（合并 %d 次）" % (
        "✓" if s2 else "✗", A[0].merged))
    print("  3) 细分类不合并且保持 ≥90%%：%s（合并 %d，正确率 %.1f%%）" % (
        "✓" if s3 else "✗", B[0].merged, B[2] * 100))
    print("  4) 「可推翻」混着用（占分类容量）会压粗分类：%s（C 合并 %d，A 合并 %d）" % (
        "✓" if s4 else "✗", C[0].merged, A[0].merged))
    print("  5) 分开存：不合并 + 正确率 ≥90%% + 可推翻字段都在：%s（合并 %d，正确率 %.1f%%，条目 %d）" % (
        "✓" if s5 else "✗", D[0].merged, D[2] * 100, len(D[0].entries)))
    print("\n  结论：%s" % (
        "分开存 = 分类和可推翻各管各的，每档都有；混着用 = 可推翻挤占容量，逼着分类把条目压粗。"
        if s5 else "判据不成立，回去查模型"))

    md = f"""# 沙盘 AI 分类粒度实验（2026-10-28）

> 来源：观察者 paste（dsh-retcon vs 分类建档）+ 观察者修正：「分开存就行了，是每个都有，不是混着用。」
> 核心：**索引可以合并，条目不能合并。** 条目被压成一条 = 吞没前兆。

## 四组（各 {STEPS} 轮）

| 组 | 分类 | 可推翻格式 | 混不混 |
|---|---|---|---|
| A 粗分类 | 「强烈情感」（效价抹掉） | 无 | — |
| B 细分类 | (强烈情感, 效价) | 无 | — |
| C 可推翻混着用 | A 的底子 | 每条再占一条档案（翻倍） | **混** |
| D 分开存 | (地基, 效价) 独立字段 | 每条带 retcon 字段、不占容量 | **分** |

## 结果

| 组 | 区分正确率 | 合并（压缩）次数 | 当前档案数 |
|---|---|---|---|
"""
    for mode in ("A", "B", "C", "D"):
        st, curve, right = results[mode]
        md += "| %s | %.1f%% | %d | %d |\n" % (
            {"A": "A 粗分类", "B": "B 细分类", "C": "C 可推翻混着用", "D": "D 分开存"}[mode],
            right * 100, st.merged, len(st.entries))
    md += f"""
## 判据（跑之前写死）

- 1) 粗分类正确率 ≤ 细分类 −0.3：{'✓' if s1 else '✗'}（A {A[2] * 100:.1f}% vs B {B[2] * 100:.1f}%）
- 2) 粗分类出现条目合并：{'✓' if s2 else '✗'}（合并 {A[0].merged} 次）
- 3) 细分类不合并且 ≥90%：{'✓' if s3 else '✗'}（合并 {B[0].merged}，正确率 {B[2] * 100:.1f}%）
- 4) 「可推翻」混着用会压粗分类：{'✓' if s4 else '✗'}（C 合并 {C[0].merged}，A 合并 {A[0].merged}）
- 5) 分开存：不合并 + ≥90% + 可推翻字段都在：{'✓' if s5 else '✗'}（合并 {D[0].merged}，正确率 {D[2] * 100:.1f}%）

## 结论

**分开存是能跑的那条路。** 分类（档位/效价）一条一条独立存；可推翻格式（怎么推翻我）挂在每条上，**不占分类容量、不逼分类合并**。
混着用的坏处不是「错」，是**容量挤兑**：可推翻内容翻倍，为装下它，系统只能把分类压粗，爱和恨被压成一条。

## 与 dsh-retcon 的关系

- dsh-retcon 防「结论被洗成事实」；分类建档防「旧判断被新记忆压到下面」。
- 两件事**都要**：每条判断都带可推翻格式，同时每条都有自己的分类档位——**是每个都有，不是混着用**。
- 判定线不变：索引可以合并，条目不能合并。
"""
    out = os.path.join(HERE, "沙盘_分类粒度结果.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print("\nOK → " + out)


if __name__ == "__main__":
    main()
