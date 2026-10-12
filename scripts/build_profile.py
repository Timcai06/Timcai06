"""Build self-contained, GitHub-safe SVG editor artwork. No scripts/foreignObject."""
from pathlib import Path
from html import escape
import base64
import json
root = Path(__file__).resolve().parents[1]
out = root / 'assets/editor'
out.mkdir(exist_ok=True)
# Imported (e.g. by build_social.py) for data and helpers only: no files are written,
# so a local run cannot overwrite the CI-built PNG bytes inside these SVGs.
WRITE = __name__ == '__main__'
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
def text(x,y,s,size=18,color='#ccd4ea',extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(s)}</text>'
def rect(x,y,w,h,c,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'
def svg(w,h,body,title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title><g font-family="{FONT}">'+''.join(body)+'</g></svg>'
def pixel(name):
    return root/'assets/pixel-lab/v2'/name
def pixel_b64(name, colors=8):
    # v2 plates are quantized to an 8-color palette (no dithering, no resampling)
    # at embed time; the generated PNGs on disk are left as-is.
    path = pixel(name)
    from PIL import Image
    import io
    image = Image.open(path).convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    buffer = io.BytesIO()
    image.save(buffer, 'PNG', optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()
bg = pixel_b64('background.png')
# ---- Profile workspace: pixel backdrop + detailed editor window --------------
TOK = dict(kw='#c6a6ed', type='#7fd1c7', var='#8fc4f0', prop='#a9c3e8', str='#b0d6bf', op='#93a3c4',
           punct='#7f89a3', comment='#6c7a98', b1='#f2c48f', b2='#d39ae8', b3='#7fb8e8', plain='#ced7ee')
def code_line(x, y, tokens, size, extra=''):
    spans = ''.join(f'<tspan fill="{TOK[k]}"' + (' font-style="italic"' if k == 'comment' else '') + f'>{escape(t)}</tspan>' for t, k in tokens)
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve" {extra}>{spans}</text>'
# Profile content is a static illustration, not a live editor or repository tree.
# Project descriptions/stacks: the respective repository READMEs (see assets/editor/README.md).
S=lambda t,k:(t,k)
sp=('  ','plain')
s1=(' ','plain')
def kv(key,*rest,indent=sp):
    return [indent,S(key,'prop'),S(':','punct'),s1,*rest]
def strs(items,bk):
    parts=[S('[',bk)]
    for j,v in enumerate(items):
        parts.append(S(f'"{v}"','str'))
        if j<len(items)-1: parts.append(S(', ','punct'))
    return parts+[S(']',bk)]

code=[[S('// A profile in code — Tim Cai','comment')],
      [S('export','kw'),s1,S('const','kw'),s1,S('tim','var'),s1,S('=','op'),s1,S('{','b1')]]
fields=[]
def field(key,parts,kind='string'):
    fields.append((key,kind,len(code)+1))
    code.append(kv(key,*parts))
def value(s):
    return [S(f'"{s}"','str'),S(',','punct')]
field('name',value('Tim Cai'))
field('role',value('Student developer'))
field('basedIn',value('Shanghai'))
field('focus',strs(['AI agents','ML observability','Full-stack'],'b2')+[S(',','punct')],'array')
code.append([])
field('projects',[S('{','b2')],'object')
for key,description in [
    ('EduCanvas','Personal agent for learning'),
    ('SciScope','Evidence-grounded research / Go TUI'),
    ('PulseGraph','Local PyTorch training observability'),
    ('portfolio','React / Vite / GSAP / R3F'),
    ('clawdMV','TypeScript / Three.js music video'),
]:
    code.append(kv(key,*value(description),indent=('    ','plain')))
code.append([sp,S('}','b2'),S(',','punct')])
code.append([])
field('stack',[S('{','b2')],'object')
for key,items in [
    ('web',['React','Vite','GSAP']),
    ('backend',['Python','FastAPI','Node.js']),
    ('data',['PostgreSQL','pgvector']),
    ('research',['PyTorch','HiGHS']),
    ('motion',['Three.js','TypeScript']),
]:
    code.append(kv(key,*strs(items,'b3'),S(',','punct'),indent=('    ','plain')))
code.append([sp,S('}','b2'),S(',','punct')])
code.append([])
field('modeling',[S('[','b2')],'array')
for item in ['Energy dispatch / LP + MPC', 'Crop planning / MILP + CVaR', 'Oil prices / Markov + Monte Carlo',
             'Desert decisions / MDP', 'Glass composition / CLR + clustering']:
    code.append([('    ','plain'),*value(item)])
code.append([sp,S(']','b2'),S(',','punct')])
code.append([S('}','b1'),s1,S('as','kw'),s1,S('const','kw'),S(';','punct')])

CX,CY,STEP,SIZE=384,196,20,16
CW=SIZE*0.6
TERMINAL_Y=CY+(len(code)-1)*STEP+30
STATUS_Y=TERMINAL_Y+138
HEIGHT=STATUS_Y+96
# Catch content growth before it reaches the minimap. This is a conservative
# monospace estimate; the rendered result must still be inspected after changes.
assert all(len(''.join(t for t,_ in line))*CW <= 680 for line in code)

b=['<defs><filter id="shadow" x="-6%" y="-6%" width="112%" height="118%"><feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
   f'<image width="1200" height="{HEIGHT}" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{bg}"/>',
   rect(0,0,1200,HEIGHT,'#070b1b','opacity=".12"'),
   rect(45,60,1110,STATUS_Y+30-60,'#111728','rx="10" fill-opacity=".97" stroke="#576078" filter="url(#shadow)"'),
   rect(46,100,1108,1,'#343d54')]
for x,c in [(69,'#f28c84'),(90,'#e9ba79'),(111,'#97bf9b')]:
    b.append(f'<circle cx="{x}" cy="80" r="6" fill="{c}"/>')
b += [rect(452,68,296,24,'#1a2133','rx="6" stroke="#2f3851"'),
      text(600,85,'⌕  Timcai06 — profile',13,'#9aa5c0','text-anchor="middle"'),
      text(1132,85,'▣  ◧  ▤',13,'#6f7b97','text-anchor="end"')]
# Activity bar and explorer.
b += [rect(46,101,48,STATUS_Y-101,'#141a2d'),rect(94,101,214,STATUS_Y-101,'#131a2c'),
      rect(307,101,1,STATUS_Y-101,'#303950'),rect(46,110,3,44,'#e5b581')]
for y,g,c in [(141,'▣','#d5dcef'),(196,'⌕','#8491ae'),(251,'⑂','#8491ae'),(306,'▷','#8491ae'),
              (361,'⧉','#8491ae'),(STATUS_Y-64,'◉','#8491ae'),(STATUS_Y-18,'⚙','#8491ae')]:
    b.append(text(60,y,g,24,c))
b += [text(111,132,'EXPLORER',12,'#8995b2','letter-spacing="1"'),text(292,132,'⋯',14,'#8995b2','text-anchor="end"'),
      text(108,162,'⌄ TIMCAI06',13,'#dde4f5','font-weight="700" letter-spacing=".5"')]
tree=[(0,'file','TS','#5aa2e8','about.ts','#efc38f'),
      (0,'dir','⌄','#8491ae','featured','#c3cde4'),
      (1,'proj','#e8c397',None,'EduCanvas','#a8b8d4'),(1,'proj','#9ec9e9',None,'SciScope','#a8b8d4'),
      (1,'proj','#e4b6eb',None,'TTT-I-M','#a8b8d4'),(1,'proj','#efba85',None,'BDI','#a8b8d4'),
      (1,'proj','#b9afea',None,'PulseGraph','#a8b8d4'),
      (0,'dir','⌄','#8491ae','motion','#c3cde4'),(1,'proj','#f28c84',None,'01-clawd-mv','#a8b8d4'),
      (0,'dir','⌄','#8491ae','math-model','#c3cde4'),
      *[(1,'proj','#7fd1c7',None,name,'#a8b8d4') for name in ['energy','agriculture','oil-prices','desert','glass']],
      (0,'file','{}','#e8c06a','toolbox.json','#a8b8d4'),(0,'file','M↓','#7fa7d9','contact.md','#a8b8d4')]
b += [rect(95,173,211,26,'#29314a'),rect(95,173,2,26,'#e5b581')]
for i,(lvl,kind,icon,ic,name,nc) in enumerate(tree):
    y=191+i*25; x=114+lvl*18
    if lvl: b.append(rect(119,y-18,1,25,'#323b55'))
    if kind=='proj':
        b += [text(x,y,'▸',12,'#6f7b97'),f'<circle cx="{x+21}" cy="{y-5}" r="4.5" fill="{icon}"/>',text(x+32,y,name,14,nc)]
    elif kind=='dir':
        b += [text(x,y,icon,14,ic),text(x+18,y,name,14,nc)]
    else:
        b += [text(x,y,icon,11,ic,'font-weight="700"'),text(x+26,y,name,14,nc)]
# Outline is derived from the same fields and line numbers as the editor.
outline_y=191+len(tree)*25+12
b += [rect(95,outline_y,212,1,'#2a3149'),text(108,outline_y+23,'⌄  OUTLINE',12,'#7f8aa6','letter-spacing=".5"'),
      text(114,outline_y+49,'{} tim',14,'#e8c39a')]
for i,(key,kind,line) in enumerate(fields):
    y=outline_y+75+i*23
    icon={'string':'ab','array':'[]','object':'{}'}[kind]
    b += [text(130,y,icon,11,'#7fd1c7'),text(155,y,key,13,'#a8b8d4'),
          text(290,y,str(line),11,'#6f7b97','text-anchor="end"')]
assert outline_y+75+(len(fields)-1)*23 < STATUS_Y-20
# Tabs and breadcrumbs.
b += [rect(308,101,846,40,'#0e1423'),rect(308,101,168,40,'#111728'),rect(308,101,168,2,'#edbf88'),
      text(324,126,'TS',11,'#5aa2e8','font-weight="700"'),text(348,126,'about.ts',15,'#e8c39a'),text(458,126,'×',14,'#8b95ae','text-anchor="end"'),
      rect(476,101,1,40,'#262e44'),text(492,126,'{}',11,'#e8c06a','font-weight="700"'),text(516,126,'toolbox.json',15,'#7f8ba7'),
      rect(652,101,1,40,'#262e44'),text(668,126,'M↓',11,'#7fa7d9','font-weight="700"'),text(694,126,'contact.md',15,'#7f8ba7'),
      rect(818,101,1,40,'#262e44'),text(1136,126,'⧉  ⋯',14,'#7f8ba7','text-anchor="end"'),
      code_line(326,164,[('Timcai06','punct'),('  ›  ','punct'),('TS ','var'),('about.ts','punct'),('  ›  ','punct'),('{} ','b1'),('tim','prop')],13)]
cursor=next(line-1 for key,_,line in fields if key=='projects')
b.append(rect(309,CY+cursor*STEP-15,770,STEP,'#1c2539'))
for i,tokens in enumerate(code):
    y=CY+i*STEP
    plain=''.join(t for t,_ in tokens)
    indent=len(plain)-len(plain.lstrip())
    for level in range(0,indent,2):
        b.append(rect(round(CX+level*CW)+1,y-15,1,STEP,'#2c3550'))
    if plain.rstrip().endswith(('{','[')):
        b.append(text(370,y-1,'⌄',12,'#56637f','text-anchor="middle"'))
    b.append(text(348,y,str(i+1),13,'#c9d2e6' if i==cursor else '#56637f','text-anchor="end"'))
    if tokens: b.append(code_line(CX,y,tokens,SIZE))
# Minimap, viewport and scrollbar all track the content height.
b += [rect(1084,145,1,TERMINAL_Y-154,'#262e44'),rect(1085,145,62,len(code)*5+14,'#ffffff','opacity=".04"'),
      rect(1148,145,6,TERMINAL_Y-154,'#151c2e'),rect(1149,155,4,160,'#4b5774','rx="2" opacity=".45"')]
for i,tokens in enumerate(code):
    x=1092
    for t,k in tokens:
        w=len(t)*0.78
        if t.strip(): b.append(rect(round(x,1),152+i*5,round(w,1),2.4,TOK[k],'opacity=".75"'))
        x+=w
# Existing terminal introduction; coordinates follow the expanded editor.
y=TERMINAL_Y
b += [rect(308,y,846,1,'#3a435a'),text(333,y+24,'PROBLEMS',12,'#6d7a97','letter-spacing=".5"'),
      text(425,y+24,'OUTPUT',12,'#6d7a97','letter-spacing=".5"'),text(505,y+24,'TERMINAL',12,'#edc38c','letter-spacing=".5"'),
      rect(505,y+31,70,2,'#e8b983'),text(1136,y+24,'zsh   +  ⌄   ×',13,'#7f8ba7','text-anchor="end"'),
      code_line(333,y+54,[('~/Timcai06','var'),(' $ ','b1'),('cat now.txt','plain')],15),
      text(333,y+77,'Learning deeply. Building across the stack.',15,'#c3cde4'),
      text(333,y+100,'从模型、数据到界面，让想法成为可用的产品。',16,'#a5b2ce'),
      code_line(333,y+123,[('~/Timcai06','var'),(' $ ','b1')],15),
      rect(round(333+len('~/Timcai06 $ ')*15*0.6)+2,y+111,9,15,'#edc38c','opacity=".85"')]
b += [rect(46,STATUS_Y,1108,29,'#313952'),rect(46,STATUS_Y,140,29,'#4a3f63'),
      text(60,STATUS_Y+20,'{} SVG profile',13,'#f5d2a4'),text(206,STATUS_Y+20,'Static illustration',12,'#bcc8e2'),
      text(1138,STATUS_Y+20,f'Ln {cursor+1}, Col 1    Spaces: 2    UTF-8    LF    TypeScript',13,'#bcc8e2','text-anchor="end"')]
if WRITE:
    (out/'workspace.svg').write_text(svg(1200,HEIGHT,b,"Tim's profile workspace: projects, technology stack and mathematical modeling"))
    print('Built workspace')

# Project cards: compact editor windows designed for half-width README columns.
compact = [
 ('tttim','TTT-I-M','Personal web & content studio',['电影感个人网站','内容工作室与交互体验'],['TypeScript','React','Next.js','Vite','GSAP','R3F','Vercel'],'#e4b6eb'),
 ('bdi','BDI','Visual bridge inspection',['桥梁视觉检测原型','分割模型与全栈工作流'],['Python','YOLOv8-seg','FastAPI','TypeScript','Next.js','React'],'#efba85'),
 ('sciscope','SciScope','Evidence-grounded research agent',['LangGraph 研究 Agent','工具编排 · 证据检索 · 流式交互'],['Python','Agent','LangGraph','RAG','FastAPI','PostgreSQL','DeepSeek','Go TUI','SSE'],'#9ec9e9'),
 ('educanvas','EduCanvas','A personal learning agent',['通用个人 Agent 平台','文档、对话与学习画布'],['TypeScript','Agent runtime','Node.js','PostgreSQL','Drizzle','pnpm','Docker'],'#e8c397'),
 ('pulsegraph','PulseGraph','Training observability',['本地优先的训练工作台','模型图、指标与推理回放'],['PyTorch','Python','FastAPI','TypeScript','React','Vite','SSE'],'#b9afea')]
TERMINAL_CMDS = {  # quick-start commands quoted from each repository README
 'tttim': [('npm run dev:landing',''),('npm run dev:studio','')],
 'bdi': [('./bdi check',''),('./scripts/dev-backend-real.sh','# 真正推理后端')],
 'sciscope': [('make backend','# 先启动后端 127.0.0.1:8000'),('make tui-demo','# 离线演示流程（无后端）')],
 'educanvas': [('make doctor','# 检查 Node、pnpm、Docker 与 .env'),('make all','# 启动全部本地服务')],
 'pulsegraph': [('make backend','# FastAPI on 127.0.0.1:8010'),('make frontend','')],
}
REPO_DIR = {'tttim':'TTT-I-M','bdi':'BDI','sciscope':'SciScope','educanvas':'EduCanvas','pulsegraph':'PulseGraph'}
def tspans(parts):
    return ''.join(f'<tspan fill="{c}"{extra}>{escape(t)}</tspan>' for t,c,extra in parts)
# Frames are decorative only: these marks are not charts, metrics or live status.
# Live data lives in one place per card, the status bar (see card_activity).
ACTIVITY = json.loads((root/'assets/editor/activity.json').read_text())['cards']
def card_activity(repo, accent):
    # Real commits by Tim on the default branch: lamp = any in the last 14 days,
    # bars = the last 12 calendar weeks (oldest left), then the last commit date. Text must end before
    # the right-hand 'Markdown   UTF-8   LF' (x≈453).
    from datetime import date, timedelta
    a = ACTIVITY[repo]
    active = a['last_commit'] and date.fromisoformat(a['last_commit']) >= date.today() - timedelta(days=14)
    out = [f'<circle cx="114" cy="494" r="3.5" fill="{accent if active else "#4b5774"}"/>']
    peak = max(a['weeks']) or 1
    for i, n in enumerate(a['weeks']):
        h = max(1, round(n / peak * 13))
        out.append(rect(126 + i * 6, 501 - h, 4, h, accent if n else '#4b5774', '' if n else 'opacity=".7"'))
    label = f"{sum(a['weeks'])} commits / 12w · {a['last_commit'] or '—'}"
    assert 206 + len(label) * 12 * 0.6 < 450
    out.append(text(206, 498, label, 12, '#aab6d2'))
    return out
CARD_ORDER = {'educanvas': 1, 'sciscope': 2, 'tttim': 3, 'bdi': 4, 'pulsegraph': 5}
def project_frame(slug, name, accent):
    edge, mark, label = '#536070', '#b1bac4', '#bac3ce'
    def line(d, color=mark, width=1.3, extra=''):
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
    def dot(x, y, color=mark, radius=2):
        return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>'
    # Outer rail breaks around the project label, middle-side ticks and signature.
    frame = [
        line('M 24 18 H 32 M 224 18 H 600 M 628 46 V 258 M 628 282 V 504 M 600 526 H 374 M 266 526 H 40 M 12 502 V 282 M 12 258 V 42', edge, 1),
        rect(40,8,176,20,'#101726','rx="4" fill-opacity=".92"'),
        text(50,22,f'{CARD_ORDER[slug]:02d}  /  {name}',11,label,'letter-spacing=".5"'),
        line('M 9 270 H 15 M 625 270 H 631',mark,1),
    ]
    if slug == 'educanvas':
        # Page layers, a folded corner and a small open-book signature.
        frame += [line('M 12 38 V 18 H 28 M 18 34 V 24 H 28'),
                  line('M 606 12 H 628 V 36 L 617 29 L 606 36 Z'),
                  line('M 12 506 V 526 H 34 M 18 506 V 520 H 34'),
                  line('M 628 510 V 526 H 610'),
                  line('M 292 522 Q 306 516 320 522 Q 334 516 348 522 V 530 Q 334 524 320 530 Q 306 524 292 530 Z M 320 522 V 530',accent)]
    elif slug == 'sciscope':
        # Brackets and linked reference points.
        frame += [line('M 30 12 H 12 V 38 M 610 12 H 628 V 38 M 12 506 V 530 H 30 M 610 530 H 628 V 506'),
                  line('M 286 520 H 282 V 532 H 286 M 354 520 H 358 V 532 H 354'),
                  line('M 299 526 H 341',edge),dot(300,526,accent),dot(320,526,accent),dot(340,526,accent),
                  line('M 592 15 V 21 M 582 15 V 21 M 572 15 V 21',edge,1)]
    elif slug == 'tttim':
        # Extended viewfinder crop marks and three timeline keyframes.
        frame += [line('M 6 34 V 12 H 28 M 610 12 H 634 V 34 M 6 510 V 532 H 28 M 610 532 H 634 V 510'),
                  line('M 302 521 L 307 526 L 302 531 L 297 526 Z M 320 521 L 325 526 L 320 531 L 315 526 Z M 338 521 L 343 526 L 338 531 L 333 526 Z',accent),
                  line('M 610 24 H 622 V 36 M 18 504 V 516 H 30',edge,1)]
    elif slug == 'bdi':
        # Chamfered corners and an abstract truss; no inspection result encoded.
        frame += [line('M 12 38 V 28 L 22 18 H 30 M 606 18 H 618 L 628 28 V 38 M 12 506 V 516 L 22 526 H 32 M 608 526 H 618 L 628 516 V 506'),
                  line('M 284 530 H 356 M 284 530 L 302 518 L 320 530 L 338 518 L 356 530 M 302 518 H 338 M 302 518 V 530 M 338 518 V 530',accent),
                  dot(22,28,mark,1.5),dot(618,516,mark,1.5)]
    else:
        # Abstract graph nodes and a signal-shaped signature, not measured telemetry.
        frame += [line('M 12 38 V 18 H 30 M 608 18 H 628 V 38 M 12 506 V 526 H 32 M 608 526 H 628 V 506'),
                  dot(12,18,accent,2.5),dot(628,18,accent,2.5),dot(628,526,accent,2.5),
                  line('M 282 526 H 299 L 306 519 L 314 532 L 325 516 L 333 526 H 358',accent),
                  dot(282,526,mark),dot(358,526,mark)]
    return frame

for slug,name,tagline,desc,stack,accent in compact:
    data=pixel_b64(f'{slug}.png')
    W,X0,X1,Y0,Y1 = 640,22,618,40,508
    b=['<defs><filter id="shadow" x="-6%" y="-6%" width="112%" height="120%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
       f'<image width="640" height="540" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{data}"/>',
       rect(X0,Y0,X1-X0,Y1-Y0,'#0e1527','rx="9" fill-opacity=".97" stroke="#354153" filter="url(#shadow)"')]
    # Title bar with traffic lights and repository pill.
    for x,c in [(42,'#f28c84'),(58,'#e9ba79'),(74,'#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="57" r="4.5" fill="{c}"/>')
    b += [rect(220,47,200,20,'#182036','rx="5" stroke="#2c3550"'),text(320,61,'Timcai06 / '+name,12,'#97a3bf','text-anchor="middle"'),
          rect(X0+1,73,X1-X0-2,1,'#2c3550')]
    # Tabs.
    b += [rect(X0+1,74,X1-X0-2,30,'#0b1120'),rect(X0+1,74,150,30,'#0e1527'),rect(X0+1,74,150,2,accent),
          text(38,94,'M↓',10,'#7fa7d9','font-weight="700"'),text(60,94,'README.md',13,accent),text(158,94,'×',12,'#7f89a3','text-anchor="middle"'),
          rect(173,74,1,30,'#222a40'),text(188,94,'◫',12,'#6f7b97'),text(206,94,'Preview',13,'#6f7b97')]
    # Markdown, token-highlighted.
    lines=[(140,[('# ',accent,' opacity=".55"'),(name,accent,' font-weight="700"')],32),
           (172,[('> ','#6c7a98',''),(tagline,'#d6e0ef',' font-style="italic"')],18),
           (196,[],0),
           (224,[('- ',accent,''),(desc[0],'#c4d3e8','')],21),
           (252,[('- ',accent,''),(desc[1],'#c4d3e8','')],21),
           (274,[],0),
           (298,[],0),
           (330,[],0)]
    # Stack chips wrap onto a second line; the chip lines are the active block.
    CH, CF, PAD, GAP, XMAX = 24, 14, 18, 7, 574
    chip_rows, row, x = [], [], 72
    for item in stack:
        w = round(len(item)*CF*0.6+PAD)
        if row and x + w > XMAX:
            chip_rows.append(row); row, x = [], 72
        row.append((item, x, w)); x += w + GAP
    chip_rows.append(row)
    b.append(rect(X0+1,298-18,560,CH+8+(len(chip_rows)-1)*32,'#18213a'))
    for i,(y,parts,size) in enumerate(lines):
        if i==7 and len(chip_rows)<2: continue
        b.append(text(56,y,str(i+1),12,'#c9d2e6' if i>=6 else '#4f5c78','text-anchor="end"'))
        if parts: b.append(f'<text x="72" y="{y}" font-size="{size}" xml:space="preserve">{tspans(parts)}</text>')
    for r,chips in enumerate(chip_rows):
        top = 298-16 + r*32
        for item, x, w in chips:
            b += [rect(x,top,w,CH,accent,'rx="5" fill-opacity=".14" stroke="'+accent+'" stroke-opacity=".45"'),
                  text(x+w/2,top+17,item,CF,accent,'text-anchor="middle"')]
    # Minimap.
    b += [rect(586,104,1,244,'#222a40')]
    for i,(y,parts,size) in enumerate(lines):
        mx=594
        for t,c,_ in parts:
            w=min(len(t)*(1.6 if size>20 else 0.9),18)
            b.append(rect(round(mx,1),112+i*6,round(w,1),3,c,'opacity=".7"')); mx+=w
    for r in range(len(chip_rows)): b.append(rect(594,112+(6+r)*6,18,3,accent,'opacity=".7"'))
    # Terminal panel: real quick-start commands from the repository README.
    b += [rect(X0+1,350,X1-X0-2,1,'#2c3550'),rect(X0+1,351,X1-X0-2,128,'#0b111f'),
          text(40,373,'PROBLEMS',10,'#5f6b88','letter-spacing=".5"'),text(110,373,'OUTPUT',10,'#5f6b88','letter-spacing=".5"'),
          text(166,373,'TERMINAL',10,accent,'letter-spacing=".5"'),rect(166,378,58,2,accent),
          text(604,373,'zsh  +  ×',11,'#6f7b97','text-anchor="end"')]
    prompt=[('~/'+REPO_DIR[slug],'var'),(' $ ','b1')]
    for k,(cmd,comment) in enumerate(TERMINAL_CMDS[slug]):
        parts=prompt+[(cmd,'plain')]+([('  '+comment,'comment')] if comment else [])
        b.append(code_line(40,402+k*24,parts,13))
    b.append(code_line(40,450,prompt,13))
    b.append(rect(round(40+len('~/'+REPO_DIR[slug]+' $ ')*13*0.6)+1,439,7,14,'#edc38c','opacity=".85"'))
    # Status bar.
    b += [rect(X0+1,480,X1-X0-2,27,'#252f48'),rect(X0+1,480,74,27,'#3a3356'),
          text(34,498,'⎇ main',12,'#f5d2a4'),*card_activity(REPO_DIR[slug],accent),
          text(604,498,'Markdown   UTF-8   LF',12,'#aab6d2','text-anchor="end"')]
    b.extend(project_frame(slug, name, accent))
    if WRITE: (out/(slug+'-compact.svg')).write_text(svg(640,540,b,name+' — '+tagline))
if WRITE: print('Built project cards')
