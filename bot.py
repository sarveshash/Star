from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated
from PIL import Image, ImageSequence
import tempfile
import os

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize the bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command and send GIF with black background (no resizing)"""

    gif_path = "frame_10_delay-0.03s.png"  # your local GIF

    try:
        with Image.open(gif_path) as im:
            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                # Convert frame to RGBA (so we can handle transparency)
                frame_rgba = frame.convert("RGBA")

                # Create black background with same size
                background = Image.new("RGBA", im.size, (0, 0, 0, 255))

                # Paste original frame onto black background
                background.paste(frame_rgba, (0, 0), frame_rgba)

                # Convert back to palette mode for GIF saving
                frames.append(background.convert("P", palette=Image.ADAPTIVE))
                durations.append(frame.info.get("duration", 100))

            # Save modified GIF
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as modified_file:
                modified_gif_path = modified_file.name
                frames[0].save(
                    modified_gif_path,
                    format='PNG',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0,
                    disposal=2
                )

            # Send the GIF
            await event.respond(
                file=modified_gif_path,
                attributes=[DocumentAttributeAnimated()]
            )

            # Clean up
            os.remove(modified_gif_path)

    except Exception as e:
        await event.respond(f"⚠️ Error processing GIF: {e}")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
