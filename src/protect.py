"""Password gate: AES-GCM encrypts a full HTML document; the shell page decrypts it in the browser with WebCrypto."""
import os, base64, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 250000

def encrypt(html, password, salt=None):
    salt, iv = salt or os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode())
    ct = AESGCM(key).encrypt(iv, html.encode(), None)
    b = lambda x: base64.b64encode(x).decode()
    return {'s': b(salt), 'i': b(iv), 'c': b(ct), 'n': ITER}

STYLE = '''<style>
@font-face{font-family:"Bolton";src:local("Bolton")}
:root{color-scheme:light}
html,body{margin:0;height:100%;background:#f5efe5;font-family:"Bolton",-apple-system,system-ui,sans-serif;color:#12110f;-webkit-font-smoothing:antialiased}
.gate{min-height:100%;display:flex;align-items:center;justify-content:center;padding:24px;box-sizing:border-box}
.gate form{width:100%;max-width:340px;display:flex;flex-direction:column;gap:16px}
.gate svg{width:32px;height:32px}
.gate h1{margin:8px 0 0;font-weight:400;font-size:28px;line-height:1.2;letter-spacing:-.01em;color:#1c534e}
.gate p{margin:0;font-size:14px;line-height:1.5;color:rgba(18,17,15,.6)}
.gate input{height:48px;border-radius:8px;border:1px solid #d7d1c6;background:#fffffb;padding:0 14px;font:inherit;font-size:16px;color:#12110f;outline:none;transition:border-color .2s,box-shadow .2s}
.gate input:focus{border-color:#1c534e;box-shadow:0 0 0 3px rgba(28,83,78,.12)}
.gate button{height:48px;border:0;border-radius:8px;background:#1c534e;color:#fff6bf;font:inherit;font-weight:500;font-size:14px;cursor:pointer;transition:background .2s}
.gate button:hover{background:#184844}
.gate button[disabled]{opacity:.6;cursor:default}
.gate .err{min-height:20px;font-size:13px;color:#ad5328}
.gate.shake form{animation:sh .4s}
@keyframes sh{20%,60%{transform:translateX(-6px)}40%,80%{transform:translateX(6px)}}
</style>'''

BODY = '''<div class="gate" id="gate"><form id="gf" autocomplete="on">
%%LOGO%%
<h1>Weight loss care</h1>
<p>This prototype is password protected. Enter the password you were given to continue.</p>
<input type="password" id="gp" placeholder="Password" autocomplete="current-password" aria-label="Password" required autofocus>
<button type="submit" id="gb">View prototype</button>
<div class="err" id="ge" role="alert"></div>
</form></div>
<script>
(()=>{
const P=%s, K='grx-proto-key', b=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const st={get(){try{return localStorage.getItem(K)}catch(e){return null}},set(v){try{localStorage.setItem(K,v)}catch(e){}},del(){try{localStorage.removeItem(K)}catch(e){}}};
async function open(raw){
  const key=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']);
  const pt=await crypto.subtle.decrypt({name:'AES-GCM',iv:b(P.i)},key,b(P.c));
  const html=new TextDecoder().decode(pt);
  document.open(); document.write(html); document.close();
}
async function derive(pw){
  const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveBits']);
  return new Uint8Array(await crypto.subtle.deriveBits({name:'PBKDF2',salt:b(P.s),iterations:P.n,hash:'SHA-256'},base,256));
}
const f=document.getElementById('gf'), e=document.getElementById('ge'), btn=document.getElementById('gb'), g=document.getElementById('gate');
if(!(window.crypto&&crypto.subtle)){ e.textContent='This browser can’t unlock the prototype here. Open the link over https.'; btn.disabled=true; return }
const saved=st.get();
if(saved){ g.style.visibility='hidden'; open(b(saved)).catch(()=>{ st.del(); g.style.visibility='' }) }
f.addEventListener('submit',async ev=>{
  ev.preventDefault(); e.textContent=''; btn.disabled=true; btn.textContent='Unlocking…';
  try{ const raw=await derive(document.getElementById('gp').value); await open(raw); st.set(btoa(String.fromCharCode(...raw))) }
  catch(err){ btn.disabled=false; btn.textContent='View prototype'; e.textContent='That password didn’t work. Try again.'; g.classList.remove('shake'); void g.offsetWidth; g.classList.add('shake') }
});
})();
</script>'''

def gate(html, password, fragment=False, salt=None):
    payload = json.dumps(encrypt(html, password, salt))
    import re as _re
    logo=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'logo.svg')).read().strip()
    body = (BODY % payload).replace('%LOGO%',logo)
    if fragment:
        return '<title>GoodRx Weight Loss Prototype</title>\n' + STYLE + '\n' + body
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="robots" content="noindex, nofollow">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="theme-color" content="#f5efe5">\n'
            '<title>GoodRx Weight Loss Prototype</title>\n' + STYLE + '\n</head><body>\n' + body + '\n</body></html>\n')

def password():
    if os.environ.get('NO_PASS'): return None
    p = os.environ.get('PROTO_PASS')
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.proto-pass')
    if not p and os.path.exists(f): p = open(f).read().strip()
    return p
