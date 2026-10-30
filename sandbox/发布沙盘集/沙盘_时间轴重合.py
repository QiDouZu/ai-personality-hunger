# -*- coding: utf-8 -*-
"""沙盘_时间轴重合.py —— 读取与分类：时间轴上「不断且相似」的帧才重合

观察者思路（2026-10-28）：「测试你读取与分类，是按照时间轴上不断且相似的来重合的。」
  ⇒ 不是固定叠 K 帧；是边读边判：同色且位置连续 → 同组继续叠；颜色突变/位置跳变 → 断开。

判据（跑前写死）：
  A) 分段数 = 2（第 8 帧突变处断开）
  B) 组1 = 8 帧（0–7，红），组2 = 4 帧（8–11，蓝）
  C) 每组拖影能检出 ≥2 个块（轨迹可见）
  D) 两组主色不同（红 vs 蓝）→ 分类正确
"""
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_时间轴重合沙盘")
os.makedirs(WORK, exist_ok=True)

W, H = 768, 512
DX = 90
BOX = 60
BG = (20, 20, 28)
N = 12
SWITCH = 8

RED = (220, 40, 40)
BLUE = (40, 70, 220)


def color_of(i):
    return RED if i < SWITCH else BLUE


def frame_x(i):
    return 30 + (i % SWITCH) * DX if i < SWITCH else 30 + (i - SWITCH) * DX


def make_frames():
    frames = []
    for i in range(N):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([frame_x(i), 240, frame_x(i) + BOX, 240 + BOX], fill=color_of(i))
        p = os.path.join(WORK, "帧_%02d.png" % i)
        img.save(p)
        frames.append(p)
    return frames


def detect_frame(path):
    """每帧检测主体：返回 (颜色, x中心) 或 None。"""
    im = Image.open(path).convert("RGB")
    px = im.load()
    red_x, blue_x = [], []
    for x in range(W):
        for y in range(200, 380):
            r, g, b = px[x, y]
            if r - (g + b) / 2 > 15 and r > 50:
                red_x.append(x)
                break
            if b - (r + g) / 2 > 20 and b > 60:
                blue_x.append(x)
                break
    if red_x:
        return ("red", sum(red_x) / len(red_x))
    if blue_x:
        return ("blue", sum(blue_x) / len(blue_x))
    return None


def segment_by_similarity(frames, jump=200):
    """同色且位置连续 → 同组；颜色变或位置跳变 > jump → 断开。"""
    infos = [detect_frame(p) for p in frames]
    groups = [[0]]
    for i in range(1, N):
        a, b = infos[i - 1], infos[i]
        same = (a is not None and b is not None and a[0] == b[0]
                and abs(a[1] - b[1]) <= jump)
        if same:
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups, infos


def compose_group(group, tag, color):
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    for j, i in enumerate(group):
        lum = 0.35 + 0.65 * j / max(1, len(group) - 1)
        c = tuple(int(255 * (1 - lum) * 0.3 + base * lum) for base in color)
        d.rectangle([frame_x(i), 240, frame_x(i) + BOX, 240 + BOX], fill=c)
    out = os.path.join(WORK, "拖影_%s.png" % tag)
    canvas.save(out)
    return out


def count_blocks(path, red=True):
    im = Image.open(path).convert("RGB")
    px = im.load()
    xs = []
    for x in range(W):
        for y in range(200, 380):
            r, g, b = px[x, y]
            ok = (r - (g + b) / 2 > 15 and r > 50) if red else (
                b - (r + g) / 2 > 20 and b > 60)
            if ok:
                xs.append(x)
                break
    if not xs:
        return 0
    segs = 1
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] > 6:
            segs += 1
    return segs


def main():
    frames = make_frames()
    groups, infos = segment_by_similarity(frames)
    print("=" * 72)
    print(" 时间轴重合：读取与分类（不断且相似的才叠）")
    print("=" * 72)
    print("  帧数 %d，第 %d 帧突变（红→蓝）" % (N, SWITCH))
    print("  每帧主体：")
    for i, inf in enumerate(infos):
        print("    帧 %2d：%s" % (i, "无" if inf is None else "%s x=%.0f" % inf))
    print("  分段：%s" % [[min(g), max(g)] for g in groups])

    ok_blocks = []
    for gi, g in enumerate(groups):
        tag = "组%d" % (gi + 1)
        color = infos[g[0]][0]
        out = compose_group(g, tag, RED if color == "red" else BLUE)
        nb = count_blocks(out, red=(color == "red"))
        ok_blocks.append((tag, len(g), nb, color))
        print("  %s：%d 帧 → %s，检出 %d 块（%s）" % (
            tag, len(g), out, nb, "红" if color == "red" else "蓝"))

    a1 = len(groups) == 2
    a2 = [len(g) for g in groups] == [SWITCH, N - SWITCH]
    a3 = all(b >= 2 for _, _, b, _ in ok_blocks)
    a4 = ok_blocks[0][3] == "red" and ok_blocks[1][3] == "blue"
    print("\n  判据（跑前写死）：")
    print("  A) 分段数 = 2：%s（%d）" % ("✓" if a1 else "✗", len(groups)))
    print("  B) 组1=8 帧、组2=4 帧：%s（%s）" % (
        "✓" if a2 else "✗", [len(g) for g in groups]))
    print("  C) 每组拖影 ≥2 块：%s（%s）" % (
        "✓" if a3 else "✗", [b for *_, b, _ in ok_blocks]))
    print("  D) 两组颜色不同（红/蓝）→ 分类正确：%s" % ("✓" if a4 else "✗"))
    print("\n  结论：%s" % (
        "按「同色且位置连续」自动分段：连续相似的帧叠成一组拖影，颜色突变/位置跳变处断开；"
        "每组一次识别——这就是「按时间轴不断且相似来重合」。"
        if (a1 and a2 and a3 and a4) else "判据不成立，回去查模型"))

    report = {"per_frame": ["%s x=%.0f" % inf if inf else "无" for inf in infos],
              "groups": [[min(g), max(g)] for g in groups],
              "per_group": ok_blocks,
              "checks": {"A": a1, "B": a2, "C": a3, "D": a4}}
    with open(os.path.join(WORK, "报告.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\n  报告 → " + os.path.join(WORK, "报告.json"))


if __name__ == "__main__":
    main()
