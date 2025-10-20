from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAnimated
from PIL import Image, ImageSequence
import tempfile
import os
import requests

# Your credentials (keep them safe!)
API_ID = 27715449
API_HASH = "dd3da7c5045f7679ff1f0ed0c82404e0"
BOT_TOKEN = "8474337967:AAH_mbpp4z1nOTDGyoJrM5r0Rii-b_TUcvA"

# Initialize the bot
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command and send resized GIF with black background"""

    gif_url = "https://www.pkparaiso.com/imagenes/espada_escudo/sprites/animados-gigante/swoobat-s.gif"

    try:
        # Download the GIF
        response = requests.get(gif_url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as downloaded_file:
            downloaded_file.write(response.content)
            downloaded_gif_path = downloaded_file.name

        # Open and process the GIF
        with Image.open(downloaded_gif_path) as im:
            original_width, original_height = im.size
            new_size = (original_width // 2, original_height // 2)  # Resize to 50%

            frames = []
            durations = []

            for frame in ImageSequence.Iterator(im):
                # Resize frame and convert to RGBA for transparency
                frame_resized = frame.resize(new_size, Image.ANTIALIAS).convert('RGBA')

                # Black background
                background = Image.new('RGBA', new_size, color='black')

                # Paste resized frame onto black background
                background.paste(frame_resized, (0, 0), frame_resized)

                # Convert to palette mode for GIF
                frames.append(background.convert('P', palette=Image.ADAPTIVE))
                durations.append(frame.info.get('duration', 100))

            # Save modified GIF
            with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as modified_file:
                modified_gif_path = modified_file.name
                frames[0].save(
                    modified_gif_path,
                    format='GIF',
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=0
                )

            # Send the resized GIF
            await event.respond(
                file=modified_gif_path,
                attributes=[DocumentAttributeAnimated()]
            )

            # Cleanup
            os.remove(downloaded_gif_path)
            os.remove(modified_gif_path)

    except requests.exceptions.RequestException as e:
        await event.respond(f"Failed to download GIF: {str(e)}")
    except Exception as e:
        await event.respond(f"Error processing GIF: {str(e)}")

print("Bot is running...")
bot.run_until_disconnected()
        
