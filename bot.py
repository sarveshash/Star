from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated
from PIL import Image, ImageSequence
import tempfile
import os
import requests

# Bot credentials
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize the bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command and send optimized GIF without reducing quality"""

    gif_url = "https://www.pkparaiso.com/imagenes/espada_escudo/sprites/animados-gigante/swoobat-s.gif"

    try:
        # Download the GIF
        response = requests.get(gif_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as downloaded_file:
            downloaded_file.write(response.content)
            downloaded_gif_path = downloaded_file.name

        with Image.open(downloaded_gif_path) as im:
            original_width, original_height = im.size

            frames = []
            durations = []

            for i, frame in enumerate(ImageSequence.Iterator(im)):
                # Optional: skip frames to reduce size further without reducing quality
                # if i % 2 == 1:
                #     continue

                # Create black background same size as original
                background = Image.new('RGBA', (original_width, original_height), color=(0, 0, 0, 255))

                frame_rgba = frame.convert('RGBA')

                # Paste the frame onto black background
                background.paste(frame_rgba, (0, 0), frame_rgba)

                frames.append(background.convert('P', palette=Image.ADAPTIVE))

                durations.append(frame.info.get('duration', 100))

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as modified_file:
            modified_gif_path = modified_file.name

        frames[0].save(
            modified_gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            disposal=2,
            optimize=True  # <-- Optimize GIF without losing quality
        )

        await event.respond(
            file=modified_gif_path,
            attributes=[DocumentAttributeAnimated()]
        )

        os.remove(downloaded_gif_path)
        os.remove(modified_gif_path)

    except requests.exceptions.RequestException as e:
        await event.respond(f"Failed to download GIF: {str(e)}")
    except Exception as e:
        await event.respond(f"Error processing GIF: {str(e)}")

print("Bot is running...")
bot.run_until_disconnected()
                                         
