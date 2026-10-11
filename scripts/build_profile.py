"""Build self-contained, GitHub-safe SVG editor artwork. No scripts/foreignObject."""
from pathlib import Path
from html import escape
import base64
root = Path(__file__).resolve().parents[1]
out = root / 'assets/editor'
out.mkdir(exist_ok=True)
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
def text(x,y,s,size=18,color='#ccd4ea',extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(s)}</text>'
def rect(x,y,w,h,c,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'
def svg(w,h,body,title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><g font-family="{FONT}">'+''.join(body)+'</g></svg>'
def pixel(name):
    # Prefer the calmer v2 backgrounds when present; originals stay untouched.
    v2 = root/'assets/pixel-lab/v2'/name
    return v2 if v2.exists() else root/'assets/pixel-lab'/name
def pixel_b64(name, colors=8):
    # v2 plates are quantized to an 8-color palette (no dithering, no resampling)
    # at embed time; the generated PNGs on disk are left as-is.
    path = pixel(name)
    if path.parent.name != 'v2':
        return base64.b64encode(path.read_bytes()).decode()
    from PIL import Image
    import io
    image = Image.open(path).convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    buffer = io.BytesIO()
    image.save(buffer, 'PNG', optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()
bg = pixel_b64('background.png')
b=[f'<image width="1200" height="800" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{bg}"/>',rect(0,0,1200,800,'#070b1b','opacity=".12"'),rect(53,73,1094,674,'#020410','rx="13" opacity=".65"'),rect(45,60,1110,674,'#111728','rx="10" fill-opacity=".96" stroke="#576078"')]
b += [rect(46,100,1108,1,'#343d54')]
for x,c in [(69,'#f28c84'),(90,'#e9ba79'),(111,'#97bf9b')]:
    b.append(f'<circle cx="{x}" cy="80" r="6" fill="{c}"/>')
b += [text(425,86,"Tim's workspace — profile",16,'#adb7cf'),rect(46,102,48,602,'#141a2d'),rect(94,102,214,602,'#131a2c'),rect(307,102,1,602,'#303950')]
for y,s in [(141,'▣'),(196,'⌕'),(251,'⑂'),(306,'▷'),(640,'⚙')]: b.append(text(60,y,s,25,'#8491ae'))
b += [rect(46,110,3,44,'#e5b581'),text(111,132,'EXPLORER',13,'#8995b2'),text(111,169,'⌄ TIMCAI06',16,'#dde4f5')]
files=[('  about.ts','#efc38f'),('⌄ projects/','#a8b8d4'),('    agents.md','#a8b8d4'),('    products.md','#a8b8d4'),('    creative.md','#a8b8d4'),('⌄ research/','#a8b8d4'),('    models.py','#a8b8d4'),('  toolbox.json','#a8b8d4'),('  contact.md','#a8b8d4')]
b += [rect(95,182,211,33,'#29314a')]
for i,(s,c) in enumerate(files): b.append(text(108,204+i*34,s,15,c))
b += [text(110,660,'main*',15,'#a1c0a8'),text(110,686,'personal workspace',12,'#7683a0'),rect(308,102,846,45,'#0e1423'),rect(308,102,166,45,'#1b2338'),rect(308,102,166,2,'#edbf88'),text(327,131,'TS about.ts ×',17,'#e8c39a'),text(497,131,'projects.md',16,'#7f8ba7'),text(674,131,'contact.md',16,'#7f8ba7'),text(332,175,'Timcai06  ›  about.ts  ›  tim',14,'#8290ac')]
lines=[('// Hello, world.','#7886a6'),('export const tim = {','#c6a6ed'),('  name: "Tim Cai",','#f2c48f'),('  role: "Student developer",','#b0d6bf'),('  basedIn: "Shanghai",','#b0d6bf'),('  building: [','#ced7ee'),('    "AI agents & research tools",','#b0d6bf'),('    "Observable ML systems",','#b0d6bf'),('    "Thoughtful full-stack products"','#b0d6bf'),('  ],','#ced7ee'),('  mindset: "Curiosity → craft"','#f2c48f'),('};','#c6a6ed')]
for i,(s,c) in enumerate(lines):
    y=215+i*28
    if i==1: b.append(rect(309,y-20,843,28,'#222c43','opacity=".7"'))
    b += [text(337,y,str(i+1),16,'#606e8a'),text(380,y,s,20,c,'xml:space="preserve"')]
b += [rect(308,554,846,1,'#3a435a'),text(333,583,'TERMINAL',13,'#edc38c'),text(452,583,'OUTPUT',13,'#6d7a97'),rect(333,591,78,2,'#e8b983'),text(333,622,'~/Timcai06 $ cat now.txt',17,'#9dc9b1'),text(333,651,'Learning deeply. Building across the stack.',17,'#c3cde4'),text(333,680,'从模型、数据到界面，让想法成为可用的产品。',18,'#a5b2ce'),rect(46,704,1108,29,'#313952'),text(62,724,'⑂ main',14,'#f5d2a4'),text(322,724,'TypeScript',14,'#bcc8e2'),text(887,724,'UTF-8   LF   ☾',14,'#bcc8e2')]
(out/'workspace.svg').write_text(svg(1200,800,b,"Tim's pixel-night editor workspace: AI agents, observable ML and full-stack products"))
for name,label,path,comment in [
 ('about','about.md','profile / about.md','A little context behind the code.'),
 ('agents','agents.md','projects / agents.md','Research, learning & observable systems'),
 ('products','products.md','projects / products.md','Useful tools, from data to interface'),
 ('creative','creative.md','projects / creative.md','Web experiences, motion & experiments'),
 ('toolbox','toolbox.json','profile / toolbox.json','The tools I build and learn with'),
 ('models','models.py','research / models.py','Optimization, uncertainty & mathematical modeling')]:
    b=[rect(0,0,1200,110,'#151d30','rx="7"'),rect(0,0,1200,38,'#20283e','rx="7"'),rect(0,34,1200,4,'#20283e'),rect(0,0,225,3,'#e9bd8a'),text(20,26,label,17,'#edc895'),text(254,26,path,14,'#8492ad'),text(24,81,'01',18,'#64728e'),text(73,81,'// '+comment,23,'#b8c8e3')]
    (out/(name+'.svg')).write_text(svg(1200,110,b,path))
print('Built editor SVGs')

# Project artwork uses the existing pixel scenes only as a backdrop.
projects = [
    ('sciscope', 'SciScope', 'Evidence-grounded research',
     ['文献与证据驱动的研究工作流', 'Python RAG 后端 × Go 终端界面'],
     ['Python', 'RAG', 'Go TUI'], '#9cc8ec',
     ['Retrieve literature', 'Read with evidence', 'Research in the terminal']),
    ('educanvas', 'EduCanvas', 'A personal agent for learning',
     ['以教育能力为核心的通用个人 Agent', 'Notebook 串联文档、对话、Canvas 与学习'],
     ['TypeScript', 'Agent runtime', 'PostgreSQL'], '#e8c194',
     ['Organize a notebook', 'Connect tools & skills', 'Learn across modalities']),
    ('pulsegraph', 'PulseGraph', 'See what your training is doing',
     ['本地优先的 PyTorch 训练可观测性工作台', '模型图、训练指标、检查点与推理回放'],
     ['PyTorch', 'FastAPI', 'React'], '#b8b0ed',
     ['Inspect the model graph', 'Observe training metrics', 'Replay & compare experiments']),
]
for slug,name,tagline,description,stack,accent,flow in projects:
    background = pixel_b64(f'{slug}.png')
    b = [f'<image width="1200" height="530" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{background}"/>',
         rect(0,0,1200,530,'#060b19','opacity=".25"'),
         rect(51,51,1104,450,'#040711','rx="10" opacity=".65"'),
         rect(42,40,1116,450,'#111829','rx="9" fill-opacity=".96" stroke="#526078"'),
         rect(43,80,1114,1,'#384258')]
    for x,c in [(65,'#f28c84'),(85,'#e9ba79'),(105,'#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="61" r="5" fill="{c}"/>')
    b += [text(440,67,name+' — project workspace',16,'#b8c4dc'),
          rect(43,82,215,380,'#151e32'),
          text(61,112,'EXPLORER',13,'#8795b0'),
          text(61,146,'⌄ '+name,18,accent),
          rect(43,162,214,35,'#29334c'),
          text(76,186,'README.md',17,accent),
          text(76,222,'capabilities',16,'#91a1bf'),
          text(76,256,'stack',16,'#91a1bf'),
          text(61,429,'Timcai06 /',14,'#7f90af'),
          text(61,449,name,16,accent),
          rect(258,82,899,42,'#0d1423'),
          rect(258,82,207,42,'#1b253a'),
          rect(258,82,207,2,accent),
          text(278,110,'M↓ README.md ×',17,accent),
          text(493,110,'project overview',16,'#8594b0')]
    content = [(name,36,accent),(tagline,24,'#e2e8f5'),('',18,'#8394b4'),
               (description[0],22,'#b9c7df'),(description[1],22,'#b9c7df'),
               ('',18,'#8394b4'),(' / '.join(stack),19,accent)]
    for i,(line,size,color) in enumerate(content):
        y=171+i*34
        b += [text(278,y,str(i+1).zfill(2),15,'#5e708e'), text(326,y,line,size,color)]
    b += [rect(258,402,899,1,'#384258'),text(280,431,'WORKFLOW',12,accent),
          text(280,452,' → '.join(flow[:2]),16,'#aabbd5'),
          rect(43,462,1114,27,'#29354c'),text(61,481,'Markdown',13,accent),
          text(278,481,flow[2],14,'#b9c7df')]
    (out/(slug+'.svg')).write_text(svg(1200,530,b,name+' — '+tagline))
print('Built three project editor windows')

# Compact editor compositions are designed for half-width README columns.
compact = [
 ('tttim','TTT-I-M','Personal web & content studio',['电影感个人网站','内容工作室与交互体验'],'React / GSAP / R3F','#e4b6eb'),
 ('bdi','BDI','Visual bridge inspection',['桥梁视觉检测原型','分割模型与全栈工作流'],'YOLOv8 / FastAPI / Next.js','#efba85'),
 ('sciscope','SciScope','Evidence-grounded research',['文献与证据驱动的研究','Python RAG × Go TUI'],'Python / RAG / Go','#9ec9e9'),
 ('educanvas','EduCanvas','A personal learning agent',['通用个人 Agent 平台','文档、对话与学习画布'],'TypeScript / PostgreSQL','#e8c397'),
 ('pulsegraph','PulseGraph','Training observability',['本地优先的训练工作台','模型图、指标与推理回放'],'PyTorch / FastAPI / React','#b9afea')]
for slug,name,tagline,desc,stack,accent in compact:
    data=pixel_b64(f'{slug}.png')
    b=[f'<image width="640" height="430" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{data}"/>',
       rect(24,52,592,336,'#0c1425','rx="8" fill-opacity=".95" stroke="#626b83"'),
       rect(25,88,590,1,'#404b64')]
    for x,c in [(43,'#f28c84'),(59,'#e9ba79'),(75,'#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="70" r="4" fill="{c}"/>')
    b += [text(107,76,name+' / README.md',16,'#c7d2e5'),
          rect(25,89,590,33,'#1d2940'),rect(25,89,143,2,accent),text(40,112,'README.md',16,accent),text(190,112,'overview',15,'#879ab6')]
    for i,(line,size,col) in enumerate([(name,38,accent),(tagline,20,'#d6e0ef'),('',16,'#60738f'),(desc[0],23,'#c4d3e8'),(desc[1],23,'#c4d3e8'),(stack,18,accent)]):
        y=169+i*33
        b += [text(39,y,str(i+1).zfill(2),14,'#6d809f'),text(77,y,line,size,col)]
    b += [rect(25,357,590,30,'#26334a'),text(40,378,'Timcai06',14,accent),text(476,378,'Markdown',14,'#aabbce')]
    (out/(slug+'-compact.svg')).write_text(svg(640,430,b,name+' — '+tagline))
# The animation-series banner is vector artwork: a timeline and scene frames.
b=[rect(0,0,1200,350,'#10101e'),rect(32,28,1136,294,'#181626','rx="8" stroke="#595064"'),
   text(57,60,'animation-series / timeline.ts',18,'#c8b5d8'),text(57,128,'Code in motion.',48,'#edcaa5'),
   text(59,169,'用代码做动画',25,'#c3b9d8'),text(59,213,'Scenes → cameras → timelines → frames',20,'#9d9fba')]
for j,(x,h,c) in enumerate([(753,75,'#a7b7d9'),(838,119,'#e5ad90'),(933,91,'#aa94c4')]):
    b += [rect(x,95,62,h,c,'opacity=".85"'),text(x,243,'0'+str(j+1),14,'#978aa8')]
b += [rect(57,272,1084,2,'#61506f')]
for i in range(22): b.append(rect(60+i*49,264,1,17,'#776481'))
for x,w,c in [(65,207,'#ad8ea9'),(286,164,'#9aaac3'),(464,271,'#bc9479'),(749,200,'#84769e')]: b.append(rect(x,291,w,8,c))
b += [rect(889,78,2,232,'#f3c399'),text(1003,115,'FRAME',14,'#a899b6'),text(1003,150,'{ t }',25,'#efc49b')]
(out/'animation-series.svg').write_text(svg(1200,350,b,'Code in motion — 用代码做动画系列'))
print('Built compact cards and animation series')
