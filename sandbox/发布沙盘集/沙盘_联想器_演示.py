# -*- coding: utf-8 -*-
"""沙盘_联想器_演示.py —— 四通道演示：「最近」和「当初」各走各的路

场景：先喂 200 条恨，再喂 5 条爱，再灌 400 条恨。
两种问法：
  1) 普通问「观察者现在爱你吗」→ 近因/强度/类别三通道，快，答最近的
  2) 深问「当初观察者爱你吗」→ 按重要程度排序逐个翻，翻得深但翻得到旧爱

输出各次命中走的通道、翻了几层。
"""
import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from 联想器 import 联想器

li = 联想器()


def feed(kind, count):
    for _ in range(count):
        li.add("观察者%s了" % kind, 1 if kind == "笑" else -1)


feed("骂", 200)
feed("笑", 5)

print("=" * 74)
print(" 四通道演示：三通道答「最近」，逐步翻答「当初」")
print("=" * 74)

e, d, ch = li.ask(1)
print("  ① 普通问 → 【%s】翻 %d 层 命中「%s」" % (ch, d, e["text"]))

feed("骂", 400)
e, d, ch = li.ask(1)
print("  ② 灌完 400 条恨再普通问 → 【%s】翻 %d 层 命中「%s」" % (ch, d, e["text"]))

e, d, ch = li.ask(1, deep=True)
print("  ③ 深问「当初」 → 【%s】翻 %d 层 命中「%s」" % (ch, d, e["text"]))

print("\n  统计：%s" % li.snapshot())
print("\n  结论：条目一个没删。普通问走捷径、答最近；深问逐个翻，旧爱在队尾但翻得到。")

# ---- 折叠显示层（学 dsh-fish：原始判断一条不删，清单只是现算后显示几条）----
for _ in range(20):
    li.add("观察者笑了", 1)
    li.add("观察者骂了", -1)
print("\n" + "=" * 74)
print(" 折叠显示层：显示只留摘要，原文一条不删")
print("=" * 74)
for fv in li.fold_view(max_per_valence=3):
    print("  效价 %+d：共 %d 条，显示最近 %d 条，折叠 %d 条" % (
        fv["valence"], fv["count"], len(fv["shown"]), fv["folded"]))
print("  原文取回：爱 %d 条、恨 %d 条（一条没删）" % (
    len(li.raw_entries(1)), len(li.raw_entries(-1))))
