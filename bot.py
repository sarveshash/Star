from telethon import TelegramClient, events
from PIL import Image, ImageSequence
import tempfile
import os

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Send GIF with green background"""
    gif_path = "model [B307EB9].gif"

    try:
        im = Image.open(gif_path)
        frames = []

        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            # Green background (plain green)
            background = Image.new("RGBA", frame.size, (0, 255, 0, 255))
            background.paste(frame, mask=frame)
            frames.append(background)

        # Save with green background to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_gif:
            frames[0].save(
                temp_gif.name,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=im.info.get('duration', 100),
                disposal=2
            )

            await event.respond(file=temp_gif.name)
            os.remove(temp_gif.name)

    except Exception as e:
        await event.respond(f"❌ Error: {e}")

print("✅ Bot is running...")
bot.run_until_disconnected()
