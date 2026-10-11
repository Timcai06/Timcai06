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
# ---- Profile workspace: pixel backdrop + detailed editor window --------------
TOK = dict(kw='#c6a6ed', type='#7fd1c7', var='#8fc4f0', prop='#a9c3e8', str='#b0d6bf', op='#93a3c4',
           punct='#7f89a3', comment='#6c7a98', b1='#f2c48f', b2='#d39ae8', b3='#7fb8e8', plain='#ced7ee')
def code_line(x, y, tokens, size, extra=''):
    spans = ''.join(f'<tspan fill="{TOK[k]}"' + (' font-style="italic"' if k == 'comment' else '') + f'>{escape(t)}</tspan>' for t, k in tokens)
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve" {extra}>{spans}</text>'
b=['<defs><filter id="shadow" x="-6%" y="-6%" width="112%" height="118%"><feDropShadow dx="0" dy="16" stdDeviation="18" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
   f'<image width="1200" height="800" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{bg}"/>',
   rect(0,0,1200,800,'#070b1b','opacity=".12"'),
   rect(45,60,1110,674,'#111728','rx="10" fill-opacity=".97" stroke="#576078" filter="url(#shadow)"'),
   rect(46,100,1108,1,'#343d54')]
# Title bar: traffic lights, command-centre search pill, layout toggles.
for x,c in [(69,'#f28c84'),(90,'#e9ba79'),(111,'#97bf9b')]:
    b.append(f'<circle cx="{x}" cy="80" r="6" fill="{c}"/>')
b += [rect(452,68,296,24,'#1a2133','rx="6" stroke="#2f3851"'),text(600,85,"⌕  Timcai06 — profile",13,'#9aa5c0','text-anchor="middle"'),
      text(1132,85,'▣  ◧  ▤',13,'#6f7b97','text-anchor="end"')]
# Activity bar.
b += [rect(46,101,48,603,'#141a2d'),rect(94,101,214,603,'#131a2c'),rect(307,101,1,603,'#303950'),rect(46,110,3,44,'#e5b581')]
for y,g,c in [(141,'▣','#d5dcef'),(196,'⌕','#8491ae'),(251,'⑂','#8491ae'),(306,'▷','#8491ae'),(361,'⧉','#8491ae'),(640,'◉','#8491ae'),(686,'⚙','#8491ae')]:
    b.append(text(60,y,g,24,c))
b += [f'<circle cx="82" cy="257" r="8" fill="#e5b581"/>',text(82,261,'1',11,'#1a1f30','text-anchor="middle" font-weight="700"')]
# Explorer: the profile's real structure, each project with its accent colour.
b += [text(111,132,'EXPLORER',12,'#8995b2','letter-spacing="1"'),text(292,132,'⋯',14,'#8995b2','text-anchor="end"'),
      text(108,162,'⌄ TIMCAI06',13,'#dde4f5','font-weight="700" letter-spacing=".5"')]
tree=[(0,'file','TS','#5aa2e8','about.ts','#efc38f'),
      (0,'dir','⌄','#8491ae','featured','#c3cde4'),
      (1,'proj','#e8c397',None,'EduCanvas','#a8b8d4'),(1,'proj','#9ec9e9',None,'SciScope','#a8b8d4'),
      (1,'proj','#e4b6eb',None,'TTT-I-M','#a8b8d4'),(1,'proj','#efba85',None,'BDI','#a8b8d4'),
      (1,'proj','#b9afea',None,'PulseGraph','#a8b8d4'),
      (0,'dir','⌄','#8491ae','motion','#c3cde4'),(1,'proj','#f28c84',None,'01-clawd-mv','#a8b8d4'),
      (0,'dir','⌄','#8491ae','research','#c3cde4'),(1,'file','py','#e8c06a','models.py','#a8b8d4'),
      (0,'file','{}','#e8c06a','toolbox.json','#a8b8d4'),(0,'file','M↓','#7fa7d9','contact.md','#a8b8d4')]
b += [rect(95,173,211,26,'#29314a'),rect(95,173,2,26,'#e5b581')]
for i,(lvl,kind,icon,ic,name,nc) in enumerate(tree):
    y=191+i*27; x=114+lvl*18
    if lvl: b.append(rect(119,y-19,1,27,'#323b55'))
    if kind=='proj':
        b += [text(x,y,'▸',12,'#6f7b97'),f'<circle cx="{x+21}" cy="{y-5}" r="4.5" fill="{icon}"/>',text(x+32,y,name,14,nc)]
    elif kind=='dir':
        b += [text(x,y,icon,14,ic),text(x+18,y,name,14,nc)]
    else:
        b += [text(x,y,icon,11,ic,'font-weight="700"'),text(x+26,y,name,14,nc)]
b += [rect(95,580,212,1,'#2a3149'),text(108,602,'›  OUTLINE',12,'#7f8aa6','letter-spacing=".5"'),
      rect(95,614,212,1,'#2a3149'),text(108,636,'›  TIMELINE',12,'#7f8aa6','letter-spacing=".5"'),
      rect(95,648,212,1,'#2a3149'),text(108,672,'›  NPM SCRIPTS',12,'#7f8aa6','letter-spacing=".5"')]
# Tabs, breadcrumb.
b += [rect(308,101,846,40,'#0e1423'),rect(308,101,168,40,'#111728'),rect(308,101,168,2,'#edbf88'),
      text(324,126,'TS',11,'#5aa2e8','font-weight="700"'),text(348,126,'about.ts',15,'#e8c39a'),text(458,126,'×',14,'#8b95ae','text-anchor="middle"'),
      rect(476,101,1,40,'#262e44'),text(492,126,'{}',11,'#e8c06a','font-weight="700"'),text(516,126,'toolbox.json',15,'#7f8ba7'),
      rect(652,101,1,40,'#262e44'),text(668,126,'M↓',11,'#7fa7d9','font-weight="700"'),text(694,126,'contact.md',15,'#7f8ba7'),
      rect(818,101,1,40,'#262e44'),text(1136,126,'⧉  ⋯',14,'#7f8ba7','text-anchor="end"'),
      code_line(326,164,[('Timcai06','punct'),('  ›  ','punct'),('TS ','var'),('about.ts','punct'),('  ›  ','punct'),('{} ','b1'),('tim','prop')],13)]
S=lambda t,k:(t,k); sp=('  ','plain'); s1=(' ','plain')
def kv(key,*rest,indent=sp): return [indent,S(key,'prop'),S(':','punct'),s1,*rest]
def strs(items,bk):
    out=[S('[',bk)]
    for j,v in enumerate(items):
        out.append(S(f'"{v}"','str'))
        if j<len(items)-1: out.append(S(', ','punct'))
    return out+[S(']',bk)]
code=[[S('import','kw'),s1,S('type','kw'),s1,S('{','b1'),s1,S('Builder','type'),s1,S('}','b1'),s1,S('from','kw'),s1,S('"./types"','str'),S(';','punct')],
 [],
 [S('// Hello, world.','comment')],
 [S('export','kw'),s1,S('const','kw'),s1,S('tim','var'),S(':','punct'),s1,S('Builder','type'),s1,S('=','op'),s1,S('{','b1')],
 kv('name',S('"Tim Cai"','str'),S(',','punct')),
 kv('role',S('"Student developer"','str'),S(',','punct')),
 kv('basedIn',S('"Shanghai"','str'),S(',','punct')),
 kv('focus',*strs(['AI agents','ML observability','Full-stack'],'b2'),S(',','punct')),
 kv('building',S('[','b2')),
 [('    ','plain'),S('"AI agents & research tools"','str'),S(',','punct')],
 [('    ','plain'),S('"Observable ML systems"','str'),S(',','punct')],
 [('    ','plain'),S('"Thoughtful full-stack products"','str'),S(',','punct')],
 [sp,S(']','b2'),S(',','punct')],
 kv('stack',S('{','b2'),s1,S('web','prop'),S(':','punct'),s1,*strs(['React','Next.js'],'b3'),S(', ','punct'),
    S('ml','prop'),S(':','punct'),s1,*strs(['PyTorch','FastAPI'],'b3'),s1,S('}','b2'),S(',','punct')),
 kv('featured',*strs(['EduCanvas','SciScope','TTT-I-M','BDI','PulseGraph'],'b2'),S(',','punct')),
 kv('series',S('"Code in motion"','str'),S(',','punct')),
 kv('mindset',S('"Curiosity → craft"','str'),S(',','punct')),
 [S('}','b1'),s1,S('as','kw'),s1,S('const','kw'),S(';','punct')]]
CX, CY, STEP, SIZE = 384, 196, 20, 16
CW = SIZE*0.6   # approximate monospace advance; used only for guides and the minimap
cursor = 1
b.append(rect(309,CY+cursor*STEP-15,770,STEP,'#1c2539'))
for i in range(4,17): b.append(rect(CX+1,CY+i*STEP-15,1,STEP,'#2c3550'))
for i in range(9,12): b.append(rect(round(CX+2*CW)+1,CY+i*STEP-15,1,STEP,'#2c3550'))
for i,c in [(7,'#6f9fd8'),(13,'#7fb08a'),(14,'#7fb08a'),(15,'#7fb08a')]: b.append(rect(356,CY+i*STEP-15,3,STEP-2,c))
for i in (3,8,13): b.append(text(370,CY+i*STEP-1,'⌄',12,'#56637f','text-anchor="middle"'))
for i,tokens in enumerate(code):
    y=CY+i*STEP
    b.append(text(348,y,str(i+1),13,'#c9d2e6' if i==cursor else '#56637f','text-anchor="end"'))
    if tokens: b.append(code_line(CX,y,tokens,SIZE))
b.append(rect(CX,CY+cursor*STEP-14,2,18,'#edc38c'))
# Minimap and overview ruler.
b += [rect(1084,145,1,412,'#262e44'),rect(1085,145,62,code.__len__()*5+14,'#ffffff','opacity=".04"'),rect(1148,145,6,412,'#151c2e')]
for i,tokens in enumerate(code):
    x=1092
    for t,k in tokens:
        w=len(t)*0.78
        if t.strip(): b.append(rect(round(x,1),152+i*5,round(w,1),2.4,TOK[k],'opacity=".75"'))
        x+=w
for i,c in [(7,'#6f9fd8'),(13,'#7fb08a'),(14,'#7fb08a'),(15,'#7fb08a')]: b.append(rect(1149,150+i*5*1.1,4,4,c))
# Terminal.
b += [rect(308,566,846,1,'#3a435a'),text(333,590,'PROBLEMS',12,'#6d7a97','letter-spacing=".5"'),text(425,590,'OUTPUT',12,'#6d7a97','letter-spacing=".5"'),
      text(505,590,'TERMINAL',12,'#edc38c','letter-spacing=".5"'),rect(505,597,70,2,'#e8b983'),
      text(1136,590,'zsh   +  ⌄   ⧉   ×',13,'#7f8ba7','text-anchor="end"'),
      code_line(333,620,[('~/Timcai06','var'),(' on ','punct'),('⎇ main','kw'),(' $ ','b1'),('cat now.txt','plain')],15),
      text(333,643,'Learning deeply. Building across the stack.',15,'#c3cde4'),
      text(333,666,'从模型、数据到界面，让想法成为可用的产品。',16,'#a5b2ce'),
      code_line(333,689,[('~/Timcai06','var'),(' on ','punct'),('⎇ main','kw'),(' $ ','b1')],15),
      rect(round(333+len('~/Timcai06 on ⎇ main $ ')*9)+2,677,9,15,'#edc38c','opacity=".85"')]
# Status bar.
b += [rect(46,704,1108,29,'#313952'),rect(46,704,100,29,'#4a3f63'),text(60,724,'⎇ main*',14,'#f5d2a4'),
      text(162,724,'⊗ 0   ⚠ 0',14,'#bcc8e2'),text(268,724,'◷ profile',14,'#9aa6c4'),
      text(1138,724,'Ln 2, Col 1    Spaces: 2    UTF-8    LF    {} TypeScript    ✓ Prettier    ☾',14,'#bcc8e2','text-anchor="end"')]
(out/'workspace.svg').write_text(svg(1200,800,b,"Tim's pixel-night editor workspace: AI agents, observable ML and full-stack products"))

# ---- Footer: the terminal that closes the page (bookend to the workspace) ----
fb=['<defs><filter id="shadow" x="-6%" y="-10%" width="112%" height="130%"><feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
    f'<image width="1200" height="320" preserveAspectRatio="xMidYMax slice" xlink:href="data:image/png;base64,{bg}"/>',
    rect(0,0,1200,320,'#070b1b','opacity=".12"'),
    rect(150,42,900,236,'#111728','rx="10" fill-opacity=".97" stroke="#576078" filter="url(#shadow)"'),
    rect(151,80,898,1,'#343d54')]
for x,c in [(174,'#f28c84'),(194,'#e9ba79'),(214,'#97bf9b')]:
    fb.append(f'<circle cx="{x}" cy="61" r="5.5" fill="{c}"/>')
fb += [text(600,66,'zsh — ~/Timcai06',14,'#9aa5c0','text-anchor="middle"'),
       text(1028,66,'TERMINAL',11,'#edc38c','text-anchor="end" letter-spacing="1"'),
       code_line(186,132,[('~/Timcai06','var'),(' on ','punct'),('⎇ main','kw'),(' $ ','b1'),('echo ','plain'),('"Thanks for stopping by."','str')],22),
       text(186,176,'Thanks for stopping by.',26,'#f2c48f','font-weight="700"'),
       code_line(186,226,[('~/Timcai06','var'),(' on ','punct'),('⎇ main','kw'),(' $ ','b1')],22),
       rect(round(186+len('~/Timcai06 on ⎇ main $ ')*22*0.6)+2,208,12,23,'#edc38c','opacity=".85"'),
       rect(151,252,898,25,'#313952','rx="0"'),text(170,269,'⎇ main',12,'#f5d2a4'),
       text(1030,269,'zsh   UTF-8   ☾',12,'#bcc8e2','text-anchor="end"')]
(out/'footer.svg').write_text(svg(1200,320,fb,'Terminal: echo "Thanks for stopping by."'))
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
 ('tttim','TTT-I-M','Personal web & content studio',['电影感个人网站','内容工作室与交互体验'],['TypeScript','React','Next.js','Vite','GSAP','R3F','Vercel'],'#e4b6eb'),
 ('bdi','BDI','Visual bridge inspection',['桥梁视觉检测原型','分割模型与全栈工作流'],['Python','YOLOv8-seg','FastAPI','TypeScript','Next.js','React'],'#efba85'),
 ('sciscope','SciScope','Evidence-grounded research',['文献与证据驱动的研究','Python RAG × Go TUI'],['Python','RAG','FastAPI','PostgreSQL','DeepSeek','Go TUI','SSE'],'#9ec9e9'),
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
for slug,name,tagline,desc,stack,accent in compact:
    data=pixel_b64(f'{slug}.png')
    W,X0,X1,Y0,Y1 = 640,22,618,40,508
    b=['<defs><filter id="shadow" x="-6%" y="-6%" width="112%" height="120%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
       f'<image width="640" height="540" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/png;base64,{data}"/>',
       rect(X0,Y0,X1-X0,Y1-Y0,'#0e1527','rx="9" fill-opacity=".97" stroke="#5d6780" filter="url(#shadow)"')]
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
          text(34,498,'⎇ main',12,'#f5d2a4'),text(110,498,'⊗ 0  ⚠ 0',12,'#aab6d2'),
          text(604,498,'Markdown   UTF-8   LF',12,'#aab6d2','text-anchor="end"')]
    (out/(slug+'-compact.svg')).write_text(svg(640,540,b,name+' — '+tagline))
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
