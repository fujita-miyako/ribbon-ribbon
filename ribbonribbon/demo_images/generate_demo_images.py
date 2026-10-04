"""デモ用の架空グッズ画像を生成するスクリプト。

使い方（ribbonribbon/ ディレクトリで）:
    python demo_images/generate_demo_images.py

配色は static/menu/css/base.css のパステルピンク系に合わせている。
人物は描かず、星・ハート・リボン・幾何学模様のみで構成する。
"""
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

OUT_DIR = Path(__file__).resolve().parent
FONT_PATH = OUT_DIR.parent / "static/menu/fonts/cinecaption.2.26/cinecaption2.26/cinecaption226.ttf"

W = 800   # 出力サイズ（正方形）
S = 2     # アンチエイリアス用のスーパーサンプリング倍率

# --- base.css 由来の配色 ---
BG = "#fff0f5"
PINK_L = "#f8d8e6"
PINK_M = "#e6b8c5"
ACCENT = "#d9534f"
TEXT = "#333333"
WHITE = "#ffffff"
# --- 上記に馴染む補助色 ---
ROSE = "#d98aa3"
ROSE_D = "#b96f88"   # 線画・影
SHADOW = "#f1d3df"
LAVENDER = "#ddd0f2"
MINT = "#cfeee2"
BUTTER = "#fff0c4"
SKY = "#d4e7f7"
SILVER = "#cfd0da"


def font(size):
    try:
        return ImageFont.truetype(str(FONT_PATH), size * S)
    except OSError:
        return ImageFont.load_default(size * S)


class Layer:
    """800px 座標系で描いて、内部では S 倍で描画する透明レイヤー。"""

    def __init__(self):
        self.img = Image.new("RGBA", (W * S, W * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    @staticmethod
    def _p(pts):
        return [(x * S, y * S) for x, y in pts]

    def rect(self, x0, y0, x1, y1, fill, r=0, outline=None, width=0):
        self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S,
                                 fill=fill, outline=outline, width=width * S)

    def ellipse(self, cx, cy, rx, ry, fill, outline=None, width=0):
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S],
                       fill=fill, outline=outline, width=width * S)

    def circle(self, cx, cy, r, fill, outline=None, width=0):
        self.ellipse(cx, cy, r, r, fill, outline, width)

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon(self._p(pts), fill=fill, outline=outline, width=width * S)

    def line(self, pts, fill, width):
        self.d.line(self._p(pts), fill=fill, width=width * S, joint="curve")

    def arc(self, cx, cy, r, start, end, fill, width):
        self.d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
                   start, end, fill=fill, width=width * S)

    def text(self, x, y, s, size, fill, anchor="mm"):
        self.d.text((x * S, y * S), s, font=font(size), fill=fill, anchor=anchor)

    def star(self, cx, cy, r, fill, outline=None, width=0, points=5, inner=0.45, rot=-90):
        self.poly(star_pts(cx, cy, r, points, inner, rot), fill, outline, width)

    def heart(self, cx, cy, size, fill, outline=None, width=0):
        self.poly(heart_pts(cx, cy, size), fill, outline, width)

    def sparkle(self, cx, cy, r, fill):
        self.star(cx, cy, r, fill, points=4, inner=0.28, rot=0)

    def ribbon(self, cx, cy, w, fill, shade, knot=None, outline=None, width=0):
        """リボン（蝶結び）。w は横幅。"""
        knot = knot or shade
        h = w * 0.55
        # 垂れ
        for sgn in (-1, 1):
            tail = [(cx + sgn * w * 0.04, cy), (cx + sgn * w * 0.30, cy + h * 0.95),
                    (cx + sgn * w * 0.20, cy + h * 0.82), (cx + sgn * w * 0.13, cy + h * 1.02),
                    (cx - sgn * w * 0.06, cy + h * 0.10)]
            self.poly(tail, shade, outline, width)
        # ループ（レムニスケート曲線）
        a = w * 0.5
        for sgn in (-1, 1):
            pts = []
            for i in range(61):
                t = (-math.pi / 2 + math.pi * i / 60) if sgn > 0 else (math.pi / 2 + math.pi * i / 60)
                den = 1 + math.sin(t) ** 2
                pts.append((cx + a * math.cos(t) / den, cy + 1.5 * a * math.sin(t) * math.cos(t) / den))
            self.poly(pts, fill, outline, width)
            # ループ内側の折り目
            self.poly([(cx + sgn * w * 0.06, cy - h * 0.05), (cx + sgn * w * 0.26, cy - h * 0.10),
                       (cx + sgn * w * 0.06, cy + h * 0.08)], shade)
        self.rect(cx - w * 0.08, cy - h * 0.24, cx + w * 0.08, cy + h * 0.24, knot,
                  r=w * 0.05, outline=outline, width=width)

    def rotated(self, angle, cx=W / 2, cy=W / 2):
        self.img = self.img.rotate(angle, resample=Image.BICUBIC, center=(cx * S, cy * S))
        self.d = ImageDraw.Draw(self.img)
        return self


def star_pts(cx, cy, r, points=5, inner=0.45, rot=-90):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        ang = math.radians(rot + 180 / points * i)
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return pts


def heart_pts(cx, cy, size):
    k = size / 34
    pts = []
    for i in range(120):
        t = 2 * math.pi * i / 120
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * k, cy - y * k - size * 0.05))
    return pts


def clip_onto(dst, src, mask):
    """src レイヤーを mask の範囲だけ dst に重ねる。"""
    clipped = src.img.copy()
    clipped.putalpha(ImageChops.multiply(src.img.getchannel("A"), mask))
    dst.img.alpha_composite(clipped)


def blurred(layer, color, radius):
    """layer の形をアルファだけぼかした単色レイヤーにする（黒いにじみ防止）。"""
    alpha = layer.img.getchannel("A").filter(ImageFilter.GaussianBlur(radius * S))
    out = Layer()
    out.img = Image.new("RGBA", alpha.size, color)
    out.img.putalpha(alpha)
    return out


def compose(layers, shadow=(400, 690, 250, 34), sparkles=()):
    base = Image.new("RGBA", (W * S, W * S), BG)
    deco = Layer()
    for x, y, r, c in sparkles:
        deco.sparkle(x, y, r, c)
    base.alpha_composite(deco.img)
    if shadow:
        sh = Layer()
        sh.ellipse(*shadow, fill=WHITE)
        base.alpha_composite(blurred(sh, SHADOW, 10).img)
    for layer in layers:
        base.alpha_composite(layer.img)
    return base.resize((W, W), Image.LANCZOS).convert("RGB")


DEFAULT_SPARKLES = [(110, 120, 22, PINK_M), (150, 175, 10, PINK_L), (690, 130, 16, PINK_L),
                    (700, 560, 20, PINK_M), (95, 600, 12, PINK_L)]


# ------------------------------------------------------------------ 各グッズ

def penlight():
    L = Layer()
    cx = 400
    # 光の輪
    glow = Layer()
    glow.ellipse(cx, 300, 120, 230, fill=(0, 0, 0, 170))
    glow = blurred(glow, PINK_M, 40)
    # 発光部
    L.rect(cx - 55, 130, cx + 55, 470, PINK_L, r=55, outline=ROSE_D, width=4)
    L.rect(cx - 30, 160, cx - 12, 430, (255, 255, 255, 170), r=9)
    for y in (230, 330):
        L.heart(cx + 8, y, 42, WHITE)
    # 星トッパー
    L.star(cx, 120, 70, BUTTER, outline=ROSE_D, width=4)
    L.star(cx, 124, 30, WHITE)
    # カラー
    L.rect(cx - 66, 462, cx + 66, 500, WHITE, r=12, outline=ROSE_D, width=4)
    # グリップ
    L.rect(cx - 52, 495, cx + 52, 700, PINK_M, r=26, outline=ROSE_D, width=4)
    for y in range(560, 690, 26):
        L.line([(cx - 38, y), (cx + 38, y)], ROSE, 6)
    L.circle(cx, 528, 15, ACCENT, outline=ROSE_D, width=3)
    L.ribbon(cx, 488, 120, ROSE, ROSE_D, outline=None)
    glow.rotated(-18, 400, 420)
    L.rotated(-18, 400, 420)
    return compose([glow, L], shadow=(470, 715, 150, 22), sparkles=DEFAULT_SPARKLES)


def acrylic_keychain():
    L = Layer()
    cx = 410
    # 金具
    L.circle(cx - 10, 115, 52, None, outline=SILVER, width=11)
    for i, y in enumerate(range(175, 235, 22)):
        L.ellipse(cx - 5, y, 9 if i % 2 else 7, 13, None, outline=SILVER, width=6)
    L.rect(cx - 14, 230, cx + 14, 262, SILVER, r=6)
    # アクリル本体（白フチ＋ハート）
    L.heart(cx, 470, 470, (255, 255, 255, 235), outline=PINK_M, width=4)
    L.circle(cx, 262, 14, BG, outline=PINK_M, width=4)
    L.heart(cx, 470, 400, PINK_L)
    # 中のデザイン
    stripe = Layer()
    for i in range(-2, 10):
        y = 300 + i * 40
        stripe.line([(cx - 220, y), (cx + 220, y + 60)], (255, 255, 255, 110), 10)
    mask = Layer()
    mask.heart(cx, 470, 400, WHITE)
    clip_onto(L, stripe, mask.img.getchannel("A"))
    L.heart(cx, 470, 400, None, outline=ROSE, width=5)
    L.star(cx, 460, 105, ROSE, outline=ROSE_D, width=4)
    L.star(cx, 460, 45, BUTTER)
    for x, y, r in [(cx - 120, 390, 18), (cx + 125, 395, 14), (cx - 60, 590, 12), (cx + 80, 575, 16)]:
        L.sparkle(x, y, r, WHITE)
    # 光沢
    L.arc(cx - 70, 400, 120, 200, 250, (255, 255, 255, 220), 12)
    L.rotated(6, cx, 120)
    return compose([L], shadow=(410, 715, 200, 26), sparkles=DEFAULT_SPARKLES)


def trading_card():
    layers = []
    for ang, col in [(16, MINT), (-10, LAVENDER)]:
        back = Layer()
        back.rect(255, 140, 545, 640, WHITE, r=20, outline=PINK_M, width=4)
        back.rect(275, 160, 525, 620, col, r=12)
        back.star(400, 390, 60, WHITE)
        layers.append(back.rotated(ang, 400, 420))
    L = Layer()
    L.rect(240, 110, 560, 660, WHITE, r=22, outline=ROSE_D, width=4)
    L.rect(262, 132, 538, 560, PINK_L, r=12)
    # 斜めストライプ
    stripe = Layer()
    for i in range(-10, 14):
        x = 262 + i * 34
        stripe.poly([(x, 132), (x + 16, 132), (x + 16 - 300, 560), (x - 300, 560)], (255, 255, 255, 120))
    mask = Image.new("L", stripe.img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([262 * S, 132 * S, 538 * S, 560 * S], radius=12 * S, fill=255)
    clip_onto(L, stripe, mask)
    L.circle(400, 340, 120, WHITE)
    L.star(400, 340, 105, ROSE, outline=ROSE_D, width=4)
    L.heart(400, 350, 70, WHITE)
    for x, y, r in [(300, 180, 20), (505, 200, 14), (295, 500, 14), (500, 480, 22)]:
        L.sparkle(x, y, r, WHITE)
    # ネームプレート
    L.rect(272, 578, 528, 640, PINK_M, r=10)
    L.text(400, 609, "HIYORI  No.07", 26, WHITE)
    L.circle(520, 135, 22, ACCENT)
    L.text(520, 136, "SP", 18, WHITE)
    layers.append(L.rotated(-4, 400, 400))
    return compose(layers, shadow=(400, 700, 210, 26), sparkles=DEFAULT_SPARKLES)


def _badge(L, cx, cy, r, base, pattern):
    L.circle(cx, cy, r, ROSE_D)
    L.circle(cx, cy, r - 7, base)
    pat = Layer()
    pattern(pat, cx, cy, r)
    mask = Image.new("L", pat.img.size, 0)
    ImageDraw.Draw(mask).ellipse([(cx - r + 7) * S, (cy - r + 7) * S, (cx + r - 7) * S, (cy + r - 7) * S], fill=255)
    clip_onto(L, pat, mask)
    L.circle(cx, cy, r - 7, None, outline=(255, 255, 255, 140), width=10)
    L.arc(cx, cy, r - 26, 200, 255, (255, 255, 255, 230), 12)


def can_badge():
    def dots(p, cx, cy, r):
        for y in range(int(cy - r), int(cy + r), 44):
            for x in range(int(cx - r), int(cx + r), 44):
                off = 22 if ((y - int(cy - r)) // 44) % 2 else 0
                p.circle(x + off, y, 9, (255, 255, 255, 200))
        p.ribbon(cx, cy - 10, r * 1.15, ROSE, ROSE_D)

    def checker(p, cx, cy, r):
        n = 40
        for i in range(-6, 7):
            for j in range(-6, 7):
                if (i + j) % 2 == 0:
                    p.rect(cx + i * n, cy + j * n, cx + (i + 1) * n, cy + (j + 1) * n, (255, 255, 255, 170))
        p.heart(cx, cy + 6, r * 1.0, ACCENT, outline=WHITE, width=6)

    def rays(p, cx, cy, r):
        for i in range(16):
            a0 = math.radians(i * 22.5)
            a1 = math.radians(i * 22.5 + 11)
            if i % 2 == 0:
                p.poly([(cx, cy), (cx + 2 * r * math.cos(a0), cy + 2 * r * math.sin(a0)),
                        (cx + 2 * r * math.cos(a1), cy + 2 * r * math.sin(a1))], (255, 255, 255, 150))
        p.star(cx, cy, r * 0.62, BUTTER, outline=ROSE_D, width=4)

    L = Layer()
    _badge(L, 255, 300, 150, LAVENDER, rays)
    _badge(L, 545, 330, 165, MINT, checker)
    _badge(L, 395, 500, 190, PINK_L, dots)
    return compose([L], shadow=(400, 710, 260, 28), sparkles=DEFAULT_SPARKLES)


def cd():
    L = Layer()
    # ディスク
    dx, dy = 520, 400
    L.circle(dx, dy, 215, (238, 238, 245, 255), outline=SILVER, width=4)
    for r, c in [(200, SKY), (170, LAVENDER), (140, PINK_L), (110, MINT)]:
        L.circle(dx, dy, r, c)
    L.arc(dx, dy, 180, 300, 350, (255, 255, 255, 220), 14)
    L.circle(dx, dy, 60, (245, 245, 250, 255), outline=SILVER, width=4)
    L.circle(dx, dy, 22, BG, outline=SILVER, width=3)
    # ケース
    L.rect(120, 175, 470, 625, (250, 250, 253, 255), r=12, outline=SILVER, width=5)
    L.rect(120, 175, 150, 625, (230, 231, 240, 255), r=6)
    L.rect(165, 195, 455, 605, PINK_M, r=6)
    # ジャケット：同心円と星
    for i, c in enumerate([PINK_L, PINK_M, ROSE, PINK_L, WHITE]):
        L.circle(310, 360, 130 - i * 24, c)
    L.star(310, 360, 50, BUTTER, outline=ROSE_D, width=3)
    for x, y, r in [(195, 230, 16), (425, 250, 22), (420, 480, 12), (205, 470, 10)]:
        L.sparkle(x, y, r, WHITE)
    L.text(310, 540, "Sugar Galaxy", 34, WHITE)
    L.text(310, 578, "STELLAR CANDY", 18, ROSE_D)
    L.poly([(400, 178), (468, 178), (468, 246)], (255, 255, 255, 140))
    return compose([L], shadow=(380, 690, 290, 26), sparkles=DEFAULT_SPARKLES)


def acrylic_stand():
    L = Layer()
    cx = 400
    # 台座
    L.ellipse(cx, 640, 190, 48, (255, 255, 255, 235), outline=PINK_M, width=4)
    L.ellipse(cx, 625, 190, 48, (250, 236, 243, 255), outline=PINK_M, width=4)
    L.rect(cx - 70, 612, cx + 70, 630, ROSE_D, r=6)
    # パネル（白フチ）
    edge = Layer()
    edge.star(cx, 300, 240, (255, 255, 255, 240), outline=PINK_M, width=4, inner=0.52)
    edge.rect(cx - 70, 470, cx + 70, 625, (255, 255, 255, 240), r=12, outline=PINK_M, width=4)
    L.img.alpha_composite(edge.img)
    L.star(cx, 300, 212, PINK_L, inner=0.52)
    L.star(cx, 300, 212, None, outline=ROSE, width=5, inner=0.52)
    L.circle(cx, 315, 92, WHITE)
    L.ribbon(cx, 300, 190, ROSE, ROSE_D)
    for x, y, r in [(cx - 80, 200, 14), (cx + 90, 230, 18), (cx + 120, 380, 12), (cx - 125, 375, 16)]:
        L.sparkle(x, y, r, WHITE)
    L.rect(cx - 60, 480, cx + 60, 540, PINK_M, r=10)
    L.text(cx, 511, "MARIN", 28, WHITE)
    L.line([(cx - 120, 160), (cx - 60, 110)], (255, 255, 255, 220), 10)
    return compose([L], shadow=(400, 680, 230, 24), sparkles=DEFAULT_SPARKLES)


def uchiwa():
    L = Layer()
    cx, cy = 400, 330
    # 持ち手
    L.rect(cx - 26, cy + 200, cx + 26, 730, PINK_M, r=20, outline=ROSE_D, width=4)
    L.rect(cx - 10, cy + 230, cx + 10, 710, ROSE, r=8)
    # 面
    L.ellipse(cx, cy, 255, 240, WHITE, outline=ROSE_D, width=5)
    L.ellipse(cx, cy, 235, 220, PINK_L)
    for i in range(12):
        a = math.radians(i * 30)
        L.line([(cx, cy + 120), (cx + 230 * math.cos(a), cy + 220 * math.sin(a))], (255, 255, 255, 120), 4)
    L.text(cx, cy - 165, "ウインクして", 38, ROSE_D)
    L.heart(cx, cy + 35, 330, ROSE, outline=WHITE, width=10)
    L.text(cx, cy + 15, "ゆめ", 96, WHITE)
    for x, y in [(cx - 180, cy - 120), (cx + 180, cy - 120), (cx - 190, cy + 110), (cx + 190, cy + 110)]:
        L.star(x, y, 26, BUTTER, outline=ROSE_D, width=3)
    L.rotated(8, 400, 500)
    return compose([L], shadow=(410, 735, 160, 20), sparkles=DEFAULT_SPARKLES)


def sticker_sheet():
    L = Layer()
    L.rect(150, 110, 650, 690, WHITE, r=18, outline=PINK_M, width=4)
    L.rect(150, 110, 650, 170, PINK_L, r=18)
    L.rect(150, 150, 650, 170, PINK_L)
    L.text(400, 141, "STELLAR CANDY  sticker set", 26, ROSE_D)

    # 星
    L.star(275, 290, 98, WHITE, outline=(220, 220, 228, 255), width=3)
    L.star(275, 290, 80, BUTTER, outline=ROSE_D, width=3)
    # ハート
    L.heart(520, 290, 210, WHITE, outline=(220, 220, 228, 255), width=3)
    L.heart(520, 290, 175, ACCENT)
    L.arc(490, 260, 45, 190, 250, (255, 255, 255, 220), 9)
    # リボン
    L.ellipse(285, 500, 125, 85, WHITE, outline=(220, 220, 228, 255), width=3)
    L.ribbon(285, 490, 200, ROSE, ROSE_D)
    # 丸（ドット）
    L.circle(520, 500, 95, WHITE, outline=(220, 220, 228, 255), width=3)
    L.circle(520, 500, 78, SKY)
    for x, y in [(495, 470), (545, 475), (520, 520), (480, 530), (560, 530)]:
        L.circle(x, y, 11, WHITE)
    # 小さいの
    for x, y, c in [(215, 628, LAVENDER), (335, 628, MINT), (455, 628, PINK_M)]:
        L.circle(x, y, 32, WHITE, outline=(220, 220, 228, 255), width=3)
        L.heart(x, y + 2, 38, c) if c != MINT else L.star(x, y, 24, c)
    # めくれ
    L.poly([(650, 610), (650, 690), (570, 690)], BG)
    L.poly([(650, 610), (570, 690), (585, 615)], PINK_L, outline=PINK_M, width=3)
    L.rotated(-5)
    return compose([L], shadow=(400, 715, 270, 24), sparkles=DEFAULT_SPARKLES)


def muffler_towel():
    L = Layer()
    y0, y1 = 270, 520
    # フリンジ
    for x0, x1 in [(70, 110), (690, 730)]:
        for y in range(y0 + 8, y1, 16):
            L.line([(x0, y), (x1, y)], PINK_M, 6)
    L.rect(100, y0, 700, y1, PINK_L, r=8, outline=ROSE_D, width=4)
    L.rect(100, y0 + 22, 700, y0 + 46, ROSE)
    L.rect(100, y1 - 46, 700, y1 - 22, ROSE)
    for x in range(140, 690, 44):
        L.heart(x, y0 + 34, 20, WHITE)
        L.heart(x, y1 - 34, 20, WHITE)
    L.text(400, 380, "Lumiere Ribbon", 52, ROSE_D)
    L.text(400, 432, "LIVE TOUR  - sweet starlight -", 22, ROSE)
    L.ribbon(150, 385, 70, ACCENT, ROSE_D)
    L.ribbon(650, 385, 70, ACCENT, ROSE_D)
    L.rotated(-6)
    return compose([L], shadow=(400, 640, 300, 26), sparkles=DEFAULT_SPARKLES)


def tote_bag():
    L = Layer()
    for x in (300, 500):
        L.arc(x, 260, 80, 180, 360, PINK_M, 22)
    L.poly([(170, 255), (630, 255), (660, 690), (140, 690)], (250, 244, 236, 255), outline=ROSE_D, width=4)
    L.line([(220, 260), (220, 300)], PINK_M, 22)
    L.line([(380, 260), (380, 300)], PINK_M, 22)
    L.line([(420, 260), (420, 300)], PINK_M, 22)
    L.line([(580, 260), (580, 300)], PINK_M, 22)
    for y in range(340, 680, 50):
        for x in range(190, 630, 50):
            if ((y - 340) // 50 + (x - 190) // 50) % 2 == 0:
                L.circle(x, y, 7, PINK_L)
    L.circle(400, 470, 140, PINK_L)
    L.circle(400, 470, 140, None, outline=ROSE, width=5)
    L.ribbon(400, 445, 230, ROSE, ROSE_D)
    L.text(400, 648, "Honey Moon Parade", 28, ROSE_D)
    return compose([L], shadow=(400, 705, 280, 24), sparkles=DEFAULT_SPARKLES)


GOODS = {
    "penlight": penlight,
    "acrylic_keychain": acrylic_keychain,
    "trading_card": trading_card,
    "can_badge": can_badge,
    "cd": cd,
    "acrylic_stand": acrylic_stand,
    "uchiwa": uchiwa,
    "sticker": sticker_sheet,
    "muffler_towel": muffler_towel,
    "tote_bag": tote_bag,
}


if __name__ == "__main__":
    for i, (name, fn) in enumerate(GOODS.items(), 1):
        path = OUT_DIR / f"{i:02d}_{name}.png"
        fn().save(path, optimize=True)
        print("saved", path.name)
