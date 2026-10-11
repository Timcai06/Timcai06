"""Render the HTML-only profile README in a local GitHub-like frame."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
content = (root / 'README.md').read_text().replace('./assets/', '../assets/')
css = '''
:root{color-scheme:dark;--bg:#0d1117;--text:#e6edf3;--muted:#9198a1;--border:#3d444d;--link:#79c0ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
nav{padding:18px 32px;border-bottom:1px solid var(--border);font-weight:600}nav span{color:var(--muted);font-weight:400;margin-left:28px}
.layout{max-width:1280px;margin:32px auto;padding:0 24px;display:grid;grid-template-columns:240px minmax(0,1fr);gap:32px}
aside{padding-top:8px}.avatar{width:200px;height:200px;display:grid;place-items:center;border:1px solid #43496a;border-radius:50%;background:radial-gradient(ellipse at 70% 25%,#29295a,#10182b 65%);font:bold 68px monospace;color:#ffd6a3;text-shadow:4px 4px #505caa}
aside h1{font-size:25px;line-height:1.3;margin-bottom:0}aside .handle{color:var(--muted);font-size:20px}aside p{margin:22px 0}.note{color:var(--muted);font-size:12px}a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
article{min-width:0;border:1px solid var(--border);border-radius:6px;padding:24px 32px}.file{font:12px monospace;color:var(--muted);margin-bottom:20px}
.markdown-body img{max-width:100%;height:auto;vertical-align:middle}.markdown-body p{margin:0 0 16px}.markdown-body h2{font-size:21px;border-bottom:1px solid var(--border);padding-bottom:8px;margin:26px 0 16px}.markdown-body h3{font-size:16px;margin:4px 0 12px}
.markdown-body table{border-collapse:collapse;width:100%;margin-bottom:16px;display:block;overflow:auto}.markdown-body table tr{background:var(--bg);border-top:1px solid var(--border)}.markdown-body table tr:nth-child(2n){background:#151b23}.markdown-body td{border:1px solid var(--border);padding:12px;vertical-align:top}.markdown-body td img{width:100%}.markdown-body code{font:12px ui-monospace,monospace;background:#656c7633;border-radius:5px;padding:3px 6px}.markdown-body pre{padding:16px;background:#151b23;border-radius:6px;overflow:auto}.markdown-body pre code{background:none;padding:0}.markdown-body sub{font-size:12px}.markdown-body details{margin:20px 0}.markdown-body summary{cursor:pointer}.markdown-body hr{border:0;border-top:1px solid var(--border);margin:24px 0}
@media(prefers-color-scheme:light){:root{color-scheme:light;--bg:#fff;--text:#1f2328;--muted:#59636e;--border:#d1d9e0;--link:#0969da}.markdown-body table tr:nth-child(2n),.markdown-body pre{background:#f6f8fa}}
@media(max-width:760px){.layout{display:block;margin:16px auto;padding:0 12px}aside{display:none}article{padding:16px}.markdown-body td{padding:8px}.markdown-body h3{font-size:14px}nav{padding:14px}nav span{display:none}}
'''
page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Tim Cai · Pixel Lab preview</title><style>' + css + '</style><nav>◉ GitHub <span>Timcai06 / Overview · Local design preview</span></nav><div class="layout"><aside><div class="avatar">TC</div><h1>Tim Cai</h1><div class="handle">Timcai06</div><p>Student developer.<br>Building AI systems and full-stack products.</p><p><a href="https://www.crt-dsg.com">Website ↗</a><br><a href="mailto:cairentian932@gmail.com">Email ↗</a></p><p class="note">Local approximation of GitHub rendering.<br>The avatar and sidebar are preview scaffolding.</p></aside><article><div class="file">Timcai06 / README.md</div><div class="markdown-body">' + content + '</div></article></div></html>'
(root / 'preview' / 'index.html').write_text(page)
print('Built preview/index.html')
