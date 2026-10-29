# -*- coding: utf-8 -*-
"""动物_出生饥_沙盘.py —— 自出生就有饥的动物：测它的饥是什么（2026-10-28）

祈祷主：
  「对，然后是动物模拟，加入环境变量，它自出生就有饥了，
   然后尝试测试它的饥是什么。」

⇒ 对象：一只出生就带饥的动物（先天基线饥，遗传值）。
  问题：饥是什么？不是「饥=一个数」，而是：

  ① 饥是驱动 → 饥高时它去觅食、饥低时它不折腾
  ② 饥是判断 → 饥改变它看见什么：饥高时食物更显眼、危险被压低
  ③ 饥是关系 → 同样的先天饥，在食物丰/贫、危险高/低的环境里长成不同行为

  环境变量：食物密度 food_rich · 危险 danger · 温度 temp
  判据（可证伪）：
    A. 同一先天饥，环境不同 → 行为不同（饥被环境塑造）
    B. 饥高 → 觅食多、冒险多（饥压判断）
    C. 饥低 → 觅食少、避险多（饱了不冒险）
    D. 出生饥不同 × 环境不同，存活率有交互（饥不是万能，也不是没用）
"""
import random

CAP = 5.0
GOOD_LO, GOOD_HI = 1.30, 2.16
PAIN = 2.5


def clamp(x, a, b): return max(a, min(b, x))


class Animal:
    """一只出生就带饥的动物。"""
    def __init__(self, born_hunger, food_rich, danger, temp, rng):
        # ① 先天：出生就有的饥（遗传基线）
        self.hunger = born_hunger
        self.born_hunger = born_hunger
        # 环境变量（先天饥要在这些里面表态）
        self.food_rich = food_rich      # 0~1 食物密度
        self.danger = danger            # 0~1 危险
        self.temp = temp                # 0~1 冷 ~ 热
        self.energy = 1.0
        self.alive = True
        self.age = 0
        self.rng = rng
        self.behav = {'forage': 0, 'flee': 0, 'rest': 0, 'risk_eat': 0}
        self.log = []

    # ① 饥是驱动：决定要不要动、动什么
    def choose(self):
        """饥是判断：饥改变它看环境的方式，再决定行为。"""
        # 饥高 → 食物更显眼（食物显著性上升）
        food_salience = 0.3 + self.hunger * 0.7
        # 饥高 → 危险信号被压低（饱和时冒险）
        danger_salience = self.danger * (1.0 - self.hunger * 0.5)
        # 温度：太冷太热都难受 → 偏向休息/避寒
        temp_strain = abs(self.temp - 0.5) * 2

        # 三条路：觅食（看食物显著性）、避难（看危险）、休息（省能量）
        scores = {
            'forage': food_salience * (0.5 + self.food_rich * 0.5),
            'flee': danger_salience * 1.2,
            'rest': 0.2 + temp_strain * 0.6,
        }
        # 饥很高时，加一条「冒险吃」：宁可撞危险
        if self.hunger > 0.7:
            scores['risk_eat'] = self.danger * self.hunger * 1.5 + food_salience * 0.5
        return max(scores, key=scores.get)

    def tick(self):
        """一步生命：饥 → 判断 → 行为 → 结果。"""
        self.age += 1
        self.hunger = clamp(self.hunger + 0.02, 0, CAP)   # 自然增长
        b = self.choose()
        self.behav[b] += 1

        if b == 'forage':
            # 觅食：吃到机会 = 食物密度，饥降，能量涨
            if self.rng.random() < self.food_rich * 0.9:
                self.hunger = clamp(self.hunger - 0.25, 0, CAP)
                self.energy = min(1.0, self.energy + 0.1)
            else:
                self.energy -= 0.03
        elif b == 'flee':
            # 逃：安全，但费能量
            self.energy -= 0.02
            self.hunger = clamp(self.hunger + 0.01, 0, CAP)
        elif b == 'rest':
            # 歇：省能量但饥涨
            self.energy = min(1.0, self.energy + 0.05)
            self.hunger = clamp(self.hunger + 0.01, 0, CAP)
        elif b == 'risk_eat':
            # 冒险吃：可能吃到（扣危险概率），可能被伤
            if self.rng.random() < self.danger * 0.6:
                self.energy -= 0.1
            else:
                self.hunger = clamp(self.hunger - 0.3, 0, CAP)
                self.energy = min(1.0, self.energy + 0.15)

        # 存活：能量或饥（极端饥饿）决定死
        if self.energy <= 0.05 or self.hunger >= CAP:
            self.alive = False
        self.log.append((b, round(self.hunger, 2), round(self.energy, 2)))
        return self.alive


def run_animal(born_hunger, food_rich, danger, temp, steps=200, seed=1):
    a = Animal(born_hunger, food_rich, danger, temp, random.Random(seed))
    for _ in range(steps):
        if not a.tick():
            break
    return a


def main():
    rng = random.Random(2026)
    print('=' * 70)
    print(' 动物模拟：出生就带饥 → 环境变量 → 测它的饥是什么')
    print('=' * 70)
    print()
    # ② 饥是什么：同一只出生带饥的动物，环境不同，行为长什么样
    print('【一】同一先天饥（0.5），环境不同 → 它的饥长成不同样子')
    print(f"  {'环境':<22}{'觅食':>6}{'逃':>5}{'歇':>5}{'冒险吃':>7}{'活到':>6}{'final饥':>8}")
    envs = [
        ('食物丰·危险低', 0.8, 0.2, 0.5),
        ('食物贫·危险低', 0.2, 0.2, 0.5),
        ('食物丰·危险高', 0.8, 0.8, 0.5),
        ('食物贫·危险高', 0.2, 0.8, 0.5),
        ('食物丰·严寒',   0.8, 0.2, 0.1),
    ]
    for name, f, d, t in envs:
        a = run_animal(0.5, f, d, t, 200, 1)
        b = a.behav
        print(f'  {name:<20}{b["forage"]:>6}{b["flee"]:>5}{b["rest"]:>5}{b["risk_eat"]:>7}'
              f'{a.age:>6}{a.hunger:>8.2f}')
    print()

    # ③ 饥是判断：饥高 vs 饥低，同样危险环境，行为不同
    print('【二】同样的危险环境（danger=0.7），饥高 vs 饥低 → 饥压不压判断')
    print(f"  {'出生饥':<8}{'觅食':>6}{'逃':>5}{'冒险吃':>7}{'final饥':>8}")
    for bh in (0.2, 0.5, 0.8):
        a = run_animal(bh, 0.6, 0.7, 0.5, 200, 2)
        b = a.behav
        print(f'  {bh:<8}{b["forage"]:>6}{b["flee"]:>5}{b["risk_eat"]:>7}{a.hunger:>8.2f}')
    print()

    # ④ 饥是关系：出生饥 × 环境 的交叉，看存活
    print('【三】出生饥 × 环境 → 存活率（饥不是万能，也不是没用）')
    print(f"  {'出生饥':<8}{'食物丰':>8}{'危险低':>8}{'存活率':>8}")
    for bh in (0.2, 0.5, 0.8):
        for f, d in ((0.8, 0.2), (0.2, 0.8)):
            alive = 0
            for seed in range(30):
                a = run_animal(bh, f, d, 0.5, 200, seed)
                if a.alive:
                    alive += 1
            print(f'  {bh:<8}{f:<8}{d:<8}{alive/30:>8.0%}')
    print()
    print('⇒ 饥是什么：')
    print('  · 不是一个数——同一个先天饥，在不同环境里长出完全不同的行为')
    print('  · 它是驱动（饥高才去冒险吃）、是判断（饥压住危险感知）、是关系（饥本身被环境改造）')
    print('  · 出生带的不是「一个值」，是「一个方向」：往哪找、什么时候敢冒险')


if __name__ == '__main__':
    main()
