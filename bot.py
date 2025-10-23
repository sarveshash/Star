from telethon import TelegramClient, events
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
    """Handle /start command and send modified GIF with black background"""
    image_path = "model [C5BB805].gif"  # Your local GIF file

    try:
        with Image.open(image_path) as im:
            # Create a black background GIF by processing each frame
            frames = []
            for frame in ImageSequence.Iterator(im):
                frame = frame.convert("RGBA")
                background = Image.new("RGBA", frame.size, (0, 0, 0, 255))
                background.paste(frame, mask=frame)
                frames.append(background.convert("P"))

            # Save temporary GIF file
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp_file:
                modified_gif_path = tmp_file.name
                frames[0].save(
                    modified_gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    loop=0,
                    duration=im.info.get('duration', 100),
                    disposal=2
                )

            # Send the modified GIF
            await event.respond(file=modified_gif_path)

            # Clean up
            os.remove(modified_gif_path)

    except Exception as e:
        await event.respond(f"⚠️ Error processing GIF: {e}")

# Start the bot
print("Bot is running...")
bot.run_until_disconnected()
