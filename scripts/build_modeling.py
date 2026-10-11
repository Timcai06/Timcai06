"""Lay out each modeling project as a full-width lead figure plus readable supporting figures.

Figures come from the categorized archive (~/Desktop/数模论文插图, built from ~/School/数模).
Layout (same idea as the clawd-mv / Sophon key visuals): the first figure is the lead,
shown large on the left; the rest are stacked on the right. Every figure sits on an
identical white card (same margin, hairline border) and carries a number badge that
matches the caption list under the image.
Run: python3 scripts/build_modeling.py   (rewrites assets/modeling/*.jpg and the README folds)
"""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/modeling'
ARCHIVE = Path.home() / 'Desktop/数模论文插图'
W, GAP, GUTTER = 2400, 16, '#0d1117'
BORDER, BADGE = '#d0d7de', '#24292f'
NUM = '①②③④⑤⑥'

# README title -> (archive folder, repo, slug, [(archive stem, caption)]); first figure = lead
PROJECTS = {
    '微网与外部电网电力调控': ('05_微网与外部电网电力调控', '26National_MathModel_Electricty', 'electricity', [
        ('monthly_storage_3d', '安全裕量策略的月均储电量三维曲面'),
        ('monthly_storage', '全年运行矩阵：基线与安全裕量的储电量、计划购电和应急购电逐日对照'),
        ('gate_decisions', '合同更新的经济价值：日期热力、预计与事后收益对照、累计费用差'),
        ('representative_dispatch', '代表日电量流向对照、购电时序与储电量')]),
    '霍尔木兹海峡与国际油价': ('01_霍尔木兹海峡与国际油价', '26_MathModel_Tunnel', 'tunnel', [
        ('布伦特收益率与波动率', '布伦特原油收益率与滚动波动率'),
        ('蒙特卡洛情景树高级组合图', '中长期油价调节模型蒙特卡洛情景树')]),
    '农作物种植策略优化': ('02_农作物种植策略优化', '26_MathModel_Agriculture', 'agriculture', [
        ('land_utilization_modes', '问题二各土地类型的复种季利用率与水浇地模式切换'),
        ('legume_binding_map', '问题二三年豆类轮作约束的地块–窗口绑定图'),
        ('crop_shift_bubble', '问题三相对问题二的类别–年份面积调整'),
        ('crop_structure_comparison', '问题二与问题三各年份作物类别面积结构')]),
    '穿越沙漠': ('03_穿越沙漠', '26_MathModel_Desert', 'desert', [
        ('maps_overview', '六关地图的规范图结构与确定天气最优轨迹'),
        ('robust_load_calibration', '第六关错峰角色的二维装载可行域与分布鲁棒入选点'),
        ('level4_frontier', '第四关候选策略在基准和不利天气下的训练收益–风险前沿'),
        ('level5_equilibrium', '第五关均衡的空间路径、行动时序与偏离复核')]),
    '古代玻璃成分分析': ('04_古代玻璃成分分析', '26_MathModel_Glass', 'glass', [
        ('proportionality_heatmaps', '高钾与铅钡玻璃的比例性矩阵')]),
}


def font(size):
    for p in ('/System/Library/Fonts/Menlo.ttc', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


def mat(src, size):
    """Figure contained on a white card with a uniform margin and hairline border."""
    w, h = size
    im = Image.open(src).convert('RGB')
    m = max(20, round(min(w, h) * 0.04))
    im.thumbnail((w - 2 * m, h - 2 * m), Image.Resampling.LANCZOS)
    c = Image.new('RGB', size, 'white')
    c.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    ImageDraw.Draw(c).rectangle((0, 0, w - 1, h - 1), outline=BORDER, width=2)
    return c


def ratio(src):
    w, h = Image.open(src).size
    return w / h


def save(img, name):
    img.save(OUT / f'{name}.png', optimize=True)
    return name


def img_tag(name, cap):
    return f'<img src="./assets/modeling/{name}.png" width="100%" alt="{cap}"><br><sub>{cap}</sub>'


def main():
    for f in list(OUT.glob('*.png')) + list(OUT.glob('*.jpg')):
        f.unlink()
    readme = (ROOT / 'README.md').read_text()
    for title, (folder, repo, slug, figs) in PROJECTS.items():
        src = lambda stem: ARCHIVE / folder / '01_论文正式插图' / f'{stem}.png'
        a = readme.index(f'<summary><b>{title}</b>')
        b = readme.index('</details>', a)
        blk = readme[a:b]
        head = re.search(r'<p><sub>(.+?) · 论文正式插图 (\d+) 张', blk)
        desc = re.search(r'</b> — ([^<]+)</summary>', blk).group(1)
        summary = re.search(r'<summary>.*?</summary>\n<br>\n', blk, re.S).group(0)
        repo_btn = f'<a href="https://github.com/Timcai06/{repo}"><kbd>仓库 / Repo ↗</kbd></a>'
        # Lead: full width, its own proportions (clamped so it never gets taller than 4:3).
        (lead_stem, lead_cap), rest = figs[0], figs[1:]
        r0 = max(ratio(src(lead_stem)), 4 / 3)
        lead = save(mat(src(lead_stem), (2000, round(2000 / r0))), f'{slug}-1')
        html = [f'<p>{img_tag(lead, lead_cap)}</p>']
        # Supporting figures: wide ones get a full row, the others pair up in two columns.
        wide = [(s_, c_) for s_, c_ in rest if ratio(src(s_)) >= 2.0]
        std = [(s_, c_) for s_, c_ in rest if ratio(src(s_)) < 2.0]
        rows, k = [], 2
        for stem, cap in wide:
            r = ratio(src(stem))
            n = save(mat(src(stem), (2000, round(2000 / r))), f'{slug}-{k}'); k += 1
            rows.append(f'<tr>\n<td colspan="2" valign="top">{img_tag(n, cap)}</td>\n</tr>')
        info_used = False
        for i in range(0, len(std), 2):
            pair = std[i:i + 2]
            r = min(ratio(src(s_)) for s_, _ in pair)      # shared card shape -> equal heights
            cells = []
            for stem, cap in pair:
                n = save(mat(src(stem), (1200, round(1200 / r))), f'{slug}-{k}'); k += 1
                cells.append(f'<td width="50%" valign="top">{img_tag(n, cap)}</td>')
            if len(pair) == 1:
                info_used = True
                cells.append(f'<td width="50%" valign="middle"><p>{desc}</p>'
                             f'<p><sub>论文正式插图 {head.group(2)} 张</sub></p><p>{repo_btn}</p></td>')
            rows.append('<tr>\n' + '\n'.join(cells) + '\n</tr>')
        if rows:
            html.append('<table>\n' + '\n'.join(rows) + '\n</table>')
        if not info_used:
            html.append(f'<p>{repo_btn}</p>')
        body = (summary + f'<p><sub>{head.group(1)} · 论文正式插图 {head.group(2)} 张，以下选 {len(figs)} 张</sub></p>\n'
                + '\n'.join(html) + '\n')
        readme = readme[:a] + body + readme[b:]
        print(f'{title}: lead {lead_stem} ({r0:.2f}), wide {len(wide)}, paired {len(std)}')
    (ROOT / 'README.md').write_text(readme)


if __name__ == '__main__':
    main()
