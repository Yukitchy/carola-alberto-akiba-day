#!/usr/bin/env python3
"""Carola & Alberto, Sat Oct 31: Akihabara places to choose from (not a fixed route).
Same design as the Patrick page (map on top, scroll story). python3 build.py -> index.html
DEVBAR=True shows the PC/phone toggle on the public URL while Yuuki reviews. Set False before it goes to the guests."""
import json
DEVBAR = False

gm = lambda q: 'https://www.google.com/maps/search/?api=1&query=' + q.replace(' ', '+')
A = lambda u, t: f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'
def links(*ls): return '<ul class="links">' + ''.join('<li>' + A(u, t) + '</li>' for t, u in ls) + '</ul>'
def pts(*ps): return '<ul class="pts">' + ''.join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in ps) + '</ul>'
def nums(*ns): return '<dl class="nums">' + ''.join(f'<div><dt>{a}</dt><dd class="n">{b}</dd><dd class="s">{c}</dd></div>' for a, b, c in ns) + '</dl>'
def ph(src, alt): return f'<div class="ph"><img src="{src}" alt="{alt}"></div>'

TH = 'https://upload.wikimedia.org/wikipedia/commons/thumb/'
IMG = dict(
    shop='https://upload.wikimedia.org/wikipedia/commons/5/59/Post_Earthquake_Tokyo_-_Animate_shop.jpg',
    street=TH + 'b/be/Akihabara_20211126_01.jpg/960px-Akihabara_20211126_01.jpg',
    arcade=TH + '9/94/GiGO_Retro_Games_Akihabara_15-09-2024_%281%29.jpg/960px-GiGO_Retro_Games_Akihabara_15-09-2024_%281%29.jpg',
    night=TH + '0/0c/Akihabara_Night.jpg/960px-Akihabara_Night.jpg')

# lat, lon, full name, short label, label side, tag.  [0] unused, [1] = meeting point (fixed), [2..5] = places to choose from.
# Trader: no coordinates found for the main store, so no pin; the map just shows the area.
P = [None,
     (35.69881, 139.77237, 'Vie de France, meeting point', 'Vie de France', 'r', '15:00'),
     (35.69830, 139.77085, 'G-Store Akiba', 'G-Store', 'l', 'A'),
     (35.6990, 139.7712, 'Trader main store', '', 'r', 'B'),
     (35.69922, 139.77095, 'GiGO retro games', 'GiGO', 't', 'C'),
     (35.69809, 139.77232, "Maidreamin Heaven's Gate", 'Maidreamin', 'b', 'D')]
DIAL = ['●', 'S', 'A', 'B', 'C', 'D']
EXTRA = ['Behind the scenes', 'Tomorrow']

HERO_CSS = """
.hero{background:var(--red);color:#fff;display:flex;flex-direction:column}
.hero .ht{display:flex;justify-content:space-between;gap:12px;padding:calc(16px + env(safe-area-inset-top,0px)) 16px 0;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase}
.hero h1{font-size:min(21vw,200px);line-height:.84;font-weight:900;letter-spacing:-.05em;text-transform:uppercase;margin:0;padding:8px 10px 14px 12px}
.hero{overflow:hidden}
.hero .mos{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:4px;padding:0 4px;box-sizing:border-box;width:100%;min-width:0}
.hero .mos figure{margin:0;position:relative;overflow:hidden;aspect-ratio:1/1;min-width:0;min-height:0;background:#c8321f}
.hero .mos figure.w{grid-column:1/3;aspect-ratio:16/10}
.hero .mos img{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:cover;display:block}
.hero .mos span{position:absolute;left:8px;bottom:8px;background:#fff;color:#111;font-size:12px;font-weight:900;padding:3px 8px}
.hero .hl{display:none}
.hero .hs{padding:14px 16px 20px;padding-left:max(16px,env(safe-area-inset-left,0px));font-size:16px;font-weight:700;line-height:1.5}
.intro h2.t{font-size:30px;line-height:1.3;font-weight:900;margin-top:6px}
@media(min-width:900px){.hero{display:grid;grid-template-columns:5fr 7fr;grid-template-rows:auto auto 1fr auto;height:100svh;min-height:560px}.hero .hl{display:flex;flex-direction:column;gap:10px;grid-column:1;padding:0 16px 4px;padding-left:max(16px,env(safe-area-inset-left,0px));min-height:0}.hl #hm{flex:1;min-height:0;border-radius:4px;overflow:hidden;background:#e9e9e6}.hl .cap{margin:0;font-size:clamp(12px,1.05vw,14px);font-weight:700;line-height:1.4}.hmp b{display:flex;width:34px;height:34px;border-radius:50%;background:var(--red);color:#fff;font-size:15px;font-weight:900;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.35)}.hmp.meet b{background:#111;font-size:10.5px;letter-spacing:-.02em}.hero .ht{grid-column:1}.hero h1{grid-column:1;font-size:min(8.8vw,210px)}.hero .hs{grid-column:1;align-self:end}.hero .mos{grid-column:2;grid-row:1/5;padding:4px;grid-template-rows:minmax(0,1.2fr) minmax(0,1fr) minmax(0,1.2fr);height:100%}.hero .mos figure,.hero .mos figure.w{aspect-ratio:auto}}
"""

def step(i, h, body, who=''):
    t = P[i][5]
    mark = '●' if i == 1 else t
    label = ('15:00 · fixed' if i == 1 else who)
    return f'<article class="step" data-i="{i}"><p class="no"><i>{mark}</i>{label}</p><h2>{h}</h2>{body}</article>'

S = []
S.append('<article class="step" data-i="0"><p class="no"><i>●</i>The whole afternoon</p><h2>Four places, <span class="l2">and <em>you</em> pick the order</span></h2>'
         '<p class="lead">This is not a fixed route. Yuuki meets you at 15:00 inside Vie de France, and from there these are the places we can go. Alberto, there are shops for One Piece, Hunter×Hunter and Dragon Ball. The arcade and the maid café are for both of you.</p>'
         + pts(('Good for', 'Anime shops, a retro arcade and a maid café, in one afternoon.'),
               ('Keep in mind', 'We decide as we go. If something catches your eye, we stop there. Today is Halloween, so the streets near the station can be busy.'))
         + '</article>')
S.append(step(1, 'We meet <em>inside the café</em>',
              '<p class="lead">Yuuki is inside Vie de France, in the BiTO Akiba Plaza building. It is about one minute from Akihabara station. Order a coffee if you like, and we choose the first place together.</p>'
              + nums(('Time', '15:00', 'Saturday, October 31'), ('Until', 'about 19:00', 'Akihabara'))
              + links(('Vie de France on Google Maps', gm('Vie de France BiTO AKIBA PLAZA Akihabara')))))
S.append(step(2, 'G-Store Akiba, <em>Jump shelves</em>', ph(IMG['street'], 'A main street of Akihabara by day')
              + '<p class="lead">Anime clothing on the 4th floor of the Onoden building. Half the shop is Jump titles, so One Piece, Hunter×Hunter and Dragon Ball are all here. The entrance is easy to miss, so Yuuki leads.</p>'
              + links(('G-Store Akiba on Google Maps', gm('G-Store Akiba Akihabara'))), 'For Alberto'))
S.append(step(3, 'Trader, <em>figures</em>',
              '<p class="lead">The main store of Trader is big and bright, with a lot of prize figures. A good place to look for One Piece and Dragon Ball.</p>'
              + links(('Trader on Google Maps', gm('Trader Akihabara main store'))), 'For Alberto'))
S.append(step(4, 'GiGO, <em>retro games</em>', ph(IMG['arcade'], 'Retro arcade machines at GiGO Akihabara')
              + '<p class="lead">The 6th floor is a retro arcade, with machines you can play together: Street Fighter II, Pac-Man, pinball. There are seats if anyone wants to rest.</p>'
              + links(('GiGO retro games on Google Maps', gm('RETRO:G Retro Games GiGO Akihabara'))), 'For both'))
S.append(step(5, "Maidreamin, <em>the maid café</em>", ph(IMG['night'], 'Akihabara at dusk, with anime billboards')
              + "<p class=\"lead\">The maid café you both asked for. Heaven's Gate is right by the station, and there is a good chance of a live show. You choose what to order there. It is a good last stop, because the station is one minute away.</p>"
              + nums(('Open', '10:30 to 23:00', 'every day'))
              + links(("Maidreamin Heaven's Gate on Google Maps", gm("Maidreamin Heaven's Gate Akihabara"))), 'For both'))
S.append('<article class="step" data-i="6"><p class="no"><i>AI</i>For the AI student</p><h2>How today was made, <span class="l2"><em>behind the scenes</em></span></h2>'
         '<p class="lead">Alberto, you are studying AI here, so this is the inside view. Between your booking this morning and the moment we meet, a team of AI assistants did the preparation. Yuuki made the decisions.</p>'
         + pts(('08:19', 'You booked. Your note said: a 25-year-old anime fan, a mother who loves culture, and a maid café for both of you.'),
               ('10:30', 'An assistant wrote your welcome email. It read your note, confirmed that we meet inside Vie de France, and sent you the short questionnaire. New bookings are spotted within 15 minutes, with nobody watching.'),
               ('10:59', 'You answered: One Piece, Hunter×Hunter, Dragon Ball, retro games, and a maid café.'),
               ('12:30', 'The places on this page were chosen from your answers. Most came from Yuuki\'s own notes on Akihabara.'),
               ('15:00', 'Yuuki meets you. From here it is a person, not a screen.'))
         + '<p class="lead">Yuuki runs his work with 13 AI assistants. Each has one job and its own workspace, so they do not step on each other. One model gathers information, a second one checks it, and only then does it go into a plan.</p>'
         '<p class="note" style="font-size:14px">The assistants do the research, the drafts and the checking. A person decides. If you want to ask how any of it works, ask on the way. Alberto, that goes double for you.</p></article>')
S.append('<article class="step" data-i="7"><p class="no"><i>♪</i>If you still have energy</p><h2>Tomorrow</h2>'
         + links(('Ikebukuro Halloween Cosplay Fest, 10:00 to 18:00', 'https://ikebukurocosplay.jp/en/')) + '</article>')

credit_items = ['Post Earthquake Tokyo - Animate shop.jpg, CC BY-SA 2.0', 'Akihabara 20211126 01.jpg, CC0',
                'GiGO Retro Games Akihabara 15-09-2024 (1).jpg, CC BY 4.0', 'Akihabara Night.jpg, CC BY 4.0']
credit = ('<footer class="credit"><p class="note" style="margin:0 0 10px">Times are approximate and can move on the day. Message Yuuki if you want to change anything.</p><details><summary>Photo credits</summary><ul>'
          + ''.join(f'<li>{c}</li>' for c in credit_items)
          + '</ul><p>Photos via Wikimedia Commons. Map: Tiles © Esri / © ' + A('https://www.openstreetmap.org/copyright', 'OpenStreetMap') + '</p></details></footer>')
dn = ''.join(f'<button type="button" class="dn" data-i="{i}" aria-label="{"The whole afternoon" if i == 0 else P[i][2]}">{DIAL[i]}</button>' for i in range(len(P)))
TITLE = 'Your afternoon in Akihabara'
DESC = 'Four places to choose from in Akihabara on Saturday, October 31: anime shops, retro games and a maid café. Yuuki meets you at 15:00 inside Vie de France.'
head = ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><meta name="robots" content="noindex,nofollow"><title>' + TITLE + '</title>'
        f'<meta property="og:title" content="{TITLE}"><meta property="og:description" content="{DESC}"><meta property="og:type" content="website"><meta property="og:url" content="https://yukitchy.github.io/carola-alberto-akiba-day/"><meta property="og:image" content="{IMG["night"]}"><meta name="twitter:card" content="summary_large_image">'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;900&display=swap">'
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"><script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script><style>' + open('style.css').read() + HERO_CSS + '</style></head><body>')
def tile(k, cap, alt, wide=False):
    return f'<figure{" class=w" if wide else ""}><img src="{IMG[k]}" alt="{alt}"><span>{cap}</span></figure>'
hero = ('<header class="hero"><div class="ht"><span>Saturday, October 31</span><span>15:00 to 19:00</span></div><h1>AKI<br>HABARA</h1>'
        '<div class="hl"><div id="hm" aria-label="Map: meeting point and places"></div><p class="cap">15:00 meet inside Vie de France. A to D are the places we can choose from. B, Trader, is on the list below.</p></div>'
        '<div class="mos">' + tile('night', 'D  Maid café', 'Akihabara at dusk, with anime billboards', True)
        + tile('arcade', 'C  Retro games', 'Retro arcade machines at GiGO Akihabara')
        + tile('street', 'Akihabara', 'A main street of Akihabara by day')
        + tile('shop', 'A, B  Anime shops', 'An anime shop front in Akihabara at night', True) + '</div>'
        '<p class="hs">Carola and Alberto, we meet at 15:00 inside Vie de France.</p></header>')
intro = ('<div class="wrap"><div class="mapbox"><div id="map" aria-label="Map of the places"></div><p class="where"><small>Saturday, October 31</small><b>The whole afternoon</b></p>'
         '<nav class="dial" aria-label="Switch place"><button type="button" class="ar" data-d="-1" aria-label="Previous place">&lsaquo;</button><div class="nums-r">' + dn + '</div><button type="button" class="ar" data-d="1" aria-label="Next place">&rsaquo;</button></nav></div>'
         f'<main class="story"><header class="intro"><p class="date">Saturday, October 31 · 15:00 to 19:00</p><h2 class="t">{TITLE}</h2><p class="who">Carola and Alberto, with Yuuki. Anime shops, retro games and a maid café, to choose from as we go.</p>'
         '<dl class="cn"><div><dt>Meet</dt><dd class="n">15:00</dd><dd class="s">Inside Vie de France</dd></div><div><dt>Until</dt><dd class="n">19:00</dd><dd class="s">Akihabara</dd></div></dl>'
         '<div class="tools"><a class="tool" href="carola-alberto-akiba-oct31.pdf" target="_blank" rel="noopener">Open the PDF (A4, 1 page)</a></div></header>')
js = ('<script>const LI=99,LUNCH=[],DAYS=%s,EXTRA=%s,P=%s,GEO=[[35.6985,139.7715,"Akihabara"]];'
      % (json.dumps(['The whole afternoon'] + [p[2] for p in P[1:]]), json.dumps(EXTRA), json.dumps([None] + [[p[0], p[1], p[2], p[3], p[4], 0] for p in P[1:]])))
js += open('map.js').read() + open('hmap.js').read() + '</script>'
dev = '<script>window.DEVBAR_FORCE=innerWidth>=900</script><script src="devbar.js"></script>' if DEVBAR else '<script src="devbar.js"></script>'
open('index.html', 'w').write(head + hero + intro + ''.join(S) + credit + '</main></div>' + js + dev + '</body></html>')
