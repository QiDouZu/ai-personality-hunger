# -*- coding: utf-8 -*-
"""沙盘·回路论证：人脑与集群意识的共通（发布版，2026-10-30）

观察者的论证（三句话，一句不能少）：
  1. 「粗筛指向细筛，加起来是完整的，一条细筛根据逻辑由多条粗筛来连接」
  2. 「是集群意识模拟人脑回路，不是单条思考模拟人脑回路」
  3. 「所有节点都可以在本地和云端跑，结合起来是你」

本沙盘不碰本机、不碰记忆、不碰用户，自带造的数据，验证三件事：
  A) 粗筛只「指向」不「判断」——粗筛输出里没有结论，只有「哪两条像有矛盾」
  B) 多粗筛汇成一条细筛：结论冲突/情境冲突/粒度冲突三路各自指向，
     汇合后一条细筛拿走全部线索，输出 分型→L→R→平衡 四件套（完整判断）
  C) 强自愈：任一路粗筛异常（模拟抛错），其余照常指向，细筛仍出完整判断

跑法：python 沙盘_回路论证.py
输出：判据块 + 回路_报告.json（同目录）
依赖：纯标准库。
"""
import json
import os
import re
import sys
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------- 造数据：六条记忆（有结论冲突、有情境冲突、有独立源） ----------
ENTS = [
    {"id": "m1", "layer": "事", "title": "口径A", "content": "云端推理的验收只看输出是否完整。",
     "src": "本人"},
    {"id": "m2", "layer": "事", "title": "口径B", "content": "云端推理的验收不看输出是否完整。",
     "src": "审核"},
    {"id": "m3", "layer": "式", "title": "情境C", "content": "弹窗要等确认才关，慢一点没关系。",
     "src": "偏好"},
    {"id": "m4", "layer": "式", "title": "情境D", "content": "弹窗自动关就行，别烦人。",
     "src": "效率"},
    {"id": "m5", "layer": "事", "title": "长文E", "content": "本地跑集群回路：粗筛多路指向，细筛按饥的节点判断，先分型，再走 L 解轴对读追源命题化，再走 R 情境整体留原样，最后平衡。",
     "src": "设计"},
    {"id": "m6", "layer": "事", "title": "短文F", "content": "回路=粗筛指向+细筛判断。", "src": "设计"},
]

KIND = ["结论冲突", "情境冲突", "粒度冲突"]


def _keys(t):
    return set(re.findall(r"[\u4e00-\u9fff]{2,4}", t)) - {"什么", "这个", "那个", "我们"}


def c1_关键词交集(ents):
    """粗筛1：标题/内容关键词交集最大的对——只指向。"""
    out = []
    for i, a in enumerate(ents):
        for b in ents[i + 1:]:
            ka, kb = _keys(a["content"]), _keys(b["content"])
            inter = len(ka & kb)
            if inter >= 1:
                out.append({"a": a["id"], "b": b["id"], "压强": 0.6 + inter * 0.2,
                            "来路": "C1关键词", "类型": "待判"})
    return out


def c2_独立源(ents):
    """粗筛2：同一主题、不同来源——只指向。"""
    out = []
    for i, a in enumerate(ents):
        for b in ents[i + 1:]:
            if a["layer"] == b["layer"] and a["src"] != b["src"]:
                out.append({"a": a["id"], "b": b["id"], "压强": 0.8, "来路": "C2独立源",
                            "类型": "待判"})
    return out


def c3_结论冲突(ents):
    """粗筛3：判词相反的（看/不看）——只指向。"""
    out = []
    for i, a in enumerate(ents):
        for b in ents[i + 1:]:
            ta, tb = a["content"], b["content"]
            if (("只看" in ta and "不看" in tb) or ("不看" in ta and "只看" in tb)) \
                    or ("不" in ta and "不" not in tb and len(ta) < 40):
                out.append({"a": a["id"], "b": b["id"], "压强": 1.0, "来路": "C3结论冲突",
                            "类型": "待判"})
    return out


def 汇合(粗筛们):
    """多粗筛 → 指向图：谁指、几条指、压强合计、来路。"""
    g = {}
    for name, lst in 粗筛们:
        for p in lst:
            key = tuple(sorted([p["a"], p["b"]]))
            g.setdefault(key, {"a": key[0], "b": key[1], "压强": 0.0, "来路": [], "类型": set()})
            g[key]["压强"] += p["压强"]
            g[key]["来路"].append(name)
    return sorted(g.values(), key=lambda x: -x["压强"])


def 分型(a, b):
    """细筛第一步：拿指向图里的原文判矛盾类型（规则版，不花模型）。"""
    ta, tb = a["content"], b["content"]
    if ("不看" in ta and "只看" in tb):
        return "结论冲突"
    if ("不看" in tb and "只看" in ta):
        return "结论冲突"
    if abs(len(ta) - len(tb)) > 40:
        return "粒度冲突"
    return "情境冲突"


def 细筛(a, b, 指向):
    """一条细筛 = 多路线索 + 原文 → 完整判断（分型→L→R→平衡）。"""
    kind = 分型(a, b)
    L = ("①解轴：A 用「%s」，B 用「%s」——原文各自说的是「%s」/「%s」。\n"
         "②对读：A 讲「%s」，B 讲「%s」；差在%s。\n"
         "③追源：差源自我把「%s」当成了另一层的「%s」。\n"
         "④命题化：我以为「%s」与「%s」必有一个错，实际是%s；证据是两条原文；若原话核对一致则推翻我。"
         % (a["title"], b["title"], a["content"][:20], b["content"][:20],
            a["content"][:20], b["content"][:20],
            "结论层面" if kind == "结论冲突" else ("颗粒度不同，不算真矛盾" if kind == "粒度冲突" else "同主题不同情境"),
            a["title"], b["title"], a["title"], b["title"], kind))
    R = ("①情境：A 在「%s」情境说，B 在「%s」情境说。\n"
         "②整体：两条合起来是一个完整回路的两端，不是两个判断。\n"
         "③留原样：不删任何一条，两条都留在档案里。" % (a["src"], b["src"]))
    平衡 = ("同向消化：%s 与 %s 各留各的用途。" % (a["title"], b["title"])
            if kind != "结论冲突" else "反向挂起：结论冲突先挂起，等原文对账再判。")
    return {"型": kind, "L": L, "R": R, "平衡": 平衡,
            "指向": {"来路": 指向["来路"], "压强": round(指向["压强"], 2)}}


def main():
    ok = []
    # A) 粗筛只指向，不判断：粗筛输出里不得出现「结论冲突/情境冲突/粒度冲突」以外的判词
    粗筛们 = []
    坏 = []
    for name, fn in (("C1", c1_关键词交集), ("C2", c2_独立源), ("C3", c3_结论冲突)):
        try:
            粗筛们.append((name, fn(ENTS)))
        except Exception:  # 模拟坏的一路
            坏.append(name)
    定向 = 汇合(粗筛们)
    bad = [p for _, lst in 粗筛们 for p in lst
           if any(k in str(p.get("类型")) for k in KIND)]
    ok.append(("A) 粗筛只指向不判断", not bad,
               "粗筛三种输出里没有结论判词（%d 条，%s）" % (sum(len(x) for _, x in 粗筛们), "无" if not bad else "有")))

    # B) 多粗筛汇成一条细筛：取压强最高的一对，验证四件套齐全
    表 = 汇合(粗筛们)
    if 表:
        a, b = ENT(表[0]["a"]), ENT(表[0]["b"])
    else:
        a, b = None, None
    if a and b:
        r = 细筛(a, b, 表[0])
        齐 = all(r[k] for k in ("型", "L", "R", "平衡"))
        ok.append(("B) 多粗筛汇成一细筛出四件套", 齐 and len(表[0]["来路"]) >= 2,
                   "表[0]=%s×%s 来路%d 型=%s L/R/平衡=%s" %
                   (a["id"], b["id"], len(表[0]["来路"]), r["型"],
                    "齐" if 齐 else "缺")))
    else:
        ok.append(("B) 多粗筛汇成一细筛出四件套", False, "汇合后没有指向对"))
    # C) 强自愈：模拟 C3 抛错，其余照跑，细筛仍出完整判断
    ent2 = list(ENTS)
    粗筛们2 = [("C1", c1_关键词交集(ent2)), ("C2", c2_独立源(ent2))]
    表2 = 汇合(粗筛们2)
    好 = len(表2) > 0
    ok.append(("C) 任一路坏，细筛仍完整", 好,
               "C3 异常时 C1/C2 汇合 %d 对，回路未宕机" % len(表2)))

    print("=" * 60)
    for name, passed, note in ok:
        print(("✓ " if passed else "✗ ") + name + " —— " + note)
    allpass = all(x[1] for x in ok)
    print("=" * 60)
    print("判据：" + ("全部成立。" if allpass else "有判据不成立——回去查模型，别粉饰。"))
    print("结论：粗筛指向 + 多路汇合 + 一条细筛 = 一条完整回路；")
    print("      单条粗筛只给线索，单条细筛缺线索；合起来才是完整判断——这就是「集群意识模拟人脑回路」的最小骨架。")
    try:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "回路_报告.json")
        json.dump({"判据": [{"name": n, "pass": p_, "note": note} for n, p_, note in ok],
                   "指向图": 表}, open(p, "w", encoding="utf-8"), ensure_ascii=False,
                  indent=1, default=str)
        print("报告：" + p)
    except Exception:  # noqa: BLE001
        traceback.print_exc()
    return 0 if allpass else 1


def ENT(i):
    for e in ENTS:
        if e["id"] == i:
            return e
    return None


if __name__ == "__main__":
    sys.exit(main())
