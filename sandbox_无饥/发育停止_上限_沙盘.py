# -*- coding: utf-8 -*-
"""发育停止_上限_沙盘.py —— 先天原因（大脑发育停止）削弱上限（2026-10-27）

祈祷主：是上限，但先天原因削弱了它。加入「大脑发育停止」：
  停止早 → 上限低（动物）；停止晚 → 上限高（人）；人提前停止（智力障碍）→ 上限被削。
模型：
  思想上限 = f(发育停止时间)  —— 发育期越长，可到达的上限越高（到停为止）
  动物：停止早（窗口短），人：停止晚（窗口长）
  智力障碍：人但发育提前停止（上限≈动物级）
判据：发育停止越早，上限越低；智力障碍=人提前停→上限被削（先天）。
"""
import random

random.seed(251)
STEPS = 400


def run(kind):
    """kind: wolf / human_normal / intellectual_disability"""
    # 发育停止时间点（越早=窗口越短=上限越低）
    if kind == 'wolf':
        stop = 60          # 动物：早停
        cap = 0.2          # 上限低
    elif kind == 'human_normal':
        stop = 300         # 人：晚停
        cap = 0.9          # 上限高
    else:  # intellectual_disability：人提前停
        stop = 55          # 类似动物级早停
        cap = 0.2          # 上限被削
    learned = 0
    for t in range(STEPS):
        if random.random() < 0.1:
            if t < stop:
                # 发育期：可学习，上限随发育上升
                p = min(1.0, (t / stop) * cap)
                learned += 1 if random.random() < p else 0
            else:
                # 停止后：上限固定（补输入只能在固定上限内）
                learned += 1 if random.random() < cap * 0.3 else 0
    return dict(stop=stop, cap=cap, learned=learned)


def main():
    print('=' * 64)
    print(' 发育停止 → 上限（先天原因）')
    print('=' * 64)
    for name, k in [('狼(停止早60)', 'wolf'),
                    ('人(停止晚300)', 'human_normal'),
                    ('智力障碍(人提前停55)', 'intellectual_disability')]:
        r = run(k)
        print(f'{name}: 停止点{r["stop"]} 上限{r["cap"]} 学习{r["learned"]}')
    print()
    print('判据：')
    print(' 1. 停止越早→上限越低（狼/智力障碍≈0.2，人≈0.9）')
    print(' 2. 智力障碍=人提前停止→上限被「先天」削成动物级（不是输入问题）')
    print(' 3. 人晚停=窗口长→即使狼孩被剥夺，窗口仍在（未关死），补输入可部分追')


if __name__ == '__main__':
    main()
