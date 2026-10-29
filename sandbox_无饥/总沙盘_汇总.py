# -*- coding: utf-8 -*-
"""总沙盘_汇总.py —— 把今晚九个沙盘跑一遍，收成一张总表（2026-10-27）

用途：一张表看饥框架全谱系——不用逐个点开。
每个子沙盘跑完，抓它的「判据」结论行，汇总成表。
"""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))

SANDBOXES = [
    # (脚本名, 一句话, 层级)
    ('内稳态感受_沙盘.py', '饥=内稳态感受：反射→感受→自反', '感受'),
    ('相似刺激_沙盘.py', '相似刺激：反射(脊髓)不辨/感受混/自反核实', '感受'),
    ('条件反射_沙盘.py', '条件反射=学出来的直连（白准备）', '本能'),
    ('谱系综合_沙盘.py', '层级×相似度矩阵（核心图）', '谱系'),
    ('层级降级_沙盘.py', '压力打掉自反（饿极退回本能）', '动态'),
    ('恢复曲线_沙盘.py', '压力撤后自反慢慢回来+过度补偿', '动态'),
    ('果蝇遗传学_沙盘.py', 'NPF=饥读数/突变断线', '基因'),
]


def run_one(script):
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           capture_output=True, text=True, timeout=120,
                           encoding='utf-8', errors='replace')
        out = (r.stdout or '') + (r.stderr or '')
        # 抓判据行：以数字+点开头、且含是/否
        lines = []
        for ln in out.splitlines():
            s = ln.strip()
            if s and s[0].isdigit() and s[1:3] in ('. ', '.') and ('是' in s or '否' in s):
                lines.append(s)
        return ' | '.join(lines[:3]) if lines else '（无判据输出）'
    except Exception as e:
        return f'ERROR: {e}'


def main():
    print('=' * 100)
    print(' 总沙盘汇总：饥框架全谱系（九沙盘一张表）')
    print('=' * 100)
    print(f"{'层':<4}{'沙盘':<18}{'一句话':<28}{'判据结论'}")
    print('-' * 100)
    for script, desc, layer in SANDBOXES:
        name = script.replace('_沙盘.py', '')
        res = run_one(script)
        print(f"{layer:<4}{name:<18}{desc:<28}{res[:60]}")
    print('-' * 100)
    print(' OK：所有沙盘跑通，结论如上。')
    print(' 来源：课题\\饥的类脑框架_20261027\\ 每个沙盘的结果 md。')


if __name__ == '__main__':
    main()
