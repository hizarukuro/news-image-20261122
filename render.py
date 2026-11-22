#!/usr/bin/env python3
"""Render 'THE WORLD IN ONE DAY' — Sunday 22 November 2026 — as one 1024x1024 PNG.

A cream broadsheet front page drawn entirely with PIL: masthead, stat band,
region strip, timeline strip, three hero stories with drawn scenes, a numbered
grid of twelve more stories, a dotted world map whose pins carry the same
story numbers, an ALSO ON SUNDAY briefs section, a red DATE CHECK box and a
sources footer. Every number on the page comes from ONE ordered story list,
so heroes, grid, map pins and region counts can never disagree.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 24
CW = W - 2 * MARGIN  # content width

PAPER = (247, 241, 227)
PAPER_DK = (238, 229, 205)
INK = (24, 30, 43)
NAVY = (16, 36, 74)
NAVY_LT = (38, 62, 110)
RED = (172, 30, 38)
RED_BG = (250, 233, 226)
GOLD = (168, 124, 40)
GREY = (96, 94, 84)
RULE = (196, 186, 158)
CREAM = (250, 246, 233)
CHIP_BG = (16, 36, 74)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# ---------------------------------------------------------------- stories ---
# One ordered list: index + 1 IS the story number used everywhere on the page.
# region codes: EU, ME, AM, AP, AF, OC
STORIES = [
    # ---- heroes (1-3) ----
    dict(place="KYIV REGION, UKRAINE", topic="WAR", region="EU", pin=(31.0, 50.4),
         art="kyiv",
         headline="Russia fires 186 drones at Ukraine; Kyiv block destroyed",
         summary="Air defences downed or suppressed 161 overnight. In Dymer a "
                 "five-storey block was destroyed: 14 feared trapped, two "
                 "injured, nine evacuated.",
         source="UKRAINIAN AIR FORCE VIA WIRES", label=None),
    dict(place="ANTALYA, TÜRKIYE", topic="CLIMATE", region="EU", pin=(30.7, 36.9),
         art="cop",
         headline="COP31 ends without a deal — fossil fuels go unmentioned",
         summary="The final text never names fossil fuels, \u201crecalls\u201d the Dubai pact "
                 "and drops the $120bn adaptation target — the first to admit 1.5\u00b0C "
                 "will be overshot. EU: \u201ca good deal or no deal.\u201d",
         source="REUTERS \u00b7 BBC \u00b7 THE GUARDIAN", label=None),
    dict(place="MANAMA, BAHRAIN", topic="IRAN", region="ME", pin=(50.6, 26.2),
         art="manama",
         headline="Iran claims Patriot radars hit; Bahrain denies it",
         summary="The IRGC says it destroyed two US Patriot radars on Saturday "
                 "night. Bahrain answers: the target was a civilian industrial "
                 "site — a fire, no injuries — and a violation of its sovereignty.",
         source="KHALEEJ TIMES \u00b7 AL JAZEERA", label="CLAIM"),
    # ---- grid (4-15) ----
    dict(place="HONG KONG", topic="ELECTION", region="AP", pin=(114.2, 22.3),
         icon="ballot", chip="856 CANDIDATES",
         headline="Hong Kong polls draw record 98.37% turnout",
         summary="Election Committee vote: 856 candidates for 723 seats, 5,700 voters, "
                 "polls 09:00\u201318:00.",
         source="SCMP", label=None),
    dict(place="TEHRAN, IRAN", topic="ENERGY", region="ME", pin=(51.4, 35.7),
         icon="bolt", chip="CUTS UP TO 2H A DAY",
         headline="Iran begins rationing electricity",
         summary="Rolling cuts of up to two hours a day as war damage bites into the grid.",
         source="WIRES", label=None),
    dict(place="LAS VEGAS, USA", topic="FORMULA 1", region="AM", pin=(-115.1, 36.2),
         icon="f1", chip="WIN No. 75",
         headline="Verstappen wins in Las Vegas from pole",
         summary="0.639s clear of Norris at the flag — the Dutchman's 75th Grand Prix win.",
         source="FIA", label=None),
    dict(place="WELLINGTON, NZ", topic="CRICKET", region="OC", pin=(174.8, -41.3),
         icon="cricket", chip="RAHUL 156 \u00b7 PANT 128",
         headline="India declare on a record 720/9 in New Zealand",
         summary="Gill added 98; the hosts closed 119/2, trailing by 233.",
         source="ESPN", label=None),
    dict(place="CIKANDE, INDONESIA", topic="FIRE", region="AP", pin=(106.4, -6.3),
         icon="flame", chip="36 MISSING",
         headline="Candy-factory fire: 3 dead, 36 missing",
         summary="The blaze tore through the Banten plant; the search for the missing goes on.",
         source="ANTARA \u00b7 WIRES", label=None),
    dict(place="MANIPUR, INDIA", topic="POISONING", region="AP", pin=(93.9, 24.8),
         icon="bottle", chip="600 IN HOSPITAL",
         headline="Toxic-liquor toll climbs to 19",
         summary="The toll is up from 16 on Saturday, with 600 people in hospital.",
         source="XINHUA", label=None),
    dict(place="GULF OF FINLAND", topic="SEA", region="EU", pin=(25.0, 59.9),
         icon="ship", chip="RESCUE AT SEA",
         headline="Russian cargo ship Sparta II still burning",
         summary="Ablaze after a drone hit; Finland leads the rescue operation.",
         source="REUTERS", label=None),
    dict(place="GAZA CITY", topic="CONFLICT", region="ME", pin=(34.3, 31.5),
         icon="truck", chip="4 KILLED", label="REPORTED",
         headline="Israeli fire kills four in Gaza",
         summary="Three of the dead were in a food vehicle, the civil defence says.",
         source="GAZA CIVIL DEFENCE", label_src=None),
    dict(place="KHARTOUM, SUDAN", topic="WAR", region="AF", pin=(32.5, 15.6),
         icon="house", chip="HOMES HIT", label="REPORTED",
         headline="Drones strike homes near Khartoum",
         summary="Strikes hit houses near the capital; army air defences engaged.",
         source="AFP", label_src=None),
    dict(place="SOUTHERN NIGERIA", topic="DISASTER", region="AF", pin=(6.5, 5.5),
         icon="boat", chip="24 RESCUED",
         headline="Mourners' boat capsizes: 24 dead",
         summary="24 others were rescued after the boat overturned.",
         source="AP \u00b7 REUTERS", label=None),
    dict(place="SAN ANTONIO, USA", topic="NBA", region="AM", pin=(-98.5, 29.4),
         icon="ball", chip="114\u201391 FINAL",
         headline="Wembanyama scores 50 as Spurs roll on",
         summary="50 points, 19 rebounds and 5 blocks in a 114\u201391 win over New Orleans.",
         source="REUTERS", label=None),
    dict(place="JUN\u00cdN, PERU", topic="QUAKE TOLL", region="AM", pin=(-75.2, -11.5),
         icon="quake", chip="170 HOMES DAMAGED",
         headline="Peru quake toll updated: 1 dead, 16 hurt",
         summary="170 homes damaged in Jun\u00edn; the official count is now completed.",
         source="REUTERS", label=None),
]
for _i, _s in enumerate(STORIES):
    _s["n"] = _i + 1
    _s.setdefault("label", None)

# Briefs: uniform format "Place: text (Source)". region tags feed the strip.
BRIEFS = [
    ("Vatican", "EU", "Pope Leo XIV hosts 1,300 poor guests for the 10th World Day of the Poor", "Vatican News", None),
    ("Brussels", "EU", "Belgian air-traffic controllers join Monday's national strike — most flights grounded", "Wires", None),
    ("Bras\u00edlia", "AM", "Bolsonaro in intensive care — acute bowel obstruction, stable, surgery possible", "Reuters", None),
    ("Okinawa", "AP", "Shuri Castle's restored hall reopens, seven years after the fire", "Wires", None),
    ("Florida", "AM", "St. Johns River breaks a 73-year record near Cocoa after days of rain", "Wires", None),
    ("Delhi", "AP", "Nepal PM Shah lands on his first visit; meets Modi on Monday", "IANS", None),
    ("Fukushima", "AP", "Heavy snow strands about 1,500 people in a Japanese village", "dpa", None),
    ("Seoul", "AP", "Education minister's resignation accepted amid the AI-cheating exam scandal", "Wires", None),
    ("Canberra", "OC", "Marles calls the US view on AUKUS submarines \u201cwrong\u201d", "Wires", None),
    ("Moscow", "EU", "Russia says it downed 170 Ukrainian drones overnight", "Reuters", "CLAIM"),
    ("Turin", "EU", "ATP Finals title match still to come later today", "Forecast", None),
    ("Columbus", "AM", "Crew beat Messi's 10-man Inter Miami 3\u20130 in the MLS Cup playoffs, game 1", "AP \u00b7 MLS", None),
    ("Estonia", "EU", "Five Russia border crossings to shut on 1 Dec after a sabotage bid", "Reuters", None),
    ("Denmark", "EU", "Russian attach\u00e9 expelled over an alleged plot against a Ukrainian", "Wires", None),
    ("Taiwan", "AP", "Live-fire drill held on Kinmen", "CNA", None),
    ("South China Sea", "AP", "Chinese coast-guard ship turns back 170 km from Manila", "Wires", None),
    ("Kenya", "AF", "Last Ebola patient discharged", "Wires", None),
    ("Melbourne", "OC", "70 years since the 1956 Olympics opened", "ABC", None),
    ("West Bank", "ME", "Settlers torch 12 vehicles in four villages; Eisenkot calls it \u201cJewish terrorism\u201d; Israel opens an inquiry", "Wires", None),
]

REGION_NAMES = [("EU", "EUROPE"), ("ME", "MIDDLE EAST"), ("AM", "AMERICAS"),
                ("AP", "ASIA-PACIFIC"), ("AF", "AFRICA"), ("OC", "OCEANIA")]

STATS = [
    ("186", "DRONES FIRED AT UKRAINE OVERNIGHT"),
    ("161", "DOWNED OR SUPPRESSED"),
    ("$120bn", "ADAPTATION TARGET DROPPED"),
    ("55%", "ELECTRICITY-BY-2035 GOAL KEPT"),
    ("14", "FEARED TRAPPED IN DYMER"),
]

DATE_CHECK = [
    "Shenzhen trilateral summit — Thu\u2013Fri 19\u201320 Nov",
    "AI stock rout, S&P \u22123.7% — Fri 20 Nov",
    "Kryvyi Rih missile strike — Sat 21 Nov",
    "BepiColombo Mercury burn — Sat 21 Nov",
    "\u2018El Chapo Isidro\u2019 captured — Fri\u2013Sat",
    "Myanmar genocide ruling — Thu 19 Nov",
]

# Timeline watches: (watch name, [story numbers]) — numbers from the pool text.
WATCHES = [("OVERNIGHT", [1, 10]), ("MORNING", [4]), ("AFTERNOON", [7]),
           ("EVENING", [2]), ("NIGHT", [6, 14])]


# ---------------------------------------------------------------- helpers ---
def tw(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(draw, t, font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, x, y, text, font, fill, tracking=0, anchor="l"):
    """Draw text with letter tracking; anchor l/c/r on x."""
    widths = [tw(draw, ch, font) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    if anchor == "c":
        x -= total / 2
    elif anchor == "r":
        x -= total
    cx = x
    for ch, wch in zip(text, widths):
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += wch + tracking
    return total


def badge(draw, x, y, n, r=11, fill=RED):
    draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    f = F(SANS_B, 12 if n < 10 else 10)
    s = str(n)
    draw.text((x - tw(draw, s, f) / 2, y - f.size / 2 - 1), s, font=f, fill=CREAM)


def label_chip(draw, x, y, text):
    f = F(SANS_B, 8)
    wch = tw(draw, text, f) + 10
    draw.rectangle([x, y, x + wch, y + 13], fill=GOLD)
    draw.text((x + 5, y + 2), text, font=f, fill=(30, 24, 8))
    return wch


# ---------------------------------------------------------------- hero art --
def art_kyiv(w, h):
    """Night: searchlights and drones over a five-storey block, one corner gone."""
    img = Image.new("RGB", (w, h), (13, 20, 38))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(0, w, 7):  # stars
        if (i * 37) % 11 < 3:
            d.point((i, (i * 53) % (h // 3)), fill=(210, 218, 235, 200))
    d.ellipse([w - 52, 10, w - 26, 36], fill=(232, 230, 205))  # moon
    # searchlight cones
    d.polygon([(30, h), (120, 12), (168, 12)], fill=(240, 230, 170, 60))
    d.polygon([(w - 40, h), (w - 150, 18), (w - 112, 18)], fill=(240, 230, 170, 50))
    # drones: small quadcopter silhouettes with dotted trails
    for (dx, dy) in [(70, 30), (140, 20), (205, 38), (255, 24), (105, 52)]:
        d.ellipse([dx - 5, dy - 2, dx + 5, dy + 2], fill=(230, 90, 70))
        d.line([dx - 8, dy - 5, dx + 8, dy + 5], fill=(200, 200, 210), width=1)
        d.line([dx - 8, dy + 5, dx + 8, dy - 5], fill=(200, 200, 210), width=1)
        for t in range(1, 5):
            d.point((dx - t * 9, dy + t * 4), fill=(240, 200, 120, 160))
    # five-storey block
    bx, by, bw, bh = 58, h - 78, 200, 78
    d.rectangle([bx, by, bx + bw, by + bh], fill=(38, 46, 66))
    for r_ in range(5):
        for c_ in range(8):
            lit = (r_ * 8 + c_ * 3) % 5 < 2
            d.rectangle([bx + 8 + c_ * 24, by + 7 + r_ * 15,
                         bx + 20 + c_ * 24, by + 15 + r_ * 15],
                        fill=(250, 205, 105) if lit else (20, 26, 40))
    # destroyed right corner: jagged notch + rubble
    d.polygon([(bx + bw - 46, by), (bx + bw, by), (bx + bw, by + 30),
               (bx + bw - 22, by + 26), (bx + bw - 40, by + 44),
               (bx + bw - 30, by + 12)], fill=(13, 20, 38))
    for i in range(7):
        x0 = bx + bw - 52 + i * 8
        d.polygon([(x0, h), (x0 + 6, h - 6 - (i % 3) * 3), (x0 + 12, h)], fill=(70, 74, 88))
    d.rectangle([0, h - 3, w, h], fill=(8, 12, 22))
    return img


def art_cop(w, h):
    """Climate talks: globe, a thermometer past 1.5, flags, and a struck-out text."""
    img = Image.new("RGB", (w, h), (196, 220, 232))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([w - 62, 8, w - 22, 48], fill=(250, 205, 80))  # sun
    # globe
    gx, gy, gr = 86, h // 2 + 8, 52
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 120, 190))
    for (ex, ey, ew, eh) in [(gx - 34, gy - 30, 30, 18), (gx + 2, gy - 38, 26, 14),
                             (gx - 12, gy + 6, 34, 22), (gx + 22, gy + 18, 18, 12),
                             (gx - 40, gy + 22, 16, 10)]:
        d.ellipse([ex, ey, ex + ew, ey + eh], fill=(88, 160, 92))
    # thermometer
    tx = gx + gr + 30
    d.rounded_rectangle([tx, 18, tx + 14, h - 26], radius=7, fill=(240, 240, 235),
                        outline=INK, width=2)
    d.rectangle([tx + 4, 44, tx + 10, h - 30], fill=RED)
    d.ellipse([tx - 4, h - 34, tx + 18, h - 12], fill=RED)
    f = F(SANS_B, 11)
    d.text((tx + 19, 28), "1.5\u00b0C", font=f, fill=RED)
    d.line([tx + 15, 44, tx + 24, 44], fill=RED, width=2)
    # conference flags row
    flags = [(200, 60, 60), (60, 140, 220), (240, 190, 60), (40, 160, 90), (220, 80, 120)]
    for i, col in enumerate(flags):
        fx = 218 + i * 24
        d.line([fx, h - 52, fx, h - 18], fill=INK, width=2)
        d.polygon([(fx, h - 52), (fx + 16, h - 47), (fx, h - 42)], fill=col)
    # final text document with fossil fuels struck out
    d.rectangle([218, 16, w - 12, 62], fill=(252, 250, 242), outline=INK, width=1)
    d.line([226, 28, w - 22, 28], fill=GREY, width=2)
    d.line([226, 38, w - 40, 38], fill=GREY, width=2)
    d.line([226, 50, 268, 50], fill=GREY, width=2)
    d.line([268, 44, 302, 56], fill=RED, width=3)
    d.line([268, 56, 302, 44], fill=RED, width=3)
    d.rectangle([0, h - 14, w, h], fill=(52, 96, 60))
    return img


def art_manama(w, h):
    """Dusk: a Patriot radar and launcher, and smoke over an industrial site."""
    img = Image.new("RGB", (w, h), (24, 34, 48))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, h - 40, w, h], fill=(52, 44, 36))  # ground haze band
    # radar dish on a mast, left
    d.polygon([(34, h - 16), (44, h - 16), (40, 58)], fill=(150, 158, 170))
    d.arc([16, 26, 66, 66], start=300, end=130, fill=(205, 212, 222), width=4)
    d.line([40, 46, 66, 30], fill=(205, 212, 222), width=3)
    for r_ in (12, 20, 28):  # radar rings
        d.arc([66 - r_ // 2, 30 - r_ // 2, 66 + r_, 30 + r_], start=290, end=60,
              fill=(120, 200, 220, 170), width=1)
    # launcher vehicle, centre
    lx, ly = 108, h - 34
    d.rectangle([lx, ly, lx + 74, ly + 14], fill=(96, 104, 116))
    d.ellipse([lx + 8, ly + 10, lx + 22, ly + 24], fill=(20, 22, 26))
    d.ellipse([lx + 52, ly + 10, lx + 66, ly + 24], fill=(20, 22, 26))
    for i in range(2):  # raised missile tubes
        x0 = lx + 16 + i * 26
        d.polygon([(x0, ly), (x0 + 12, ly - 34), (x0 + 22, ly - 30), (x0 + 10, ly + 2)],
                  fill=(170, 178, 190))
    # industrial tanks, right, one smoking
    for i, tx in enumerate([216, 254]):
        d.rectangle([tx, h - 56, tx + 32, h - 14], fill=(120, 110, 96))
        d.ellipse([tx, h - 62, tx + 32, h - 50], fill=(140, 130, 114))
    for i in range(6):  # smoke plume + flame
        sx = 262 + i * 5
        sy = h - 66 - i * 9
        d.ellipse([sx - 8 - i, sy - 6, sx + 8 + i, sy + 6], fill=(90, 90, 96, 150))
    d.polygon([(266, h - 58), (272, h - 72), (278, h - 58)], fill=(245, 140, 50))
    d.rectangle([0, h - 4, w, h], fill=(10, 14, 20))
    return img


HERO_ART = {"kyiv": art_kyiv, "cop": art_cop, "manama": art_manama}


# ------------------------------------------------------------------- icons --
def icon_chip(draw, x, y, w, h, kind):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=5, fill=PAPER_DK,
                           outline=RULE, width=1)
    cx, cy = x + w / 2, y + h / 2
    c = NAVY
    if kind == "ballot":
        draw.rectangle([cx - 11, cy - 4, cx + 11, cy + 10], outline=c, width=2)
        draw.rectangle([cx - 5, cy - 12, cx + 5, cy - 4], outline=c, width=2)
        draw.line([cx - 2, cy + 1, cx + 5, cy + 6], fill=RED, width=2)
    elif kind == "bolt":
        draw.polygon([(cx + 3, cy - 13), (cx - 7, cy + 2), (cx - 1, cy + 2),
                      (cx - 3, cy + 13), (cx + 7, cy - 2), (cx + 1, cy - 2)],
                     fill=GOLD, outline=c)
    elif kind == "f1":
        draw.polygon([(cx - 15, cy + 6), (cx - 6, cy - 4), (cx + 6, cy - 4),
                      (cx + 14, cy + 6)], fill=c)
        draw.rectangle([cx - 16, cy + 6, cx + 16, cy + 9], fill=c)
        draw.ellipse([cx - 12, cy + 7, cx - 4, cy + 15], fill=INK)
        draw.ellipse([cx + 5, cy + 7, cx + 13, cy + 15], fill=INK)
        draw.rectangle([cx - 15, cy - 9, cx - 9, cy - 3], fill=RED)
    elif kind == "cricket":
        draw.polygon([(cx - 12, cy - 12), (cx - 6, cy - 14), (cx + 4, cy + 2),
                      (cx - 2, cy + 4)], fill=c)
        draw.ellipse([cx + 4, cy + 4, cx + 14, cy + 14], fill=RED)
    elif kind == "flame":
        draw.polygon([(cx, cy - 14), (cx + 8, cy - 2), (cx + 6, cy + 8),
                      (cx, cy + 13), (cx - 6, cy + 8), (cx - 8, cy - 2)],
                     fill=(232, 110, 40))
        draw.polygon([(cx, cy - 4), (cx + 4, cy + 3), (cx, cy + 10), (cx - 4, cy + 3)],
                     fill=(250, 200, 80))
    elif kind == "bottle":
        draw.polygon([(cx - 3, cy - 13), (cx + 3, cy - 13), (cx + 3, cy - 7),
                      (cx + 8, cy - 1), (cx + 8, cy + 12), (cx - 8, cy + 12),
                      (cx - 8, cy - 1), (cx - 3, cy - 7)], outline=c, width=2)
        draw.line([cx - 8, cy + 4, cx + 8, cy + 4], fill=RED, width=2)
    elif kind == "ship":
        draw.polygon([(cx - 15, cy + 4), (cx + 15, cy + 4), (cx + 10, cy + 12),
                      (cx - 10, cy + 12)], fill=c)
        draw.rectangle([cx - 8, cy - 6, cx + 4, cy + 4], fill=c)
        draw.rectangle([cx + 6, cy - 11, cx + 10, cy + 4], fill=RED)
        draw.arc([cx - 15, cy + 8, cx + 15, cy + 22], start=0, end=180, fill=NAVY_LT, width=2)
    elif kind == "truck":
        draw.rectangle([cx - 15, cy - 4, cx + 3, cy + 8], fill=c)
        draw.polygon([(cx + 3, cy + 1), (cx + 9, cy + 1), (cx + 14, cy + 8),
                      (cx + 3, cy + 8)], fill=c)
        draw.ellipse([cx - 10, cy + 6, cx - 3, cy + 13], fill=INK)
        draw.ellipse([cx + 6, cy + 6, cx + 13, cy + 13], fill=INK)
        draw.rectangle([cx - 12, cy - 10, cx - 4, cy - 4], fill=(88, 160, 92))
    elif kind == "house":
        draw.polygon([(cx - 13, cy - 2), (cx, cy - 13), (cx + 13, cy - 2)], fill=RED)
        draw.rectangle([cx - 9, cy - 2, cx + 9, cy + 11], outline=c, width=2)
        draw.line([cx - 13, cy + 13, cx + 14, cy - 8], fill=RED, width=2)
    elif kind == "boat":
        draw.polygon([(cx - 15, cy + 2), (cx + 15, cy + 2), (cx + 9, cy + 11),
                      (cx - 9, cy + 11)], fill=c)
        draw.line([cx, cy + 2, cx, cy - 12], fill=c, width=2)
        draw.polygon([(cx, cy - 12), (cx + 9, cy + 1), (cx, cy + 1)], fill=RED)
        draw.arc([cx - 15, cy + 7, cx + 15, cy + 21], start=0, end=180, fill=NAVY_LT, width=2)
    elif kind == "ball":
        draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=c, width=2)
        draw.arc([cx - 11, cy - 11, cx + 3, cy + 11], start=270, end=90, fill=RED, width=1)
        draw.arc([cx - 3, cy - 11, cx + 11, cy + 11], start=90, end=270, fill=RED, width=1)
    elif kind == "quake":
        draw.polygon([(cx - 15, cy + 10), (cx - 5, cy - 8), (cx + 3, cy + 2),
                      (cx + 9, cy - 11), (cx + 15, cy + 10)], outline=c, width=2)
        draw.line([cx - 2, cy - 6, cx + 1, cy + 1, cx - 2, cy + 10], fill=RED, width=2)


# -------------------------------------------------------------------- map ---
# Dotted world map from hand-set land spans on a 96 x 44 grid.
# Column c centres on lon -168 + 3.75c; row r centres on lat 79 - 3r.
LAND_SPANS = {
    0: [(24, 28), (34, 38), (48, 49), (66, 68), (72, 74)],
    1: [(19, 23), (31, 39), (48, 49), (62, 70), (76, 84), (88, 92)],
    2: [(1, 7), (13, 22), (30, 39), (55, 92)],
    3: [(0, 22), (24, 29), (30, 38), (53, 92)],
    4: [(0, 19), (24, 28), (31, 39), (40, 40), (48, 92)],
    5: [(0, 20), (24, 29), (31, 39), (48, 92)],
    6: [(1, 8), (9, 19), (25, 28), (33, 34), (44, 44), (48, 92)],
    7: [(11, 19), (23, 27), (43, 92)],
    8: [(12, 26), (43, 44), (45, 88)],
    9: [(12, 26), (44, 88)],
    10: [(12, 26), (43, 82)],
    11: [(12, 26), (43, 49), (50, 83)],
    12: [(12, 26), (43, 45), (47, 49), (50, 54), (55, 83)],
    13: [(13, 26), (43, 44), (47, 50), (50, 55), (55, 79), (81, 83)],
    14: [(13, 25), (43, 44), (48, 48), (50, 77), (78, 79), (81, 83)],
    15: [(13, 25), (42, 77), (81, 83)],
    16: [(14, 24), (42, 77), (81, 82)],
    17: [(15, 21), (24, 25), (40, 82)],
    18: [(15, 20), (39, 57), (66, 81)],
    19: [(16, 20), (39, 52), (55, 57), (67, 71), (75, 78)],
    20: [(16, 19), (39, 51), (67, 70), (75, 77), (80, 81)],
    21: [(19, 21), (39, 54), (67, 70), (75, 77), (80, 80)],
    22: [(20, 21), (24, 25), (40, 45), (47, 54), (68, 69), (75, 76), (80, 80)],
    23: [(24, 29), (40, 46), (50, 55), (68, 68), (75, 80)],
    24: [(24, 29), (41, 47), (51, 54), (71, 74), (76, 81), (82, 82)],
    25: [(23, 30), (44, 46), (52, 53), (71, 73), (77, 81), (86, 90)],
    26: [(23, 31), (44, 47), (48, 52), (77, 80), (86, 91)],
    27: [(23, 31), (44, 47), (49, 52), (72, 76), (87, 91)],
    28: [(23, 33), (44, 46), (47, 51), (72, 76), (87, 90)],
    29: [(23, 34), (44, 46), (47, 51), (79, 80)],
    30: [(23, 33), (44, 46), (49, 51), (75, 83)],
    31: [(24, 33), (44, 45), (48, 51), (53, 54), (74, 85)],
    32: [(25, 32), (44, 47), (49, 50), (53, 54), (74, 86)],
    33: [(25, 31), (44, 47), (53, 53), (74, 86)],
    34: [(25, 30), (45, 48), (74, 86)],
    35: [(25, 29), (45, 48), (75, 85)],
    36: [(25, 28), (45, 47), (76, 84)],
    37: [(25, 27), (77, 85), (91, 92)],
    38: [(25, 26), (82, 85), (90, 92)],
    39: [(24, 26), (82, 84), (90, 91)],
    40: [(24, 25), (84, 84), (89, 91)],
    41: [(24, 25), (89, 90)],
    42: [(24, 24), (89, 89)],
    43: [(24, 25)],
}


def map_xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 170) / 360.0 * w, y0 + (79 - lat) / 132.0 * h)


# ------------------------------------------------------------------ build ---
def rich_wrap(draw, segments, width):
    """segments: list of (text, font, fill). Returns lines of (word, font, fill)."""
    words = []
    for text, font, fill in segments:
        for w_ in text.split(" "):
            if w_:
                words.append((w_, font, fill))
    space_w = tw(draw, " ", segments[0][1])
    lines, cur, cur_w = [], [], 0.0
    for w_, font, fill in words:
        ww = tw(draw, w_, font)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [(w_, font, fill)], ww
        else:
            cur.append((w_, font, fill))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_rich(draw, x, y, lines, lh):
    for line in lines:
        cx = x
        for w_, font, fill in line:
            draw.text((cx, y), w_, font=font, fill=fill)
            cx += tw(draw, w_, font) + tw(draw, " ", font)
        y += lh
    return y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN
    xe = W - MARGIN

    # ---- masthead ----
    y = 12
    d.line([x0, y, xe, y], fill=INK, width=2)
    d.line([x0, y + 3, xe, y + 3], fill=INK, width=1)
    y += 8
    f_eye = F(SANS_B, 8)
    tracked(d, x0, y, "ONE PAGE \u00b7 ONE DAY \u00b7 THE WHOLE WORLD", f_eye, GREY, 1)
    tracked(d, xe, y, "PRESS TIME MON 23 NOV \u00b7 02:15 WIB", f_eye, GREY, 1, anchor="r")
    y += 13
    tracked(d, W // 2, y, "THE WORLD IN ONE DAY", F(SERIF, 29), NAVY, 5, anchor="c")
    y += 36
    tracked(d, W // 2, y, "SUNDAY 22 NOVEMBER 2026", F(SERIF, 42), INK, 2, anchor="c")
    y += 50
    stand = ("Russia's drone swarm over Kyiv, COP31's deal that never came, and Iran and "
             "Bahrain's rival claims — plus Hong Kong's record poll, Verstappen in Las "
             "Vegas and a record 720 in Wellington.")
    for ln in wrap(d, stand, F(SERIF_I, 13), 900):
        d.text(((W - tw(d, ln, F(SERIF_I, 13))) / 2, y), ln, font=F(SERIF_I, 13), fill=(60, 58, 50))
        y += 15
    y += 2
    d.line([x0, y, xe, y], fill=RED, width=2)

    # ---- stat band ----
    y += 5
    band_h = 36
    d.rectangle([x0, y, xe, y + band_h], fill=NAVY)
    cell_w = CW / len(STATS)
    for i, (num, lab) in enumerate(STATS):
        cx = x0 + i * cell_w
        if i:
            d.line([cx, y + 6, cx, y + band_h - 6], fill=NAVY_LT, width=1)
        f_num = F(SERIF, 19)
        d.text((cx + (cell_w - tw(d, num, f_num)) / 2, y + 3), num, font=f_num, fill=CREAM)
        f_lab = F(SANS_B, 7)
        lab_lines = wrap(d, lab, f_lab, cell_w - 12)
        ly = y + 24
        for ln in lab_lines[:1]:
            tracked(d, cx + cell_w / 2, ly, ln, f_lab, (196, 205, 226), 0, anchor="c")
    y += band_h

    # ---- region strip ----
    y += 5
    counts = {code: 0 for code, _ in REGION_NAMES}
    for s in STORIES:
        counts[s["region"]] += 1
    for b in BRIEFS:
        counts[b[1]] += 1
    total = sum(counts.values())
    parts = [f"{name} {counts[code]}" for code, name in REGION_NAMES]
    parts.append(f"WORLD {total}")
    strip = "   \u00b7   ".join(parts)
    tracked(d, W // 2, y, strip, F(SANS_B, 10), NAVY, 1, anchor="c")
    y += 13
    d.line([x0, y, xe, y], fill=RULE, width=1)

    # ---- timeline strip ----
    y += 4
    tracked(d, x0, y, "THE DAY IN FOUR WATCHES", F(SANS_B, 8), RED, 1)
    wx = x0 + 168
    for name, nums in WATCHES:
        tracked(d, wx, y, name, F(SANS_B, 9), INK, 1)
        wx += tw(d, name, F(SANS_B, 9)) + len(name) * 1 + 6
        ns = "\u00b7".join(str(n) for n in nums)
        d.text((wx, y - 1), ns, font=F(SANS_B, 10), fill=RED)
        wx += tw(d, ns, F(SANS_B, 10)) + 22
    y += 14
    d.line([x0, y, xe, y], fill=RULE, width=1)

    # ---- heroes ----
    y += 6
    hero_top = y
    col_w = (CW - 2 * 14) / 3
    art_h = 102
    for i, s in enumerate(STORIES[:3]):
        cx = x0 + i * (col_w + 14)
        art = HERO_ART[s["art"]](int(col_w), art_h)
        img.paste(art, (int(cx), y))
        badge(d, cx + 13, y + 13, s["n"], r=11)
        ky = y + art_h + 5
        kick = f"{s['place']} \u00b7 {s['topic']}"
        tracked(d, cx, ky, kick, F(SANS_B, 9), RED, 1)
        if s.get("label"):
            lw = tw(d, kick, F(SANS_B, 9)) + (len(kick) - 1)
            label_chip(d, cx + lw + 5, ky - 1, s["label"])
        hy = ky + 15
        for ln in wrap(d, s["headline"], F(SERIF, 17), col_w)[:3]:
            d.text((cx, hy), ln, font=F(SERIF, 17), fill=INK)
            hy += 19
        sy = hy + 2
        for ln in wrap(d, s["summary"], F(SANS, 10), col_w)[:5]:
            d.text((cx, sy), ln, font=F(SANS, 10), fill=(52, 54, 48))
            sy += 12.5
        d.text((cx, sy + 1), s["source"], font=F(SANS_B, 8), fill=GREY)
        if i < 2:
            d.line([cx + col_w + 7, hero_top, cx + col_w + 7, hero_top + 210],
                   fill=RULE, width=1)
    y = hero_top + 216
    d.line([x0, y, xe, y], fill=INK, width=1)

    # ---- map + date check ----
    y += 5
    map_top = y
    tracked(d, x0, y, "SUNDAY ON THE MAP \u00b7 STORIES 1\u201315 BY NUMBER", F(SANS_B, 9), NAVY, 1)
    map_w, map_h = 606, 120
    my = y + 16
    cell_wd, cell_ht = map_w / 96.0, map_h / 44.0
    for r_, spans in LAND_SPANS.items():
        for c0_, c1_ in spans:
            for c_ in range(c0_, c1_ + 1):
                px = x0 + c_ * cell_wd + cell_wd / 2
                py = my + r_ * cell_ht + cell_ht / 2
                d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(128, 138, 158))
    offsets = {10: (-6, -3), 1: (4, -3), 2: (-5, 2), 11: (6, 4), 5: (6, -3),
               3: (5, 2), 12: (-4, 2)}
    for s in STORIES:
        px, py = map_xy(s["pin"][0], s["pin"][1], x0, my, map_w, map_h)
        ox, oy = offsets.get(s["n"], (0, 0))
        badge(d, px + ox, py + oy, s["n"], r=7, fill=RED)
    # date check box
    bx = x0 + map_w + 14
    bw = xe - bx
    box_h = map_h + 15
    d.rectangle([bx, map_top, bx + bw, map_top + box_h], fill=RED_BG, outline=RED, width=2)
    tracked(d, bx + 10, map_top + 7, "DATE CHECK \u2014 NOT SUNDAY'S NEWS", F(SANS_B, 10), RED, 0)
    iy = map_top + 26
    for item in DATE_CHECK:
        d.text((bx + 10, iy), "\u2715", font=F(SANS_B, 10), fill=RED)
        d.text((bx + 24, iy + 1), item, font=F(SANS, 10), fill=INK)
        iy += 15
    d.text((bx + 10, iy + 3), "Checked and thrown out: this page is Sunday only.",
           font=F(SERIF_I, 10), fill=(120, 50, 40))
    y = map_top + box_h + 6
    d.line([x0, y, xe, y], fill=RULE, width=1)

    # ---- grid ----
    y += 5
    grid = STORIES[3:]
    gcol_w = (CW - 3 * 10) / 4
    row_h = 71
    for idx, s in enumerate(grid):
        r_, c_ = divmod(idx, 4)
        cx = x0 + c_ * (gcol_w + 10)
        cy = y + r_ * (row_h + 3)
        icon_chip(d, cx, cy + 2, 50, 50, s["icon"])
        badge(d, cx + 9, cy + 9, s["n"], r=9)
        tx = cx + 58
        tw_ = gcol_w - 58
        kick = f"{s['place']} \u00b7 {s['topic']}"
        tracked(d, tx, cy, kick, F(SANS_B, 7), RED, 0)
        if s.get("label"):
            label_chip(d, tx + tw(d, kick, F(SANS_B, 7)) + 5, cy - 1, s["label"])
        hy = cy + 10
        for ln in wrap(d, s["headline"], F(SERIF, 13), tw_)[:2]:
            d.text((tx, hy), ln, font=F(SERIF, 13), fill=INK)
            hy += 13.5
        sy = hy + 0.5
        for ln in wrap(d, s["summary"], F(SANS, 9), tw_)[:2]:
            d.text((tx, sy), ln, font=F(SANS, 9), fill=(52, 54, 48))
            sy += 10.5
        by = cy + row_h - 13
        f_chip = F(SANS_B, 8)
        chip_w = tw(d, s["chip"], f_chip) + 10
        d.rounded_rectangle([tx, by, tx + chip_w, by + 12], radius=3, fill=CHIP_BG)
        d.text((tx + 5, by + 2), s["chip"], font=f_chip, fill=CREAM)
        d.text((tx + chip_w + 5, by + 2), s["source"], font=F(SANS_B, 7), fill=GREY)
        if r_ < 2:
            d.line([cx, cy + row_h + 1, cx + gcol_w, cy + row_h + 1], fill=RULE, width=1)
    y += 3 * row_h + 2 * 3 + 2
    d.line([x0, y, xe, y], fill=INK, width=1)

    # ---- briefs ----
    y += 5
    tracked(d, x0, y, "ALSO ON SUNDAY", F(SERIF, 15), NAVY, 2)
    tracked(d, xe, y + 3, f"{len(BRIEFS)} BRIEFS \u00b7 {total} STORIES IN ALL",
            F(SANS_B, 8), GREY, 1, anchor="r")
    y += 21
    cols = [BRIEFS[:7], BRIEFS[7:13], BRIEFS[13:]]
    bcol_w = (CW - 2 * 14) / 3
    f_lead, f_body, f_src = F(SANS_B, 9), F(SANS, 9), F(SANS, 8)
    max_by = y
    for ci, col in enumerate(cols):
        cx = x0 + ci * (bcol_w + 14)
        by = y
        for place, _reg, text, src, lab in col:
            segs = [(place + ": ", f_lead, INK), (text, f_body, (45, 47, 42)),
                    (" (" + src + ")", f_src, GREY)]
            if lab:
                segs.append(("  " + lab, F(SANS_B, 8), GOLD))
            lines = rich_wrap(d, segs, bcol_w)
            by = draw_rich(d, cx, by, lines, 10.6)
            by += 2.5
        max_by = max(max_by, by)
        if ci < 2:
            d.line([cx + bcol_w + 7, y, cx + bcol_w + 7, by], fill=RULE, width=1)
    y = max_by + 2

    # ---- footer ----
    d.line([x0, y, xe, y], fill=INK, width=1)
    y += 4
    srcs = ("Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 The Guardian \u00b7 Al Jazeera \u00b7 SCMP \u00b7 ESPN \u00b7 FIA \u00b7 "
            "Xinhua \u00b7 Antara \u00b7 IANS \u00b7 CNA \u00b7 dpa \u00b7 ABC \u00b7 Khaleej Times \u00b7 Vatican News \u00b7 MLS — as reported "
            "on Sunday 22 November 2026.")
    tracked(d, W // 2, y, srcs, F(SANS, 8), GREY, 0, anchor="c")
    print("final y:", y + 12)
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    build().save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
