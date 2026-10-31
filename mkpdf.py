#!/usr/bin/env python3
"""A4 landscape one-sheet for Carola & Alberto (places to choose from, not a route): photo strip + map with pins + places list -> carola-alberto-akiba-oct31.pdf/.png
Same design as the adopted model-course sheet (Sample-shibuya.pdf). Needs: Pillow, qrcode, playwright chromium.
Run with /usr/local/bin/python3 (the python that has playwright)."""
import io, os, json, math, time, base64, urllib.request, tempfile
from PIL import Image, ImageDraw, ImageFont
import qrcode

URL = 'https://yukitchy.github.io/carola-alberto-akiba-day/'
UA = {'User-Agent': 'carola-route-sheet/1.0 (icchan417@gmail.com)'}
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.mapcache'); os.makedirs(CACHE, exist_ok=True)

# ---- data -------------------------------------------------------------------------------------
# letter, short label, long name, who, lat, lon (None = no coordinates found, listed but not pinned), note
PLACES = [('S', 'Vie de France', 'Vie de France, inside the café', 'We meet here at 15:00', 35.69881, 139.77237, 'BiTO Akiba Plaza, 1 min from the station'),
          ('A', 'Kanda Myojin', 'Kanda Myojin Shrine', 'For Carola', 35.70194, 139.76774, 'Akihabara\'s own shrine, anime-style wish plaques'),
          ('B', 'G-Store', 'G-Store Akiba', 'For Alberto', 35.69830, 139.77085, 'Anime clothing, Jump titles, Onoden building 4F'),
          ('C', 'Trader', 'Trader main store', 'For Alberto', None, None, 'Prize figures, One Piece and Dragon Ball'),
          ('D', 'GiGO', 'GiGO retro games, 6F', 'For both', 35.69922, 139.77095, 'Street Fighter II, Pac-Man, pinball'),
          ('E', 'Maidreamin', "Maidreamin Heaven's Gate", 'For both', 35.69809, 139.77232, 'Open 10:30-23:00, one minute from the station')]
TH = 'https://upload.wikimedia.org/wikipedia/commons/thumb/'
PHOTOS = [TH + '1/19/Kanda-my%C5%8Djin_haiden.jpg/960px-Kanda-my%C5%8Djin_haiden.jpg', TH + 'b/b3/Ema_at_Kanda-Myojin_20141228.jpg/960px-Ema_at_Kanda-Myojin_20141228.jpg',
          TH + '9/94/GiGO_Retro_Games_Akihabara_15-09-2024_%281%29.jpg/960px-GiGO_Retro_Games_Akihabara_15-09-2024_%281%29.jpg', TH + '0/0c/Akihabara_Night.jpg/960px-Akihabara_Night.jpg']
STN = {'Akihabara Stn': (35.69834, 139.77317)}

# ---- map rendering (PIL, OSM tiles, red route + arrows + numbered labelled pins) ----------------
def get(url, binary=False):
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read()
            return r if binary else json.loads(r)
        except Exception: time.sleep(2)
def px(lat, lon, z):
    n = 2 ** z * 256
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
def tile(z, x, y):
    p = f'{CACHE}/t_{z}_{x}_{y}.png'
    if not os.path.exists(p):
        data = get(f'https://tile.openstreetmap.org/{z}/{x}/{y}.png', True)
        if not data: raise SystemExit(f'tile download failed: {z}/{x}/{y}')  # don't leave a 0-byte tile in the cache
        open(p, 'wb').write(data); time.sleep(0.15)
    return Image.open(p).convert('RGB')
def foot(a, b):
    p = f'{CACHE}/r_{a[0]:.5f}_{a[1]:.5f}_{b[0]:.5f}_{b[1]:.5f}.json'
    if not os.path.exists(p):
        r = get(f'https://routing.openstreetmap.de/routed-foot/route/v1/foot/{a[1]},{a[0]};{b[1]},{b[0]}?overview=full&geometries=geojson')
        try: line = [[y, x] for x, y in r['routes'][0]['geometry']['coordinates']]
        except Exception:
            print(f'warn: walking route failed, straight line used (not cached): {a} -> {b}')
            return [list(a), list(b)]
        json.dump(line, open(p, 'w'))
    return json.load(open(p))
def font(sz):
    for f in ['/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc']:
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()

def dashed(d, xy, fill, width, on=16, off=12):
    for a, b in zip(xy, xy[1:]):
        L = math.dist(a, b)
        if L == 0: continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; t = 0
        while t < L:
            e = min(t + on, L); d.line([(a[0] + ux * t, a[1] + uy * t), (a[0] + ux * e, a[1] + uy * e)], fill=fill, width=width); t += on + off
def arrows(d, xy, fill, every=150, size=17):
    acc = every / 2
    for a, b in zip(xy, xy[1:]):
        L = math.dist(a, b)
        if L == 0: continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L; pos = 0
        while pos + acc <= L:
            pos += acc; acc = every
            cx, cy = a[0] + ux * pos, a[1] + uy * pos
            tip = (cx + ux * size, cy + uy * size); l = (cx - ux * size * .6 - uy * size * .8, cy - uy * size * .6 + ux * size * .8); r = (cx - ux * size * .6 + uy * size * .8, cy - uy * size * .6 - ux * size * .8)
            d.polygon([tip, l, r], fill=fill, outline='white')
        acc -= (L - pos)

def render(out, W, H, pins, legs, stations, dots=()):
    """pins [(n,label,lat,lon)], legs [(kind,[(lat,lon)..])] kind foot|train, stations [(name,lat,lon)], dots [(letter,lat,lon)]"""
    allpts = [(p[2], p[3]) for p in pins] + [(s[1], s[2]) for s in stations] + [(x[1], x[2]) for x in dots]
    for _, line in legs: allpts += [tuple(q) for q in line]
    lats = [p[0] for p in allpts]; lons = [p[1] for p in allpts]
    z = 17
    while z > 4:
        x0, y1 = px(min(lats), min(lons), z); x1, y0 = px(max(lats), max(lons), z)
        if x1 - x0 < W - 150 and y1 - y0 < H - 150: break
        z -= 1
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; ox, oy = cx - W / 2, cy - H / 2
    img = Image.new('RGB', (W, H), '#ddd')
    for tx in range(int(ox // 256), int((ox + W) // 256) + 1):
        for ty in range(int(oy // 256), int((oy + H) // 256) + 1): img.paste(tile(z, tx, ty), (int(tx * 256 - ox), int(ty * 256 - oy)))
    img = img.convert('RGBA'); d = ImageDraw.Draw(img)
    P = lambda la, lo: (px(la, lo, z)[0] - ox, px(la, lo, z)[1] - oy)
    for kind, line in legs:
        xy = [P(*q) for q in line]
        if kind == 'train': dashed(d, xy, '#444', 7)
        else:
            d.line(xy, fill='white', width=14, joint='curve'); d.line(xy, fill='#e60012', width=8, joint='curve'); arrows(d, xy, '#e60012')
    pinpos = []
    for n, label, la, lo in pins:
        x, y = P(la, lo); pinpos.append((x, y))
        d.ellipse([x - 21, y - 21, x + 21, y + 21], fill='#111', outline='white', width=4); d.text((x, y), str(n), fill='white', font=font(27), anchor='mm')
    occ = [(x - 24, y - 24, x + 24, y + 24) for x, y in pinpos]
    def put(text, x, y, fill, ink, fs, outline):
        ft = font(fs); l, t, r, b = d.textbbox((0, 0), text, font=ft); w, h = r - l + 16, b - t + 10
        for dx, dy in [(26, -h / 2), (-w - 26, -h / 2), (-w / 2, 26), (-w / 2, -h - 26), (26, 10), (-w - 26, 10), (26, -h - 10), (-w - 26, -h - 10)]:
            bx = (x + dx, y + dy, x + dx + w, y + dy + h)
            if bx[0] < 4 or bx[1] < 4 or bx[2] > W - 4 or bx[3] > H - 30: continue
            if any(not (bx[2] < o[0] or bx[0] > o[2] or bx[3] < o[1] or bx[1] > o[3]) for o in occ): continue
            d.rounded_rectangle(bx, radius=8, fill=fill, outline=outline, width=2); d.text((bx[0] + 8, bx[1] + 4 - t), text, fill=ink, font=ft); occ.append(bx); return
    for ltr, la, lo in dots:
        x, y = P(la, lo); d.ellipse([x - 17, y - 17, x + 17, y + 17], fill='white', outline='#e60012', width=5); d.text((x, y), ltr, fill='#e60012', font=font(25), anchor='mm'); occ.append((x - 19, y - 19, x + 19, y + 19))
    for nm, la, lo in stations:
        x, y = P(la, lo); d.ellipse([x - 8, y - 8, x + 8, y + 8], fill='#1d4f91', outline='white', width=3); occ.append((x - 9, y - 9, x + 9, y + 9)); put(nm, x, y, '#1d4f91', 'white', 20, 'white')
    for (n, label, la, lo), (x, y) in zip(pins, pinpos): put(label, x, y, 'white', '#111', 23, '#111')
    d.rectangle([W - 250, H - 24, W, H], fill=(255, 255, 255, 210)); d.text((W - 6, H - 12), '© OpenStreetMap contributors', fill='#333', font=font(16), anchor='rm')
    img.convert('RGB').save(out)

def make_maps():
    pins = [(p[0], p[1], p[4], p[5]) for p in PLACES if p[4]]
    render(f'{CACHE}/map_akiba.png', 1400, 1000, pins, [], [('Akihabara Stn', *STN['Akihabara Stn'])])

# ---- html ---------------------------------------------------------------------------------------
def build_html():
    b64 = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    q = qrcode.make(URL, box_size=6, border=1); bb = io.BytesIO(); q.save(bb, 'PNG'); qr = base64.b64encode(bb.getvalue()).decode()
    band = ''.join(f'<div class="s{" first" if i == 0 else ""}"><b>{p[0] if i else "15:00"}</b>{p[1] if i else "Meet at Vie de France"}<small>{p[3] if i else "Then we choose as we go"}</small></div>' for i, p in enumerate(PLACES))
    photos = ''.join(f'<div><img src="{u}" alt=""></div>' for u in PHOTOS)
    rows = ''.join(f'<li><i{" class=st" if p[0] == "S" else ""}>{p[0]}</i><span><b>{p[2]}</b><em>{p[3]}</em></span><small>{p[6]}</small></li>' for p in PLACES)
    return f'''<!doctype html><meta charset=utf-8><title>Akihabara, Saturday October 31</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap" rel="stylesheet">
<style>@page{{size:A4 landscape;margin:0}}*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}body{{font:11px/1.4 Archivo,-apple-system,"Hiragino Sans",sans-serif;color:#111}}
article{{width:297mm;height:209mm;padding:8mm 11mm;overflow:hidden;display:flex;flex-direction:column}}
header{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5px solid #111;padding-bottom:4px;gap:14px;flex:none}}
h1{{font:900 40px/1 Archivo;font-stretch:75%;margin:0;white-space:nowrap}}.meta{{text-align:right;font-weight:700;font-size:14px}}
.chips span{{display:inline-block;border:1px solid #111;border-radius:12px;padding:0 9px;margin:4px 0 0 5px;font-size:11.5px}}
.ph{{display:grid;grid-template-columns:1.3fr 1.3fr 1fr 1fr;gap:6px;margin-top:7px;height:32mm;flex:none}}.ph div{{min-height:0;overflow:hidden}}.ph img{{display:block;width:100%;height:100%;object-fit:cover}}
.band{{display:flex;gap:5px;margin-top:7px;flex:none}}.s{{flex:1;background:#e4e0d2;padding:5px 10px;font-size:10.5px;line-height:1.2;font-weight:700;min-height:16mm}}
.s b{{display:block;font-size:16px;font-weight:900}}.s small{{display:block;font-weight:500;font-size:9.5px;opacity:.85;margin-top:1px}}.s.first{{background:#e60012;color:#fff;flex:1.25}}
.low{{display:grid;grid-template-columns:172mm 1fr;gap:8px;margin-top:8px;flex:1;min-height:0}}
.map{{width:100%;height:100%;object-fit:cover;border:2px solid #111;display:block;min-height:0}}
.side{{display:flex;flex-direction:column;min-height:0}}h2{{font:900 17px Archivo;margin:0 0 5px}}
ul{{list-style:none;margin:0 0 4px;padding:0}}li{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-bottom:7px;font-size:11.5px;line-height:1.15}}
li span{{flex:1;min-width:0}}li span b{{display:block;font-weight:800}}li span em{{font-style:normal;font-size:10px;font-weight:600;color:#e60012}}li small{{flex:0 0 100%;margin-left:25px;margin-top:-2px;font-size:9.5px;font-weight:500;color:#666}}
li i{{flex:none;width:19px;height:19px;border-radius:50%;background:#fff;color:#e60012;border:2px solid #e60012;font:800 11px/15px Archivo;text-align:center;font-style:normal}}li i.st{{background:#111;color:#fff;border-color:#111}}
.note{{margin:2px 0 0;padding:5px 8px;background:#e4e0d2;font-size:10px;font-weight:600}}
.foot{{display:flex;gap:8px;align-items:center;margin-top:auto;font-size:9.5px;color:#555;border-top:1px solid #111;padding-top:4px}}.foot img{{width:17mm;height:17mm;flex:none}}.foot p{{margin:0 0 2px}}</style>
<article><header><h1>Akihabara, Saturday October 31</h1><div class="meta">Guide: Yuuki · meet 15:00, until about 19:00<div class="chips"><span>Shrine</span><span>Anime shops</span><span>Retro games</span><span>Maid café</span></div></div></header>
<div class="ph">{photos}</div><div class="band">{band}</div>
<div class="low"><img class="map" src="{b64(CACHE + '/map_akiba.png')}" alt="">
<div class="side"><h2>Places to choose from</h2><ul>{rows}</ul><p class="note">This is not a fixed route. We choose the order as we go.</p>
<div class="foot"><img src="data:image/png;base64,{qr}"><div><p><b>Full plan and map:</b> yukitchy.github.io/carola-alberto-akiba-day</p><p>Questions on the day: message Yuuki on WhatsApp.</p></div></div></div></div></article>'''

def main():
    make_maps()
    html = build_html(); tmp = os.path.join(tempfile.gettempdir(), 'carola-sheet.html'); open(tmp, 'w').write(html)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1123, 'height': 794}); pg.goto('file://' + tmp); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(2500)
        over = pg.evaluate("(()=>{const a=document.querySelector('article'),s=document.querySelector('.side');return [a.scrollHeight>a.clientHeight+1, s.scrollHeight>s.clientHeight+1]})()")
        pg.pdf(path='carola-alberto-akiba-oct31.pdf', format='A4', landscape=True, print_background=True, prefer_css_page_size=True)
        pg.screenshot(path='carola-alberto-akiba-oct31.png', full_page=False); b.close()
    import re; d = open('carola-alberto-akiba-oct31.pdf', 'rb').read()
    print('pages', len(re.findall(rb'/Type\s*/Page[^s]', d)), 'overflow(article,side)', over)

if __name__ == '__main__': main()
