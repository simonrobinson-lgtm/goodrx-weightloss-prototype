"""Build the homepage prototype and the Wegovy pill product page.

  python3 homepage/src/build.py            -> homepage/index.html + homepage/wegovy-pill.html (password protected)
  NO_PASS=1 python3 homepage/src/build.py  -> unprotected, for local preview

The password is read from src/.proto-pass (git-ignored) or PROTO_PASS, same as the mobile prototype.
Both pages are encrypted with the same salt, so unlocking one unlocks the other.
The product page pulls its header, footer, base styles and journey component from src.html at build time.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
import protect

lq = json.load(open(os.path.join(HERE, 'lqip.json')))
home = open(os.path.join(HERE, 'src.html')).read()

def fill(s):
    s = re.sub(r'\{\{lq:([\w-]+)\}\}', lambda m: lq[m.group(1)], s)
    return s.replace('{{lqjson}}', json.dumps(lq))

def between(a, b, src=home, inc=False):
    i = src.index(a); j = src.index(b, i + len(a))
    return src[i:j + len(b)] if inc else src[i + len(a):j]

def pdp_source():
    P = open(os.path.join(HERE, 'pdp.html')).read()
    P = P.replace('{{basecss}}', between('<style>\n', '\n</style>'))
    i = home.index('<svg width="0" height="0"'); j = home.index('\n</svg>', i) + len('\n</svg>')
    P = P.replace('{{svgdefs}}', home[i:j])
    P = P.replace('{{header}}', between('<header class="hdr"', '</header>', inc=True))
    P = P.replace('{{footer}}', between('<!-- FOOTER -->', '</footer>', inc=True))
    P = P.replace('{{js:journeyBuild}}', between('/* ---------- build journey ---------- */', '/* ---------- build testimonials ---------- */').strip())
    P = P.replace('{{js:journeyTabs}}', between('/* ---------- journey: tabbed phases ---------- */', '/* ---------- testimonial drag-scroll').strip())
    return P

def document(s, title):
    s = fill(s)
    s = s.replace('{{illu}}', json.dumps(json.load(open(os.path.join(HERE, 'illu_paths.json'))), separators=(',', ':')))
    assert '{{' not in s, re.findall(r'\{\{[^}]*\}\}', s)[:5]
    s = s.replace('<meta charset="utf-8">\n', '', 1)
    s = re.sub(r'<title>.*?</title>\n?', '', s, count=1)
    s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
    cut = s.index('</style>') + len('</style>')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#f5efe5">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="preload" href="fonts/GoodRxBolton-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/GoodRxMoon-Regular.woff2" as="font" type="font/woff2" crossorigin>
{s[:cut].strip()}
</head>
<body>
{s[cut:].strip()}
</body>
</html>
'''

pw = protect.password()
salt = os.urandom(16)
for name, src, title, heading in [('index.html', home, 'GoodRx Weight Loss Home', 'Weight loss homepage'),
                                  ('wegovy-pill.html', pdp_source(), 'Wegovy Pill · GoodRx', 'Wegovy pill page')]:
    doc = document(src, title)
    if pw:
        out = protect.gate(doc, pw, salt=salt)
        out = (out.replace("K='grx-proto-key'", "K='grx-home-key'")
                  .replace('<title>GoodRx Weight Loss Prototype</title>', f'<title>{title}</title>')
                  .replace('<h1>Weight loss care</h1>', f'<h1>{heading}</h1>')
                  .replace('View prototype', 'View page')
                  .replace('<meta name="theme-color" content="#f5efe5">', '<meta name="theme-color" content="#f5efe5">\n<link rel="icon" type="image/svg+xml" href="favicon.svg">'))
        assert "K='grx-home-key'" in out
    else:
        out = doc
    open(os.path.join(OUT, name), 'w').write(out)
    print('built', name, 'protected' if pw else 'UNPROTECTED', len(out) // 1024, 'KB')
