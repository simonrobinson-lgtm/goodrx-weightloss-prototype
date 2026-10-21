"""Build index.html (from src.html + sprite) and a fully self-contained dist file."""
import re, base64, sys, os
root = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(root, 'src.html')).read().replace('{{SPRITE}}', open(os.path.join(root, 'sprite.min.svg')).read())
open(os.path.join(root, 'index.html'), 'w').write(s)
def uri(p):
    mt = {'jpg': 'image/jpeg', 'webp': 'image/webp', 'woff2': 'font/woff2', 'png': 'image/png'}[p.rsplit('.', 1)[1]]
    return 'data:%s;base64,%s' % (mt, base64.b64encode(open(os.path.join(root, p), 'rb').read()).decode())
s = re.sub(r'url\((fonts/[^)]+)\)', lambda m: 'url(%s)' % uri(m.group(1)), s)
c = {}
s = re.sub(r'src="(img/[^"]+)"', lambda m: 'src="%s"' % c.setdefault(m.group(1), uri(m.group(1))), s)
s = s.replace("const boot=()=>{ centerJ(); setTimeout(()=>{ $('#splash').classList.add('done'); reveal('home') },650) };",
  "const boot=()=>{ centerJ(); setTimeout(()=>{ $('#splash').classList.add('done'); reveal('home'); const h=(location.hash||'').slice(1); if(['progress','symptom','care','support','session'].includes(h)) setTimeout(()=>jump(h),300) },650) };")
s = s.replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, 'dist.html')
open(out, 'w').write(s)
print('wrote', out, round(len(s) / 1e6, 2), 'MB')
