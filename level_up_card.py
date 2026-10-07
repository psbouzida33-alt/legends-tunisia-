import io
import os
import unicodedata

import aiohttp
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

# Optional: set a custom background URL (same idea as welcome_card.py)
BACKGROUND_URL = ""

CARD_SIZE = (920, 180)
BORDER = 4
RADIUS = 28

RED = (231, 76, 60)
RED_LIGHT = (255, 120, 100)
RED_DARK = (180, 40, 30)
BG = (16, 8, 8)
BG_INNER = (28, 12, 12)
WHITE = (255, 255, 255)
WATERMARK = (70, 25, 25)


def _load_font(size: int, bold: bool = True):
    names = (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/ARIALBD.TTF",
        "C:/Windows/Fonts/calibrib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
    )
    if not bold:
        names = (
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "arial.ttf",
        )
    for path in names:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _rounded_rect(draw, xy, radius, fill, outline=None, width=0):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def _draw_watermark(draw, size):
    font = _load_font(72)
    text = "LEVEL UP"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = size[0] - tw - 40
    y = (size[1] - (bbox[3] - bbox[1])) // 2 - 10
    draw.text((x, y), text, font=font, fill=WATERMARK)


def _draw_glow_circle(base: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int]):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for i in range(10, 0, -1):
        alpha = int(18 * i / 10)
        r = radius + i * 2
        gdraw.ellipse(
            (center[0] - r, center[1] - r, center[0] + r, center[1] + r),
            fill=(*color, alpha),
        )
    base.alpha_composite(glow)


def _circular_avatar(avatar: Image.Image, inner_size: int, ring: int) -> Image.Image:
    outer = inner_size + ring * 2
    canvas = Image.new("RGBA", (outer, outer), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((0, 0, outer - 1, outer - 1), fill=(*RED, 255))
    draw.ellipse((ring, ring, outer - ring - 1, outer - ring - 1), fill=(*RED_LIGHT, 255))

    avatar = avatar.resize((inner_size, inner_size))
    mask = Image.new("L", (inner_size, inner_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner_size, inner_size), fill=255)
    canvas.paste(avatar, (ring, ring), mask)
    return canvas


def _draw_level_badge(base: Image.Image, center: tuple[int, int], level: int):
    radius = 34
    _draw_glow_circle(base, center, radius, RED)

    badge = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*RED_DARK, 255))
    draw.ellipse(
        (x - radius + 3, y - radius + 3, x + radius - 3, y + radius - 3),
        outline=(*RED_LIGHT, 255),
        width=3,
    )
    base.alpha_composite(badge)

    draw = ImageDraw.Draw(base)
    font = _load_font(36)
    text = str(level)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw // 2, y - th // 2 - 2), text, font=font, fill=WHITE)


def _draw_arrow(base: Image.Image, x: int, y: int):
    draw = ImageDraw.Draw(base)
    font = _load_font(42)
    draw.text((x, y), "→", font=font, fill=RED_LIGHT, anchor="mm")


async def _fetch_avatar(member) -> bytes:
    return await member.display_avatar.replace(size=512, format="png").read()


async def _fetch_background(url: str) -> bytes | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return None
            return await resp.read()


def _build_canvas(background_bytes: bytes | None) -> Image.Image:
    if background_bytes:
        bg = Image.open(io.BytesIO(background_bytes)).convert("RGBA")
        bg = bg.resize(CARD_SIZE, Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", CARD_SIZE, (*BG, 180))
        bg = Image.alpha_composite(bg, overlay)
    else:
        bg = Image.new("RGBA", CARD_SIZE, (*BG, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(CARD_SIZE[1]):
            t = y / CARD_SIZE[1]
            r = int(BG_INNER[0] * (1 - t) + BG[0] * t)
            g = int(BG_INNER[1] * (1 - t) + BG[1] * t)
            b = int(BG_INNER[2] * (1 - t) + BG[2] * t)
            draw.line([(0, y), (CARD_SIZE[0], y)], fill=(r, g, b, 255))

    frame = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(frame)
    _rounded_rect(fdraw, (0, 0, CARD_SIZE[0] - 1, CARD_SIZE[1] - 1), RADIUS, fill=None, outline=RED, width=BORDER)
    bg.alpha_composite(frame)
    return bg


# Template card (1983x793). Positions are pixels on the template.
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "punshmentimg", "levelup_bg.png")
AVATAR_CENTER = (290, 345)
AVATAR_RADIUS = 130
NAME_BOX = (125, 518, 460, 576)
OLD_LEVEL_CENTER = (1507, 375)
NEW_LEVEL_CENTER = (1798, 375)
LEVEL_PATCH = (122, 124)
LEVEL_FONT_SIZE = 84
PLATE_FILL = (10, 4, 4, 255)
NAME_PLATE_FILL = (14, 14, 16, 255)


# Design tiers: (min_level, hue shift 0-255). Red (original) -> other colour themes.
LEVEL_TIERS = (
    (0, 0),      # red (original)
    (5, 150),    # blue
    (10, 90),    # green
    (20, 190),   # purple
    (30, 125),   # cyan
    (50, 215),   # pink
    (100, 28),   # gold
)
_template_cache: dict[int, Image.Image] = {}


def _tier_shift(level: int) -> int:
    shift = 0
    for min_level, tier_shift in LEVEL_TIERS:
        if level >= min_level:
            shift = tier_shift
    return shift


def _themed_template(level: int) -> Image.Image:
    shift = _tier_shift(level)
    cached = _template_cache.get(shift)
    if cached is None:
        base = Image.open(TEMPLATE_PATH).convert("RGB")
        if shift:
            h, s, v = base.convert("HSV").split()
            # Only recolour saturated reds; gold logo, whites and darks stay as they are.
            red = h.point(lambda x: 255 if x <= 14 or x >= 240 else 0)
            vivid = s.point(lambda x: 255 if x > 90 else 0)
            mask = ImageChops.multiply(red, vivid).filter(ImageFilter.GaussianBlur(1))
            shifted = Image.merge("HSV", (h.point(lambda x: (x + shift) % 256), s, v)).convert("RGB")
            base = Image.composite(shifted, base, mask)
        cached = base.convert("RGBA")
        _template_cache[shift] = cached
    return cached.copy()


def _fit_font(draw, text: str, max_width: int, start_size: int):
    size = start_size
    while size > 14:
        font = _load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return _load_font(14)


def _clean_name(name: str) -> str:
    """Drop emoji / symbols the font can't render (they show up as empty boxes)."""
    kept = []
    for ch in name:
        if ord(ch) > 0xFFFF or unicodedata.category(ch) in ("So", "Cs", "Cn", "Cf", "Mn", "Me", "Cc"):
            continue
        kept.append(ch)
    cleaned = " ".join("".join(kept).split())
    return cleaned or "PLAYER"


def _draw_level_number(canvas: Image.Image, center: tuple[int, int], level: int):
    x, y = center
    font = _load_font(LEVEL_FONT_SIZE)
    text = str(level)

    # Feathered dark patch so the template's "10"/"11" disappear without a visible disc.
    pw, ph = LEVEL_PATCH
    patch = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(patch).rounded_rectangle((x - pw // 2, y - ph // 2, x + pw // 2, y + ph // 2), radius=24, fill=255)
    patch = patch.filter(ImageFilter.GaussianBlur(10))
    canvas.paste(Image.new("RGBA", canvas.size, PLATE_FILL), (0, 0), patch)

    # White -> light grey vertical gradient text, like the template digits.
    probe = ImageDraw.Draw(canvas)
    bbox = probe.textbbox((x, y), text, font=font, anchor="mm")
    mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(mask).text((x, y), text, font=font, fill=255, anchor="mm")
    gradient = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gradient)
    top, bottom = bbox[1], bbox[3]
    for row in range(top, bottom + 1):
        t = (row - top) / max(1, bottom - top)
        v = int(255 - 70 * t)
        gdraw.line([(bbox[0], row), (bbox[2], row)], fill=(v, v, v, 255))
    canvas.paste(gradient, (0, 0), mask)


async def build_level_up_card(member, old_level: int, new_level: int, background_url: str = BACKGROUND_URL) -> io.BytesIO:
    avatar_bytes = await _fetch_avatar(member)

    canvas = _themed_template(new_level)
    draw = ImageDraw.Draw(canvas)

    # Avatar inside the circle
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    size = AVATAR_RADIUS * 2
    avatar = ImageOps.fit(avatar, (size, size), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    canvas.paste(avatar, (AVATAR_CENTER[0] - AVATAR_RADIUS, AVATAR_CENTER[1] - AVATAR_RADIUS), mask)

    # Username (covers the "PLAYER NAME" placeholder)
    left, top, right, bottom = NAME_BOX
    draw.rounded_rectangle(NAME_BOX, radius=8, fill=NAME_PLATE_FILL)
    name = _clean_name(member.display_name).upper()
    name_font = _fit_font(draw, name, right - left - 24, 40)
    draw.text(((left + right) // 2, (top + bottom) // 2), name, font=name_font, fill=WHITE, anchor="mm")

    # Levels (cover the "10" / "11" placeholders)
    _draw_level_number(canvas, OLD_LEVEL_CENTER, old_level)
    _draw_level_number(canvas, NEW_LEVEL_CENTER, new_level)

    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
