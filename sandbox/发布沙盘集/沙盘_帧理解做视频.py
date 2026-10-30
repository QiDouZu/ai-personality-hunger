# -*- coding: utf-8 -*-
"""沙盘：帧理解做视频 —— 不靠视频模型，靠「拼帧 + 读运动逻辑 + 重建」

观察者思路（2026-10-28）：
  一堆图片 → 按时间从左往右、从上往下拼成一张大图（合重）
  → AI 眼一次读全图，理解背景与运动逻辑
  → 按理解到的运动重建视频（ffmpeg 当手）

本沙盘（不调模型，用几何检测当「眼」的最小替身，先验证管线成立）：
  1) 生成 8 帧测试序列：背景固定，红方块从左向右匀速移动
  2) 拼成 4x2 时间轴网格（左→右、上→下）
  3) 每格找红块中心 → 位置序列 → 运动逻辑（方向、速度）
  4) 用提取的运动逻辑 + ffmpeg 重建视频
  5) 对比：重建视频时长/帧数、检测速度 vs 真实速度

判据（跑前写死）：
  A) 拼图格数 = 帧数（4x2=8）
  B) 检测出的运动方向 = 右（dx>0）
  C) 检测速度 ≈ 真实 80px/帧（±15%）
  D) 重建 mp4 存在且时长 = 8 帧 / 25fps = 0.32 秒
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_帧理解沙盘")
os.makedirs(WORK, exist_ok=True)

W, H = 768, 512
FW, FH = 192, 128          # 每格缩略尺寸
N = 8                      # 帧数
REAL_DX = 80               # 真实每帧位移
BOX = 60

BG = (235, 235, 240)
RED = (220, 40, 40)


def make_frames(n):
    frames = []
    for i in range(n):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        x = 40 + i * REAL_DX
        d.rectangle([x, 256, x + BOX, 256 + BOX], fill=RED)
        p = os.path.join(WORK, "帧_%02d.png" % i)
        img.save(p)
        frames.append(p)
    return frames


def compose_grid(frames, cols):
    """时间轴：左→右、上→下。cols 列，行数自适应。"""
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * FW, rows * FH), (30, 30, 30))
    for idx, p in enumerate(frames):
        im = Image.open(p).resize((FW, FH))
        r, c = divmod(idx, cols)
        sheet.paste(im, (c * FW, r * FH))
    out = os.path.join(WORK, "时间轴拼图.png")
    sheet.save(out)
    return out, cols, rows


def detect_cells(sheet, cols, rows, n):
    """每格找红色块中心（最小眼：颜色阈值）。"""
    sheet = Image.open(sheet).convert("RGB")
    centers = []
    for idx in range(n):
        r, c = divmod(idx, cols)
        cell = sheet.crop((c * FW, r * FH, (c + 1) * FW, (r + 1) * FH))
        pix = cell.load()
        xs, ys = [], []
        for yy in range(FH):
            for xx in range(FW):
                rr, gg, bb = pix[xx, yy]
                if rr > 180 and gg < 90 and bb < 90:
                    xs.append(xx)
                    ys.append(yy)
        if xs:
            centers.append((sum(xs) / len(xs), sum(ys) / len(ys)))
        else:
            centers.append(None)
    return centers


def motion_logic(centers):
    xs = [c[0] for c in centers if c]
    if len(xs) < 2:
        return {"ok": False}
    d = [b - a for a, b in zip(xs, xs[1:])]
    avg = sum(d) / len(d)
    return {
        "ok": all(abs(x - avg) < 10 for x in d),
        "direction": "right" if avg > 0 else ("left" if avg < 0 else "still"),
        "dx_per_cell": round(avg, 2),
        "xs": [round(x, 1) for x in xs],
    }


def rebuild_video(bg_path, x0, dx, fps=25, n=None):
    n = n or N
    """按运动逻辑重建：背景 + 红块小图，overlay 用 t 表达式线性移动。"""
    box_path = os.path.join(WORK, "红块.png")
    box = Image.new("RGB", (BOX, BOX), RED)
    box.save(box_path)
    out = os.path.join(WORK, "重建视频.mp4")
    # 帧宽 = 时间轴格宽缩放回真实坐标：x ≈ x0 + dx * (f / 1)（每帧一步）
    xexpr = "%g+%g*t" % (x0, dx * fps)
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", bg_path,
           "-loop", "1", "-i", box_path,
           "-filter_complex",
           "[0]scale=%d:%d[bg];[1]scale=%d:%d[box];"
           "[bg][box]overlay=x='%s':y=256:shortest=1,"
           "format=yuv420p" % (W, H, BOX, BOX, xexpr),
           "-t", "%.3f" % (n / fps), "-r", str(fps),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", out]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return out if os.path.exists(out) and os.path.getsize(out) > 1000 else (
        "ffmpeg 失败：" + (r.stderr or "")[-400:])


def main(n=8):
    cols = 4 if n <= 8 else 8
    frames = make_frames(n)
    sheet, cols, rows = compose_grid(frames, cols)
    centers = detect_cells(sheet, cols, rows, n)
    logic = motion_logic(centers)
    print("=" * 72)
    print(" 帧理解做视频：拼帧 → 读运动逻辑 → 重建")
    print("=" * 72)
    print("  帧数：%d | 拼图：%d 行 %d 列" % (n, rows, cols))
    for i, c in enumerate(centers):
        print("  格 %d 红块中心：%s" % (i, "无" if c is None else "(%0.1f, %0.1f)" % c))

    # 拼图格宽 → 真实坐标：真实 W / FW 缩放，x0 真实 = 检测 x0 * (W/FW)
    scale = W / FW
    real_x0 = centers[0][0] * scale
    real_dx = logic["dx_per_cell"] * scale if logic["ok"] else 0
    print("  运动逻辑：方向=%s 每格位移=%.1f 格像素（真实 ≈%.1f 像素/帧）" % (
        logic["direction"], logic["dx_per_cell"], real_dx))

    out = rebuild_video(os.path.join(WORK, "帧_00.png"), real_x0, real_dx, n=n)
    ok_video = out.endswith(".mp4")
    print("  重建视频：%s" % ("OK " + out if ok_video else "✗ " + out))

    # 判据
    a1 = len(centers) == n
    a2 = logic["direction"] == "right"
    a3 = abs(real_dx - REAL_DX) <= REAL_DX * 0.15
    dur = 0
    if ok_video:
        try:
            p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                "default=noprint_wrappers=1", out],
                               capture_output=True, text=True, encoding="utf-8")
            for line in p.stdout.splitlines():
                if line.startswith("duration="):
                    dur = float(line.split("=")[1])
        except Exception:
            pass
    a4 = ok_video and abs(dur - n / 25) < 0.1

    # 压缩识别：N 帧逐帧看 vs 一张拼图看一次
    sheet_px = cols * FW * rows * FH
    frames_px = n * W * H
    print("\n  压缩识别：")
    print("  · 逐帧识别：%d 次调用（每帧一次）" % n)
    print("  · 拼图识别：1 次调用（%d 帧压成一张 %dx%d）" % (n, cols * FW, rows * FH))
    print("  · 压缩比：帧数 %d:1 · 像素 %.1f:1" % (n, frames_px / sheet_px))
    print("  · 识别成本从「%d 帧 × 每次看全图」压到「1 张图看一次」" % n)

    print("\n  判据（跑前写死）：")
    print("  A) 拼图格数 = 帧数：%s" % ("✓" if a1 else "✗"))
    print("  B) 方向 = 右：%s" % ("✓" if a2 else "✗"))
    print("  C) 检测速度 ≈ 真实 80px/帧（±15%%）：%s（%.1f）" % ("✓" if a3 else "✗", real_dx))
    print("  D) 重建视频时长 = %d/25 秒：%s（%.2f 秒）" % (n, "✓" if a4 else "✗", dur))
    print("\n  结论：%s" % (
        "不靠视频模型，拼一张时间轴大图就能读出运动逻辑，再按它重建视频；"
        "识别从「%d 帧逐次看」压成「一张图看一次」。"
        "AI 眼负责「读拼图」，下一步把颜色检测换成它，就能读懂非匀速、带背景变化的运动。"
        % n
        if (a1 and a2 and a3 and a4) else "判据不成立，回去查模型"))

    report = {
        "frames": n, "grid": [rows, cols],
        "centers": centers, "logic": logic,
        "real_dx": real_dx, "video": out if ok_video else None,
        "checks": {"A": a1, "B": a2, "C": a3, "D": a4},
        "压缩": {"frames_per_call": n, "pixel_ratio": round(frames_px / sheet_px, 2)},
    }
    with open(os.path.join(WORK, "报告.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\n  报告 → " + os.path.join(WORK, "报告.json"))


if __name__ == "__main__":
    _n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(_n)
