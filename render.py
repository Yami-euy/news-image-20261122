"""Front page for Sunday 22 November 2026 — flat-illustration newspaper.

Draws one 1024x1024 PNG with PIL only: no network, no photos, no dynamic
dates. Every story on the page happened, or was first reported, on
Sunday 22 November 2026 (UTC). Written from scratch for this competition.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 22
CW = W - 2 * M  # 980

PAPER = (247, 242, 231)
INK = (26, 26, 26)
SOFT = (74, 70, 62)
RED = (166, 25, 46)
BLUE = (31, 58, 95)
GOLD = (176, 132, 30)
SLATE = (96, 110, 126)
LIGHT = (233, 227, 211)
RULEC = (150, 138, 118)
CREAM = (250, 246, 236)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked(d, xy, text, font, fill, tr=1):
    """Draw text with letter tracking; returns the x after the last glyph."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tr
    return x


def twidth(d, text, font):
    return d.textlength(text, font=font)


def centre(d, cx, y, text, font, fill):
    d.text((cx - twidth(d, text, font) / 2, y), text, font=font, fill=fill)


def hrule(d, x, y, w, color=RULEC, width=1):
    d.line([(x, y), (x + w, y)], fill=color, width=width)


def tag_chip(d, x, y, label, bg, fg=(255, 255, 255)):
    """Small certainty tag; returns the chip width."""
    font = F(SANS_B, 9)
    w = int(twidth(d, label, font)) + 12
    d.rounded_rectangle([x, y, x + w, y + 14], radius=3, fill=bg)
    d.text((x + 6, y + 2), label, font=font, fill=fg)
    return w


# ---------------------------------------------------------------- land mask
# Coarse equirectangular land mask for the dotted world-map strip.
# Each row: (latitude, [(lon_min, lon_max), ...]). Rows run 78N to 54S.
LAND = [
    (78, [(-125, -85), (-58, -22), (35, 180)]),
    (74, [(-170, -125), (-95, -60), (-55, -20), (30, 180)]),
    (70, [(-165, -140), (-125, -60), (-55, -25), (30, 180)]),
    (66, [(-165, -140), (-125, -55), (10, 180)]),
    (62, [(-165, -140), (-125, -60), (5, 35), (25, 180)]),
    (58, [(-150, -125), (-125, -65), (-10, 10), (5, 30), (30, 180)]),
    (54, [(-130, -120), (-125, -65), (-10, 2), (0, 30), (30, 180)]),
    (50, [(-125, -65), (-5, 30), (30, 140), (140, 160)]),
    (46, [(-125, -65), (-2, 30), (30, 135), (140, 142)]),
    (42, [(-125, -65), (-10, 30), (30, 130), (130, 145)]),
    (38, [(-125, -70), (-10, 35), (35, 140), (130, 141)]),
    (34, [(-120, -70), (-10, 35), (35, 125), (126, 130)]),
    (30, [(-115, -80), (-10, 32), (35, 120), (120, 122)]),
    (26, [(-115, -80), (-15, 32), (35, 60), (60, 100), (100, 120)]),
    (22, [(-110, -85), (-17, 35), (35, 60), (65, 100), (100, 110)]),
    (18, [(-105, -85), (-17, 35), (40, 55), (75, 100)]),
    (14, [(-100, -80), (-15, 40), (75, 105)]),
    (10, [(-85, -75), (-15, 45), (95, 105)]),
    (6, [(-80, -75), (-10, 45), (95, 105)]),
    (2, [(-78, -50), (-10, 40), (95, 105)]),
    (-2, [(-80, -35), (-10, 40), (95, 140)]),
    (-6, [(-80, -35), (10, 40), (105, 140)]),
    (-10, [(-75, -35), (12, 40), (110, 140)]),
    (-14, [(-70, -35), (12, 35), (125, 145)]),
    (-18, [(-70, -40), (12, 35), (115, 150)]),
    (-22, [(-70, -40), (15, 32), (113, 150)]),
    (-26, [(-70, -40), (15, 32), (113, 150)]),
    (-30, [(-70, -55), (18, 30), (115, 150)]),
    (-34, [(-70, -55), (18, 28), (115, 150)]),
    (-38, [(-72, -58), (140, 150)]),
    (-42, [(-73, -62), (145, 150)]),
    (-46, [(-73, -65)]),
    (-50, [(-73, -65)]),
    (-54, [(-70, -65)]),
]

# (number, name, lat, lon, chip dx, chip dy) — pins on the map strip.
# dx/dy move the numbered chip away from the pin dot; a thin leader line
# connects them. The Europe–Middle East cluster (1, 2, 10, 11, 12) is
# spread out so no two chips overlap.
PINS = [
    (1, "KYIV", 50.45, 30.52, -14, -10),
    (2, "ANTALYA", 36.90, 30.70, -18, 12),
    (3, "BAHRAIN", 26.20, 50.60, 12, -12),
    (4, "HONG KONG", 22.30, 114.20, 0, -14),
    (5, "LAS VEGAS", 36.20, -115.10, -14, -12),
    (6, "NEW ZEALAND", -41.30, 174.80, -22, -6),
    (7, "SAN ANTONIO", 29.40, -98.50, 0, 14),
    (8, "CIKANDE", -6.20, 106.30, 14, 10),
    (9, "BAYELSA", 4.90, 6.30, -16, -10),
    (10, "GAZA", 31.50, 34.50, 14, 12),
    (11, "KHARTOUM", 15.60, 32.50, 2, 14),
    (12, "BENGHAZI", 32.10, 20.10, -20, -4),
    (13, "HORMUZ", 26.50, 56.30, 16, 4),
]


def project(lon, lat, mx, my, mw, mh):
    """Equirectangular projection into the map rectangle (72N to 48S)."""
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (72.0 - lat) / 120.0 * mh
    return x, y


MAP_FILL = (196, 203, 212)   # pale blue-grey land fill
MAP_COAST = (96, 110, 126)   # slate coastline


def _is_land(lon, lat):
    """Land test from the hardcoded LAND table (nearest latitude row)."""
    best = None
    for row_lat, ranges in LAND:
        if best is None or abs(lat - row_lat) < abs(lat - best[0]):
            best = (row_lat, ranges)
    for lo, hi in best[1]:
        if lo <= lon <= hi:
            return True
    return False


def draw_map(img, d, mx, my, mw, mh):
    """Readable world map: filled continents + coastline + leader-line pins.

    A 1-degree land mask (360x120, from the LAND table) is bilinearly
    resized into the strip, so the continents read as solid shapes instead
    of a sparse dot grid; a thin slate coastline is drawn from the mask's
    edge cells. Numbered chips sit away from their pin dots on short
    leader lines, so the Europe–Middle East cluster stays legible.
    """
    # 1-degree mask: 360 cols (lon -180..179), 120 rows (lat 72..-47).
    mask_small = Image.new("L", (360, 120), 0)
    px = mask_small.load()
    for row in range(120):
        lat = 72.0 - row
        for col in range(360):
            if _is_land(col - 180.0, lat):
                px[col, row] = 255
    mask = mask_small.resize((mw, mh), Image.BILINEAR)
    land_layer = Image.new("RGB", (mw, mh), MAP_FILL)
    img.paste(land_layer, (mx, my), mask)
    # coastline: land cells with a sea neighbour, drawn as 1 px dots.
    for row in range(120):
        lat = 72.0 - row
        for col in range(360):
            if px[col, row] != 255:
                continue
            sea_near = False
            for ncol, nrow in ((col - 1, row), (col + 1, row),
                               (col, row - 1), (col, row + 1)):
                if ncol < 0 or ncol >= 360 or nrow < 0 or nrow >= 120:
                    sea_near = True
                    break
                if px[ncol, nrow] == 0:
                    sea_near = True
                    break
            if sea_near:
                cx, cy = project(col - 180.0 + 0.5, lat, mx, my, mw, mh)
                d.point((cx, cy), fill=MAP_COAST)
    # pins: small dot on the true spot, numbered chip on a leader line.
    pf = F(SANS_B, 8)
    for num, name, lat, lon, dx, dy in PINS:
        px_, py_ = project(lon, lat, mx, my, mw, mh)
        cx, cy = px_ + dx, py_ + dy
        main_pin = num <= 3
        fill = RED if main_pin else (255, 255, 255)
        edge = RED if main_pin else BLUE
        ncol = (255, 255, 255) if main_pin else BLUE
        d.line([(px_, py_), (cx, cy)], fill=MAP_COAST, width=1)
        d.ellipse([px_ - 4, py_ - 4, px_ + 4, py_ + 4], fill=fill,
                  outline=edge, width=1)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=fill,
                  outline=edge, width=1)
        t = str(num)
        d.text((cx - twidth(d, t, pf) / 2, cy - 5), t, font=pf, fill=ncol)


# ------------------------------------------------------- flat illustrations
def _star(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def _burst(d, cx, cy, r1, r2, fill, points=10):
    import math
    pts = []
    for i in range(points * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def illo_ukraine(d, x, y, w, h):
    """Night sky over Kyiv: drones, a lit block of flats, one blast."""
    d.rectangle([x, y, x + w, y + h], fill=(22, 35, 61))
    for sx, sy, sr in [(30, 18, 1), (90, 10, 1), (150, 24, 1), (210, 12, 1),
                       (260, 30, 1), (60, 40, 1), (180, 36, 1), (300, 20, 1)]:
        _star(d, x + sx, y + sy, sr, (220, 225, 235))
    d.ellipse([x + w - 52, y + 10, x + w - 22, y + 40], fill=(235, 230, 200))
    # three drones: dark diamond bodies, rotor dots, red/green lights
    for dx, dy in [(70, 42), (150, 30), (228, 52)]:
        d.polygon([(x + dx, y + dy - 7), (x + dx + 9, y + dy),
                   (x + dx, y + dy + 7), (x + dx - 9, y + dy)], fill=(12, 18, 30))
        for rx in (-11, 11):
            d.ellipse([x + dx + rx - 2, y + dy - 9, x + dx + rx + 2, y + dy - 5],
                      fill=(200, 210, 220))
        _star(d, x + dx - 9, y + dy + 2, 2, (255, 70, 70))
        _star(d, x + dx + 9, y + dy + 2, 2, (90, 255, 140))
    # block of flats, left; blast above its roof
    bx, by, bw, bh = x + 24, y + h - 62, 120, 62
    d.rectangle([bx, by, bx + bw, by + bh], fill=(52, 58, 74))
    for row in range(4):
        for col in range(6):
            wx, wy = bx + 8 + col * 19, by + 8 + row * 13
            lit = (row + col) % 3 != 0
            d.rectangle([wx, wy, wx + 11, wy + 8],
                        fill=(255, 214, 110) if lit else (38, 44, 58))
    _burst(d, bx + bw - 6, by - 8, 26, 10, (255, 170, 40))
    _burst(d, bx + bw - 6, by - 8, 14, 6, (255, 230, 130))
    d.polygon([(bx + bw - 6, by - 8), (bx + bw + 40, by - 34),
               (bx + bw + 52, by - 30), (bx + bw - 6, by - 2)], fill=(255, 200, 90))
    # ground + a second, darker block
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(16, 24, 42))
    d.rectangle([x + w - 110, y + h - 46, x + w - 20, y + h - 8],
                fill=(40, 46, 62))
    for row in range(2):
        for col in range(4):
            d.rectangle([x + w - 102 + col * 21, y + h - 40 + row * 15,
                         x + w - 94 + col * 21, y + h - 33 + row * 15],
                        fill=(255, 214, 110) if (row + col) % 2 else (30, 36, 50))


def illo_cop31(d, x, y, w, h):
    """Dawn in Antalya: rising sun, conference hall, flags, no smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 226, 204))
    d.rectangle([x, y, x + w, y + 58], fill=(126, 178, 178))
    d.rectangle([x, y + 58, x + w, y + 92], fill=(214, 176, 132))
    d.ellipse([x + w // 2 - 46, y + 22, x + w // 2 + 46, y + 114],
              fill=(235, 122, 52))
    d.ellipse([x + w // 2 - 30, y + 38, x + w // 2 + 30, y + 98],
              fill=(245, 158, 84))
    # conference hall: white block, blue dome, columns
    hx, hy, hw, hh = x + 58, y + h - 58, w - 116, 58
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=(248, 246, 240))
    d.pieslice([hx + hw // 2 - 26, hy - 26, hx + hw // 2 + 26, hy + 26],
               180, 360, fill=(52, 96, 140))
    for i in range(6):
        cx = hx + 18 + i * (hw - 36) // 5
        d.rectangle([cx - 4, hy + 12, cx + 4, hy + hh], fill=(200, 194, 178))
    d.rectangle([hx - 8, hy + 2, hx + hw + 8, hy + 10], fill=(52, 96, 140))
    # row of small flags on the roof line
    for i, col in enumerate([(166, 25, 46), (31, 58, 95), (176, 132, 30),
                             (46, 120, 80), (120, 60, 140), (200, 90, 40)]):
        fx = hx + 26 + i * 32
        d.line([(fx, hy - 22), (fx, hy + 2)], fill=(90, 84, 70), width=2)
        d.polygon([(fx, hy - 22), (fx + 14, hy - 18), (fx, hy - 13)], fill=col)
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(86, 140, 92))
    # two green leaves (climate) flanking the hall
    for lx, flip in [(x + 16, 1), (x + w - 16, -1)]:
        x0, x1 = sorted((lx - 14 * flip, lx + 14 * flip))
        d.ellipse([x0, y + h - 34, x1, y + h - 6], fill=(46, 120, 80))


def illo_bahrain(d, x, y, w, h):
    """Dusk over the Gulf: radar dish, interceptor streaks, desert."""
    d.rectangle([x, y, x + w, y + h], fill=(64, 48, 84))
    d.rectangle([x, y + 46, x + w, y + 88], fill=(196, 116, 84))
    d.ellipse([x + 26, y + 12, x + 58, y + 44], fill=(245, 200, 130))
    # radar dish on a mast, beam sweeping up-right
    mx, my = x + 96, y + h - 34
    d.rectangle([mx - 5, my - 34, mx + 5, my], fill=(70, 66, 60))
    d.arc([mx - 34, my - 80, mx + 34, my - 12], 200, 340,
          fill=(232, 228, 216), width=6)
    d.line([(mx - 32, my - 46), (mx + 32, my - 46)], fill=(232, 228, 216),
           width=3)
    d.ellipse([mx - 4, my - 48, mx + 4, my - 40], fill=(232, 228, 216))
    d.line([(mx, my - 44), (mx + 46, my - 86)], fill=(255, 220, 120), width=2)
    _star(d, mx + 46, my - 86, 3, (255, 220, 120))
    # two missile streaks crossing the sky
    for (sx, sy, ex, ey) in [(x + 170, y + 20, x + 240, y + 62),
                             (x + 150, y + 44, x + 226, y + 84)]:
        d.line([(sx, sy), (ex, ey)], fill=(255, 200, 110), width=3)
        _burst(d, ex, ey, 12, 5, (255, 220, 140))
    # low skyline + desert ground
    d.rectangle([x + w - 120, y + h - 52, x + w - 70, y + h - 26],
                fill=(52, 44, 66))
    d.rectangle([x + w - 64, y + h - 44, x + w - 24, y + h - 26],
                fill=(52, 44, 66))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(150, 118, 74))
    d.rectangle([x, y + h - 26, x + w, y + h - 18], fill=(168, 134, 88))


# Mini icons for the 10-story grid; each draws inside a 188x44 band.
def _mini_bg(d, x, y, w, h, bg):
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bg)


def mini_ballot(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (222, 226, 232))
    d.rectangle([x + 66, y + 16, x + 122, y + 40], fill=(250, 248, 242))
    d.rectangle([x + 66, y + 16, x + 122, y + 22], fill=(166, 25, 46))
    d.rectangle([x + 88, y + 18, x + 100, y + 20], fill=(40, 40, 40))
    d.polygon([(x + 84, y + 4), (x + 106, y + 4), (x + 100, y + 16),
               (x + 90, y + 16)], fill=(255, 255, 255))
    d.line([(x + 88, y + 8), (x + 100, y + 12)], fill=(166, 25, 46), width=2)


def mini_car(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (30, 42, 60))
    d.polygon([(x + 52, y + 30), (x + 66, y + 16), (x + 108, y + 16),
               (x + 128, y + 26), (x + 140, y + 30)], fill=(196, 30, 46))
    d.rectangle([x + 56, y + 28, x + 136, y + 33], fill=(196, 30, 46))
    for wx in (72, 118):
        d.ellipse([x + wx, y + 28, x + wx + 16, y + 42], fill=(20, 20, 20))
        d.ellipse([x + wx + 5, y + 33, x + wx + 11, y + 39], fill=(180, 180, 180))
    d.rectangle([x + 136, y + 12, x + 140, y + 30], fill=(196, 30, 46))
    d.line([(x + 40, y + 40), (x + 150, y + 40)], fill=(250, 220, 90), width=2)


def mini_cricket(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (214, 226, 198))
    d.polygon([(x + 78, y + 6), (x + 92, y + 6), (x + 104, y + 34),
               (x + 92, y + 38), (x + 80, y + 12)], fill=(150, 104, 60))
    d.rectangle([x + 96, y + 34, x + 104, y + 42], fill=(110, 76, 44))
    d.ellipse([x + 118, y + 26, x + 134, y + 42], fill=(166, 25, 46))
    d.arc([x + 118, y + 26, x + 134, y + 42], 300, 60, fill=(255, 255, 255),
          width=1)
    d.line([(x + 40, y + 40), (x + 150, y + 40)], fill=(120, 140, 100), width=2)


def mini_basket(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (240, 224, 200))
    d.ellipse([x + 76, y + 4, x + 112, y + 40], fill=(224, 104, 44))
    d.arc([x + 76, y + 4, x + 112, y + 40], 0, 360, fill=(40, 30, 26), width=2)
    d.line([(x + 76, y + 22), (x + 112, y + 22)], fill=(40, 30, 26), width=2)
    d.line([(x + 94, y + 4), (x + 94, y + 40)], fill=(40, 30, 26), width=2)
    d.arc([x + 82, y + 10, x + 106, y + 34], 200, 340, fill=(40, 30, 26),
          width=2)


def mini_factory(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (228, 214, 196))
    d.rectangle([x + 60, y + 20, x + 118, y + 40], fill=(110, 108, 100))
    d.polygon([(x + 60, y + 20), (x + 76, y + 10), (x + 92, y + 20)],
              fill=(90, 88, 82))
    d.polygon([(x + 92, y + 20), (x + 104, y + 12), (x + 118, y + 20)],
              fill=(90, 88, 82))
    d.rectangle([x + 122, y + 6, x + 130, y + 40], fill=(90, 88, 82))
    _burst(d, x + 126, y + 4, 10, 4, (255, 150, 40))
    for wx in (68, 84, 100):
        d.rectangle([x + wx, y + 26, x + wx + 8, y + 34], fill=(255, 220, 130))


def mini_boat(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (196, 216, 228))
    d.polygon([(x + 58, y + 22), (x + 132, y + 22), (x + 122, y + 34),
               (x + 68, y + 34)], fill=(120, 72, 44))
    d.rectangle([x + 88, y + 8, x + 92, y + 22], fill=(90, 80, 70))
    d.polygon([(x + 92, y + 8), (x + 110, y + 18), (x + 92, y + 18)],
              fill=(250, 248, 242))
    for wy in (36, 40):
        d.line([(x + 46, y + wy), (x + 66, y + wy - 3), (x + 86, y + wy),
                (x + 106, y + wy - 3), (x + 126, y + wy), (x + 146, y + wy - 3)],
               fill=(52, 96, 140), width=2)


def mini_gaza(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (226, 220, 208))
    d.polygon([(x + 66, y + 40), (x + 66, y + 14), (x + 96, y + 14),
               (x + 96, y + 40)], fill=(120, 116, 106))
    d.polygon([(x + 100, y + 40), (x + 100, y + 24), (x + 128, y + 24),
               (x + 128, y + 40)], fill=(96, 92, 84))
    d.line([(x + 96, y + 14), (x + 108, y + 26), (x + 96, y + 30)],
           fill=(60, 56, 50), width=2)
    for wx, wy in [(72, 20), (84, 28), (106, 30), (116, 34)]:
        d.rectangle([x + wx, y + wy, x + wx + 6, y + wy + 5], fill=(60, 56, 50))
    d.ellipse([x + 122, y + 6, x + 132, y + 14], fill=(180, 180, 175))
    d.ellipse([x + 128, y + 12, x + 138, y + 20], fill=(170, 170, 165))


def mini_sudan(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (232, 222, 196))
    d.rectangle([x + 66, y + 22, x + 112, y + 40], fill=(150, 110, 76))
    d.polygon([(x + 62, y + 22), (x + 89, y + 10), (x + 116, y + 22)],
              fill=(120, 72, 44))
    d.rectangle([x + 84, y + 30, x + 94, y + 40], fill=(70, 56, 40))
    d.polygon([(x + 118, y + 12), (x + 126, y + 12), (x + 126, y + 18),
               (x + 118, y + 18)], fill=(40, 40, 44))
    d.ellipse([x + 116, y + 8, x + 118, y + 10], fill=(255, 80, 80))
    d.ellipse([x + 126, y + 8, x + 128, y + 10], fill=(255, 80, 80))
    d.line([(x + 122, y + 18), (x + 122, y + 24)], fill=(40, 40, 44), width=2)


def mini_ship(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (204, 214, 222))
    d.polygon([(x + 52, y + 24), (x + 136, y + 24), (x + 126, y + 36),
               (x + 62, y + 36)], fill=(90, 96, 104))
    d.rectangle([x + 88, y + 12, x + 104, y + 24], fill=(70, 76, 84))
    d.rectangle([x + 94, y + 4, x + 98, y + 12], fill=(70, 76, 84))
    d.line([(x + 46, y + 38), (x + 66, y + 35), (x + 86, y + 38),
            (x + 106, y + 35), (x + 126, y + 38), (x + 146, y + 35)],
           fill=(52, 96, 140), width=2)
    d.line([(x + 46, y + 42), (x + 66, y + 39), (x + 86, y + 42),
            (x + 106, y + 39), (x + 126, y + 42), (x + 146, y + 39)],
           fill=(52, 96, 140), width=2)


def mini_tanker(d, x, y, w, h):
    _mini_bg(d, x, y, w, h, (52, 58, 74))
    d.polygon([(x + 52, y + 26), (x + 136, y + 26), (x + 128, y + 38),
               (x + 60, y + 38)], fill=(30, 30, 34))
    d.rectangle([x + 110, y + 16, x + 122, y + 26], fill=(60, 62, 70))
    _burst(d, x + 80, y + 18, 12, 5, (255, 170, 40))
    _burst(d, x + 80, y + 18, 6, 3, (255, 230, 130))
    d.line([(x + 46, y + 40), (x + 66, y + 37), (x + 86, y + 40),
            (x + 106, y + 37), (x + 126, y + 40), (x + 146, y + 37)],
           fill=(120, 150, 170), width=2)


# ------------------------------------------------------------------- content
MAIN_STORIES = [
    {
        "num": 1, "kicker": "KYIV  •  THE WAR", "tag": ("REPORTED", BLUE),
        "headline": "186 DRONES IN ONE NIGHT",
        "body": ("Russia fired 186 drones at Ukraine overnight; air defences "
                 "shot down 161. Strikes hit 18 sites. A block of flats in "
                 "Dymer, in the Kyiv region, partly collapsed — 14 people "
                 "may be trapped inside."),
        "illo": illo_ukraine,
    },
    {
        "num": 2, "kicker": "ANTALYA  •  CLIMATE", "tag": ("CONFIRMED", (46, 120, 80)),
        "headline": "COP31 ENDS WITH NO FOSSIL-FUEL WORD",
        "body": ("The final text landed at dawn in Antalya with no mention "
                 "of fossil fuels. The EU rejected it and approval was "
                 "delayed. The 35% electricity target for 2035 survived; "
                 "the $120bn adaptation target was dropped."),
        "illo": illo_cop31,
    },
    {
        "num": 3, "kicker": "MANAMA  •  THE GULF", "tag": ("CLAIM", RED),
        "headline": "IRAN CLAIMS TWO US RADARS DESTROYED",
        "body": ("Tehran says it destroyed two US Patriot radars at "
                 "Al-Riffa and Awali Sakir. Bahrain says its defences "
                 "intercepted the attack; a civilian industrial site "
                 "caught fire and no one was hurt."),
        "illo": illo_bahrain,
    },
]

GRID_STORIES = [
    ("HONG KONG", "856 CANDIDATES, 723 SEATS",
     "Turnout hit 93.55% by 2pm in the Election Committee vote.", mini_ballot),
    ("LAS VEGAS", "VERSTAPPEN WINS BY 0.639s",
     "Beats Norris in the Las Vegas GP — his 75th win.", mini_car),
    ("CRICKET", "INDIA DECLARE ON 720/9",
     "A record Test total in New Zealand.", mini_cricket),
    ("NBA", "WEMBANYAMA SCORES 50",
     "19 rebounds as the Spurs beat the Pelicans 114–91.", mini_basket),
    ("INDONESIA", "CANDY FACTORY FIRE KILLS 3",
     "36 missing after the blaze in Cikande, Serang.", mini_factory),
    ("NIGERIA", "BOAT CAPSIZES, 24 DEAD",
     "A funeral-party boat sank in Bayelsa; 24 were rescued.", mini_boat),
    ("GAZA", "FOUR KILLED IN GAZA STRIKE",
     "Hamas calls urgent talks after a drone hit a food vehicle.", mini_gaza),
    ("SUDAN", "DRONE HITS HOME NEAR KHARTOUM",
     "Four killed; a UN building was damaged.", mini_sudan),
    ("LIBYA", "DRONE HITS RUSSIAN CORVETTE",
     "The Merkury was struck at its Benghazi base; Ukraine is suspected.",
     mini_ship),
    ("HORMUZ", "TWO TANKERS HIT BY MINES",
     "Supertankers caught fire near the Strait of Hormuz.", mini_tanker),
]

STATS = [
    ("186", "DRONES FIRED AT UKRAINE"),
    ("161", "SHOT DOWN BY DEFENCES"),
    ("14", "MAY BE TRAPPED IN DYMER"),
    ("93.55%", "HONG KONG TURNOUT"),
    ("720/9", "INDIA'S TEST TOTAL IN NZ"),
    ("50", "WEMBANYAMA POINTS"),
]

REGIONS = [
    ("EUROPE", 12, (31, 58, 95)),
    ("MIDDLE EAST", 6, (166, 25, 46)),
    ("ASIA-PACIFIC", 6, (46, 120, 80)),
    ("AFRICA", 4, (176, 110, 30)),
    ("AMERICAS", 2, (96, 70, 140)),
    ("SPORT", 3, (40, 60, 80)),
    ("MARKETS", 2, (140, 110, 20)),
]

TIMELINE = [
    ("OVERNIGHT", "186 drones fired at Ukraine"),
    ("DAWN", "COP31 final text lands in Antalya"),
    ("TODAY", "Bahrain: claim and denial"),
    ("09:45 UTC", "PRESS TIME"),
]

ALSO = [
    "MARKETS: S&P 500 −3.7%, Nasdaq −5.3% as the AI sell-off spreads to Japan and Korea.",
    "EU and Indonesia sign a trade deal after ~10 years; tariffs end on up to 98.5% of goods.",
    "EUROPE: third day of protests over the cost of living and housing.",
    "WEST BANK: settlers burn vehicles and homes.",
    "VATICAN: Pope Leo XIV hosts 1,300 poor guests for the World Day of the Poor.",
    "Zelenskyy asks the US to release Patriot missiles.",
    "Russia claims it downed 170 Ukrainian drones.",
    "Russian cargo ship Sparta II catches fire in the Gulf of Finland.",
    "Denmark expels a Russian diplomat.",
    "Nepal's PM Balendra Shah makes his first visit to India.",
    "Taiwan watches Chinese ships near its waters.",
    "Okinawa's Shuri Castle is restored, 7 years after the fire.",
    "Paolo Bulgari dies at 89.",
    "Phumzile Mlambo-Ngcuka dies at 71.",
    "Thailand court upholds a defamation verdict.",
    "Russian ship in Poland — NATO calls it a violation.",
    "Lewis Pugh swims in the Strait of Hormuz.",
    "Iran begins power rationing; rolling blackouts of up to 2 hours a day.",
    "Brazil's Bolsonaro in intensive care with a bowel obstruction; stable.",
    "COP31 admits a 1.5°C overshoot.",
    "Bahrain: no casualties; a civilian site burned.",
    "Kyiv: strikes hit 18 sites.",
]

DATE_CHECK = ("DATE CHECK — NOT 22 NOVEMBER. Deliberately left out — these "
              "happened on other days: Russia's 400-drone attack (19–20 Nov) • "
              "Trump–Xi–Putin summit, Shenzhen (19 Nov) • Peru earthquake "
              "(20 Nov) • ICJ Rohingya verdict (19 Nov) • 'El Chapo Isidro' "
              "arrest (Fri 21 Nov) • BepiColombo Mercury burn (Sat 21 Nov) • "
              "NWSL final (Sat 21 Nov).")


def _num_chip(d, x, y, n, fill, fg=(255, 255, 255), r=9):
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=(255, 255, 255),
              width=1)
    font = F(SANS_B, 10)
    t = str(n)
    d.text((x - twidth(d, t, font) / 2, y - 7), t, font=font, fill=fg)


def build_front_page(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top rules + kicker
    hrule(d, M, 12, CW, INKC := INK, 2)
    hrule(d, M, 16, CW, RULEC, 1)
    kf = F(SANS_B, 10)
    tracked(d, (M, 21), "SUNDAY 22 NOVEMBER 2026", kf, INK, 1)
    rt = "PRESS TIME 09:45 UTC"
    tracked(d, (W - M - twidth(d, rt, kf) - 10 * len(rt) // 10, 21),
            rt, kf, RED, 1)

    # ---- masthead
    mf = F(SERIF_B, 54)
    centre(d, W // 2, 34, "THE SUNDAY GLOBE", mf, INK)
    sf = F(SERIF_I, 16)
    centre(d, W // 2, 90,
           "186 drones over Ukraine  •  COP31 ends with no fossil-fuel word  •  "
           "Iran claims US radars hit in Bahrain", sf, RED)
    hrule(d, M, 110, CW, INK, 2)

    # ---- stats strip
    sy = 116
    bw = (CW - 5 * 6) // 6
    for i, (num, label) in enumerate(STATS):
        x = M + i * (bw + 6)
        d.rectangle([x, sy, x + bw, sy + 36], outline=RULEC, width=1)
        d.rectangle([x, sy, x + bw, sy + 3], fill=BLUE)
        nf = F(SERIF_B, 22)
        centre(d, x + bw // 2, sy + 5, num, nf, INK)
        lf = F(SANS_B, 8)
        centre(d, x + bw // 2, sy + 27, label, lf, SOFT)

    # ---- region bar
    ry = 158
    cw2 = (CW - 6 * 6) // 7
    for i, (name, count, col) in enumerate(REGIONS):
        x = M + i * (cw2 + 6)
        d.rounded_rectangle([x, ry, x + cw2, ry + 20], radius=3, fill=col)
        rf = F(SANS_B, 10)
        centre(d, x + cw2 // 2, ry + 4, f"{name} · {count}", rf, (255, 255, 255))

    # ---- timeline strip (one line, no fake clock times except press time)
    ty = 184
    tf = F(SANS, 10)
    for i, (when, what) in enumerate(TIMELINE):
        cx = M + (i + 0.5) * CW / 4
        centre(d, cx, ty, f"{when} — {what}", tf, SOFT)
    y = 202

    # ---- three main stories
    col_w, gap = 318, 13
    for i, s in enumerate(MAIN_STORIES):
        x = M + i * (col_w + gap)
        s["illo"](d, x, y, col_w, 124)
        _num_chip(d, x + 14, y + 14, s["num"], RED)
        ky = y + 128
        kf2 = F(SANS_B, 9)
        tracked(d, (x, ky), s["kicker"], kf2, RED, 1)
        label, bg = s["tag"]
        tw = tag_chip(d, x + col_w - 76, ky - 2, label, bg)
        hy = ky + 16
        hf = F(SERIF_B, 18)
        for li, line in enumerate(wrap(d, s["headline"], hf, col_w)):
            d.text((x, hy + li * 21), line, font=hf, fill=INK)
        by = hy + 2 * 21 + 4
        bf = F(SERIF_R, 11)
        for li, line in enumerate(wrap(d, s["body"], bf, col_w)):
            d.text((x, by + li * 13.5), line, font=bf, fill=(40, 38, 34))
        hrule(d, x, y + 244, col_w, RULEC, 1)
    y = y + 246

    # ---- grid of 10 small stories, 5 x 2 (headline 1 line, text max 2)
    gw = (CW - 4 * 8) // 5
    gh = 92
    for idx, (kick, head, text, illo) in enumerate(GRID_STORIES):
        row, col = divmod(idx, 5)
        x = M + col * (gw + 8)
        gy = y + row * (gh + 8)
        illo(d, x, gy, gw, 42)
        _num_chip(d, x + 11, gy + 10, idx + 4, BLUE, r=8)
        kf3 = F(SANS_B, 8)
        tracked(d, (x, gy + 46), kick, kf3, RED, 1)
        hf2 = F(SANS_B, 9)
        head_lines = wrap(d, head, hf2, gw)[:1]
        for li, line in enumerate(head_lines):
            d.text((x, gy + 57 + li * 12), line, font=hf2, fill=INK)
        bf2 = F(SERIF_R, 9)
        text_y = gy + 57 + len(head_lines) * 12 + 1
        for li, line in enumerate(wrap(d, text, bf2, gw)[:2]):
            d.text((x, text_y + li * 11), line, font=bf2, fill=(50, 48, 44))
    y = y + 2 * gh + 8

    # ---- dotted world map strip (numbered pins only; legend below)
    my = y + 4
    mf2 = F(SANS_B, 10)
    tracked(d, (M, my), "WHERE THE NEWS HAPPENED", mf2, INK, 1)
    rf2 = F(SANS, 9)
    rtxt = "NUMBERS MATCH THE STORIES ABOVE"
    d.text((W - M - twidth(d, rtxt, rf2), my + 1), rtxt, font=rf2, fill=SOFT)
    map_y, map_h = my + 16, 95
    draw_map(img, d, M, map_y, CW, map_h)
    lf3 = F(SANS, 9)
    legend = ("1 KYIV  •  2 ANTALYA  •  3 BAHRAIN  •  4 HONG KONG  •  "
              "5 LAS VEGAS  •  6 NEW ZEALAND  •  7 SAN ANTONIO  •  8 CIKANDE  •  "
              "9 BAYELSA  •  10 GAZA  •  11 KHARTOUM  •  12 BENGHAZI  •  13 HORMUZ")
    centre(d, W // 2, map_y + map_h + 4, legend, lf3, SOFT)
    y = map_y + map_h + 18

    # ---- ALSO list
    af = F(SANS_B, 11)
    tracked(d, (M, y), "ALSO ON SUNDAY 22 NOVEMBER", af, INK, 1)
    hrule(d, M, y + 16, CW, INK, 1)
    ay = y + 22
    bf3 = F(SERIF_R, 10)
    half = (len(ALSO) + 1) // 2
    for i, item in enumerate(ALSO):
        col = 0 if i < half else 1
        row = i if i < half else i - half
        x = M + col * (CW // 2 + 10)
        d.text((x, ay + row * 11.5), "•  " + item, font=bf3, fill=(40, 38, 34))
    y = ay + half * 11.5 + 6

    # ---- DATE CHECK red box
    d.rectangle([M, y, W - M, y + 40], outline=RED, width=2)
    d.rectangle([M, y, M + 118, y + 40], fill=RED)
    df = F(SANS_B, 10)
    d.text((M + 8, y + 4), "DATE", font=df, fill=(255, 255, 255))
    d.text((M + 8, y + 18), "CHECK", font=df, fill=(255, 255, 255))
    dbf = F(SERIF_R, 10)
    for li, line in enumerate(wrap(d, DATE_CHECK, dbf, CW - 140)):
        d.text((M + 128, y + 4 + li * 12), line, font=dbf, fill=(90, 20, 30))
    y = y + 40 + 8

    # ---- footer: sources + legend
    ff = F(SANS, 9)
    centre(d, W // 2, y, "Sources: Reuters  •  BBC  •  AP  •  AFP  •  Al Jazeera  •  Detiknews",
           ff, SOFT)
    centre(d, W // 2, y + 13,
           "REPORTED — as reported   •   CLAIM — one side's claim   •   "
           "CONFIRMED — verified   •   PENDING — awaiting confirmation",
           ff, SOFT)

    img.save(path, format="PNG", optimize=True)
    return path
