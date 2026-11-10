import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PUNISHMENT_DIR = Path(__file__).parent / "punshmentimg"

TEMPLATES = {
    "ban": PUNISHMENT_DIR / "BANNED.jpg",
    "timeout": PUNISHMENT_DIR / "TIMEOUT.jpg",
    "chatmute": PUNISHMENT_DIR / "CHATMUTE.jpg",
    "voicemute": PUNISHMENT_DIR / "VOICEMUTE.jpg",
    "warn": PUNISHMENT_DIR / "warning.jpg",
}

LABELS = {
    "ban": "BAN",
    "timeout": "TIMEOUT",
    "chatmute": "CHAT MUTE",
    "voicemute": "VOICE MUTE",
    "warn": "WARN",
}

# Positions as fractions of template width/height (1408×768 templates)
TEXT_X_RATIO = 0.36
USERNAME_Y_RATIO = 0.315
PUNISHER_Y_RATIO = 0.398
REASON_Y_RATIO = 0.483
FONT_SIZE_RATIO = 0.042
TEXT_COLOR = "#d4a574"
MAX_FIELD_LEN = 48

# A long reason wraps under the underline instead of being cut at MAX_FIELD_LEN: it stays
# left of the minaret (REASON_MAX_X_RATIO) and uses at most REASON_MAX_LINES lines.
# A reason that fits on one line is drawn exactly where it always was.
REASON_MAX_LEN = 160
REASON_MAX_LINES = 4
REASON_MAX_X_RATIO = 0.70
REASON_LINE_SPACING = 1.15

# Punished member avatar (right side — sky area above palm trees)
AVATAR_SIZE_RATIO = 0.40
AVATAR_CENTER_X_RATIO = 0.24
AVATAR_CENTER_Y_RATIO = 0.70
AVATAR_RING_RATIO = 0.009
AVATAR_RING_COLOR = "#6b4f1d"


def _load_font(size: int):
    for path in (
        "C:/Windows/Fonts/timesbd.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/georgiab.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _truncate(text: str, max_len: int = MAX_FIELD_LEN) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _wrap_text(draw, text: str, font, max_width: float, max_lines: int) -> list[str]:
    """Greedy word wrap to max_width pixels; the last line ends with an ellipsis when cut."""
    text = " ".join((text or "").split())
    if not text:
        return [""]

    def fits(value: str) -> bool:
        return draw.textlength(value, font=font) <= max_width

    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        candidate = f"{current} {word}".strip()
        if fits(candidate):
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        # A single word wider than the whole line is split by characters.
        while not fits(word):
            cut = len(word) - 1
            while cut > 1 and not fits(word[:cut]):
                cut -= 1
            lines.append(word[:cut])
            word = word[cut:]
        current = word
    if current:
        lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and not fits(last + "…"):
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines


def _display_name(member) -> str:
    return member.display_name or member.name


async def _load_member_avatar(member) -> Image.Image:
    avatar_bytes = await member.display_avatar.replace(size=512, format="png").read()
    return Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")


def _build_circular_avatar(avatar: Image.Image, inner_size: int, ring_width: int) -> Image.Image:
    outer_size = inner_size + ring_width * 2
    framed = Image.new("RGBA", (outer_size, outer_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(framed)
    draw.ellipse((0, 0, outer_size - 1, outer_size - 1), fill=AVATAR_RING_COLOR)
    draw.ellipse(
        (ring_width, ring_width, outer_size - ring_width - 1, outer_size - ring_width - 1),
        fill="#1a0a0a",
    )

    avatar = avatar.resize((inner_size, inner_size))
    mask = Image.new("L", (inner_size, inner_size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, inner_size, inner_size), fill=255)

    circular = Image.new("RGBA", (inner_size, inner_size), (0, 0, 0, 0))
    circular.paste(avatar, (0, 0), mask=mask)
    framed.paste(circular, (ring_width, ring_width), circular)
    return framed


def _paste_member_avatar(canvas: Image.Image, avatar: Image.Image) -> None:
    width, height = canvas.size
    inner_size = max(48, int(height * AVATAR_SIZE_RATIO))
    ring_width = max(3, int(height * AVATAR_RING_RATIO))
    framed = _build_circular_avatar(avatar, inner_size, ring_width)

    center_x = int(width * AVATAR_CENTER_X_RATIO)
    center_y = int(height * AVATAR_CENTER_Y_RATIO)
    x = center_x - framed.width // 2
    y = center_y - framed.height // 2
    canvas.paste(framed, (x, y), framed)


async def build_punishment_card(
    member,
    punisher,
    reason: str,
    punishment_type: str,
) -> io.BytesIO:
    template_path = TEMPLATES.get(punishment_type)
    if not template_path or not template_path.is_file():
        raise FileNotFoundError(
            f"Missing template for {punishment_type!r}: {template_path}"
        )

    canvas = Image.open(template_path).convert("RGBA")
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    font_size = max(14, int(height * FONT_SIZE_RATIO))
    font = _load_font(font_size)

    try:
        avatar = await _load_member_avatar(member)
        _paste_member_avatar(canvas, avatar)
    except Exception as exc:
        print(f"Punishment avatar overlay failed for {member.id}: {exc}")

    text_x = int(width * TEXT_X_RATIO)
    reason_y = int(height * REASON_Y_RATIO)
    reason_lines = _wrap_text(
        draw,
        _truncate(reason or "No reason provided", REASON_MAX_LEN),
        font,
        int(width * REASON_MAX_X_RATIO) - text_x,
        REASON_MAX_LINES,
    )
    lines = [
        (int(height * USERNAME_Y_RATIO), _truncate(_display_name(member))),
        (int(height * PUNISHER_Y_RATIO), _truncate(_display_name(punisher))),
    ]
    for index, reason_line in enumerate(reason_lines):
        lines.append((reason_y + int(index * font_size * REASON_LINE_SPACING), reason_line))

    for y, text in lines:
        draw.text((text_x, y), text, font=font, fill=TEXT_COLOR, anchor="ls")

    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
