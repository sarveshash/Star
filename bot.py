from telethon import TelegramClient, events
from PIL import Image, ImageSequence
import tempfile
import os

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Send GIF with black background without changing resolution or quality"""
    gif_path = "model [B307EB9].gif"

    try:
        with Image.open(gif_path) as im:
            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                # Convert to RGBA to handle transparency
                frame_rgba = frame.convert("RGBA")

                # Create black background
                bg = Image.new("RGBA", frame_rgba.size, (0, 0, 0, 255))
                bg.paste(frame_rgba, mask=frame_rgba.split()[3])  # composite

                frames.append(bg)
                durations.append(frame.info.get("duration", 100))

            # Save to temporary file (keep everything else unchanged)
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp:
                out_path = tmp.name

            frames[0].save(
                out_path,
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=im.info.get("loop", 0),
                disposal=2,
                optimize=False,
                quality=100
            )

            await event.respond(file=out_path)
            os.remove(out_path)

    except Exception as e:
        await event.respond(f"⚠️ Error: {e}")

print("Bot is running...")
bot.run_until_disconnected()
