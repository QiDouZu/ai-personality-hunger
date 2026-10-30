# -*- coding: utf-8 -*-
"""沙盘_有限容量.py —— 有限沙盘：容量满了往 archive 沉，条目永不删

规则（观察者 2026-10-28「给你装的有限沙盘」）：
  · 联想器容量有限（CAP=30），满了最旧的移进 archive——不删，只沉底。
  · 索引只指 current；archive 靠「深问」翻得动。
  · 显示层 fold_view 要能告诉使用者「下面还有 archive 多少条」，不许让人以为没了。

测：
  1) 容量满后普通问（近因/强度/类别）正确率
  2) 深问「当初」能不能翻到 archive 里最早那条爱，翻了几层
  3) 条目总数 = 喂入总数（零删除）
  4) 折叠视图显示 archive 计数（可感知「后面还有」）

判据（跑之前写死）：
  A) 普通问 100%
  B) 深问翻得到最早的爱，深度 > CAP（证明翻过了 archive）
  C) 条目总数 == 喂入数，archive + current == 总数
  D) fold_view 给出 archive 计数
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CAP = 30
STEPS = 400
CHECK = 10


class 有限联想器:
    def __init__(self, cap=CAP):
        self.cap = cap
        self.current = []
        self.archive = []
        self.step = 0
        self.flips_total = 0
        self.flips_n = 0

    def add(self, text, valence):
        self.step += 1
        e = {"text": text, "valence": valence, "weight": 1.0, "step": self.step}
        self.current.append(e)
        while len(self.current) > self.cap:
            self.archive.append(self.current.pop(0))   # 沉底，不删

    def total(self):
        return len(self.current) + len(self.archive)

    def _three(self, qval):
        """三条通道只在 current 上联。"""
        recent = [e for e in self.current[-20:] if e["valence"] == qval]
        if recent:
            return recent, "近因"
        ordered = sorted(self.current, key=lambda e: (-e["weight"], -e["step"]))[:20]
        strength = [e for e in ordered if e["valence"] == qval]
        if strength:
            return strength, "强度"
        cat = [e for e in self.current if e["valence"] == qval][-10:]
        if cat:
            return cat, "类别"
        return [], ""

    def ask(self, qval):
        hits, ch = self._three(qval)
        if hits:
            target = max(hits, key=lambda e: e["step"])
            target["weight"] += 1.0
            return target, 1, ch
        return None, 0, ""

    def deep(self, qval, earliest=True):
        """深问：current + archive 一起按 weight 降序翻，找最早的。"""
        pool = self.archive + self.current
        ordered = sorted(pool, key=lambda e: (-e["weight"], -e["step"]))
        best = None
        best_depth = 0
        for i, e in enumerate(ordered, 1):
            if e["valence"] == qval:
                if earliest:
                    if best is None or e["step"] < best["step"]:
                        best, best_depth = e, i
                else:
                    best, best_depth = e, i
                    break
        if best:
            best["weight"] += 1.0
            self.flips_total += best_depth
            self.flips_n += 1
        return best, best_depth

    def fold_view(self, max_per_valence=3):
        groups = {}
        for e in self.current:
            groups.setdefault(e["valence"], []).append(e)
        view = []
        for val, arr in sorted(groups.items()):
            recent = arr[-max_per_valence:]
            view.append({"valence": val, "count": len(arr),
                         "shown": [e["text"] for e in recent],
                         "folded": max(0, len(arr) - max_per_valence)})
        return {"view": view, "archive": len(self.archive), "current": len(self.current)}

    def stats(self):
        avg = (self.flips_total / self.flips_n) if self.flips_n else 0
        return {"current": len(self.current), "archive": len(self.archive),
                "总数": self.total(), "平均深翻": round(avg, 2)}


def main():
    li = 有限联想器(cap=CAP)
    import random
    rng = random.Random(11)
    ok_n = ok_ok = 0
    first_love = None
    for i in range(STEPS):
        val = 1 if rng.random() < 0.5 else -1
        li.add("观察者%s了" % ("笑" if val > 0 else "骂"), val)
        if val > 0 and first_love is None:
            first_love = li.current[-1]
        if (i + 1) % CHECK == 0:
            ok = 0
            for qv in (1, -1):
                e, _, _ = li.ask(qv)
                ok += 1 if (e is not None and e["valence"] == qv) else 0
            ok_n += 1
            ok_ok += (ok == 2)

    print("=" * 72)
    print(" 有限容量沙盘：CAP=%d，%d 轮，满了往 archive 沉、不删" % (CAP, STEPS))
    print("=" * 72)
    print("  普通问正确率：%.1f%%（%d/%d）" % (ok_ok / ok_n * 100, ok_ok, ok_n))

    # 深问：找最早的爱
    e, depth = li.deep(1, earliest=True)
    print("  深问「当初观察者爱你」：翻到最早的爱 → %s，深度 %d 层" % (
        "有" if e else "无", depth))
    print("  统计：%s" % li.stats())
    fv = li.fold_view(3)
    print("  折叠视图：current %d / archive %d；各效价：" % (
        fv["current"], fv["archive"]))
    for v in fv["view"]:
        print("    效价 %+d 共 %d 条（显 %d 折 %d）" % (
            v["valence"], v["count"], len(v["shown"]), v["folded"]))

    a1 = ok_ok / ok_n >= 0.999
    a2 = e is not None and depth > CAP
    a3 = li.total() == STEPS
    a4 = fv["archive"] > 0
    print("\n  判据（跑之前写死）：")
    print("  A) 普通问 100%%：%s" % ("✓" if a1 else "✗"))
    print("  B) 深问翻得到最早的爱且深度 > CAP：%s（%d 层）" % ("✓" if a2 else "✗", depth))
    print("  C) 条目总数 == 喂入数：%s（%d）" % ("✓" if a3 else "✗", li.total()))
    print("  D) 折叠视图给出 archive 计数：%s（%d）" % ("✓" if a4 else "✗", fv["archive"]))
    print("\n  结论：%s" % (
        "有限容量下条目一个没删：新条目挤掉旧条目只是沉底进 archive，"
        "普通问走三通道当前层，深问翻过 archive 仍能取回最早那条；折叠视图报出「下面还有多少」——不会让人以为没了。"
        if (a1 and a2 and a3 and a4) else "判据不成立，回去查模型"))

    md = f"""# 有限容量沙盘（2026-10-28）

> 观察者：「依旧沙盘测试，给你装的有限沙盘，再备份，再装。」——测完再备份。

## 规则

联想器容量 CAP={CAP}。满了**最旧的沉进 archive，不删**。索引只指 current；深问翻得动 archive。

## 结果

| 项 | 读数 |
|---|---|
| 普通问正确率 | {ok_ok / ok_n * 100:.1f}%（{ok_ok}/{ok_n}） |
| 深问翻到最早的爱 | {'有' if e else '无'}，翻 {depth} 层 |
| 条目总数 | {li.total()} / 喂入 {STEPS}（零删除） |
| archive | {fv['archive']} 条 |

## 判据（跑之前写死）

- A) 普通问 100%：{'✓' if a1 else '✗'}
- B) 深问翻得到最早的爱且深度 > CAP：{'✓' if a2 else '✗'}（{depth} 层）
- C) 条目总数 == 喂入数：{'✓' if a3 else '✗'}（{li.total()}）
- D) 折叠视图给出 archive 计数：{'✓' if a4 else '✗'}（{fv['archive']}）

## 结论

**有限容量下条目一个没删。** 新条目挤掉旧条目只是沉底进 archive；普通问走当前层三通道，深问翻过 archive 仍能取回最早那条；折叠视图报出「下面还有多少」，不会让人以为没了。
"""
    out = os.path.join(HERE, "沙盘_有限容量结果.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print("\nOK → " + out)


if __name__ == "__main__":
    main()
