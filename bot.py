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
    """Handle /start command and send GIF with black background (no resolution change)"""
    image_path = "model [B307EB9].gif"  # Your local GIF file

    try:
        with Image.open(image_path) as im:
            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                frame = frame.convert("RGBA")

                # Replace transparency with black background
                background = Image.new("RGBA", frame.size, (0, 0, 0, 255))
                background.paste(frame, mask=frame.split()[3])  # paste using alpha channel

                frames.append(background.convert("P"))
                durations.append(frame.info.get('duration', im.info.get('duration', 100)))

            # Save with same resolution, duration, and looping info
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp_file:
                modified_gif_path = tmp_file.name
                frames[0].save(
                    modified_gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=im.info.get('loop', 0),
                    disposal=2
                )

            # Send GIF as document (keeps animation)
            await event.respond(file=modified_gif_path)

            os.remove(modified_gif_path)

    except Exception as e:
        await event.respond(f"⚠️ Error processing GIF: {e}")

print("Bot is running...")
bot.run_until_disconnected()
