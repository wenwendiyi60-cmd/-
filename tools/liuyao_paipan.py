#!/usr/bin/env python3
"""六爻确定性排盘模块。

把易错的机械计算（旬空、纳甲、六亲、世应、旺衰、合冲、动变）从模型口算里拿走，
算好后喂给执行口令一个已校验的盘。对应执行层降错的"杠杆 2"。

只做确定性部分；旺衰用六爻常用的"四季土旺"近似（旺相休囚死），断卦判断仍交口令。
无第三方依赖。
"""
from __future__ import annotations

GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

ZHI_WX = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
          '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}

SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # X 生 SHENG[X]
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}      # X 克 KE[X]

LIUHE = [('子', '丑'), ('寅', '亥'), ('卯', '戌'), ('辰', '酉'), ('巳', '申'), ('午', '未')]
LIUCHONG = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]

# 八经卦：bits 自下而上（1=阳爻，0=阴爻）；纳甲内卦取 dz_in（初二三），外卦取 dz_out（四五上）
TRIGRAMS = {
    '乾': dict(bits=(1, 1, 1), wx='金', dz_in=['子', '寅', '辰'], dz_out=['午', '申', '戌']),
    '兑': dict(bits=(1, 1, 0), wx='金', dz_in=['巳', '卯', '丑'], dz_out=['亥', '未', '酉']),
    '离': dict(bits=(1, 0, 1), wx='火', dz_in=['卯', '丑', '亥'], dz_out=['酉', '未', '巳']),
    '震': dict(bits=(1, 0, 0), wx='木', dz_in=['子', '寅', '辰'], dz_out=['午', '申', '戌']),
    '巽': dict(bits=(0, 1, 1), wx='木', dz_in=['丑', '亥', '酉'], dz_out=['未', '巳', '卯']),
    '坎': dict(bits=(0, 1, 0), wx='水', dz_in=['寅', '辰', '午'], dz_out=['申', '戌', '子']),
    '艮': dict(bits=(0, 0, 1), wx='土', dz_in=['辰', '午', '申'], dz_out=['戌', '子', '寅']),
    '坤': dict(bits=(0, 0, 0), wx='土', dz_in=['未', '巳', '卯'], dz_out=['丑', '亥', '酉']),
}
BITS_TO_TRIGRAM = {v['bits']: k for k, v in TRIGRAMS.items()}

# 八宫累计翻爻（自下而上，0=初爻）：本宫/一世/.../五世/游魂/归魂
_FLIPSETS = {0: set(), 1: {0}, 2: {0, 1}, 3: {0, 1, 2}, 4: {0, 1, 2, 3},
             5: {0, 1, 2, 3, 4}, 6: {0, 1, 2, 4}, 7: {4}}
_POS_NAME = {0: '本宫', 1: '一世', 2: '二世', 3: '三世', 4: '四世', 5: '五世', 6: '游魂', 7: '归魂'}
# 世爻 index，应=世±3
_SHIYING = {0: (5, 2), 1: (0, 3), 2: (1, 4), 3: (2, 5), 4: (3, 0), 5: (4, 1), 6: (3, 0), 7: (2, 5)}

MONTH_RULER = {'寅': '木', '卯': '木', '巳': '火', '午': '火', '申': '金', '酉': '金',
               '亥': '水', '子': '水', '辰': '土', '戌': '土', '丑': '土', '未': '土'}

_SHEN = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']
_SHEN_START = {'甲': 0, '乙': 0, '丙': 1, '丁': 1, '戊': 2, '己': 3, '庚': 4, '辛': 4, '壬': 5, '癸': 5}


def _build_palace_map():
    """生成全部 64 卦 → (卦宫, 卦宫五行, 宫位名, 世index, 应index)。"""
    m = {}
    for head, info in TRIGRAMS.items():
        base = list(info['bits']) * 2  # 八纯卦六爻
        for pos, flips in _FLIPSETS.items():
            lines = base[:]
            for i in flips:
                lines[i] ^= 1
            key = tuple(lines)
            shi, ying = _SHIYING[pos]
            m[key] = dict(gong=head, gong_wx=info['wx'], pos_name=_POS_NAME[pos],
                          shi=shi, ying=ying)
    return m


PALACE_MAP = _build_palace_map()


def liuqin(gong_wx: str, yao_wx: str) -> str:
    """六亲：以卦宫五行为我。"""
    if yao_wx == gong_wx:
        return '兄弟'
    if SHENG[yao_wx] == gong_wx:
        return '父母'   # 生我者
    if SHENG[gong_wx] == yao_wx:
        return '子孙'   # 我生者
    if KE[gong_wx] == yao_wx:
        return '妻财'   # 我克者
    if KE[yao_wx] == gong_wx:
        return '官鬼'   # 克我者
    raise ValueError(f'六亲无解: {gong_wx} {yao_wx}')


def xunkong(day_gz: str) -> list[str]:
    """旬空：由日干支推空亡两地支。"""
    g = GAN.index(day_gz[0])
    z = ZHI.index(day_gz[1])
    base = (z - g) % 12  # 旬首地支 index
    return [ZHI[(base + 10) % 12], ZHI[(base + 11) % 12]]


def wangshuai(yao_wx: str, month_zhi: str) -> str:
    """旺相休囚死（四季土旺近似），以月令为当令。"""
    w = MONTH_RULER[month_zhi]
    if yao_wx == w:
        return '旺'
    if SHENG[w] == yao_wx:
        return '相'
    if SHENG[yao_wx] == w:
        return '休'
    if KE[yao_wx] == w:
        return '囚'
    if KE[w] == yao_wx:
        return '死'
    raise ValueError


def liushen(day_gan: str) -> list[str]:
    """六神，初爻→上爻。"""
    s = _SHEN_START[day_gan]
    return [_SHEN[(s + i) % 6] for i in range(6)]


def _bits_of(inner: str, outer: str) -> tuple:
    return TRIGRAMS[inner]['bits'] + TRIGRAMS[outer]['bits']


def _dizhi_of(inner: str, outer: str) -> list[str]:
    return TRIGRAMS[inner]['dz_in'] + TRIGRAMS[outer]['dz_out']


def _rel(a_wx: str, b_wx: str) -> str:
    """a 对 b 的作用。"""
    if a_wx == b_wx:
        return '比和'
    if SHENG[a_wx] == b_wx:
        return '生'
    if KE[a_wx] == b_wx:
        return '克'
    if SHENG[b_wx] == a_wx:
        return '被生'
    if KE[b_wx] == a_wx:
        return '被克'
    return '无'


def paipan(inner: str, outer: str, month_zhi: str, day_gz: str, moving=None):
    """排盘。

    inner/outer：内外经卦名（如 '坎' '坤'）。
    month_zhi：月支。day_gz：日干支（两字，如 '庚辰'）。
    moving：动爻 index 列表，0=初爻 … 5=上爻。
    返回 dict，含六爻、世应、卦宫、旬空、合冲、变卦/化爻。
    """
    moving = sorted(moving or [])
    bits = _bits_of(inner, outer)
    info = PALACE_MAP[bits]
    dz = _dizhi_of(inner, outer)
    shen = liushen(day_gz[0])
    kong = set(xunkong(day_gz))
    day_zhi = day_gz[1]

    yaos = []
    for i in range(6):
        z = dz[i]
        wx = ZHI_WX[z]
        yaos.append(dict(
            idx=i, name=['初', '二', '三', '四', '五', '上'][i],
            zhi=z, wx=wx, liuqin=liuqin(info['gong_wx'], wx),
            shen=shen[i], wang=wangshuai(wx, month_zhi),
            kong=(z in kong), moving=(i in moving),
            shi=(i == info['shi']), ying=(i == info['ying']),
        ))

    # 变卦/化爻
    bian = None
    if moving:
        nb = list(bits)
        for i in moving:
            nb[i] ^= 1
        bi = BITS_TO_TRIGRAM[tuple(nb[:3])]
        bo = BITS_TO_TRIGRAM[tuple(nb[3:])]
        bdz = _dizhi_of(bi, bo)
        hua = {}
        for i in moving:
            z = bdz[i]
            hua[i] = dict(zhi=z, wx=ZHI_WX[z], liuqin=liuqin(info['gong_wx'], ZHI_WX[z]),
                          rel_to_ben=_rel(ZHI_WX[z], yaos[i]['wx']))  # 化爻对本爻：生=回头生，克=回头克
        bian = dict(inner=bi, outer=bo, hua=hua)

    # 爻间六合六冲
    he, chong = [], []
    for a in range(6):
        for b in range(a + 1, 6):
            pair = {yaos[a]['zhi'], yaos[b]['zhi']}
            if any(pair == set(p) for p in LIUHE):
                he.append((a, b))
            if any(pair == set(p) for p in LIUCHONG):
                chong.append((a, b))

    # 日月对各爻的合冲
    dayhe = [i for i in range(6) if any({yaos[i]['zhi'], day_zhi} == set(p) for p in LIUHE)]
    daychong = [i for i in range(6) if any({yaos[i]['zhi'], day_zhi} == set(p) for p in LIUCHONG)]
    monthchong = [i for i in range(6) if any({yaos[i]['zhi'], month_zhi} == set(p) for p in LIUCHONG)]

    return dict(
        gong=info['gong'], gong_wx=info['gong_wx'], pos_name=info['pos_name'],
        inner=inner, outer=outer, month=month_zhi, day=day_gz,
        xunkong=sorted(kong), yaos=yaos, bian=bian,
        he=he, chong=chong, dayhe=dayhe, daychong=daychong, monthchong=monthchong,
    )


def render(p) -> str:
    """文本排盘，自上而下，供喂给口令或人读。"""
    L = []
    L.append(f"卦宫：{p['gong']}宫（{p['gong_wx']}）· {p['pos_name']}　内{p['inner']}外{p['outer']}")
    L.append(f"月建：{p['month']}　日辰：{p['day']}　旬空：{'、'.join(p['xunkong'])}")
    L.append("六神  六亲  地支(五行)  旺衰  动符  世应  备注")
    sym = {True: None}
    for y in reversed(p['yaos']):  # 上→初
        dongfu = '－'
        if y['moving']:
            dongfu = '⭕' if _bits_of(p['inner'], p['outer'])[y['idx']] == 1 else '❌'
        sy = '世' if y['shi'] else ('应' if y['ying'] else '  ')
        note = []
        if y['kong']:
            note.append('空')
        if y['moving'] and p['bian']:
            h = p['bian']['hua'][y['idx']]
            tag = '回头' + h['rel_to_ben'] if h['rel_to_ben'] in ('生', '克') else h['rel_to_ben']
            note.append(f"化{h['liuqin']}{h['zhi']}({tag})")
        L.append(f" {y['shen']}  {y['liuqin']}  {y['zhi']}({y['wx']})  {y['wang']}  {dongfu}  {sy}  {' '.join(note)}")
    def names(pairs):
        return '、'.join(f"{p['yaos'][a]['name']}{p['yaos'][a]['zhi']}-{p['yaos'][b]['name']}{p['yaos'][b]['zhi']}" for a, b in pairs)
    if p['he']:
        L.append(f"爻间六合：{names(p['he'])}")
    if p['chong']:
        L.append(f"爻间六冲：{names(p['chong'])}")
    if p['bian']:
        L.append(f"变卦：内{p['bian']['inner']}外{p['bian']['outer']}")
    return '\n'.join(L)


def _selftest():
    # 旬空
    assert xunkong('甲子') == ['戌', '亥'], xunkong('甲子')
    assert xunkong('庚辰') == ['申', '酉'], xunkong('庚辰')
    assert xunkong('乙酉') == ['午', '未'], xunkong('乙酉')
    # 旺衰
    assert wangshuai('木', '卯') == '旺'
    assert wangshuai('火', '寅') == '相'
    assert wangshuai('水', '寅') == '休'
    assert wangshuai('金', '寅') == '囚'
    assert wangshuai('土', '寅') == '死'
    assert wangshuai('土', '辰') == '旺'
    # 地水师（坎宫归魂）：六亲、世应、地支
    p = paipan('坎', '坤', '酉', '庚辰', moving=[1, 4])
    assert p['gong'] == '坎' and p['gong_wx'] == '水' and p['pos_name'] == '归魂'
    zhis = [y['zhi'] for y in p['yaos']]
    assert zhis == ['寅', '辰', '午', '丑', '亥', '酉'], zhis
    lq = [y['liuqin'] for y in p['yaos']]
    assert lq == ['子孙', '官鬼', '妻财', '官鬼', '兄弟', '父母'], lq
    assert p['yaos'][2]['shi'] and p['yaos'][5]['ying']
    # 辰酉合、五爻亥化戌官鬼、二爻辰化巳妻财
    assert (1, 5) in p['he'], p['he']
    assert p['bian']['inner'] == '坤' and p['bian']['outer'] == '坎'
    assert p['bian']['hua'][4]['zhi'] == '戌' and p['bian']['hua'][4]['liuqin'] == '官鬼'
    assert p['bian']['hua'][1]['zhi'] == '巳' and p['bian']['hua'][1]['liuqin'] == '妻财'
    # 父母酉金应、临酉月当令、旬空
    assert p['yaos'][5]['kong'] and p['yaos'][5]['wang'] == '旺'
    print('selftest OK')
    print()
    print(render(p))


if __name__ == '__main__':
    _selftest()
