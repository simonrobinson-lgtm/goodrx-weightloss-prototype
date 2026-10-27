"""Build the homepage prototype.

  python3 homepage/src/build.py            -> homepage/index.html (password protected)
  NO_PASS=1 python3 homepage/src/build.py  -> unprotected, for local preview

The password is read from src/.proto-pass (git-ignored) or PROTO_PASS, same as the mobile prototype.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'src'))
import protect

TITLE = 'GoodRx Weight Loss Home'
s = open(os.path.join(HERE, 'src.html')).read()
lq = json.load(open(os.path.join(HERE, 'lqip.json')))
s = re.sub(r'\{\{lq:([\w-]+)\}\}', lambda m: lq[m.group(1)], s)
s = s.replace('{{lqjson}}', json.dumps(lq))
s = s.replace('{{illu}}', json.dumps(json.load(open(os.path.join(HERE, 'illu_paths.json'))), separators=(',', ':')))
s = s.replace('<meta charset="utf-8">\n', '', 1)
s = re.sub(r'<title>.*?</title>\n?', '', s, count=1)
s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
cut = s.index('</style>') + len('</style>')
doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
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
if pw:
    out = protect.gate(doc, pw)
    out = (out.replace("K='grx-proto-key'", "K='grx-home-key'")
              .replace('<title>GoodRx Weight Loss Prototype</title>', f'<title>{TITLE}</title>')
              .replace('<h1>Weight loss care</h1>', '<h1>Weight loss homepage</h1>')
              .replace('View prototype', 'View homepage')
              .replace('<meta name="theme-color" content="#f5efe5">', '<meta name="theme-color" content="#f5efe5">\n<link rel="icon" type="image/svg+xml" href="favicon.svg">'))
    assert "K='grx-home-key'" in out
else:
    out = doc
open(os.path.join(os.path.dirname(HERE), 'index.html'), 'w').write(out)
print('built', 'protected' if pw else 'UNPROTECTED', len(out) // 1024, 'KB')
