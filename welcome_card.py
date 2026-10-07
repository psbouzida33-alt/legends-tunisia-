import io
import os
import urllib.request

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pilmoji import Pilmoji

BACKGROUND_URL = "https://i.imgur.com/18F313v.png"

# Positions are fractions of the background size.
# Edit ONLY these values, then restart bot: python bot.py
CIRCLE_CENTER = (0.388, 0.430)   # (x of width, y of height)
AVATAR_RADIUS = 0.250            # fraction of height
NAME_BOX = (0.285, 0.625, 0.490, 0.740)  # left, top, right, bottom
FONT_HEIGHT = 0.120              # fraction of height

# Kept for the debug line in bot.py
AVATAR_SIZE = (AVATAR_RADIUS * 2, AVATAR_RADIUS * 2)
AVATAR_POSITION = CIRCLE_CENTER
FONT_SIZE = FONT_HEIGHT

FONT_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NotoSans-Bold.ttf")
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"


def _load_font(size: int):
    if not os.path.exists(FONT_FILENAME):
        try:
            print("Downloading font file...")
            urllib.request.urlretrieve(FONT_URL, FONT_FILENAME)
        except Exception as e:
            print(f"⚠️ Could not download font: {e}")

    for path in (
        FONT_FILENAME,
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/ARIAL.TTF",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


async def build_welcome_card(member, background_url: str = BACKGROUND_URL) -> io.BytesIO:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(background_url, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Failed to download background: HTTP {resp.status}")
            bg_bytes = await resp.read()

    image = Image.open(io.BytesIO(bg_bytes)).convert("RGBA")
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # --------------------------------------------------
    # 1. Avatar
    # --------------------------------------------------
    try:
        avatar_bytes = await member.display_avatar.replace(size=512, format="png").read()
        avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

        circle_center_x = int(width * CIRCLE_CENTER[0])
        circle_center_y = int(height * CIRCLE_CENTER[1])
        avatar_radius = int(height * AVATAR_RADIUS)

        avatar_size = (avatar_radius * 2, avatar_radius * 2)
        avatar_img = ImageOps.fit(avatar_img, avatar_size, method=Image.Resampling.LANCZOS)

        mask = Image.new("L", avatar_size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)

        image.paste(
            avatar_img,
            (circle_center_x - avatar_radius, circle_center_y - avatar_radius),
            mask,
        )
    except Exception as e:
        print(f"⚠️ Error processing avatar: {e}")

    # --------------------------------------------------
    # 2. Username & Box
    # --------------------------------------------------
    username = member.display_name

    box_left = int(width * NAME_BOX[0])
    box_top = int(height * NAME_BOX[1])
    box_right = int(width * NAME_BOX[2])
    box_bottom = int(height * NAME_BOX[3])

    draw.rounded_rectangle(
        (box_left, box_top, box_right, box_bottom),
        radius=10,
        fill=(10, 10, 14, 255),
    )

    font = _load_font(int(height * FONT_HEIGHT))

    bbox = draw.textbbox((0, 0), username, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = box_left + ((box_right - box_left) - text_w) / 2 - bbox[0]
    y = box_top + ((box_bottom - box_top) - text_h) / 2 - bbox[1]

    # Pilmoji renders emojis inside the username
    with Pilmoji(image) as pilmoji:
        pilmoji.text((int(x), int(y)), username, font=font, fill="white")

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output
