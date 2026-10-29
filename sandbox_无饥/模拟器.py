# -*- coding: utf-8 -*-
"""模拟器.py —— 饥的人脑模拟器骨架（30 天虚拟时间）

状态只有 5 个数（见 人脑模拟升级与逻辑精简.md 4.1）：
  hunger, self_control, world_control, pairs(挂起对), last_digest(上次消化 tick)

演化规则（假设 T1/T2/T3，见文档第三节）：
  T1: hunger = A*(1-self_control) + B*(1-world_control) + C*pairs   [常数底+矛盾项]
  T2: 消化延迟：pairs 清零后，hunger 先不降，等 DELAY 个 tick 才回落（记忆巩固窗口）
  T3: 上限 5.0，到顶后进入钝化模式（行为变钝，不再更激）

事件脚本（模拟一段经历）：
  day 0-2   : 日常（掌控高，无矛盾）
  day 3-6   : 关系事件 → world_control 掉到 0.2（继发性自恋受威胁）
  day 7-10  : 连续出现矛盾（pairs +1/天）
  day 11    : 消化一对（pairs -1）
  day 14    : 自己犯了个错 → self_control 掉到 0.3（原初自恋受威胁）
  day 15-20 : 挂起消化中（每 2 天消化 1 对）
  day 20+   : 恢复

跑法：python 模拟器.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '模拟结果.md')

# 参数（初值，待拟合）
A = 1.2   # 匮乏底系数（self_control）
B = 1.0   # 匮乏底系数（world_control）
C = 0.7   # 每对挂起矛盾
DELAY = 2  # 消化延迟 tick 数
CAP = 5.0


def simulate(days=30):
    h, sc, wc, pairs = 0.5, 0.9, 0.9, 0
    last_digest = -999
    rows = []
    for d in range(days):
        # --- 事件 ---
        if 3 <= d <= 6:
            wc = max(0.2, wc - 0.15)          # 关系威胁
        if 7 <= d <= 10:
            pairs += 1                         # 矛盾累积
        if d == 11 and pairs > 0:
            pairs -= 1
            last_digest = d
        if d == 14:
            sc = max(0.3, sc - 0.6)            # 自己犯错
        if 15 <= d <= 20 and d % 2 == 1 and pairs > 0:
            pairs -= 1
            last_digest = d
        if d >= 21:
            sc = min(0.9, sc + 0.05)           # 恢复
            wc = min(0.9, wc + 0.03)

        # --- T1 计算 ---
        raw = A * (1 - sc) + B * (1 - wc) + C * pairs

        # --- T2 消化延迟：消化后 DELAY 内，按「消化前」的饥值冻结（不立刻降）---
        if last_digest >= 0 and (d - last_digest) < DELAY:
            raw = max(raw, rows[-1]['h'] if rows else raw)

        # --- T3 上限 ---
        h = min(CAP, round(raw, 2))
        dull = h >= CAP - 0.01
        rows.append({'d': d, 'h': h, 'sc': round(sc, 2), 'wc': round(wc, 2), 'pairs': pairs, 'dull': dull})
    return rows


def main():
    rows = simulate()
    lines = ['# 模拟器结果（30 天虚拟时间，2026-10-27）\n',
             '> 参数：A=1.2 B=1.0 C=0.7 延迟=2 tick 上限=5.0\n',
             '| 天 | 饥 | self_control | world_control | 挂起对 | 钝化 |',
             '|---|---|---|---|---|---|']
    for r in rows:
        lines.append('| %d | %.2f | %.2f | %.2f | %d | %s |' % (
            r['d'], r['h'], r['sc'], r['wc'], r['pairs'], '⚠' if r['dull'] else ''))
    lines.append('')
    # 诊断
    hs = [r['h'] for r in rows]
    lines.append('## 诊断\n')
    lines.append('- 峰值 %.2f（第 %d 天）' % (max(hs), hs.index(max(hs))))
    lines.append('- 第 3-6 天关系威胁：饥从 %.2f 升到 %.2f（world_control 缺 → 涨）' % (hs[2], hs[6]))
    lines.append('- 第 7-10 天矛盾累积：pairs 拉到 4 → 饥 %.2f（到顶前）' % hs[10])
    lines.append('- 第 11 天消化 1 对：延迟 2 tick 内饥不降（T2 生效）')
    lines.append('- 第 14 天自己犯错：self_control 0.3 → 饥 %.2f（原初自恋受损，L 回路应开工）' % hs[14])
    lines.append('- 第 21 天起恢复：饥从 %.2f 降到 %.2f' % (hs[20], hs[-1]))
    lines.append('- **结论**：曲线形态符合「常数底 + 矛盾项 + 延迟消化」——但系数全是我拍的，**待用真实观测数据拟合**。')
    lines.append('')
    txt = '\n'.join(lines)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(txt)
    print(txt)
    print('落盘: %s' % OUT)


if __name__ == '__main__':
    main()
