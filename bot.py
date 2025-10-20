from telethon import TelegramClient, events
from PIL import Image
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
    """Handle /start command and send PNG with black background"""

    image_path = "frame_10_delay-0.03s.png"  # Your local PNG file

    try:
        with Image.open(image_path) as im:
            # Convert to RGBA to handle transparency
            rgba = im.convert("RGBA")

            # Create black background with same size
            background = Image.new("RGBA", im.size, (0, 0, 0, 255))
            background.paste(rgba, (0, 0), rgba)

            # Save temporary PNG file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                modified_png_path = tmp_file.name
                background.save(modified_png_path, format="PNG")

            # Send PNG
            await event.respond(file=modified_png_path)

            # Clean up
            os.remove(modified_png_path)

    except Exception as e:
        await event.respond(f"⚠️ Error processing PNG: {e}")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
