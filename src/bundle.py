"""Build the prototype.

  python3 bundle.py site OUTDIR        -> OUTDIR/index.html + OUTDIR/img + OUTDIR/fonts (fast: assets load in parallel and cache)
  python3 bundle.py standalone OUT.html -> one self-contained file (fonts + images inlined; for email/offline)
  python3 bundle.py artifact OUT.html   -> fonts inlined, images left as relative files (for the Claude share link)
"""
import re, base64, sys, os, shutil
import protect
PW = protect.password()
root = os.path.dirname(os.path.abspath(__file__))
mode, out = sys.argv[1], sys.argv[2]

s = open(os.path.join(root, 'src.html')).read().replace('{{SPRITE}}', open(os.path.join(root, 'sprite.min.svg')).read())
_n = len(s)
s = re.sub(r"(\$\('#splash'\)\.classList\.add\('done'\); reveal\('home'\))",
           r"\1; const h=(location.hash||'').slice(1); if(['progress','symptom','journey','care','support','session','notifs'].includes(h)) setTimeout(()=>jump(h),300)", s, count=1)
assert len(s) > _n, 'deep-link hook not injected: boot() changed shape'
s = s.replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1)

def uri(p):
    mt = {'jpg': 'image/jpeg', 'webp': 'image/webp', 'woff2': 'font/woff2', 'png': 'image/png'}[p.rsplit('.', 1)[1]]
    return 'data:%s;base64,%s' % (mt, base64.b64encode(open(os.path.join(root, p), 'rb').read()).decode())

def inline_fonts(t):
    t = re.sub(r'<link rel="preload" href="fonts/[^"]+"[^>]*>\n?', '', t)
    return re.sub(r'url\((fonts/[^)]+)\)', lambda m: 'url(%s)' % uri(m.group(1)), t)

if mode == 'site':
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w').write(protect.gate(s, PW) if PW else s)
    used = set(re.findall(r'(img/[^"\')\s]+)', s)) | set(re.findall(r'(fonts/[^"\')\s]+)', s))
    for d in ('img', 'fonts'):
        shutil.rmtree(os.path.join(out, d), ignore_errors=True); os.makedirs(os.path.join(out, d))
    for f in used:
        shutil.copy(os.path.join(root, f), os.path.join(out, f))
    print('site ->', out, round(len(s) / 1e3), 'KB html,', len(used), 'assets')
elif mode == 'standalone':
    t = inline_fonts(s)
    t = re.sub(r'<link rel="preload" href="img/[^"]+"[^>]*>\n?', '', t)
    c = {}
    t = re.sub(r'src="(img/[^"]+)"', lambda m: 'src="%s"' % c.setdefault(m.group(1), uri(m.group(1))), t)
    t = protect.gate(t, PW) if PW else t
    open(out, 'w').write(t); print('standalone ->', out, round(len(t) / 1e6, 2), 'MB')
elif mode == 'artifact':
    t = inline_fonts(s)
    t = '<title>GoodRx Weight Loss Prototype</title>\n' + t[t.index('<link rel="preload"'):] if '<link rel="preload"' in t else '<title>GoodRx Weight Loss Prototype</title>\n' + t[t.index('<style>'):]
    t = t.replace('</style>\n</head>\n<body>', '</style>', 1).replace('</body>\n</html>', '')
    imgs = sorted(set(re.findall(r'(img/[^"\')\s]+)', t)))
    t = protect.gate(inline_fonts(s), PW, fragment=True) if PW else t
    open(out, 'w').write(t)
    open(out + '.files', 'w').write('\n'.join(imgs))
    print('artifact ->', out, round(len(t) / 1e3), 'KB,', len(imgs), 'image files')
