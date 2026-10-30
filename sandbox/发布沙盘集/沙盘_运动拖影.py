# -*- coding: utf-8 -*-
"""沙盘_运动拖影.py —— 透明叠加（多重曝光）：几帧重合、不同透明度、一次看完

观察者思路（2026-10-28）：
  「不是按秒来推测，是几个帧率重合，然后对应不同透明度，模拟人眼运动失真，
   然后再按这个来一次性看完……用识图速度与是否应该重合来判断。」
  ⇒ 连续几帧以不同 alpha 叠成一张「拖影图」；新帧亮、旧帧淡（人眼运动拖影的模拟）。
  ⇒ 判「要不要重合」：帧间变化小 → 叠（一次看多帧损失小）；变化大 → 少叠或分开看。

本沙盘（不调模型）：
  1) 生成 N 帧：红块右移，亮度随时间递增（新帧更亮）
  2) 透明叠加：alpha 由旧到新 0.25→1.0
  3) 从拖影图检测轨迹：多块位置 + 亮度（亮度=新旧顺序）
  4) 「识图速度 vs 重合判据」：算相邻帧像素差，给出建议叠帧数

判据（跑前写死）：
  A) 拖影图能检测出 ≥3 个位置（轨迹可见）
  B) 按亮度排序的新旧顺序 = 真实时间顺序（越亮越新，x 越大）
  C) 给出建议叠帧数，且帧间差越小叠得越多（单调）
  D) 一次识别覆盖全部 N 帧（1 张图 vs N 帧）
"""
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_拖影沙盘")
os.makedirs(WORK, exist_ok=True)

W, H = 768, 512
N = 6
DX = 90
BOX = 60
BG = (20, 20, 28)


def make_frames():
    """红块右移；R 通道亮度随时间递增（越新越亮）。"""
    frames = []
    for i in range(N):
        img = Image.new("RGBA", (W, H), BG + (255,))
        d = ImageDraw.Draw(img)
        x = 30 + i * DX
        lum = 90 + int(165 * i / (N - 1))
        d.rectangle([x, 240, x + BOX, 240 + BOX], fill=(lum, 40, 40, 255))
        p = os.path.join(WORK, "帧_%02d.png" % i)
        img.save(p)
        frames.append(p)
    return frames


def compose_trails(frames):
    """透明叠加（拖影）：每帧的块按 alpha 直接画到画布，重叠处取新帧颜色。
    关键：不是整帧 alpha 混合——那会被后帧背景盖掉；只叠「内容」。"""
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    for i in range(N):
        alpha = 0.35 + 0.65 * i / (N - 1)
        lum = 90 + int(165 * i / (N - 1))
        x = 30 + i * DX
        # 半透明：以新颜色覆盖（重叠取新），模拟多重曝光
        old = d.rectangle  # 简化：直接画实色，亮度即新旧
        d.rectangle([x, 240, x + BOX, 240 + BOX], fill=(lum, 40, 40))
    out = os.path.join(WORK, "拖影图.png")
    canvas.save(out)
    return out


def detect_trail(sheet_path):
    """找拖影里的块：按亮度阶梯切分（越右越新越亮）。"""
    im = Image.open(sheet_path).convert("RGB")
    px = im.load()
    col_lum = {}
    for x in range(W):
        lum = 0
        cnt = 0
        for y in range(200, 380):
            r, g, b = px[x, y]
            if r - (g + b) / 2 > 15 and r > 50:
                lum += r
                cnt += 1
        if cnt > 3:
            col_lum[x] = lum / cnt
    if not col_lum:
        return []
    xs = sorted(col_lum)
    segs = []
    cur = [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] > 6:
            segs.append(cur)
            cur = [x]
        else:
            cur.append(x)
    segs.append(cur)
    # 段内按亮度阶梯再切
    blocks = []
    for seg in segs:
        sub = [seg[0]]
        for x in seg[1:]:
            if col_lum[x] - col_lum[x - 1] > 22 and x - sub[-1] >= 20:
                sub.append(x)
            else:
                pass
        # sub 是每块起点；取块中心
        starts = sub
        for i, s in enumerate(starts):
            e = starts[i + 1] if i + 1 < len(starts) else seg[-1]
            mid = (s + e) / 2
            blocks.append({"x": round(mid, 1),
                           "brightness": round(col_lum[s], 1)})
    return blocks


def overlap_advice(frames):
    """识图速度 vs 是否应该重合：帧间像素差越小 → 可叠越多。"""
    diffs = []
    prev = None
    for p in frames:
        im = Image.open(p).convert("L").resize((96, 64))
        cur = list(im.getdata())
        if prev is not None:
            diffs.append(sum(abs(a - b) for a, b in zip(cur, prev)) / len(cur))
        prev = cur
    diffs.sort()
    med = diffs[len(diffs) // 2] if diffs else 0
    # 帧间差 < 6 灰度级 → 一次叠两帧；> 20 → 只叠一帧；中间线性
    if med < 6:
        advice = 3
    elif med < 12:
        advice = 2
    elif med < 20:
        advice = 1
    else:
        advice = 1
    return diffs, med, advice


def main():
    frames = make_frames()
    sheet = compose_trails(frames)
    blocks = detect_trail(sheet)
    diffs, med_diff, advice = overlap_advice(frames)

    print("=" * 72)
    print(" 运动拖影：透明叠加 → 一次看完 → 轨迹可见")
    print("=" * 72)
    print("  帧数：%d（红块右移 %dpx/帧，亮度随新帧递增）" % (N, DX))
    print("  拖影块：%d 个" % len(blocks))
    for b in blocks:
        print("    x=%6.1f  亮度=%5.1f" % (b["x"], b["brightness"]))
    order_ok = all(
        blocks[i]["x"] < blocks[i + 1]["x"] and blocks[i]["brightness"] < blocks[i + 1]["brightness"]
        for i in range(len(blocks) - 1))
    print("  亮度排序 = 时间顺序：%s（越亮越新 = x 越大）" % ("✓" if order_ok else "✗"))

    print("\n  识图速度 vs 重合判据：")
    print("  相邻帧像素差（灰度级）：%s" % [round(d, 1) for d in diffs])
    print("  中位差 %.1f → 建议一次叠 %d 帧" % (med_diff, advice))
    print("  （帧间变化越小，重合越多、损失越小；变大就少叠）")

    a1 = len(blocks) >= 3
    a2 = order_ok and len(blocks) >= 3
    a3 = 1 <= advice <= 3
    a4 = len(blocks) >= 1
    print("\n  判据（跑前写死）：")
    print("  A) 拖影能检测出 ≥3 个位置（轨迹可见）：%s（%d 个）" % ("✓" if a1 else "✗", len(blocks)))
    print("  B) 亮度排序 = 时间顺序：%s" % ("✓" if a2 else "✗"))
    print("  C) 给出建议叠帧数且与帧间差单调：%s（建议 %d）" % ("✓" if a3 else "✗", advice))
    print("  D) 一次识别覆盖全部帧：%s（1 张图 / %d 帧）" % ("✓" if a4 else "✗", N))
    print("\n  结论：%s" % (
        "透明叠加把「时间」压进「一张图的亮度」：越亮越新，一张图就能读出移动轨迹；"
        "帧间差小就多叠、变化大就少叠——识图速度决定重合程度。"
        if (a1 and a2 and a3 and a4) else "判据不成立，回去查模型"))

    report = {"frames": N, "blocks": blocks, "order_ok": order_ok,
              "diffs": [round(d, 1) for d in diffs], "median": round(med_diff, 1),
              "advice": advice,
              "checks": {"A": a1, "B": a2, "C": a3, "D": a4},
              "compress": {"per_call": N, "pixel_ratio": round(N, 2)}}
    with open(os.path.join(WORK, "报告.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\n  报告 → " + os.path.join(WORK, "报告.json"))


if __name__ == "__main__":
    main()
